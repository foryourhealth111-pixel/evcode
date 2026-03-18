from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "packages" / "assistant-adapters" / "python"))
sys.path.insert(0, str(REPO_ROOT / "packages" / "specialist-routing" / "python"))

from evcode_assistant_adapters import resolve_assistant_provider_catalog  # type: ignore
from evcode_specialist_routing import load_assistant_policy, load_routing_policy, resolve_specialist_route  # type: ignore


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_profile(repo_root: Path, channel: str) -> dict[str, Any]:
    return json.loads((repo_root / "profiles" / channel / "profile.json").read_text(encoding="utf-8"))


def load_baseline_families(repo_root: Path) -> dict[str, Any]:
    return json.loads((repo_root / "config" / "baseline-families.json").read_text(encoding="utf-8"))


def run_scenario(
    *,
    repo_root: Path,
    family_name: str,
    scenario: dict[str, Any],
    routing_policy: dict[str, Any],
) -> dict[str, Any]:
    channel = scenario["channel"]
    assistant_policy = load_assistant_policy(repo_root, channel)
    provider_catalog = resolve_assistant_provider_catalog(assistant_policy, env=os.environ)
    route = resolve_specialist_route(
        task=scenario["task"],
        channel=channel,
        routing_policy=routing_policy,
        assistant_policy=assistant_policy,
        provider_catalog=provider_catalog,
    )
    requested = sorted(item["assistant_name"] for item in route.get("requested_delegates", []))
    suppressed = sorted(item["assistant_name"] for item in route.get("suppressed_delegates", []))
    expected_requested = sorted(scenario.get("expected_requested_delegates", []))
    expected_suppressed = sorted(scenario.get("expected_suppressed_delegates", []))
    checks = {
        "route_kind": route["route_kind"] == scenario["expected_route_kind"],
        "requested_delegates": requested == expected_requested,
        "suppressed_delegates": suppressed == expected_suppressed,
        "codex_final_authority": bool(route.get("codex_final_authority")),
        "final_executor": route.get("final_executor") == "codex",
    }
    return {
        "id": scenario["id"],
        "family": family_name,
        "channel": channel,
        "task": scenario["task"],
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "expected": {
            "route_kind": scenario["expected_route_kind"],
            "requested_delegates": expected_requested,
            "suppressed_delegates": expected_suppressed,
        },
        "observed": {
            "route_kind": route["route_kind"],
            "classification": route["classification"],
            "requested_delegates": requested,
            "suppressed_delegates": suppressed,
            "degraded_delegates": sorted(item["assistant_name"] for item in route.get("degraded_delegates", [])),
            "active_delegates": sorted(item["assistant_name"] for item in route.get("active_delegates", [])),
        },
    }


def maybe_run_live_probe(repo_root: Path) -> dict[str, Any] | None:
    env = os.environ.copy()
    if env.get("EVCODE_ENABLE_LIVE_SPECIALISTS", "").lower() not in {"1", "true", "yes", "on"}:
        return None
    completed = subprocess.run(
        [
            "python3",
            str(repo_root / "scripts" / "verify" / "probe_assistant_providers.py"),
            "--repo-root",
            str(repo_root),
            "--channel",
            "standard",
            "--json",
            "--live",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    return json.loads(completed.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run EvCode baseline-family verification.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    baseline_families = load_baseline_families(repo_root)
    routing_policy = load_routing_policy(repo_root)
    standard_profile = load_profile(repo_root, "standard")
    benchmark_profile = load_profile(repo_root, "benchmark")

    profile_mapping = {
        "standard": standard_profile.get("baseline_family"),
        "benchmark": benchmark_profile.get("baseline_family"),
    }
    profile_checks = {
        "standard_family": profile_mapping["standard"] == "hybrid_governed",
        "benchmark_family": profile_mapping["benchmark"] == "core_benchmark",
    }

    family_reports: dict[str, Any] = {}
    for family_name, family in baseline_families.get("families", {}).items():
        scenario_reports = [
            run_scenario(repo_root=repo_root, family_name=family_name, scenario=scenario, routing_policy=routing_policy)
            for scenario in family.get("scenarios", [])
        ]
        family_reports[family_name] = {
            "channel": family.get("channel"),
            "mode": family.get("mode"),
            "reporting_group": family.get("reporting_group"),
            "requires_live_providers": family.get("requires_live_providers", False),
            "status": "pass" if all(item["status"] == "pass" for item in scenario_reports) else "fail",
            "scenarios": scenario_reports,
        }

    live_probe = maybe_run_live_probe(repo_root) if args.live else None
    payload = {
        "task": "evcode baseline family verification",
        "generated_at": utc_now(),
        "repo_root": str(repo_root),
        "status": "pass"
        if all(profile_checks.values()) and all(item["status"] == "pass" for item in family_reports.values())
        else "fail",
        "profile_mapping": profile_mapping,
        "profile_checks": profile_checks,
        "families": family_reports,
        "live_probe": live_probe,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"status={payload['status']}")
        for family_name, family in family_reports.items():
            print(f"{family_name}: {family['status']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
