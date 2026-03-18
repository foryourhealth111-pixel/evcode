from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "packages" / "assistant-adapters" / "python"))
sys.path.insert(0, str(REPO_ROOT / "packages" / "specialist-routing" / "python"))

from evcode_assistant_adapters import resolve_assistant_provider_catalog
from evcode_specialist_routing import load_assistant_policy, load_routing_policy, resolve_specialist_route


class SpecialistRoutingTests(unittest.TestCase):
    def test_plan_heavy_standard_task_requests_claude(self) -> None:
        assistant_policy = load_assistant_policy(REPO_ROOT, "standard")
        routing_policy = load_routing_policy(REPO_ROOT)
        provider_catalog = resolve_assistant_provider_catalog(assistant_policy, env={})
        route = resolve_specialist_route(
            task="Plan the product architecture and UX workflow for an ambiguous redesign",
            channel="standard",
            routing_policy=routing_policy,
            assistant_policy=assistant_policy,
            provider_catalog=provider_catalog,
        )
        requested = {item["assistant_name"] for item in route["requested_delegates"]}
        self.assertTrue(route["codex_final_authority"])
        self.assertEqual("codex", route["final_executor"])
        self.assertIn("claude", requested)
        self.assertEqual("planning", route["classification"]["domain"])
        self.assertEqual("vco_artifacts", route["memory_policy"]["owner"])
        self.assertIn("codex_only", route["capability_policy"]["classes"])
        claude_delegate = next(item for item in route["requested_delegates"] if item["assistant_name"] == "claude")
        self.assertEqual("autonomous", claude_delegate["exploration_mode"])
        self.assertEqual("proxy_mediated", claude_delegate["capability_mode"])
        self.assertIn("planning", claude_delegate["skill_capsule_classes"])
        self.assertIn("routing_receipt", claude_delegate["required_receipts"])
        self.assertEqual(
            "translate_advisory_output_into_engineering_plan_and_execution",
            route["codex_followup"]["purpose"],
        )

    def test_documentation_task_defaults_to_claude(self) -> None:
        assistant_policy = load_assistant_policy(REPO_ROOT, "standard")
        routing_policy = load_routing_policy(REPO_ROOT)
        provider_catalog = resolve_assistant_provider_catalog(assistant_policy, env={})
        route = resolve_specialist_route(
            task="Write a project summary report and architecture documentation for the platform",
            channel="standard",
            routing_policy=routing_policy,
            assistant_policy=assistant_policy,
            provider_catalog=provider_catalog,
        )
        requested = {item["assistant_name"] for item in route["requested_delegates"]}
        self.assertEqual("documentation", route["classification"]["domain"])
        self.assertEqual("narrative", route["classification"]["evidence"])
        self.assertIn("claude", requested)
        self.assertNotIn("gemini", requested)
        claude_delegate = next(item for item in route["requested_delegates"] if item["assistant_name"] == "claude")
        self.assertEqual("document_artifact", claude_delegate["expected_output_type"])
        self.assertEqual("documentation_defaults_to_claude", claude_delegate["reason"])
        self.assertEqual("autonomous", claude_delegate["exploration_mode"])
        self.assertIn("documentation", claude_delegate["skill_capsule_classes"])

    def test_visual_frontend_task_requests_gemini(self) -> None:
        assistant_policy = load_assistant_policy(REPO_ROOT, "standard")
        routing_policy = load_routing_policy(REPO_ROOT)
        provider_catalog = resolve_assistant_provider_catalog(assistant_policy, env={})
        route = resolve_specialist_route(
            task="Design a responsive frontend landing page with typography, spacing, motion, and visual polish",
            channel="standard",
            routing_policy=routing_policy,
            assistant_policy=assistant_policy,
            provider_catalog=provider_catalog,
        )
        requested = {item["assistant_name"] for item in route["requested_delegates"]}
        self.assertIn("gemini", requested)
        self.assertEqual("frontend_visual", route["classification"]["domain"])
        self.assertEqual("visual", route["classification"]["evidence"])
        gemini_delegate = next(item for item in route["requested_delegates"] if item["assistant_name"] == "gemini")
        self.assertEqual("packetized", gemini_delegate["exploration_mode"])
        self.assertEqual("proxy_mediated", gemini_delegate["capability_mode"])
        self.assertIn("visual_design", gemini_delegate["skill_capsule_classes"])
        self.assertIn("capability_proxy_receipt", gemini_delegate["required_receipts"])

    def test_high_risk_backend_task_suppresses_gemini(self) -> None:
        assistant_policy = load_assistant_policy(REPO_ROOT, "standard")
        routing_policy = load_routing_policy(REPO_ROOT)
        provider_catalog = resolve_assistant_provider_catalog(assistant_policy, env={})
        route = resolve_specialist_route(
            task="Implement a runtime provider migration and verification contract for backend auth",
            channel="standard",
            routing_policy=routing_policy,
            assistant_policy=assistant_policy,
            provider_catalog=provider_catalog,
        )
        requested = {item["assistant_name"] for item in route["requested_delegates"]}
        self.assertNotIn("gemini", requested)
        self.assertEqual("high", route["classification"]["risk"])

    def test_backend_runtime_task_can_stay_codex_only(self) -> None:
        assistant_policy = load_assistant_policy(REPO_ROOT, "standard")
        routing_policy = load_routing_policy(REPO_ROOT)
        provider_catalog = resolve_assistant_provider_catalog(assistant_policy, env={})
        route = resolve_specialist_route(
            task="Implement a runtime provider migration and backend verification contract",
            channel="standard",
            routing_policy=routing_policy,
            assistant_policy=assistant_policy,
            provider_catalog=provider_catalog,
        )
        self.assertEqual("codex_only", route["route_kind"])
        self.assertFalse(route["requested_delegates"])
        self.assertEqual({"claude", "gemini"}, {item["assistant_name"] for item in route["suppressed_delegates"]})

    def test_benchmark_channel_suppresses_specialists(self) -> None:
        assistant_policy = load_assistant_policy(REPO_ROOT, "benchmark")
        routing_policy = load_routing_policy(REPO_ROOT)
        provider_catalog = resolve_assistant_provider_catalog(assistant_policy, env={})
        route = resolve_specialist_route(
            task="Design a polished frontend benchmark run with visual evidence",
            channel="benchmark",
            routing_policy=routing_policy,
            assistant_policy=assistant_policy,
            provider_catalog=provider_catalog,
        )
        self.assertEqual("codex_only_benchmark", route["route_kind"])
        self.assertFalse(route["requested_delegates"])
        self.assertEqual({"claude", "gemini"}, {item["assistant_name"] for item in route["suppressed_delegates"]})
        self.assertEqual("vco_artifacts", route["memory_policy"]["owner"])


if __name__ == "__main__":
    unittest.main()
