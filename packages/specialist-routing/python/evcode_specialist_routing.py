from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


RISK_ORDER = {"low": 0, "medium": 1, "high": 2}
AMBIGUITY_ORDER = {"low": 0, "medium": 1, "high": 2}



def load_assistant_policy(repo_root: Path, channel: str) -> dict[str, Any]:
    policy_name = f"assistant-policy.{channel}.json"
    return json.loads((repo_root / "config" / policy_name).read_text(encoding="utf-8"))



def load_routing_policy(repo_root: Path) -> dict[str, Any]:
    return json.loads((repo_root / "config" / "specialist-routing.json").read_text(encoding="utf-8"))



def _keyword_score(task_lower: str, keywords: list[str]) -> int:
    return sum(1 for keyword in keywords if keyword in task_lower)



def classify_task(task: str, routing_policy: dict[str, Any]) -> dict[str, Any]:
    classification = routing_policy["classification"]
    task_lower = task.lower()
    frontend_score = _keyword_score(task_lower, classification["frontend_keywords"])
    backend_score = _keyword_score(task_lower, classification["backend_keywords"])
    planning_score = _keyword_score(task_lower, classification["planning_keywords"])
    documentation_score = _keyword_score(task_lower, classification.get("documentation_keywords", []))
    ambiguity_score = _keyword_score(task_lower, classification["ambiguity_keywords"])
    visual_evidence_score = _keyword_score(task_lower, classification["visual_evidence_keywords"])
    high_risk_score = _keyword_score(task_lower, classification["high_risk_keywords"])

    if documentation_score > 0 and backend_score == 0 and visual_evidence_score == 0:
        domain = "documentation"
    elif frontend_score > 0 and backend_score > 0:
        domain = "mixed_ui"
    elif planning_score > 0 and (planning_score >= frontend_score or visual_evidence_score == 0):
        domain = "planning"
    elif frontend_score > 0 and (visual_evidence_score > 0 or frontend_score >= backend_score):
        domain = "frontend_visual"
    elif backend_score > 0:
        domain = "backend_engineering"
    else:
        domain = "general_engineering"

    if high_risk_score > 0 or domain == "backend_engineering":
        risk = "high"
    elif domain == "mixed_ui" or backend_score > 0:
        risk = "medium"
    else:
        risk = "low"

    if domain == "documentation":
        ambiguity = "low"
    elif ambiguity_score >= 2 or (planning_score > 0 and "?" in task):
        ambiguity = "high"
    elif ambiguity_score >= 1 or planning_score > 0:
        ambiguity = "medium"
    else:
        ambiguity = "low"

    if domain in {"frontend_visual", "mixed_ui"} or visual_evidence_score > 0:
        evidence = "visual"
    elif domain == "documentation":
        evidence = "narrative"
    elif risk == "high":
        evidence = "strict"
    else:
        evidence = "standard"

    return {
        "domain": domain,
        "risk": risk,
        "ambiguity": ambiguity,
        "evidence": evidence,
        "scores": {
            "frontend": frontend_score,
            "backend": backend_score,
            "planning": planning_score,
            "documentation": documentation_score,
            "ambiguity": ambiguity_score,
            "visual_evidence": visual_evidence_score,
            "high_risk": high_risk_score,
        },
    }



def _minimum_ambiguity_met(actual: str, minimum: str) -> bool:
    return AMBIGUITY_ORDER[actual] >= AMBIGUITY_ORDER[minimum]



def _maximum_risk_met(actual: str, maximum: str) -> bool:
    return RISK_ORDER[actual] <= RISK_ORDER[maximum]



def _claude_exploration_mode(classification: dict[str, Any], claude_policy: dict[str, Any]) -> str:
    domain = classification["domain"]
    by_domain = claude_policy.get("default_exploration_mode_by_domain", {})
    if classification["risk"] == "high":
        return "packetized"
    return by_domain.get(domain, claude_policy.get("default_exploration_mode", "packetized"))



def _assistant_capability_fields(assistant_config: dict[str, Any]) -> dict[str, Any]:
    capability_access = assistant_config.get("capability_access", {})
    return {
        "capability_mode": capability_access.get("mode", "proxy_mediated"),
        "direct_read_only_allowlist": deepcopy(capability_access.get("direct_read_only_allowlist", [])),
        "proxy_allowlist": deepcopy(capability_access.get("proxy_allowlist", [])),
        "mutation_allowlist": deepcopy(capability_access.get("mutation_allowlist", [])),
        "denied_capabilities": deepcopy(capability_access.get("denied", [])),
    }



def _delegate_common(
    *,
    assistant_name: str,
    purpose: str,
    expected_output_type: str,
    reason: str,
    authority_tier: str,
    exploration_mode: str,
    assistant_config: dict[str, Any],
    routing_policy: dict[str, Any],
) -> dict[str, Any]:
    return {
        "assistant_name": assistant_name,
        "purpose": purpose,
        "expected_output_type": expected_output_type,
        "reason": reason,
        "authority_tier": authority_tier,
        "exploration_mode": exploration_mode,
        "skill_capsule_classes": deepcopy(assistant_config.get("required_skill_capsules", [])),
        "required_receipts": deepcopy(routing_policy.get("required_receipts", [])),
        **_assistant_capability_fields(assistant_config),
    }



def _claude_delegate_config(
    classification: dict[str, Any],
    claude_policy: dict[str, Any],
    claude_config: dict[str, Any],
    routing_policy: dict[str, Any],
) -> dict[str, Any] | None:
    domain = classification["domain"]
    exploration_mode = _claude_exploration_mode(classification, claude_policy)
    if domain == "documentation":
        return _delegate_common(
            assistant_name="claude",
            purpose="documentation_and_synthesis",
            expected_output_type="document_artifact",
            reason="documentation_defaults_to_claude",
            authority_tier=claude_policy["default_authority_tier"],
            exploration_mode=exploration_mode,
            assistant_config=claude_config,
            routing_policy=routing_policy,
        )
    if domain == "planning":
        return _delegate_common(
            assistant_name="claude",
            purpose="requirements_and_project_design",
            expected_output_type="project_design_brief",
            reason="planning_defaults_to_claude",
            authority_tier=claude_policy["default_authority_tier"],
            exploration_mode=exploration_mode,
            assistant_config=claude_config,
            routing_policy=routing_policy,
        )
    if domain in claude_policy["allowed_domains"] and _minimum_ambiguity_met(
        classification["ambiguity"], claude_policy["minimum_ambiguity"]
    ):
        return _delegate_common(
            assistant_name="claude",
            purpose="planning_and_ux_structure",
            expected_output_type="plan_artifact",
            reason="task_is_ambiguous_or_plan_heavy",
            authority_tier=claude_policy["default_authority_tier"],
            exploration_mode=exploration_mode,
            assistant_config=claude_config,
            routing_policy=routing_policy,
        )
    return None



def resolve_specialist_route(
    *,
    task: str,
    channel: str,
    routing_policy: dict[str, Any],
    assistant_policy: dict[str, Any],
    provider_catalog: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    classification = classify_task(task, routing_policy)
    requested_delegates: list[dict[str, Any]] = []
    suppressed_delegates: list[dict[str, Any]] = []
    degraded_delegates: list[dict[str, Any]] = []
    memory_policy = deepcopy(routing_policy.get("memory_policy", {}))
    capability_policy = deepcopy(routing_policy.get("capability_policy", {}))
    skill_capsule_defaults = deepcopy(routing_policy.get("skill_capsule_defaults", {}))

    if channel == "benchmark" and routing_policy.get("benchmark_suppresses_specialists", False):
        for assistant_name in ("claude", "gemini"):
            suppressed_delegates.append(
                {
                    "assistant_name": assistant_name,
                    "reason": "benchmark_policy_suppression",
                }
            )
        return {
            "stage": routing_policy["route_stage"],
            "channel": channel,
            "codex_final_authority": True,
            "final_executor": "codex",
            "classification": classification,
            "route_kind": "codex_only_benchmark",
            "requested_delegates": requested_delegates,
            "degraded_delegates": degraded_delegates,
            "suppressed_delegates": suppressed_delegates,
            "memory_policy": memory_policy,
            "capability_policy": capability_policy,
            "skill_capsule_defaults": skill_capsule_defaults,
        }

    claude_policy = routing_policy["policies"]["claude"]
    gemini_policy = routing_policy["policies"]["gemini"]
    claude_config = assistant_policy["assistants"].get("claude", {})
    gemini_config = assistant_policy["assistants"].get("gemini", {})

    claude_delegate = _claude_delegate_config(classification, claude_policy, claude_config, routing_policy)
    if claude_delegate is not None:
        requested_delegates.append(claude_delegate)
    else:
        suppressed_delegates.append(
            {
                "assistant_name": "claude",
                "reason": "task_not_plan_heavy_enough",
            }
        )

    if (
        classification["domain"] in gemini_policy["allowed_domains"]
        and _maximum_risk_met(classification["risk"], gemini_policy["maximum_risk"])
        and (classification["evidence"] == "visual" or not gemini_policy["requires_visual_evidence"])
    ):
        requested_delegates.append(
            _delegate_common(
                assistant_name="gemini",
                purpose="visual_and_frontend_design",
                expected_output_type="visual_plan",
                reason="task_requires_visual_frontend_judgment",
                authority_tier=gemini_policy["default_authority_tier"],
                exploration_mode="packetized",
                assistant_config=gemini_config,
                routing_policy=routing_policy,
            )
        )
    else:
        suppressed_delegates.append(
            {
                "assistant_name": "gemini",
                "reason": "task_not_visual_frontend_fit",
            }
        )

    active_delegates: list[dict[str, Any]] = []
    for delegate in requested_delegates:
        assistant_name = delegate["assistant_name"]
        provider_spec = provider_catalog.get(assistant_name, {})
        assistant_config = assistant_policy["assistants"].get(assistant_name, {})
        if not assistant_config.get("enabled", False):
            degraded_delegates.append(
                {
                    **delegate,
                    "status": "suppressed_by_channel_policy",
                    "reason": assistant_config.get("suppression_reason", "assistant_disabled"),
                }
            )
            continue
        if provider_spec.get("live_available"):
            active_delegates.append({**delegate, "status": "live_advisory_available"})
            continue
        degraded_delegates.append(
            {
                **delegate,
                "status": "contract_ready_live_unavailable",
                "reason": (
                    "Specialist policy allows advisory delegation, but live invocation is not enabled. "
                    "Codex remains the execution path."
                ),
            }
        )

    route_kind = "codex_with_specialists" if requested_delegates else "codex_only"
    return {
        "stage": routing_policy["route_stage"],
        "channel": channel,
        "codex_final_authority": True,
        "final_executor": "codex",
        "classification": classification,
        "route_kind": route_kind,
        "codex_followup": {
            "purpose": "translate_advisory_output_into_engineering_plan_and_execution",
            "required": True,
        },
        "requested_delegates": deepcopy(requested_delegates),
        "active_delegates": active_delegates,
        "degraded_delegates": degraded_delegates,
        "suppressed_delegates": suppressed_delegates,
        "memory_policy": memory_policy,
        "capability_policy": capability_policy,
        "skill_capsule_defaults": skill_capsule_defaults,
    }
