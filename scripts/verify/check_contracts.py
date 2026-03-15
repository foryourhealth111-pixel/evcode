from __future__ import annotations

import json
from pathlib import Path


EXPECTED_STAGE_ORDER = [
    "skeleton_check",
    "deep_interview",
    "requirement_doc",
    "xl_plan",
    "plan_execute",
    "phase_cleanup",
]


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    runtime_contract = json.loads((repo_root / "config" / "runtime-contract.json").read_text(encoding="utf-8"))
    distributions = json.loads((repo_root / "config" / "distributions.json").read_text(encoding="utf-8"))
    standard_profile = json.loads((repo_root / "profiles" / "standard" / "profile.json").read_text(encoding="utf-8"))
    benchmark_profile = json.loads((repo_root / "profiles" / "benchmark" / "profile.json").read_text(encoding="utf-8"))

    assert runtime_contract["stage_order"] == EXPECTED_STAGE_ORDER, runtime_contract["stage_order"]
    assert distributions["channels"]["standard"]["default_mode"] == "interactive_governed"
    assert distributions["channels"]["benchmark"]["default_mode"] == "benchmark_autonomous"
    assert standard_profile["default_mode"] == "interactive_governed"
    assert benchmark_profile["default_mode"] == "benchmark_autonomous"
    assert (repo_root / "docs" / "architecture" / "evcode-host-runtime-bridge.md").exists()
    assert (repo_root / "docs" / "architecture" / "evcode-benchmark-adapter.md").exists()
    assert (repo_root / "profiles" / "standard" / "config.toml").exists()
    assert (repo_root / "profiles" / "benchmark" / "config.toml").exists()
    assert (repo_root / "scripts" / "hooks" / "user_prompt_submit.py").exists()
    assert (repo_root / "core" / "skill-contracts" / "v1" / "vibe.json").exists()
    assert (repo_root / "protocols" / "runtime.md").exists()
    assert (repo_root / "vendor" / "codex-host" / "UPSTREAM.md").exists()
    assert (repo_root / "runtime" / "vco" / "required-runtime-markers.json").exists()
    print("contract checks: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
