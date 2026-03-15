from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "packages" / "host-integration" / "python"))

from upstream_bridge import analyze_materialized_host


class HostBridgeAnalysisTests(unittest.TestCase):
    def test_materialized_host_requires_physical_suffix_patch(self) -> None:
        analysis = analyze_materialized_host(REPO_ROOT)
        self.assertEqual("stellarlinkco/codex", analysis["host"])
        self.assertTrue(analysis["user_prompt_submit"]["hook_receives_prompt_snapshot"])
        self.assertTrue(analysis["user_prompt_submit"]["hook_updated_input_is_pre_tool_use_only"])
        self.assertTrue(analysis["user_prompt_submit"]["dispatcher_records_context_only"])
        self.assertTrue(analysis["user_prompt_submit"]["turn_uses_original_items_after_hook"])
        self.assertTrue(analysis["user_prompt_submit"]["requires_host_patch_for_physical_suffix"])
        self.assertTrue(analysis["subagent_start"]["hook_supports_additional_context"])
        self.assertTrue(analysis["subagent_start"]["hook_updated_input_is_pre_tool_use_only"])
        self.assertTrue(analysis["subagent_start"]["dispatcher_collects_context_only"])
        self.assertTrue(analysis["subagent_start"]["requires_host_patch_for_physical_suffix"])
        self.assertGreaterEqual(len(analysis["evidence"]), 10)

    def test_patch_inventory_is_concrete(self) -> None:
        analysis = analyze_materialized_host(REPO_ROOT)
        patch_path = REPO_ROOT / analysis["subagent_start"]["recommended_patch"]
        patch_text = patch_path.read_text(encoding="utf-8")
        self.assertIn("append_vibe_suffix_to_input_items", patch_text)
        self.assertIn("core/src/codex.rs", patch_text)
        self.assertIn("spawn.rs", patch_text)
        self.assertIn("spawn_team.rs", patch_text)
        self.assertIn(" $vibe", patch_text)

    def test_host_contract_matches_analysis(self) -> None:
        analysis = analyze_materialized_host(REPO_ROOT)
        contract = json.loads((REPO_ROOT / "config" / "host-integration.json").read_text(encoding="utf-8"))
        self.assertEqual(
            contract["physical_suffix_enforcement"]["patch_file"],
            analysis["user_prompt_submit"]["recommended_patch"],
        )
        self.assertEqual(
            contract["physical_suffix_enforcement"]["patch_file"],
            analysis["subagent_start"]["recommended_patch"],
        )


if __name__ == "__main__":
    unittest.main()
