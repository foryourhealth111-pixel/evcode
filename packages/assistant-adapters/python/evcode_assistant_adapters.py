from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from copy import deepcopy
from typing import Any


CONFIDENCE_KEYWORDS = {"low": 0.35, "medium": 0.6, "high": 0.8}

RESPONSES_WIRE_API = "responses"
CHAT_COMPLETIONS_WIRE_API = "chat_completions"



def resolve_assistant_provider_catalog(
    assistant_policy: dict[str, Any],
    env: dict[str, str] | None = None,
) -> dict[str, dict[str, Any]]:
    env = env or os.environ
    live_opt_in_env = assistant_policy.get("live_specialists_require_opt_in_env", "EVCODE_ENABLE_LIVE_SPECIALISTS")
    live_specialists_enabled = env.get(live_opt_in_env, "").lower() in {"1", "true", "yes", "on"}
    catalog: dict[str, dict[str, Any]] = {}
    for assistant_name, config in assistant_policy.get("assistants", {}).items():
        base_url = env.get(config.get("base_url_env_var", ""), config.get("default_base_url"))
        model = env.get(config.get("model_env_var", ""), config.get("default_model"))
        api_key_env_var = config.get("api_key_env_var", "")
        api_key = env.get(api_key_env_var, "")
        capability_access = deepcopy(config.get("capability_access", {}))
        live_available = bool(config.get("enabled")) and (
            assistant_name == "codex" or (bool(api_key) and live_specialists_enabled)
        )
        catalog[assistant_name] = {
            "assistant_name": assistant_name,
            "enabled": bool(config.get("enabled")),
            "authority_tier": config.get("authority_tier", "advisory_only"),
            "provider_family": config.get("provider_family", "api"),
            "provider": config.get("provider"),
            "wire_api": config.get("wire_api", RESPONSES_WIRE_API),
            "base_url": base_url,
            "model": model,
            "api_key_env_var": api_key_env_var,
            "api_key_present": bool(api_key),
            "live_opt_in_env": live_opt_in_env,
            "live_opt_in_enabled": live_specialists_enabled,
            "live_available": live_available,
            "suppression_reason": config.get("suppression_reason"),
            "allowed_domains": deepcopy(config.get("allowed_domains", [])),
            "allowed_output_types": deepcopy(config.get("allowed_output_types", [])),
            "required_skill_capsules": deepcopy(config.get("required_skill_capsules", [])),
            "capability_mode": capability_access.get("mode", "proxy_mediated"),
            "direct_read_only_allowlist": deepcopy(capability_access.get("direct_read_only_allowlist", [])),
            "proxy_allowlist": deepcopy(capability_access.get("proxy_allowlist", [])),
            "mutation_allowlist": deepcopy(capability_access.get("mutation_allowlist", [])),
            "denied_capabilities": deepcopy(capability_access.get("denied", [])),
        }
    return catalog



def sanitize_provider_catalog(catalog: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    sanitized: dict[str, dict[str, Any]] = {}
    for assistant_name, spec in catalog.items():
        sanitized[assistant_name] = {
            key: value
            for key, value in spec.items()
            if key not in {"api_key", "raw_api_key"}
        }
    return sanitized



def build_adapter_request_preview(task_packet: dict[str, Any], provider_spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "assistant_name": provider_spec["assistant_name"],
        "provider": provider_spec["provider"],
        "wire_api": provider_spec["wire_api"],
        "base_url": provider_spec["base_url"],
        "model": provider_spec["model"],
        "task_id": task_packet["task_id"],
        "task_goal": task_packet["task_goal"],
        "allowed_authority_tier": task_packet["allowed_authority_tier"],
        "expected_output_type": task_packet["expected_output_type"],
        "authority_tier": provider_spec["authority_tier"],
        "capability_mode": task_packet.get("allowed_capabilities", {}).get("mode", provider_spec.get("capability_mode")),
        "skill_capsule_classes": deepcopy(task_packet.get("skill_capsule", {}).get("classes", [])),
        "required_skill_capsules": deepcopy(provider_spec.get("required_skill_capsules", [])),
        "api_key_present": provider_spec["api_key_present"],
        "live_available": provider_spec["live_available"],
    }



def build_system_prompt(task_packet: dict[str, Any], provider_spec: dict[str, Any]) -> str:
    assistant_name = provider_spec["assistant_name"]
    if assistant_name == "claude":
        specialty = "planning, product framing, UX structure, and acceptance criteria refinement"
    elif assistant_name == "gemini":
        specialty = "visual direction, UI polish, component styling, and front-end design articulation"
    else:
        specialty = "engineering integration, verification, and execution closure"
    return (
        f"You are {assistant_name} inside EvCode's governed specialist pipeline. "
        f"Your role is limited to {specialty}. "
        "Return strict JSON with keys: summary, assumptions, proposed_actions, "
        "files_touched_or_proposed, confidence_level, unresolved_risks, recommended_next_actor, capability_requests, receipt_refs. "
        "Do not claim final completion. Keep Codex as the final next actor."
    )



def build_user_prompt(task_packet: dict[str, Any]) -> str:
    return json.dumps(task_packet, indent=2, ensure_ascii=False)



def build_claude_compact_context(task_packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_goal": task_packet.get("task_goal"),
        "expected_output_type": task_packet.get("expected_output_type"),
        "file_scope": task_packet.get("file_scope", []),
        "task_domain": task_packet.get("task_domain"),
        "task_risk": task_packet.get("task_risk"),
        "evidence_mode": task_packet.get("evidence_mode"),
        "exploration_mode": task_packet.get("exploration_mode"),
        "delegation_purpose": task_packet.get("delegation_purpose"),
        "mission_brief": task_packet.get("mission_brief"),
        "guardrails": task_packet.get("guardrails", []),
        "architecture_notes": task_packet.get("architecture_notes", []),
        "design_system_notes": task_packet.get("design_system_notes", []),
        "skill_capsule_classes": task_packet.get("skill_capsule", {}).get("classes", []),
        "authoritative_context_refs": task_packet.get("authoritative_context_refs", []),
        "capability_mode": task_packet.get("allowed_capabilities", {}).get("mode"),
    }



def build_combined_user_message(task_packet: dict[str, Any], provider_spec: dict[str, Any]) -> str:
    if provider_spec.get("assistant_name") == "claude" and provider_spec.get("wire_api") == CHAT_COMPLETIONS_WIRE_API:
        compact_context = json.dumps(build_claude_compact_context(task_packet), separators=(",", ":"), ensure_ascii=False)
        autonomy_clause = (
            "If repository inspection would reduce assumptions, request repo_read_context in capability_requests instead of inventing files. "
            "Do not invent file paths or package names that are not grounded in the provided context. "
        )
        return (
            "Return ONLY one minified JSON object with keys summary, assumptions, proposed_actions, "
            "files_touched_or_proposed, confidence_level, unresolved_risks, recommended_next_actor, capability_requests, receipt_refs. "
            "Use at most: summary 1 sentence, assumptions max 3 items, proposed_actions max 3 items, "
            "files_touched_or_proposed max 4 items, unresolved_risks max 2 items. "
            "Each string must be under 120 characters. capability_requests and receipt_refs must be arrays. "
            "confidence_level must be a number. Do not use markdown. Do not output shell commands. "
            f"{autonomy_clause}"
            "recommended_next_actor must be codex. "
            f"Context={compact_context}"
        )
    return (
        f"{build_system_prompt(task_packet, provider_spec)}\n\n"
        "Task context JSON:\n"
        f"{build_user_prompt(task_packet)}"
    )



def provider_endpoint(provider_spec: dict[str, Any]) -> str:
    normalized = str(provider_spec["base_url"]).rstrip("/")
    if normalized.endswith("/responses") or normalized.endswith("/chat/completions"):
        return normalized
    if provider_spec.get("wire_api") == CHAT_COMPLETIONS_WIRE_API:
        return f"{normalized}/chat/completions"
    return f"{normalized}/responses"



def build_provider_request(task_packet: dict[str, Any], provider_spec: dict[str, Any]) -> dict[str, Any]:
    if provider_spec.get("wire_api") == CHAT_COMPLETIONS_WIRE_API:
        request = {
            "model": provider_spec["model"],
            "messages": [
                {
                    "role": "user",
                    "content": build_combined_user_message(task_packet, provider_spec),
                }
            ],
        }
        if provider_spec.get("assistant_name") == "claude":
            request["max_tokens"] = 650
        return request
    return {
        "model": provider_spec["model"],
        "stream": False,
        "input": [
            {
                "role": "system",
                "content": build_system_prompt(task_packet, provider_spec),
            },
            {
                "role": "user",
                "content": build_user_prompt(task_packet),
            },
        ],
    }



def parse_sse_payload(text: str) -> dict[str, Any]:
    last_payload: dict[str, Any] | None = None
    merged_response: dict[str, Any] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("data:"):
            continue
        payload_text = line[len("data:") :].strip()
        if not payload_text or payload_text == "[DONE]":
            continue
        try:
            event_payload = json.loads(payload_text)
        except json.JSONDecodeError:
            continue
        if not isinstance(event_payload, dict):
            continue
        last_payload = event_payload
        response_payload = event_payload.get("response")
        if isinstance(response_payload, dict):
            merged_response.update(response_payload)
    if merged_response:
        return merged_response
    if last_payload is None:
        raise ValueError("Unable to extract JSON payload from SSE response")
    return last_payload



def parse_json_payload_text(text: str) -> dict[str, Any]:
    candidates: list[str] = [text.strip()]
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 3 and lines[-1].strip() == "```":
            candidates.append("\n".join(lines[1:-1]).strip())
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidates.append(stripped[start : end + 1].strip())
    seen: set[str] = set()
    for candidate in candidates:
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    raise RuntimeError(f"provider_malformed_json:{text}")



def parse_response_text(payload: dict[str, Any]) -> str:
    output_text = payload.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text
    output = payload.get("output")
    if isinstance(output, list):
        fragments: list[str] = []
        for item in output:
            if not isinstance(item, dict):
                continue
            for content in item.get("content", []):
                if isinstance(content, dict):
                    text = content.get("text") or content.get("output_text")
                    if isinstance(text, str) and text.strip():
                        fragments.append(text)
        if fragments:
            return "\n".join(fragments)
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        message = choices[0].get("message", {})
        content = message.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            fragments = []
            for item in content:
                if isinstance(item, dict):
                    text = item.get("text")
                    if isinstance(text, str) and text.strip():
                        fragments.append(text)
            if fragments:
                return "\n".join(fragments)
    raise ValueError("Unable to extract assistant text from provider response")



def invoke_specialist_json(
    task_packet: dict[str, Any],
    provider_spec: dict[str, Any],
    *,
    env: dict[str, str] | None = None,
    timeout_sec: int = 75,
) -> dict[str, Any]:
    env = env or os.environ
    api_key = env.get(provider_spec["api_key_env_var"], "")
    if not provider_spec.get("live_available"):
        raise RuntimeError("live specialist invocation is not available under the current policy/env")
    endpoint = provider_endpoint(provider_spec)
    request_body = build_provider_request(task_packet, provider_spec)
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(request_body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_sec) as response:
            raw_text = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:  # pragma: no cover - network path
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"provider_http_error:{exc.code}:{body}") from exc
    except urllib.error.URLError as exc:  # pragma: no cover - network path
        raise RuntimeError(f"provider_url_error:{exc.reason}") from exc

    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError:
        if "event:" in raw_text and "data:" in raw_text:
            payload = parse_sse_payload(raw_text)
        else:
            raise RuntimeError(f"provider_malformed_json:{raw_text}")

    assistant_text = parse_response_text(payload)
    return parse_json_payload_text(assistant_text)
