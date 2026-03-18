from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "packages" / "delegation-contracts" / "python"))

from evcode_delegation_contracts import DelegationContractError, build_result_packet, build_task_packet


class DelegationContractTests(unittest.TestCase):
    def test_build_task_packet_accepts_valid_payload(self) -> None:
        packet = build_task_packet(
            specialist_name="claude",
            task_id="run-1-claude",
            run_id="run-1",
            repository_path_summary="repo=evcode",
            file_scope=["scripts/", "tests/"],
            task_goal="Plan a redesign",
            constraints=["Stay advisory only"],
            acceptance_criteria=["Be actionable"],
            non_goals=["Do not claim completion"],
            architecture_notes=["Codex is final executor"],
            design_system_notes=["Prefer explicit rationale"],
            allowed_authority_tier="advisory_only",
            expected_output_type="plan_artifact",
        )
        self.assertEqual("claude", packet["specialist_name"])
        self.assertEqual("advisory_only", packet["allowed_authority_tier"])
        self.assertEqual("vco_compiled_capsule", packet["skill_capsule"]["compiler"])
        self.assertEqual("proxy_mediated", packet["allowed_capabilities"]["mode"])
        self.assertEqual("vco_artifacts", packet["memory_policy"]["owner"])
        self.assertIn("routing_receipt", packet["required_receipts"])

    def test_build_task_packet_rejects_invalid_authority(self) -> None:
        with self.assertRaises(DelegationContractError):
            build_task_packet(
                specialist_name="claude",
                task_id="run-1-claude",
                run_id="run-1",
                repository_path_summary="repo=evcode",
                file_scope=["scripts/"],
                task_goal="Plan a redesign",
                constraints=["Stay advisory only"],
                acceptance_criteria=["Be actionable"],
                non_goals=["Do not claim completion"],
                architecture_notes=["Codex is final executor"],
                design_system_notes=["Prefer explicit rationale"],
                allowed_authority_tier="unsafe",
                expected_output_type="plan_artifact",
            )

    def test_build_task_packet_rejects_invalid_capability_mode(self) -> None:
        with self.assertRaises(DelegationContractError):
            build_task_packet(
                specialist_name="claude",
                task_id="run-1-claude",
                run_id="run-1",
                repository_path_summary="repo=evcode",
                file_scope=["scripts/"],
                task_goal="Plan a redesign",
                constraints=["Stay advisory only"],
                acceptance_criteria=["Be actionable"],
                non_goals=["Do not claim completion"],
                architecture_notes=["Codex is final executor"],
                design_system_notes=["Prefer explicit rationale"],
                allowed_authority_tier="advisory_only",
                expected_output_type="plan_artifact",
                extras={
                    "allowed_capabilities": {
                        "mode": "unsafe",
                        "direct_read_only_allowlist": [],
                        "proxy_allowlist": [],
                        "mutation_allowlist": [],
                        "denied": [],
                    }
                },
            )

    def test_build_result_packet_accepts_valid_payload(self) -> None:
        packet = build_result_packet(
            specialist_name="gemini",
            task_id="run-1-gemini",
            summary="Provide a visual plan",
            assumptions=["UI scope only"],
            proposed_actions=["Refine spacing"],
            files_touched_or_proposed=["apps/"],
            confidence_level=0.7,
            unresolved_risks=["Needs Codex integration"],
            recommended_next_actor="codex",
        )
        self.assertEqual("gemini", packet["specialist_name"])
        self.assertEqual("codex", packet["recommended_next_actor"])
        self.assertEqual([], packet["capability_requests"])
        self.assertEqual([], packet["receipt_refs"])

    def test_build_result_packet_rejects_invalid_confidence(self) -> None:
        with self.assertRaises(DelegationContractError):
            build_result_packet(
                specialist_name="gemini",
                task_id="run-1-gemini",
                summary="Provide a visual plan",
                assumptions=["UI scope only"],
                proposed_actions=["Refine spacing"],
                files_touched_or_proposed=["apps/"],
                confidence_level=1.5,
                unresolved_risks=["Needs Codex integration"],
                recommended_next_actor="codex",
            )


if __name__ == "__main__":
    unittest.main()
