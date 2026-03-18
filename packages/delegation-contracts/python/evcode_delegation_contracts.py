from __future__ import annotations

from copy import deepcopy
from typing import Any


TASK_PACKET_REQUIRED_FIELDS = (
    "specialist_name",
    "task_id",
    "run_id",
    "repository_path_summary",
    "file_scope",
    "task_goal",
    "constraints",
    "acceptance_criteria",
    "non_goals",
    "architecture_notes",
    "design_system_notes",
    "allowed_authority_tier",
    "expected_output_type",
    "skill_capsule",
    "allowed_capabilities",
    "required_receipts",
    "authoritative_context_refs",
    "memory_policy",
)

RESULT_PACKET_REQUIRED_FIELDS = (
    "specialist_name",
    "task_id",
    "summary",
    "assumptions",
    "proposed_actions",
    "files_touched_or_proposed",
    "confidence_level",
    "unresolved_risks",
    "recommended_next_actor",
    "capability_requests",
    "receipt_refs",
)

VALID_SPECIALISTS = {"codex", "claude", "gemini"}
VALID_AUTHORITY_TIERS = {"advisory_only", "isolated_candidate_apply", "final_executor"}
VALID_CAPABILITY_MODES = {"codex_only", "proxy_mediated", "specialist_read_only"}

DEFAULT_SKILL_CAPSULE = {
    "capsule_id": "default-governed-advisory",
    "compiler": "vco_compiled_capsule",
    "version": "2026-03-18",
    "classes": ["governed_advisory"],
    "guidance": ["Respect Codex final authority."],
    "prohibited_actions": ["never claim completion"],
    "output_contract": [
        "summary",
        "assumptions",
        "proposed_actions",
        "files_touched_or_proposed",
        "confidence_level",
        "unresolved_risks",
        "recommended_next_actor",
        "capability_requests",
        "receipt_refs",
    ],
}

DEFAULT_ALLOWED_CAPABILITIES = {
    "mode": "proxy_mediated",
    "direct_read_only_allowlist": [],
    "proxy_allowlist": [],
    "mutation_allowlist": [],
    "denied": [],
}

DEFAULT_REQUIRED_RECEIPTS = [
    "routing_receipt",
    "task_packet_receipt",
    "capability_proxy_receipt",
    "specialist_result_receipt",
    "codex_integration_receipt",
    "verification_receipt",
    "cleanup_receipt",
]

DEFAULT_MEMORY_POLICY = {
    "owner": "vco_artifacts",
    "specialist_local_memory": "ephemeral",
    "authoritative_sources": [
        "requirement_doc",
        "execution_plan",
        "assistant_policy_snapshot",
        "specialist_routing_receipt",
        "codex_integration_receipt",
    ],
}


class DelegationContractError(ValueError):
    pass



def _require_fields(payload: dict[str, Any], required_fields: tuple[str, ...], name: str) -> None:
    missing = [field for field in required_fields if field not in payload]
    if missing:
        raise DelegationContractError(f"{name} missing required fields: {', '.join(missing)}")



def _require_list(payload: dict[str, Any], field: str, name: str) -> None:
    if not isinstance(payload.get(field), list):
        raise DelegationContractError(f"{name}.{field} must be a list")



def _require_scalar(payload: dict[str, Any], field: str, name: str) -> None:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise DelegationContractError(f"{name}.{field} must be a non-empty string")



def _require_dict(payload: dict[str, Any], field: str, name: str) -> dict[str, Any]:
    value = payload.get(field)
    if not isinstance(value, dict):
        raise DelegationContractError(f"{name}.{field} must be a dict")
    return value



def _normalize_task_defaults(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(payload)
    normalized.setdefault("skill_capsule", deepcopy(DEFAULT_SKILL_CAPSULE))
    normalized.setdefault("allowed_capabilities", deepcopy(DEFAULT_ALLOWED_CAPABILITIES))
    normalized.setdefault("required_receipts", deepcopy(DEFAULT_REQUIRED_RECEIPTS))
    normalized.setdefault("authoritative_context_refs", ["requirement_doc", "execution_plan"])
    normalized.setdefault("memory_policy", deepcopy(DEFAULT_MEMORY_POLICY))
    return normalized



def _normalize_result_defaults(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(payload)
    normalized.setdefault("capability_requests", [])
    normalized.setdefault("receipt_refs", [])
    return normalized



def _validate_skill_capsule(value: dict[str, Any]) -> None:
    required = ("capsule_id", "compiler", "version", "classes", "guidance", "prohibited_actions", "output_contract")
    missing = [field for field in required if field not in value]
    if missing:
        raise DelegationContractError(f"task_packet.skill_capsule missing fields: {', '.join(missing)}")
    for list_field in ("classes", "guidance", "prohibited_actions", "output_contract"):
        if not isinstance(value.get(list_field), list):
            raise DelegationContractError(f"task_packet.skill_capsule.{list_field} must be a list")



def _validate_allowed_capabilities(value: dict[str, Any]) -> None:
    required = ("mode", "direct_read_only_allowlist", "proxy_allowlist", "mutation_allowlist", "denied")
    missing = [field for field in required if field not in value]
    if missing:
        raise DelegationContractError(f"task_packet.allowed_capabilities missing fields: {', '.join(missing)}")
    if value["mode"] not in VALID_CAPABILITY_MODES:
        raise DelegationContractError(f"Unsupported capability mode: {value['mode']}")
    for list_field in ("direct_read_only_allowlist", "proxy_allowlist", "mutation_allowlist", "denied"):
        if not isinstance(value.get(list_field), list):
            raise DelegationContractError(f"task_packet.allowed_capabilities.{list_field} must be a list")



def _validate_memory_policy(value: dict[str, Any]) -> None:
    required = ("owner", "specialist_local_memory", "authoritative_sources")
    missing = [field for field in required if field not in value]
    if missing:
        raise DelegationContractError(f"task_packet.memory_policy missing fields: {', '.join(missing)}")
    if not isinstance(value["owner"], str) or not value["owner"].strip():
        raise DelegationContractError("task_packet.memory_policy.owner must be a non-empty string")
    if not isinstance(value["specialist_local_memory"], str) or not value["specialist_local_memory"].strip():
        raise DelegationContractError("task_packet.memory_policy.specialist_local_memory must be a non-empty string")
    if not isinstance(value["authoritative_sources"], list):
        raise DelegationContractError("task_packet.memory_policy.authoritative_sources must be a list")



def validate_task_packet(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = _normalize_task_defaults(payload)
    _require_fields(normalized, TASK_PACKET_REQUIRED_FIELDS, "task_packet")
    _require_scalar(normalized, "specialist_name", "task_packet")
    _require_scalar(normalized, "task_id", "task_packet")
    _require_scalar(normalized, "run_id", "task_packet")
    _require_scalar(normalized, "repository_path_summary", "task_packet")
    _require_scalar(normalized, "task_goal", "task_packet")
    _require_scalar(normalized, "allowed_authority_tier", "task_packet")
    _require_scalar(normalized, "expected_output_type", "task_packet")
    for list_field in (
        "file_scope",
        "constraints",
        "acceptance_criteria",
        "non_goals",
        "architecture_notes",
        "design_system_notes",
        "required_receipts",
        "authoritative_context_refs",
    ):
        _require_list(normalized, list_field, "task_packet")
    specialist_name = str(normalized["specialist_name"]).lower()
    if specialist_name not in VALID_SPECIALISTS:
        raise DelegationContractError(f"Unsupported specialist_name: {normalized['specialist_name']}")
    if normalized["allowed_authority_tier"] not in VALID_AUTHORITY_TIERS:
        raise DelegationContractError(
            f"Unsupported allowed_authority_tier: {normalized['allowed_authority_tier']}"
        )
    _validate_skill_capsule(_require_dict(normalized, "skill_capsule", "task_packet"))
    _validate_allowed_capabilities(_require_dict(normalized, "allowed_capabilities", "task_packet"))
    _validate_memory_policy(_require_dict(normalized, "memory_policy", "task_packet"))
    return deepcopy(normalized)



def build_task_packet(
    *,
    specialist_name: str,
    task_id: str,
    run_id: str,
    repository_path_summary: str,
    file_scope: list[str],
    task_goal: str,
    constraints: list[str],
    acceptance_criteria: list[str],
    non_goals: list[str],
    architecture_notes: list[str],
    design_system_notes: list[str],
    allowed_authority_tier: str,
    expected_output_type: str,
    extras: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "specialist_name": specialist_name,
        "task_id": task_id,
        "run_id": run_id,
        "repository_path_summary": repository_path_summary,
        "file_scope": file_scope,
        "task_goal": task_goal,
        "constraints": constraints,
        "acceptance_criteria": acceptance_criteria,
        "non_goals": non_goals,
        "architecture_notes": architecture_notes,
        "design_system_notes": design_system_notes,
        "allowed_authority_tier": allowed_authority_tier,
        "expected_output_type": expected_output_type,
    }
    if extras:
        payload.update(extras)
    return validate_task_packet(payload)



def validate_result_packet(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = _normalize_result_defaults(payload)
    _require_fields(normalized, RESULT_PACKET_REQUIRED_FIELDS, "result_packet")
    _require_scalar(normalized, "specialist_name", "result_packet")
    _require_scalar(normalized, "task_id", "result_packet")
    _require_scalar(normalized, "summary", "result_packet")
    _require_scalar(normalized, "recommended_next_actor", "result_packet")
    for list_field in (
        "assumptions",
        "proposed_actions",
        "files_touched_or_proposed",
        "unresolved_risks",
        "capability_requests",
        "receipt_refs",
    ):
        _require_list(normalized, list_field, "result_packet")
    specialist_name = str(normalized["specialist_name"]).lower()
    if specialist_name not in VALID_SPECIALISTS:
        raise DelegationContractError(f"Unsupported specialist_name: {normalized['specialist_name']}")
    if normalized["recommended_next_actor"] not in VALID_SPECIALISTS:
        raise DelegationContractError(
            f"Unsupported recommended_next_actor: {normalized['recommended_next_actor']}"
        )
    confidence = normalized["confidence_level"]
    if not isinstance(confidence, (int, float)) or not 0.0 <= float(confidence) <= 1.0:
        raise DelegationContractError("result_packet.confidence_level must be a number between 0.0 and 1.0")
    return deepcopy(normalized)



def build_result_packet(
    *,
    specialist_name: str,
    task_id: str,
    summary: str,
    assumptions: list[str],
    proposed_actions: list[str],
    files_touched_or_proposed: list[str],
    confidence_level: float,
    unresolved_risks: list[str],
    recommended_next_actor: str,
    extras: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "specialist_name": specialist_name,
        "task_id": task_id,
        "summary": summary,
        "assumptions": assumptions,
        "proposed_actions": proposed_actions,
        "files_touched_or_proposed": files_touched_or_proposed,
        "confidence_level": confidence_level,
        "unresolved_risks": unresolved_risks,
        "recommended_next_actor": recommended_next_actor,
    }
    if extras:
        payload.update(extras)
    return validate_result_packet(payload)
