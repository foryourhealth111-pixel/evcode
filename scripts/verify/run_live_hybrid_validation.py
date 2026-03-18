from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

PLANNING_TASK = "Plan a governed redesign brief for a visually ambitious but maintainable UI with requirements, architecture, and documentation notes"
VISUAL_TASK = "Design a polished responsive landing page with typography, spacing, motion, color, and visual polish"
MIXED_TASK = "Design and integrate a polished responsive marketing surface while preserving governed engineering constraints and backend-safe integration requirements"
BENCHMARK_TASK = "Design and integrate a polished responsive marketing surface while preserving governed engineering constraints"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_json(command: list[str], *, cwd: Path, env: dict[str, str]) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    return json.loads(completed.stdout)


def provider_env_ready(env: dict[str, str]) -> tuple[bool, str]:
    if env.get("EVCODE_ENABLE_LIVE_SPECIALISTS", "").lower() not in {"1", "true", "yes", "on"}:
        return False, "live specialists opt-in env is disabled"
    if not env.get("EVCODE_RIGHTCODES_API_KEY"):
        return False, "missing EVCODE_RIGHTCODES_API_KEY"
    return True, "ready"


def summarize_standard_run(name: str, payload: dict[str, Any]) -> dict[str, Any]:
    route = payload["specialist_routing"]
    results: dict[str, Any] = {}
    for assistant_name, result_path in payload["artifacts"].get("specialist_results", {}).items():
        result_payload = json.loads(Path(result_path).read_text(encoding="utf-8"))
        results[assistant_name] = {
            "status": result_payload.get("status"),
            "recommended_next_actor": result_payload.get("recommended_next_actor"),
        }
    return {
        "name": name,
        "route_kind": route["route_kind"],
        "classification": route["classification"],
        "requested": [item["assistant_name"] for item in route.get("requested_delegates", [])],
        "active": [item["assistant_name"] for item in route.get("active_delegates", [])],
        "suppressed": [item["assistant_name"] for item in route.get("suppressed_delegates", [])],
        "result_statuses": {k: v["status"] for k, v in results.items()},
        "next_actors": {k: v["recommended_next_actor"] for k, v in results.items()},
        "summary_path": payload.get("summary_path"),
    }


def validate(repo_root: Path, keep_temp: bool) -> dict[str, Any]:
    env = os.environ.copy()
    live_ready, live_reason = provider_env_ready(env)
    if not live_ready:
        return {
            "task": "evcode live hybrid validation",
            "generated_at": utc_now(),
            "repo_root": str(repo_root),
            "status": "skipped",
            "reason": live_reason,
        }

    temp_root = Path(tempfile.mkdtemp(prefix="evcode-live-hybrid-"))
    try:
        payload: dict[str, Any] = {
            "task": "evcode live hybrid validation",
            "generated_at": utc_now(),
            "repo_root": str(repo_root),
            "validation_root": str(temp_root),
        }

        wave1 = run_json(
            [
                "node",
                str(repo_root / "apps" / "evcode" / "bin" / "evcode.js"),
                "probe-providers",
                "--json",
                "--live",
            ],
            cwd=repo_root,
            env=env,
        )
        payload["live_probe"] = {
            item["assistant_name"]: {
                "status": item["status"],
                "reason": item["reason"],
                "recommended_next_actor": item.get("recommended_next_actor"),
            }
            for item in wave1["results"]
        }

        standard_runs = {}
        for name, task in (("claude_planning", PLANNING_TASK), ("gemini_visual", VISUAL_TASK), ("mixed_ui", MIXED_TASK)):
            artifacts_root = temp_root / name
            run_payload = run_json(
                [
                    "node",
                    str(repo_root / "apps" / "evcode" / "bin" / "evcode.js"),
                    "run",
                    "--task",
                    task,
                    "--artifacts-root",
                    str(artifacts_root),
                    "--run-id",
                    f"live-{name}",
                ],
                cwd=repo_root,
                env=env,
            )
            standard_runs[name] = summarize_standard_run(name, run_payload)
        payload["standard_runs"] = standard_runs

        fake_codex = temp_root / "fake_codex.py"
        fake_codex.write_text(
            """#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path
argv = sys.argv[1:]
for index, token in enumerate(argv):
    if token == '--output-last-message' and index + 1 < len(argv):
        Path(argv[index + 1]).write_text('live hybrid benchmark control completed', encoding='utf-8')
        break
sys.exit(0)
""",
            encoding="utf-8",
        )
        fake_codex.chmod(0o755)
        benchmark_workspace = temp_root / "benchmark-workspace"
        benchmark_workspace.mkdir(parents=True, exist_ok=True)
        benchmark_payload = run_json(
            [
                "node",
                str(repo_root / "apps" / "evcode-bench" / "bin" / "evcode-bench.js"),
                "run",
                "--task",
                BENCHMARK_TASK,
                "--workspace",
                str(benchmark_workspace),
                "--artifacts-root",
                str(temp_root / "benchmark-artifacts"),
                "--run-id",
                "live-benchmark-control",
            ],
            cwd=repo_root,
            env={**env, "EVCODE_BENCH_HOST_BIN": str(fake_codex)},
        )
        payload["benchmark_control"] = {
            "route_kind": benchmark_payload["specialist_routing"]["route_kind"],
            "requested": [item["assistant_name"] for item in benchmark_payload["specialist_routing"].get("requested_delegates", [])],
            "suppressed": [item["assistant_name"] for item in benchmark_payload["specialist_routing"].get("suppressed_delegates", [])],
            "summary_path": benchmark_payload.get("summary_path"),
        }

        payload["checks"] = {
            "probe_live_compatible": all(item["status"] == "live_compatible" for item in payload["live_probe"].values()),
            "claude_planning_requested": standard_runs["claude_planning"]["requested"] == ["claude"],
            "gemini_visual_requests_gemini": "gemini" in standard_runs["gemini_visual"]["requested"],
            "mixed_ui_requests_both": set(standard_runs["mixed_ui"]["requested"]) == {"claude", "gemini"},
            "benchmark_control_suppressed": payload["benchmark_control"]["route_kind"] == "codex_only_benchmark" and set(payload["benchmark_control"]["suppressed"]) == {"claude", "gemini"},
            "all_next_actors_codex": all(
                next_actor == "codex"
                for run in standard_runs.values()
                for next_actor in run["next_actors"].values()
            ),
        }
        payload["status"] = "pass" if all(payload["checks"].values()) else "fail"
        return payload
    finally:
        if not keep_temp:
            shutil.rmtree(temp_root, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run live opt-in EvCode hybrid validation.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--keep-temp", action="store_true")
    args = parser.parse_args()

    payload = validate(Path(args.repo_root).resolve(), keep_temp=args.keep_temp)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"status={payload['status']}")
        if payload.get("reason"):
            print(payload["reason"])
    return 0 if payload["status"] in {"pass", "skipped"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
