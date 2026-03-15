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
        self.assertEqual(distributions["channels"]["standard"]["default_mode"], standard_profile["default_mode"])
        self.assertEqual(distributions["channels"]["benchmark"]["default_mode"], benchmark_profile["default_mode"])

    def test_host_integration_requires_vibe_suffix(self) -> None:
        host = json.loads((REPO_ROOT / "config" / "host-integration.json").read_text(encoding="utf-8"))
        self.assertTrue(host["user_turn_policy"]["must_append_vibe_suffix"])
        self.assertEqual(" $vibe", host["user_turn_policy"]["suffix"])
        self.assertTrue(host["subagent_policy"]["must_append_vibe_suffix"])
        self.assertEqual(" $vibe", host["subagent_policy"]["suffix"])
        self.assertEqual("host_patch_required", host["physical_suffix_enforcement"]["strategy"])
        self.assertTrue(host["physical_suffix_enforcement"]["patch_file"].endswith("subagent-vibe-suffix.patch"))


if __name__ == "__main__":
    unittest.main()
