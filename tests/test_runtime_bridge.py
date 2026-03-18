from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / 'scripts' / 'runtime'))
sys.path.insert(0, str(REPO_ROOT / 'packages' / 'assistant-adapters' / 'python'))
sys.path.insert(0, str(REPO_ROOT / 'packages' / 'specialist-routing' / 'python'))

from evcode_assistant_adapters import resolve_assistant_provider_catalog
from evcode_specialist_routing import load_assistant_policy, load_routing_policy, resolve_specialist_route
from runtime_lib import GovernedRuntimeConfig, build_specialist_delegation_payloads, normalize_live_result
EXPECTED_STAGE_ORDER = [
    "skeleton_check",
    "deep_interview",
    "requirement_doc",
    "xl_plan",
    "plan_execute",
    "phase_cleanup",
]


class RuntimeBridgeTests(unittest.TestCase):
    def test_delegation_payloads_split_autonomous_briefs_from_packetized_packets(self) -> None:
        assistant_policy = load_assistant_policy(REPO_ROOT, "standard")
        routing_policy = load_routing_policy(REPO_ROOT)
        provider_catalog = resolve_assistant_provider_catalog(assistant_policy, env={})
        config = GovernedRuntimeConfig(
            mode="interactive_governed",
            task="Plan the project architecture and write a documentation brief for an ambiguous redesign",
            repo_root=REPO_ROOT,
            workspace=REPO_ROOT,
            artifacts_root=REPO_ROOT,
            run_id="bridge-payloads",
            channel="standard",
            profile="default",
        )
        planning_route = resolve_specialist_route(
            task=config.task,
            channel="standard",
            routing_policy=routing_policy,
            assistant_policy=assistant_policy,
            provider_catalog=provider_catalog,
        )
        planning_packets, planning_briefs = build_specialist_delegation_payloads(config, planning_route)
        self.assertFalse(planning_packets)
        self.assertIn("claude", planning_briefs)
        self.assertEqual("autonomous", planning_briefs["claude"]["exploration_mode"])
        self.assertIn("mission_brief", planning_briefs["claude"])
        self.assertIn("autonomy_instructions", planning_briefs["claude"])
        self.assertIn("skill_capsule", planning_briefs["claude"])
        self.assertEqual("vco_artifacts", planning_briefs["claude"]["memory_policy"]["owner"])

        visual_route = resolve_specialist_route(
            task="Design a responsive frontend landing page with typography, spacing, motion, and visual polish",
            channel="standard",
            routing_policy=routing_policy,
            assistant_policy=assistant_policy,
            provider_catalog=provider_catalog,
        )
        visual_packets, visual_briefs = build_specialist_delegation_payloads(config, visual_route)
        self.assertIn("gemini", visual_packets)
        self.assertFalse(visual_briefs)
        self.assertEqual("packetized", visual_packets["gemini"]["exploration_mode"])
        self.assertEqual("visual_plan", visual_packets["gemini"]["expected_output_type"])
        self.assertEqual("proxy_mediated", visual_packets["gemini"]["allowed_capabilities"]["mode"])
        self.assertIn("capability_proxy_receipt", visual_packets["gemini"]["required_receipts"])
        self.assertTrue(visual_packets["gemini"]["authoritative_context_refs"])

    def test_normalize_live_result_coerces_provider_friendly_shapes(self) -> None:
        result = normalize_live_result(
            {
                "specialist_name": "gemini",
                "task_id": "run-1-gemini",
                "file_scope": ["apps/"],
                "expected_output_type": "visual_plan",
                "exploration_mode": "packetized",
            },
            {
                "provider": "rightcodes_gemini",
                "base_url": "https://right.codes/gemini/v1",
                "model": "gemini-2.5-pro",
            },
            {
                "summary": "visual plan",
                "assumptions": ["a1"],
                "proposed_actions": [{"description": "tighten spacing"}],
                "files_touched_or_proposed": ["apps/site"],
                "confidence_level": "high",
                "unresolved_risks": ["r1"],
                "recommended_next_actor": "Codex",
                "capability_requests": [{"capability": "figma_context", "mode": "proxy_mediated"}],
            },
        )
        self.assertEqual("completed_live_advisory", result["status"])
        self.assertEqual(["tighten spacing"], result["proposed_actions"])
        self.assertEqual(0.8, result["confidence_level"])
        self.assertEqual("codex", result["recommended_next_actor"])
        self.assertEqual("figma_context", result["capability_requests"][0]["capability"])

    def test_standard_run_writes_governed_and_specialist_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            completed = subprocess.run(
                [
                    "node",
                    str(REPO_ROOT / "apps" / "evcode" / "bin" / "evcode.js"),
                    "run",
                    "--task",
                    "Design a polished frontend UX and implement a governed standard channel smoke test",
                    "--artifacts-root",
                    tempdir,
                    "--run-id",
                    "standard-smoke",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(completed.stdout)
            self.assertEqual("interactive_governed", payload["mode"])
            self.assertEqual("standard", payload["channel"])
            self.assertEqual(EXPECTED_STAGE_ORDER, payload["stage_order"])
            requirement_doc = Path(payload["artifacts"]["requirement_doc"])
            execution_plan = Path(payload["artifacts"]["execution_plan"])
            cleanup_receipt = Path(payload["artifacts"]["cleanup_receipt"])
            specialist_route = Path(payload["artifacts"]["specialist_routing_receipt"])
            assistant_policy = Path(payload["artifacts"]["assistant_policy_snapshot"])
            codex_integration = Path(payload["artifacts"]["codex_integration_receipt"])
            capability_proxy = Path(payload["artifacts"]["capability_proxy_receipt"])
            self.assertTrue(requirement_doc.exists())
            self.assertTrue(execution_plan.exists())
            self.assertTrue(cleanup_receipt.exists())
            self.assertTrue(specialist_route.exists())
            self.assertTrue(assistant_policy.exists())
            self.assertTrue(codex_integration.exists())
            self.assertTrue(capability_proxy.exists())
            route_payload = json.loads(specialist_route.read_text(encoding="utf-8"))
            self.assertTrue(route_payload["codex_final_authority"])
            if "claude" in payload["artifacts"]["specialist_exploration_briefs"]:
                brief_path = Path(payload["artifacts"]["specialist_exploration_briefs"]["claude"])
                self.assertTrue(brief_path.exists())
                brief_payload = json.loads(brief_path.read_text(encoding="utf-8"))
                self.assertIn("skill_capsule", brief_payload)
            if "gemini" in payload["artifacts"]["specialist_task_packets"]:
                packet_path = Path(payload["artifacts"]["specialist_task_packets"]["gemini"])
                self.assertTrue(packet_path.exists())
                packet_payload = json.loads(packet_path.read_text(encoding="utf-8"))
                self.assertEqual("proxy_mediated", packet_payload["allowed_capabilities"]["mode"])

    def test_benchmark_run_writes_governed_artifacts_and_suppresses_specialists(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp_root = Path(tempdir)
            workspace = temp_root / "workspace"
            workspace.mkdir()
            fake_codex = temp_root / "fake_codex"
            fake_codex.write_text(
                """#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path

argv = sys.argv[1:]
for index, token in enumerate(argv):
    if token == "--output-last-message":
        Path(argv[index + 1]).write_text("runtime bridge benchmark completed", encoding="utf-8")
        break
sys.exit(0)
""",
                encoding="utf-8",
            )
            fake_codex.chmod(0o755)
            completed = subprocess.run(
                [
                    "node",
                    str(REPO_ROOT / "apps" / "evcode-bench" / "bin" / "evcode-bench.js"),
                    "run",
                    "--task",
                    "Build a benchmark-safe autonomous runtime smoke test with proof artifacts",
                    "--workspace",
                    str(workspace),
                    "--artifacts-root",
                    tempdir,
                    "--run-id",
                    "benchmark-smoke",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
                env={
                    **os.environ,
                    "EVCODE_BENCH_HOST_BIN": str(fake_codex),
                },
            )
            payload = json.loads(completed.stdout)
            self.assertEqual("benchmark_autonomous", payload["mode"])
            self.assertEqual("benchmark", payload["channel"])
            requirement_doc = Path(payload["artifacts"]["requirement_doc"])
            self.assertIn("Assumptions", requirement_doc.read_text(encoding="utf-8"))
            self.assertTrue(Path(payload["artifacts"]["benchmark_result"]).exists())
            self.assertTrue(Path(payload["artifacts"]["capability_proxy_receipt"]).exists())
            route_payload = json.loads(Path(payload["artifacts"]["specialist_routing_receipt"]).read_text(encoding="utf-8"))
            self.assertEqual("codex_only_benchmark", route_payload["route_kind"])
            self.assertFalse((workspace / "docs").exists())
            self.assertFalse((workspace / "outputs").exists())


if __name__ == "__main__":
    unittest.main()
