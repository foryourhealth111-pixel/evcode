from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "packages" / "assistant-adapters" / "python"))

from evcode_assistant_adapters import (
    CHAT_COMPLETIONS_WIRE_API,
    RESPONSES_WIRE_API,
    build_adapter_request_preview,
    build_combined_user_message,
    build_provider_request,
    parse_sse_payload,
    provider_endpoint,
    resolve_assistant_provider_catalog,
    sanitize_provider_catalog,
)


class AssistantAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = json.loads((REPO_ROOT / "config" / "assistant-policy.standard.json").read_text(encoding="utf-8"))

    def test_provider_catalog_uses_rightcodes_defaults(self) -> None:
        catalog = resolve_assistant_provider_catalog(self.policy, env={})
        self.assertEqual("https://right.codes/codex/v1", catalog["codex"]["base_url"])
        self.assertEqual("gpt-5.4", catalog["codex"]["model"])
        self.assertEqual(CHAT_COMPLETIONS_WIRE_API, catalog["codex"]["wire_api"])
        self.assertEqual("https://right.codes/claude/v1", catalog["claude"]["base_url"])
        self.assertEqual(CHAT_COMPLETIONS_WIRE_API, catalog["claude"]["wire_api"])
        self.assertEqual(CHAT_COMPLETIONS_WIRE_API, catalog["gemini"]["wire_api"])
        self.assertFalse(catalog["claude"]["live_available"])
        self.assertFalse(catalog["gemini"]["live_available"])
        self.assertEqual("proxy_mediated", catalog["claude"]["capability_mode"])

    def test_provider_catalog_respects_env_overrides(self) -> None:
        env = {
            "EVCODE_ENABLE_LIVE_SPECIALISTS": "1",
            "EVCODE_RIGHTCODES_API_KEY": "sk-test",
            "EVCODE_GEMINI_BASE_URL": "https://example.test/gemini/v1",
            "EVCODE_GEMINI_MODEL": "gemini-custom",
        }
        catalog = resolve_assistant_provider_catalog(self.policy, env=env)
        self.assertTrue(catalog["claude"]["live_available"])
        self.assertTrue(catalog["gemini"]["live_available"])
        self.assertEqual("https://example.test/gemini/v1", catalog["gemini"]["base_url"])
        self.assertEqual("gemini-custom", catalog["gemini"]["model"])

    def test_sanitized_catalog_does_not_expose_secret_values(self) -> None:
        env = {
            "EVCODE_ENABLE_LIVE_SPECIALISTS": "1",
            "EVCODE_RIGHTCODES_API_KEY": "sk-secret",
        }
        catalog = resolve_assistant_provider_catalog(self.policy, env=env)
        sanitized = sanitize_provider_catalog(catalog)
        serialized = json.dumps(sanitized)
        self.assertNotIn("sk-secret", serialized)
        self.assertTrue(sanitized["claude"]["api_key_present"])

    def test_request_preview_is_secret_safe(self) -> None:
        catalog = resolve_assistant_provider_catalog(self.policy, env=os.environ)
        preview = build_adapter_request_preview(
            {
                "task_id": "run-1-claude",
                "task_goal": "Plan a redesign",
                "allowed_authority_tier": "advisory_only",
                "expected_output_type": "plan_artifact",
                "skill_capsule": {"classes": ["planning"]},
                "allowed_capabilities": {"mode": "proxy_mediated"},
            },
            catalog["claude"],
        )
        self.assertEqual("claude", preview["assistant_name"])
        self.assertIn("api_key_present", preview)
        self.assertNotIn("api_key", preview)
        self.assertEqual("proxy_mediated", preview["capability_mode"])
        self.assertEqual(["planning"], preview["skill_capsule_classes"])

    def test_provider_endpoint_matches_wire_api(self) -> None:
        self.assertEqual(
            "https://example.test/v1/chat/completions",
            provider_endpoint({"base_url": "https://example.test/v1", "wire_api": CHAT_COMPLETIONS_WIRE_API}),
        )
        self.assertEqual(
            "https://example.test/v1/responses",
            provider_endpoint({"base_url": "https://example.test/v1", "wire_api": RESPONSES_WIRE_API}),
        )

    def test_claude_autonomous_chat_message_requests_proxy_context_instead_of_forbidding_exploration(self) -> None:
        message = build_combined_user_message(
            {
                "task_goal": "Write a brief architecture summary document for the platform",
                "expected_output_type": "document_artifact",
                "file_scope": ["docs/", "config/"],
                "exploration_mode": "autonomous",
                "mission_brief": "Autonomously inspect the repository and write a strong advisory artifact for Codex.",
                "skill_capsule": {"classes": ["documentation", "planning"]},
                "authoritative_context_refs": ["docs/requirements/current.md", "docs/plans/current.md"],
            },
            {
                "assistant_name": "claude",
                "wire_api": CHAT_COMPLETIONS_WIRE_API,
            },
        )
        self.assertIn("Return ONLY one minified JSON object", message)
        self.assertIn("If repository inspection would reduce assumptions", message)
        self.assertIn("request repo_read_context", message)
        self.assertIn("Do not invent file paths", message)
        self.assertNotIn("Do not perform tool use or repository exploration", message)
        self.assertIn('"task_goal":"Write a brief architecture summary document for the platform"', message)
        self.assertIn('"skill_capsule_classes":["documentation","planning"]', message)

    def test_build_provider_request_gives_claude_autonomous_more_output_budget(self) -> None:
        payload = build_provider_request(
            {
                "task_goal": "Plan a redesign",
                "task_id": "run-1-claude",
                "allowed_authority_tier": "advisory_only",
                "expected_output_type": "plan_artifact",
                "exploration_mode": "autonomous",
            },
            {
                "assistant_name": "claude",
                "model": "claude-opus-4-6",
                "wire_api": CHAT_COMPLETIONS_WIRE_API,
            },
        )
        self.assertEqual("claude-opus-4-6", payload["model"])
        self.assertEqual(["user"], [message["role"] for message in payload["messages"]])
        self.assertEqual(650, payload["max_tokens"])
        self.assertIn("request repo_read_context", payload["messages"][0]["content"])

    def test_build_provider_request_gives_claude_packetized_more_output_budget_too(self) -> None:
        payload = build_provider_request(
            {
                "task_goal": "Design a polished landing page",
                "task_id": "run-2-claude",
                "allowed_authority_tier": "advisory_only",
                "expected_output_type": "plan_artifact",
                "exploration_mode": "packetized",
            },
            {
                "assistant_name": "claude",
                "model": "claude-opus-4-6",
                "wire_api": CHAT_COMPLETIONS_WIRE_API,
            },
        )
        self.assertEqual(650, payload["max_tokens"])
        self.assertIn("request repo_read_context", payload["messages"][0]["content"])
        self.assertIn("Do not invent file paths", payload["messages"][0]["content"])

    def test_build_provider_request_supports_responses_shape(self) -> None:
        payload = build_provider_request(
            {
                "task_goal": "Plan a redesign",
                "task_id": "run-1-claude",
                "allowed_authority_tier": "advisory_only",
                "expected_output_type": "plan_artifact",
            },
            {
                "assistant_name": "claude",
                "model": "claude-opus-4-6",
                "wire_api": RESPONSES_WIRE_API,
            },
        )
        self.assertTrue(payload["input"])
        self.assertEqual("system", payload["input"][0]["role"])
        self.assertIsInstance(payload["input"][0]["content"], str)

    def test_parse_sse_payload_returns_last_response_object(self) -> None:
        text = "\n".join(
            [
                'event: response.created',
                'data: {"type":"response.created","response":{"id":"resp_1"}}',
                'event: response.completed',
                'data: {"type":"response.completed","response":{"output_text":"{\\"summary\\":\\"ok\\",\\"assumptions\\":[],\\"proposed_actions\\":[],\\"files_touched_or_proposed\\":[],\\"confidence_level\\":0.5,\\"unresolved_risks\\":[],\\"recommended_next_actor\\":\\"codex\\",\\"capability_requests\\":[],\\"receipt_refs\\":[]}"}}',
            ]
        )
        payload = parse_sse_payload(text)
        self.assertEqual("resp_1", payload["id"])
        self.assertIn("output_text", payload)


if __name__ == "__main__":
    unittest.main()
