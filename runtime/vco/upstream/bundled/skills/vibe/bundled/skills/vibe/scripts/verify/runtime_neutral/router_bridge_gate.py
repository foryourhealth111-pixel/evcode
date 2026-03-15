#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def resolve_repo_root(start_path: Path) -> Path:
    current = start_path.resolve()
    if current.is_file():
        current = current.parent
    candidates: list[Path] = []
    while True:
        if (current / "config" / "version-governance.json").exists():
            candidates.append(current)
        if current.parent == current:
            break
        current = current.parent
    if not candidates:
        raise RuntimeError(f"Unable to resolve VCO repo root from: {start_path}")
    git_candidates = [candidate for candidate in candidates if (candidate / ".git").exists()]
    return git_candidates[-1] if git_candidates else candidates[-1]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def run_bridge(repo_root: Path, prompt: str, grade: str, task_type: str) -> dict[str, Any]:
    bridge = repo_root / "scripts" / "router" / "invoke-pack-route.py"
    command = [
        sys.executable,
        str(bridge),
        "--prompt",
        prompt,
        "--grade",
        grade,
        "--task-type",
        task_type,
        "--force-runtime-neutral",
    ]
    completed = subprocess.run(command, cwd=repo_root, capture_output=True, text=True, check=True)
    return json.loads(completed.stdout)


def evaluate(repo_root: Path) -> dict[str, Any]:
    route_fixture = load_json(repo_root / "tests" / "replay" / "route" / "recovery-wave-curated-prompts.json")
    platform_fixture = load_json(repo_root / "tests" / "replay" / "platform" / "linux-without-pwsh.json")

    assertions: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []

    def record(condition: bool, message: str) -> None:
        print(f"[{'PASS' if condition else 'FAIL'}] {message}")
        assertions.append({"ok": condition, "message": message})

    record(platform_fixture["lane"] == "linux_without_pwsh", "platform fixture lane is linux_without_pwsh")
    record(platform_fixture["constraints"]["force_runtime_neutral"] is True, "platform fixture requires runtime-neutral execution")

    required_fields = set(platform_fixture["constraints"]["required_contract_fields"])
    for case in route_fixture["cases"]:
        result = run_bridge(repo_root, case["prompt"], case["grade"], case["task_type"])
        observed_fields = set(result.keys())
        missing_fields = sorted(required_fields - observed_fields)
        expected = case["expected"]
        expected_modes = expected.get("allowed_route_modes") or ([expected["route_mode"]] if expected.get("route_mode") else [])
        selected = result.get("selected") or {}
        ok = (
            not missing_fields
            and (not expected_modes or result.get("route_mode") in expected_modes)
            and (expected.get("selected_pack") is None or selected.get("pack_id") == expected.get("selected_pack"))
            and (expected.get("selected_skill") is None or selected.get("skill") == expected.get("selected_skill"))
        )
        record(ok, f"{case['id']} satisfies runtime-neutral route expectation")
        results.append(
            {
                "id": case["id"],
                "prompt": case["prompt"],
                "route_mode": result.get("route_mode"),
                "route_reason": result.get("route_reason"),
                "selected_pack": selected.get("pack_id"),
                "selected_skill": selected.get("skill"),
                "missing_fields": missing_fields,
            }
        )

    failures = sum(1 for item in assertions if not item["ok"])
    return {
        "gate": "runtime-neutral-router-bridge-gate",
        "generated_at": utc_now(),
        "repo_root": str(repo_root),
        "gate_result": "PASS" if failures == 0 else "FAIL",
        "assertions": assertions,
        "results": results,
        "summary": {
            "failures": failures,
            "total_assertions": len(assertions),
        },
    }


def write_artifacts(repo_root: Path, artifact: dict[str, Any]) -> None:
    output_dir = repo_root / "outputs" / "verify"
    write_text(output_dir / "runtime-neutral-router-bridge-gate.json", json.dumps(artifact, ensure_ascii=False, indent=2) + "\n")
    lines = [
        "# Runtime-Neutral Router Bridge Gate",
        "",
        f"- Gate Result: **{artifact['gate_result']}**",
        f"- Failures: {artifact['summary']['failures']}",
        "",
        "## Results",
        "",
    ]
    for row in artifact["results"]:
        lines.append(
            f"- `{row['id']}` -> mode=`{row['route_mode']}` pack=`{row['selected_pack']}` skill=`{row['selected_skill']}`"
        )
    lines.append("")
    write_text(output_dir / "runtime-neutral-router-bridge-gate.md", "\n".join(lines))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify the runtime-neutral router bridge against curated recovery prompts.")
    parser.add_argument("--write-artifacts", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    repo_root = resolve_repo_root(Path(__file__))
    artifact = evaluate(repo_root)
    if args.write_artifacts:
        write_artifacts(repo_root, artifact)
    return 0 if artifact["gate_result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
