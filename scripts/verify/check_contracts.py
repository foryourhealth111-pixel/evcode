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
    baseline_families = json.loads((repo_root / "config" / "baseline-families.json").read_text(encoding="utf-8"))

    assert runtime_contract["stage_order"] == EXPECTED_STAGE_ORDER, runtime_contract["stage_order"]
    assert distributions["channels"]["standard"]["default_mode"] == "interactive_governed"
    assert distributions["channels"]["benchmark"]["default_mode"] == "benchmark_autonomous"
    assert standard_profile["default_mode"] == "interactive_governed"
    assert benchmark_profile["default_mode"] == "benchmark_autonomous"
    assert standard_profile["assistant_policy"] == "config/assistant-policy.standard.json"
    assert benchmark_profile["assistant_policy"] == "config/assistant-policy.benchmark.json"
    assert standard_profile["specialist_routing"] == "config/specialist-routing.json"
    assert benchmark_profile["specialist_routing"] == "config/specialist-routing.json"
    assert standard_profile["baseline_family"] == "hybrid_governed"
    assert benchmark_profile["baseline_family"] == "core_benchmark"
    assert standard_profile["baseline_families_config"] == "config/baseline-families.json"
    assert benchmark_profile["baseline_families_config"] == "config/baseline-families.json"
    assert "hybrid_governed" in baseline_families["families"]
    assert "core_benchmark" in baseline_families["families"]

    for relative_path in (
        "docs/architecture/evcode-host-runtime-bridge.md",
        "docs/architecture/evcode-benchmark-adapter.md",
        "profiles/standard/config.toml",
        "profiles/benchmark/config.toml",
        "scripts/hooks/user_prompt_submit.py",
        "core/skill-contracts/v1/vibe.json",
        "protocols/runtime.md",
        "vendor/codex-host/UPSTREAM.md",
        "runtime/vco/required-runtime-markers.json",
        "config/assistant-policy.standard.json",
        "config/assistant-policy.benchmark.json",
        "config/specialist-routing.json",
        "config/baseline-families.json",
        "config/assistant-providers.env.example",
        "docs/configuration/openai-compatible-provider-setup.md",
        "scripts/verify/probe_assistant_providers.py",
        "scripts/verify/run_hybrid_baseline.py",
        "scripts/verify/validate_distribution_portability.py",
        "scripts/verify/run_live_hybrid_validation.py",
        "packages/delegation-contracts/README.md",
        "packages/assistant-adapters/README.md",
        "packages/specialist-routing/README.md",
    ):
        assert (repo_root / relative_path).exists(), relative_path

    print("contract checks: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
