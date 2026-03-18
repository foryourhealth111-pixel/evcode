from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_STAGE_ORDER = [
    "skeleton_check",
    "deep_interview",
    "requirement_doc",
    "xl_plan",
    "plan_execute",
    "phase_cleanup",
]


class ContractTests(unittest.TestCase):
    def test_runtime_contract_stage_order(self) -> None:
        contract = json.loads((REPO_ROOT / "config" / "runtime-contract.json").read_text(encoding="utf-8"))
        self.assertEqual(EXPECTED_STAGE_ORDER, contract["stage_order"])

    def test_distribution_defaults_match_profiles(self) -> None:
        distributions = json.loads((REPO_ROOT / "config" / "distributions.json").read_text(encoding="utf-8"))
        standard_profile = json.loads((REPO_ROOT / "profiles" / "standard" / "profile.json").read_text(encoding="utf-8"))
        benchmark_profile = json.loads((REPO_ROOT / "profiles" / "benchmark" / "profile.json").read_text(encoding="utf-8"))
        baseline_families = json.loads((REPO_ROOT / "config" / "baseline-families.json").read_text(encoding="utf-8"))
        self.assertEqual(distributions["channels"]["standard"]["default_mode"], standard_profile["default_mode"])
        self.assertEqual(distributions["channels"]["benchmark"]["default_mode"], benchmark_profile["default_mode"])
        self.assertEqual("config/assistant-policy.standard.json", standard_profile["assistant_policy"])
        self.assertEqual("config/assistant-policy.benchmark.json", benchmark_profile["assistant_policy"])
        self.assertEqual("config/specialist-routing.json", standard_profile["specialist_routing"])
        self.assertEqual("config/specialist-routing.json", benchmark_profile["specialist_routing"])
        self.assertEqual("hybrid_governed", standard_profile["baseline_family"])
        self.assertEqual("core_benchmark", benchmark_profile["baseline_family"])
        self.assertEqual("config/baseline-families.json", standard_profile["baseline_families_config"])
        self.assertEqual("config/baseline-families.json", benchmark_profile["baseline_families_config"])
        self.assertIn("hybrid_governed", baseline_families["families"])
        self.assertIn("core_benchmark", baseline_families["families"])

    def test_host_integration_requires_vibe_suffix(self) -> None:
        host = json.loads((REPO_ROOT / "config" / "host-integration.json").read_text(encoding="utf-8"))
        self.assertTrue(host["user_turn_policy"]["must_append_vibe_suffix"])
        self.assertEqual(" $vibe", host["user_turn_policy"]["suffix"])
        self.assertTrue(host["subagent_policy"]["must_append_vibe_suffix"])
        self.assertEqual(" $vibe", host["subagent_policy"]["suffix"])
        self.assertEqual("host_patch_required", host["physical_suffix_enforcement"]["strategy"])
        self.assertTrue(host["physical_suffix_enforcement"]["patch_file"].endswith("subagent-vibe-suffix.patch"))

    def test_specialist_configs_exist(self) -> None:
        for relative_path in (
            "config/assistant-policy.standard.json",
            "config/assistant-policy.benchmark.json",
            "config/specialist-routing.json",
            "config/baseline-families.json",
            "packages/delegation-contracts/README.md",
            "packages/assistant-adapters/README.md",
            "packages/specialist-routing/README.md",
            "docs/architecture/evcode-governed-specialist-repair.md",
        ):
            self.assertTrue((REPO_ROOT / relative_path).exists(), relative_path)

    def test_governance_configs_expose_memory_and_capability_policy(self) -> None:
        standard_policy = json.loads((REPO_ROOT / "config" / "assistant-policy.standard.json").read_text(encoding="utf-8"))
        routing_policy = json.loads((REPO_ROOT / "config" / "specialist-routing.json").read_text(encoding="utf-8"))
        self.assertEqual("vco_artifacts", standard_policy["persistent_memory_owner"])
        self.assertIn("proxy_mediated", standard_policy["capability_policy_classes"])
        self.assertIn("capability_policy", routing_policy)
        self.assertEqual("vco_artifacts", routing_policy["memory_policy"]["owner"])
        self.assertIn("compiler", routing_policy["skill_capsule_defaults"])


if __name__ == "__main__":
    unittest.main()
