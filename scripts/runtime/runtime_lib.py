from __future__ import annotations

import json
import os
import re
import shutil
import sys
import tempfile
import uuid
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PACKAGE_ROOT = Path(__file__).resolve().parents[2] / "packages"
sys.path.insert(0, str(PACKAGE_ROOT / "assistant-adapters" / "python"))
sys.path.insert(0, str(PACKAGE_ROOT / "delegation-contracts" / "python"))
sys.path.insert(0, str(PACKAGE_ROOT / "specialist-routing" / "python"))

from evcode_assistant_adapters import (  # type: ignore  # noqa: E402
    build_adapter_request_preview,
    invoke_specialist_json,
    resolve_assistant_provider_catalog,
    sanitize_provider_catalog,
)
from evcode_delegation_contracts import (  # type: ignore  # noqa: E402
    DelegationContractError,
    build_result_packet,
    build_task_packet,
)
from evcode_specialist_routing import (  # type: ignore  # noqa: E402
    load_assistant_policy,
    load_routing_policy,
    resolve_specialist_route,
)
from execute_benchmark_task import BenchmarkExecutionConfig, execute_benchmark_task


FIXED_STAGE_ORDER = [
    "skeleton_check",
    "deep_interview",
    "requirement_doc",
    "xl_plan",
    "plan_execute",
    "phase_cleanup",
]


@dataclass(frozen=True)
class GovernedRuntimeConfig:
    mode: str
    task: str
    repo_root: Path
    workspace: Path
    artifacts_root: Path
    run_id: str
    channel: str
    profile: str
    result_json_path: Path | None = None


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(task: str) -> str:
    lowered = task.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return slug[:48] or "governed-task"


def infer_internal_grade(task: str) -> str:
    lowered = task.lower()
    if any(token in lowered for token in ("parallel", "multi-agent", "benchmark", "refactor", "system", "migration")):
        return "XL"
    if any(token in lowered for token in ("design", "architecture", "review", "plan")):
        return "L"
    return "M"


def complete_requirement(task: str) -> bool:
    lowered = task.lower()
    signals = 0
    for token in ("implement", "build", "design", "deliver", "test", "verify", "cli", "agent", "benchmark"):
        if token in lowered:
            signals += 1
    return signals >= 2 or len(task.split()) >= 12


def detect_existing_artifacts(artifacts_root: Path) -> dict[str, str | None]:
    requirements_dir = artifacts_root / "docs" / "requirements"
    plans_dir = artifacts_root / "docs" / "plans"
    latest_requirement = sorted(requirements_dir.glob("*.md"))[-1] if requirements_dir.exists() and list(requirements_dir.glob("*.md")) else None
    latest_plan = sorted(plans_dir.glob("*-execution-plan.md"))[-1] if plans_dir.exists() and list(plans_dir.glob("*-execution-plan.md")) else None
    return {
        "latest_requirement_doc": str(latest_requirement) if latest_requirement else None,
        "latest_execution_plan": str(latest_plan) if latest_plan else None,
    }


def path_is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def ensure_benchmark_artifacts_root(artifacts_root: Path, workspace: Path, run_id: str) -> tuple[Path, bool]:
    if path_is_within(artifacts_root, workspace):
        redirected = Path(tempfile.mkdtemp(prefix=f"evcode-bench-artifacts-{run_id}-")).resolve()
        return redirected, True
    artifacts_root.mkdir(parents=True, exist_ok=True)
    return artifacts_root.resolve(), False


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path

RUNTIME_FAILURE_STATUSES = {"provider_failure", "malformed_live_advisory"}


def specialist_result_requires_warning(result_packet: dict[str, Any]) -> bool:
    return str(result_packet.get("status") or "") in RUNTIME_FAILURE_STATUSES


def build_fallback_warning(*, assistant_name: str, result_packet: dict[str, Any], result_path: Path) -> dict[str, Any]:
    unresolved_risks = result_packet.get("unresolved_risks") or []
    reason = unresolved_risks[0] if unresolved_risks else result_packet.get("summary", "specialist_failure")
    return {
        "kind": "specialist_fallback",
        "severity": "warning",
        "assistant_name": assistant_name,
        "status": result_packet.get("status"),
        "message": f"{assistant_name} specialist/provider failed; continuing in Codex-led degraded mode.",
        "reason": reason,
        "recommended_next_actor": result_packet.get("recommended_next_actor", "codex"),
        "result_path": str(result_path),
    }


def write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def load_phase_cleanup_policy(repo_root: Path) -> dict[str, Any]:
    policy_path = repo_root / "runtime" / "vco" / "upstream" / "config" / "phase-cleanup-policy.json"
    return json.loads(policy_path.read_text(encoding="utf-8"))


def protected_document_extensions(policy: dict[str, Any]) -> list[str]:
    configured = policy.get("protected_document_policy", {}).get("extensions", [])
    normalized: list[str] = []
    for value in configured:
        token = str(value).strip().lower()
        if not token:
            continue
        if not token.startswith("."):
            token = f".{token}"
        if token not in normalized:
            normalized.append(token)
    return normalized


def is_protected_document(path: Path, extensions: list[str]) -> bool:
    return path.suffix.lower() in extensions


def _portable_relative_path(path: Path, base_root: Path) -> str:
    return os.path.relpath(path, base_root).replace(os.sep, "/")


def snapshot_protected_documents(base_root: Path, roots: list[Path], extensions: list[str]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    seen_roots: set[str] = set()
    for root in roots:
        resolved_root = root.resolve()
        root_key = str(resolved_root)
        if root_key in seen_roots or not resolved_root.exists():
            continue
        seen_roots.add(root_key)
        for file_path in resolved_root.rglob("*"):
            if not file_path.is_file() or not is_protected_document(file_path, extensions):
                continue
            stat = file_path.stat()
            items.append(
                {
                    "full_path": str(file_path.resolve()),
                    "relative_path": _portable_relative_path(file_path.resolve(), base_root.resolve()),
                    "root": str(resolved_root),
                    "extension": file_path.suffix.lower(),
                    "size_bytes": stat.st_size,
                    "last_write_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
            )
    items.sort(key=lambda item: item["relative_path"])
    return items


def build_protected_document_manifest(base_root: Path, tmp_root: Path, policy: dict[str, Any]) -> dict[str, Any]:
    protected_policy = policy.get("protected_document_policy", {})
    extensions = protected_document_extensions(policy)
    roots = [base_root / str(rel_root) for rel_root in protected_policy.get("snapshot_roots", [])]
    if tmp_root.exists() and all(tmp_root.resolve() != root.resolve() for root in roots):
        roots.append(tmp_root)
    snapshot = snapshot_protected_documents(base_root, roots, extensions)
    tmp_items = [item for item in snapshot if path_is_within(Path(item["full_path"]), tmp_root)]
    retained_items = [item for item in snapshot if not path_is_within(Path(item["full_path"]), tmp_root)]
    return {
        "snapshot": snapshot,
        "tmp_items": tmp_items,
        "retained_items": retained_items,
        "summary": {
            "protected_total": len(snapshot),
            "tmp_protected_total": len(tmp_items),
            "retained_outside_tmp_total": len(retained_items),
        },
    }


def move_protected_documents_to_quarantine(tmp_root: Path, quarantine_root: Path, extensions: list[str]) -> list[dict[str, Any]]:
    moved: list[dict[str, Any]] = []
    if not tmp_root.exists():
        return moved
    for file_path in sorted(tmp_root.rglob("*")):
        if not file_path.is_file() or not is_protected_document(file_path, extensions):
            continue
        relative_path = _portable_relative_path(file_path.resolve(), tmp_root.resolve())
        target_path = quarantine_root / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(file_path), str(target_path))
        moved.append(
            {
                "original_path": str(file_path.resolve()),
                "relative_path": relative_path,
                "quarantine_path": str(target_path.resolve()),
                "extension": target_path.suffix.lower(),
            }
        )
    return moved


def build_protected_document_post_checks(
    manifest: dict[str, Any],
    quarantined_items: list[dict[str, Any]] | None = None,
    *,
    preview_only: bool = False,
) -> list[dict[str, Any]]:
    assertions: list[dict[str, Any]] = []
    for item in manifest["retained_items"]:
        path = Path(item["full_path"])
        assertions.append(
            {
                "pass": path.exists(),
                "message": f"protected asset retained outside tmp: {item['relative_path']}",
                "path": str(path),
            }
        )
    if preview_only:
        for item in manifest["tmp_items"]:
            path = Path(item["full_path"])
            assertions.append(
                {
                    "pass": path.exists(),
                    "message": f"protected tmp asset preserved during preview: {item['relative_path']}",
                    "path": str(path),
                }
            )
        return assertions
    for item in quarantined_items or []:
        quarantine_path = Path(item["quarantine_path"])
        assertions.append(
            {
                "pass": quarantine_path.exists(),
                "message": f"protected tmp asset moved to quarantine: {item['relative_path']}",
                "path": str(quarantine_path),
            }
        )
    return assertions


def execute_phase_cleanup(
    *,
    repo_root: Path,
    artifacts_root: Path,
    session_root: Path,
    runtime_mode: str,
    preview_only: bool = False,
) -> dict[str, Any]:
    policy = load_phase_cleanup_policy(repo_root)
    protected_policy = policy.get("protected_document_policy", {})
    extensions = protected_document_extensions(policy)
    tmp_root = artifacts_root / ".tmp"
    quarantine_root = artifacts_root / str(protected_policy.get("quarantine_root", "outputs/runtime/process-health/quarantine/protected-documents"))
    manifest = build_protected_document_manifest(artifacts_root, tmp_root, policy)
    manifest_path = write_json(session_root / "cleanup-protected-document-manifest.json", manifest)

    tmp_file_count_before = sum(1 for path in tmp_root.rglob("*") if path.is_file()) if tmp_root.exists() else 0
    quarantined_items: list[dict[str, Any]] = []
    tmp_root_removed = False
    temp_files_removed = 0

    bounded_modes = {str(item) for item in policy.get("bounded_default_modes", [])}
    cleanup_mode = "receipt_only"
    if preview_only:
        cleanup_mode = "preview_only"
    elif tmp_root.exists():
        quarantined_items = move_protected_documents_to_quarantine(tmp_root, quarantine_root, extensions)
        shutil.rmtree(tmp_root)
        tmp_root_removed = True
        temp_files_removed = max(tmp_file_count_before - len(quarantined_items), 0)
        cleanup_mode = "quarantine_only" if quarantined_items else "bounded_cleanup_executed"
    elif runtime_mode in bounded_modes and manifest["summary"]["protected_total"]:
        cleanup_mode = str(protected_policy.get("default_action_mode", "quarantine_only"))

    quarantine_receipt_path = write_json(
        session_root / "cleanup-protected-document-quarantine.json",
        {
            "run_id": session_root.name,
            "preview_only": preview_only,
            "quarantine_root": str(quarantine_root),
            "items": quarantined_items,
            "generated_at": utc_now(),
        },
    )
    assertions = build_protected_document_post_checks(manifest, quarantined_items, preview_only=preview_only)
    failure_count = sum(0 if item["pass"] else 1 for item in assertions)
    cleanup_status = "ok" if failure_count == 0 else "degraded"
    if failure_count and cleanup_mode != "preview_only":
        cleanup_mode = "cleanup_degraded"
    return {
        "temp_files_removed": temp_files_removed,
        "node_processes_cleaned": 0,
        "cleanup_status": cleanup_status,
        "cleanup_mode": cleanup_mode,
        "policy_version": policy.get("version"),
        "tmp_root": str(tmp_root),
        "tmp_root_removed": tmp_root_removed,
        "preview_only": preview_only,
        "cleanup_steps": deepcopy(policy.get("cleanup_steps", [])),
        "protected_document_summary": {
            **manifest["summary"],
            "quarantined_total": len(quarantined_items),
            "quarantine_root": str(quarantine_root),
        },
        "post_cleanup_checks": {
            "total": len(assertions),
            "failure_count": failure_count,
            "assertions": assertions,
        },
        "evidence": {
            "manifest_path": str(manifest_path),
            "quarantine_receipt_path": str(quarantine_receipt_path),
        },
        "generated_at": utc_now(),
    }


def _compact_text(value: Any, limit: int = 180) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."


class RuntimeEventRecorder:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("", encoding="utf-8")
        self.seq = 0

    def emit(
        self,
        *,
        actor: str,
        state: str,
        phase: str,
        message: str,
        content_kind: str | None = None,
        content: Any | None = None,
        refs: list[str] | None = None,
        meta: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.seq += 1
        event = {
            "seq": self.seq,
            "ts": utc_now(),
            "phase": phase,
            "actor": actor,
            "state": state,
            "message": message,
        }
        compact_content = _compact_text(content)
        if content_kind:
            event["content_kind"] = content_kind
        if compact_content:
            event["content"] = compact_content
        if refs:
            event["refs"] = deepcopy(refs)
        if meta:
            event["meta"] = deepcopy(meta)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        return event


def materialize_benchmark_artifact_handoff(
    requested_artifacts_root: Path,
    effective_artifacts_root: Path,
    summary: dict[str, Any],
    summary_path: Path,
) -> dict[str, str] | None:
    if requested_artifacts_root.resolve() == effective_artifacts_root.resolve():
        return None
    requested_artifacts_root.mkdir(parents=True, exist_ok=True)
    requested_summary_copy = requested_artifacts_root / "runtime-summary.json"
    shutil.copy2(summary_path, requested_summary_copy)
    manifest_path = requested_artifacts_root / "benchmark-artifact-handoff.json"
    manifest = {
        "requested_artifacts_root": str(requested_artifacts_root.resolve()),
        "effective_artifacts_root": str(effective_artifacts_root.resolve()),
        "effective_session_root": summary["artifacts"]["session_root"],
        "effective_benchmark_result": summary["artifacts"]["effective_benchmark_result"],
        "requested_benchmark_result": summary["artifacts"]["requested_benchmark_result"],
        "requested_summary_copy": str(requested_summary_copy),
        "generated_at": utc_now(),
    }
    write_json(manifest_path, manifest)
    return {
        "manifest_path": str(manifest_path),
        "requested_summary_copy": str(requested_summary_copy),
    }


def build_intent_contract(config: GovernedRuntimeConfig) -> dict[str, Any]:
    inferred = config.mode == "benchmark_autonomous"
    return {
        "run_id": config.run_id,
        "mode": config.mode,
        "goal": config.task,
        "deliverable": "Governed EvCode execution closure with requirement, plan, specialist routing, verification, and cleanup artifacts.",
        "constraints": [
            "Preserve the fixed 6-stage governed runtime order.",
            "Do not fork runtime truth between release channels.",
            "Emit proof artifacts before claiming completion.",
            "Keep Codex as the final execution authority even when specialists are consulted.",
        ],
        "acceptance_criteria": [
            "Requirement doc exists.",
            "Execution plan exists.",
            "Execution receipt exists.",
            "Cleanup receipt exists.",
            "Specialist routing receipts exist when specialist routing is evaluated.",
        ],
        "non_goals": [
            "Create a second router.",
            "Skip requirement freezing.",
            "Skip cleanup.",
            "Allow advisory specialists to declare final completion.",
        ],
        "autonomy_mode": config.mode,
        "open_questions": [] if inferred or complete_requirement(config.task) else ["Clarify missing acceptance details if interactive mode is active."],
        "inferred_assumptions": [
            "Benchmark mode replaces live questioning with recorded assumptions."
        ] if inferred else [],
        "internal_grade": infer_internal_grade(config.task),
        "generated_at": utc_now(),
    }


def build_requirement_doc(config: GovernedRuntimeConfig, intent: dict[str, Any]) -> str:
    assumptions = intent["inferred_assumptions"] or ["No extra inferred assumptions were required."]
    return f"""# Governed Requirement

## Goal

{intent["goal"]}

## Deliverable

{intent["deliverable"]}

## Constraints

""" + "\n".join(f"- {item}" for item in intent["constraints"]) + f"""

## Acceptance Criteria

""" + "\n".join(f"- {item}" for item in intent["acceptance_criteria"]) + f"""

## Non-Goals

""" + "\n".join(f"- {item}" for item in intent["non_goals"]) + f"""

## Assumptions

""" + "\n".join(f"- {item}" for item in assumptions) + f"""

## Runtime Mode

- mode: `{config.mode}`
- profile: `{config.profile}`
- channel: `{config.channel}`
"""


def build_execution_plan(config: GovernedRuntimeConfig, intent: dict[str, Any], requirement_doc_path: Path) -> str:
    grade = intent["internal_grade"]
    return f"""# Governed Execution Plan

## Requirement Source

- requirement_doc: `{requirement_doc_path}`

## Internal Grade

- grade: `{grade}`

## Waves

1. Prepare host/runtime context and verify contract inputs.
2. Evaluate specialist routing inside `plan_execute` without creating a second router.
3. Execute the governed task path with explicit receipts.
4. Verify outputs and run mandatory cleanup.

## Ownership Boundaries

- host integration
- governed runtime bridge
- capability and provider policy
- specialist routing, task packets, and result packets
- benchmark adapter and proof surfaces

## Verification Commands

- `python3 scripts/verify/check_contracts.py`
- `python3 scripts/verify/check_proof_docs.py`
- `python3 -m unittest discover -s tests -p 'test_*.py'`

## Rollback Rules

- Do not widen scope without updating the requirement document.
- Preserve the previous runtime contract if a new bridge breaks tests.
- Reduce specialist behavior to Codex-only execution if advisory paths become opaque or unstable.

## Phase Cleanup Expectations

- remove temp artifacts attributable to the run
- record node audit status
- write cleanup receipt before completion is claimed
"""


def build_repository_path_summary(config: GovernedRuntimeConfig) -> str:
    return f"repo={config.repo_root.name}; channel={config.channel}; profile={config.profile}; workspace={config.workspace}"


def infer_file_scope_hints(task: str, route: dict[str, Any]) -> list[str]:
    domain = route["classification"]["domain"]
    hints: list[str] = []
    if domain in {"frontend_visual", "mixed_ui"}:
        hints.extend(["apps/", "packages/", "profiles/"])
    if domain in {"planning", "backend_engineering", "general_engineering", "mixed_ui"}:
        hints.extend(["scripts/", "config/", "tests/"])
    if "bridge" in task.lower():
        hints.append("packages/governed-runtime-bridge/")
    deduped: list[str] = []
    for hint in hints:
        if hint not in deduped:
            deduped.append(hint)
    return deduped


def build_architecture_notes(route: dict[str, Any]) -> list[str]:
    notes = [
        "VCO remains the sole governed runtime and route authority.",
        "Codex owns final execution, integration, verification, and completion.",
        "Specialist routing is evaluated during plan_execute only.",
    ]
    if route["classification"]["domain"] in {"frontend_visual", "mixed_ui"}:
        notes.append("Visual specialists may advise on UI direction but cannot own backend coupling or final merge.")
    return notes


def build_design_system_notes(route: dict[str, Any]) -> list[str]:
    if route["classification"]["domain"] in {"frontend_visual", "mixed_ui"}:
        return [
            "Prefer explicit typography, spacing, color, and motion rationale.",
            "Maintain responsive behavior and repository design-system coherence.",
        ]
    return ["No design-system specific guidance was required for this task."]


def build_skill_capsule(route: dict[str, Any], delegate: dict[str, Any]) -> dict[str, Any]:
    defaults = route.get("skill_capsule_defaults", {})
    classes = deepcopy(delegate.get("skill_capsule_classes", []))
    domain = route["classification"]["domain"]
    evidence = route["classification"]["evidence"]
    return {
        "capsule_id": f"{delegate['assistant_name']}-{domain}-{evidence}",
        "compiler": defaults.get("compiler", "vco_skill_compiler"),
        "version": defaults.get("version", utc_now()[:10]),
        "classes": classes,
        "guidance": [
            f"Purpose: {delegate['purpose']}",
            f"Authority tier: {delegate['authority_tier']}",
            f"Evidence mode: {evidence}",
        ],
        "prohibited_actions": deepcopy(defaults.get("control_plane_only_rules", [])),
        "output_contract": deepcopy(defaults.get("required_output_sections", [])),
    }


def build_allowed_capabilities(delegate: dict[str, Any]) -> dict[str, Any]:
    return {
        "mode": delegate.get("capability_mode", "proxy_mediated"),
        "direct_read_only_allowlist": deepcopy(delegate.get("direct_read_only_allowlist", [])),
        "proxy_allowlist": deepcopy(delegate.get("proxy_allowlist", [])),
        "mutation_allowlist": deepcopy(delegate.get("mutation_allowlist", [])),
        "denied": deepcopy(delegate.get("denied_capabilities", [])),
    }


def build_memory_policy(route: dict[str, Any], authoritative_context_refs: list[str]) -> dict[str, Any]:
    memory_policy = deepcopy(route.get("memory_policy", {}))
    memory_policy.setdefault("owner", "vco_artifacts")
    memory_policy.setdefault("specialist_local_memory", "ephemeral")
    sources = memory_policy.setdefault("authoritative_sources", [])
    for ref in authoritative_context_refs:
        if ref not in sources:
            sources.append(ref)
    return memory_policy


def default_authoritative_context_refs(config: GovernedRuntimeConfig) -> list[str]:
    return [
        f"docs/requirements/{slugify(config.task)}",
        f"docs/plans/{slugify(config.task)}-execution-plan",
        "assistant_policy_snapshot",
        "specialist_routing_receipt",
    ]


def build_specialist_delegation_payloads(
    config: GovernedRuntimeConfig,
    route: dict[str, Any],
    authoritative_context_refs: list[str] | None = None,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    task_packets: dict[str, dict[str, Any]] = {}
    exploration_briefs: dict[str, dict[str, Any]] = {}
    authoritative_refs = authoritative_context_refs or default_authoritative_context_refs(config)
    for delegate in route.get("requested_delegates", []):
        assistant_name = delegate["assistant_name"]
        exploration_mode = delegate.get("exploration_mode", "packetized")
        skill_capsule = build_skill_capsule(route, delegate)
        allowed_capabilities = build_allowed_capabilities(delegate)
        memory_policy = build_memory_policy(route, authoritative_refs)
        common_payload = {
            "specialist_name": assistant_name,
            "task_id": f"{config.run_id}-{assistant_name}",
            "run_id": config.run_id,
            "repository_path_summary": build_repository_path_summary(config),
            "file_scope": infer_file_scope_hints(config.task, route),
            "task_goal": config.task,
            "allowed_authority_tier": delegate["authority_tier"],
            "expected_output_type": delegate["expected_output_type"],
            "delegation_reason": delegate["reason"],
            "delegation_purpose": delegate["purpose"],
            "task_domain": route["classification"]["domain"],
            "task_risk": route["classification"]["risk"],
            "evidence_mode": route["classification"]["evidence"],
            "exploration_mode": exploration_mode,
            "skill_capsule": skill_capsule,
            "allowed_capabilities": allowed_capabilities,
            "required_receipts": deepcopy(delegate.get("required_receipts", route.get("required_receipts", []))),
            "authoritative_context_refs": deepcopy(authoritative_refs),
            "memory_policy": memory_policy,
        }
        if assistant_name == "claude" and exploration_mode == "autonomous":
            exploration_briefs[assistant_name] = {
                **common_payload,
                "mission_brief": (
                    "Autonomously inspect the repository and write a strong advisory artifact for Codex. "
                    "Prefer reading the most relevant project files yourself rather than relying on a heavy pre-packed context."
                ),
                "autonomy_instructions": [
                    "Explore the repository within the provided scope hints.",
                    "Synthesize findings into an actionable artifact for Codex.",
                    "Do not claim final engineering completion.",
                ],
                "guardrails": [
                    "Stay subordinate to the governed runtime.",
                    "Respect Codex as final executor.",
                    "Keep the output traceable to real project files.",
                ],
                "architecture_notes": build_architecture_notes(route),
                "design_system_notes": build_design_system_notes(route),
            }
            continue
        task_packets[assistant_name] = build_task_packet(
            specialist_name=assistant_name,
            task_id=common_payload["task_id"],
            run_id=common_payload["run_id"],
            repository_path_summary=common_payload["repository_path_summary"],
            file_scope=common_payload["file_scope"],
            task_goal=common_payload["task_goal"],
            constraints=[
                "Stay subordinate to the governed runtime.",
                "Do not claim final completion.",
                "Respect Codex as final executor.",
            ],
            acceptance_criteria=[
                "Output is actionable for Codex.",
                "Output respects the allowed authority tier.",
                "Output records remaining risks instead of hiding them.",
            ],
            non_goals=[
                "Bypass governed verification.",
                "Write secrets into tracked files.",
                "Override Codex final authority.",
            ],
            architecture_notes=build_architecture_notes(route),
            design_system_notes=build_design_system_notes(route),
            allowed_authority_tier=common_payload["allowed_authority_tier"],
            expected_output_type=common_payload["expected_output_type"],
            extras={
                "delegation_reason": common_payload["delegation_reason"],
                "delegation_purpose": common_payload["delegation_purpose"],
                "task_domain": common_payload["task_domain"],
                "task_risk": common_payload["task_risk"],
                "evidence_mode": common_payload["evidence_mode"],
                "exploration_mode": exploration_mode,
                "skill_capsule": common_payload["skill_capsule"],
                "allowed_capabilities": common_payload["allowed_capabilities"],
                "required_receipts": common_payload["required_receipts"],
                "authoritative_context_refs": common_payload["authoritative_context_refs"],
                "memory_policy": common_payload["memory_policy"],
            },
        )
    return task_packets, exploration_briefs


def build_stub_result_packet(delegation_payload: dict[str, Any], delegate: dict[str, Any]) -> dict[str, Any]:
    status = delegate.get("status", "contract_ready_live_unavailable")
    return build_result_packet(
        specialist_name=delegation_payload["specialist_name"],
        task_id=delegation_payload["task_id"],
        summary="Specialist delegation was evaluated under governed routing, but Codex kept the execution path active.",
        assumptions=[
            "Live specialist invocation was not enabled or not required for this run.",
            "Codex remains responsible for converting advisory intent into repo-safe changes.",
        ],
        proposed_actions=[
            "Use the delegation payload as advisory context.",
            "Keep changes gated by Codex-owned verification.",
        ],
        files_touched_or_proposed=delegation_payload["file_scope"],
        confidence_level=0.35,
        unresolved_risks=[delegate.get("reason", "No live specialist response was collected.")],
        recommended_next_actor="codex",
        extras={
            "status": status,
            "expected_output_type": delegation_payload["expected_output_type"],
            "exploration_mode": delegation_payload.get("exploration_mode", "packetized"),
            "capability_requests": [],
            "receipt_refs": [],
        },
    )


def _normalize_text_list(value: Any) -> list[str]:
    if isinstance(value, list):
        normalized: list[str] = []
        for item in value:
            if isinstance(item, str):
                normalized.append(item)
            elif isinstance(item, dict):
                normalized.append(str(item.get("description") or item.get("action_type") or json.dumps(item, ensure_ascii=False)))
            else:
                normalized.append(str(item))
        return normalized
    if value is None:
        return []
    return [str(value)]


def _normalize_confidence(value: Any) -> float:
    if isinstance(value, (int, float)):
        return max(0.0, min(1.0, float(value)))
    if isinstance(value, str):
        lowered = value.strip().lower()
        keyword_map = {"low": 0.35, "medium": 0.6, "high": 0.8}
        if lowered in keyword_map:
            return keyword_map[lowered]
        return max(0.0, min(1.0, float(lowered)))
    raise ValueError("unsupported confidence shape")


def _normalize_next_actor(value: Any) -> str:
    lowered = str(value).strip().lower()
    return lowered if lowered in {"codex", "claude", "gemini"} else "codex"


def _normalize_capability_requests(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        normalized: list[dict[str, Any]] = []
        for item in value:
            if isinstance(item, dict):
                normalized.append(deepcopy(item))
            elif item is not None:
                normalized.append({"capability": str(item), "mode": "proxy_mediated"})
        return normalized
    if value is None:
        return []
    return [{"capability": str(value), "mode": "proxy_mediated"}]


def _normalize_receipt_refs(value: Any) -> list[str]:
    return _normalize_text_list(value)


def normalize_live_result(delegation_payload: dict[str, Any], provider_spec: dict[str, Any], raw_payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return build_result_packet(
            specialist_name=delegation_payload["specialist_name"],
            task_id=delegation_payload["task_id"],
            summary=str(raw_payload["summary"]),
            assumptions=_normalize_text_list(raw_payload.get("assumptions")),
            proposed_actions=_normalize_text_list(raw_payload.get("proposed_actions")),
            files_touched_or_proposed=_normalize_text_list(raw_payload.get("files_touched_or_proposed")),
            confidence_level=_normalize_confidence(raw_payload.get("confidence_level", 0.0)),
            unresolved_risks=_normalize_text_list(raw_payload.get("unresolved_risks")),
            recommended_next_actor=_normalize_next_actor(raw_payload.get("recommended_next_actor", "codex")),
            extras={
                "status": "completed_live_advisory",
                "provider": provider_spec["provider"],
                "base_url": provider_spec["base_url"],
                "model": provider_spec["model"],
                "exploration_mode": delegation_payload.get("exploration_mode", "packetized"),
                "capability_requests": _normalize_capability_requests(raw_payload.get("capability_requests")),
                "receipt_refs": _normalize_receipt_refs(raw_payload.get("receipt_refs")),
            },
        )
    except (DelegationContractError, KeyError, TypeError, ValueError) as exc:
        return build_result_packet(
            specialist_name=delegation_payload["specialist_name"],
            task_id=delegation_payload["task_id"],
            summary="Specialist provider returned data that could not be normalized into the delegation contract.",
            assumptions=["The provider call completed but the payload shape did not satisfy the governed contract."],
            proposed_actions=["Fallback to Codex-only integration for this run."],
            files_touched_or_proposed=delegation_payload["file_scope"],
            confidence_level=0.0,
            unresolved_risks=[f"malformed_provider_response: {exc}"],
            recommended_next_actor="codex",
            extras={
                "status": "malformed_live_advisory",
                "provider": provider_spec["provider"],
                "exploration_mode": delegation_payload.get("exploration_mode", "packetized"),
                "capability_requests": [],
                "receipt_refs": [],
            },
        )


def write_specialist_artifacts(
    *,
    config: GovernedRuntimeConfig,
    session_root: Path,
    route: dict[str, Any],
    assistant_policy: dict[str, Any],
    provider_catalog: dict[str, dict[str, Any]],
    authoritative_context_refs: list[str],
    event_recorder: RuntimeEventRecorder,
) -> dict[str, Any]:
    specialist_dir = session_root / "specialists"
    specialist_dir.mkdir(parents=True, exist_ok=True)

    assistant_policy_path = write_json(
        session_root / "assistant-policy-snapshot.json",
        assistant_policy,
    )
    provider_snapshot_path = write_json(
        session_root / "assistant-provider-snapshot.json",
        sanitize_provider_catalog(provider_catalog),
    )
    route_receipt_path = write_json(
        session_root / "specialist-routing-receipt.json",
        route,
    )
    event_recorder.emit(
        actor="route",
        state="CLASSIFIED",
        phase="plan_execute",
        message=(
            f"task classified as {route['classification']['domain']} "
            f"(route={route['route_kind']}, final_executor={route['final_executor']})"
        ),
        content_kind="route",
        refs=[str(route_receipt_path)],
        meta={
            "domain": route["classification"]["domain"],
            "route_kind": route["route_kind"],
            "risk": route["classification"]["risk"],
            "evidence": route["classification"]["evidence"],
        },
    )
    event_recorder.emit(
        actor="codex",
        state="ACTIVE",
        phase="plan_execute",
        message="codex-led governed execution authority is active",
        content_kind="status",
        refs=[str(route_receipt_path)],
    )
    for delegate in route.get("requested_delegates", []):
        event_recorder.emit(
            actor=delegate["assistant_name"],
            state="REQUESTED",
            phase="plan_execute",
            message=delegate.get("purpose", "specialist requested"),
            content_kind="status",
            content=delegate.get("reason"),
            refs=[str(route_receipt_path)],
        )
    for delegate in route.get("suppressed_delegates", []):
        event_recorder.emit(
            actor=delegate["assistant_name"],
            state="SUPPRESSED",
            phase="plan_execute",
            message=delegate.get("reason", "specialist suppressed by routing policy"),
            content_kind="status",
            refs=[str(route_receipt_path)],
        )
    for delegate in route.get("degraded_delegates", []):
        event_recorder.emit(
            actor=delegate["assistant_name"],
            state="DEGRADED",
            phase="plan_execute",
            message=delegate.get("status", "specialist degraded before invocation"),
            content_kind="warning",
            content=delegate.get("reason"),
            refs=[str(route_receipt_path)],
        )

    task_packets, exploration_briefs = build_specialist_delegation_payloads(config, route, authoritative_context_refs)
    task_packet_paths: dict[str, str] = {}
    exploration_brief_paths: dict[str, str] = {}
    request_preview_paths: dict[str, str] = {}
    result_paths: dict[str, str] = {}
    capability_proxy_events: list[dict[str, Any]] = []
    runtime_warning_events: list[dict[str, Any]] = []
    runtime_failure_delegates: list[dict[str, Any]] = []

    degraded_lookup = {
        item["assistant_name"]: item
        for item in (route.get("degraded_delegates") or [])
    }
    active_lookup = {
        item["assistant_name"]: item
        for item in (route.get("active_delegates") or [])
    }

    delegation_payloads = {**task_packets, **exploration_briefs}
    for assistant_name, delegation_payload in delegation_payloads.items():
        if assistant_name in exploration_briefs:
            payload_path = write_json(specialist_dir / f"{assistant_name}-exploration-brief.json", delegation_payload)
            exploration_brief_paths[assistant_name] = str(payload_path)
        else:
            payload_path = write_json(specialist_dir / f"{assistant_name}-task-packet.json", delegation_payload)
            task_packet_paths[assistant_name] = str(payload_path)
        request_preview_path = write_json(
            specialist_dir / f"{assistant_name}-request-preview.json",
            build_adapter_request_preview(delegation_payload, provider_catalog[assistant_name]),
        )
        request_preview_paths[assistant_name] = str(request_preview_path)
        event_recorder.emit(
            actor=assistant_name,
            state="DISPATCHING",
            phase="plan_execute",
            message="specialist request preview recorded",
            content_kind="status",
            refs=[str(request_preview_path)],
        )

        if assistant_name in active_lookup:
            event_recorder.emit(
                actor=assistant_name,
                state="ACTIVE",
                phase="plan_execute",
                message="live specialist invocation in progress",
                content_kind="status",
                refs=[str(request_preview_path)],
            )
            try:
                raw_payload = invoke_specialist_json(delegation_payload, provider_catalog[assistant_name])
                result_packet = normalize_live_result(delegation_payload, provider_catalog[assistant_name], raw_payload)
            except Exception as exc:  # pragma: no cover - network path
                result_packet = build_result_packet(
                    specialist_name=delegation_payload["specialist_name"],
                    task_id=delegation_payload["task_id"],
                    summary="Specialist invocation failed and the governed runtime degraded back to Codex-only execution.",
                    assumptions=["Provider calls are optional and must not break governed execution."],
                    proposed_actions=["Keep Codex-only execution for this run."],
                    files_touched_or_proposed=delegation_payload["file_scope"],
                    confidence_level=0.0,
                    unresolved_risks=[str(exc)],
                    recommended_next_actor="codex",
                    extras={
                        "status": "provider_failure",
                        "exploration_mode": delegation_payload.get("exploration_mode", "packetized"),
                        "capability_requests": [],
                        "receipt_refs": [],
                    },
                )
        else:
            result_packet = build_stub_result_packet(
                delegation_payload,
                degraded_lookup.get(assistant_name, {"status": "not_selected"}),
            )
        result_path = write_json(specialist_dir / f"{assistant_name}-result.json", result_packet)
        result_paths[assistant_name] = str(result_path)
        if result_packet.get("status") == "completed_live_advisory":
            event_recorder.emit(
                actor=assistant_name,
                state="COMPLETED",
                phase="plan_execute",
                message=f"{assistant_name} advisory completed",
                content_kind="result_summary",
                content=result_packet.get("summary"),
                refs=[str(result_path)],
            )
        elif assistant_name in active_lookup:
            event_recorder.emit(
                actor=assistant_name,
                state="DEGRADED",
                phase="plan_execute",
                message=result_packet.get("status", "specialist degraded during invocation"),
                content_kind="warning",
                content=(result_packet.get("unresolved_risks") or [result_packet.get("summary")])[0],
                refs=[str(result_path)],
            )
        else:
            event_recorder.emit(
                actor=assistant_name,
                state="DEGRADED",
                phase="plan_execute",
                message=result_packet.get("status", "specialist live invocation unavailable"),
                content_kind="result_summary",
                content=result_packet.get("summary"),
                refs=[str(result_path)],
            )
        if assistant_name in active_lookup and specialist_result_requires_warning(result_packet):
            warning_event = build_fallback_warning(
                assistant_name=assistant_name,
                result_packet=result_packet,
                result_path=result_path,
            )
            runtime_warning_events.append(warning_event)
            runtime_failure_delegates.append(
                {
                    **active_lookup[assistant_name],
                    "status": result_packet.get("status"),
                    "reason": warning_event["reason"],
                    "result_path": str(result_path),
                }
            )
        capability_proxy_events.append(
            {
                "assistant_name": assistant_name,
                "capability_mode": delegation_payload.get("allowed_capabilities", {}).get("mode"),
                "requested_capabilities": deepcopy(result_packet.get("capability_requests", [])),
                "status": "not_requested" if not result_packet.get("capability_requests") else "proxy_required",
            }
        )

    capability_proxy_receipt_path = write_json(
        specialist_dir / "capability-proxy-receipt.json",
        {
            "run_id": config.run_id,
            "owner": route.get("memory_policy", {}).get("owner", "vco_artifacts"),
            "events": capability_proxy_events,
            "generated_at": utc_now(),
        },
    )

    combined_degraded_delegates = {
        item["assistant_name"]: item
        for item in [
            *(route.get("degraded_delegates") or []),
            *runtime_failure_delegates,
        ]
    }
    integration_receipt = {
        "run_id": config.run_id,
        "final_executor": "codex",
        "route_kind": route["route_kind"],
        "requested_specialists": [item["assistant_name"] for item in route.get("requested_delegates", [])],
        "active_specialists": [item["assistant_name"] for item in route.get("active_delegates", [])],
        "degraded_specialists": sorted(combined_degraded_delegates.keys()),
        "suppressed_specialists": [item["assistant_name"] for item in route.get("suppressed_delegates", [])],
        "warning_count": len(runtime_warning_events),
        "generated_at": utc_now(),
    }
    integration_receipt_path = write_json(
        specialist_dir / "codex-integration-receipt.json",
        integration_receipt,
    )
    event_recorder.emit(
        actor="codex",
        state="INTEGRATING",
        phase="plan_execute",
        message="codex is integrating specialist outputs into governed execution",
        content_kind="integration",
        content=(
            f"requested={','.join(integration_receipt['requested_specialists']) or 'none'}; "
            f"degraded={','.join(integration_receipt['degraded_specialists']) or 'none'}"
        ),
        refs=[str(integration_receipt_path)],
    )
    return {
        "assistant_policy_snapshot": str(assistant_policy_path),
        "assistant_provider_snapshot": str(provider_snapshot_path),
        "specialist_routing_receipt": str(route_receipt_path),
        "specialist_task_packets": task_packet_paths,
        "specialist_exploration_briefs": exploration_brief_paths,
        "specialist_request_previews": request_preview_paths,
        "specialist_results": result_paths,
        "capability_proxy_receipt": str(capability_proxy_receipt_path),
        "codex_integration_receipt": str(integration_receipt_path),
        "runtime_degraded_delegates": list(combined_degraded_delegates.values()),
        "warnings": runtime_warning_events,
    }


def write_runtime_session(config: GovernedRuntimeConfig) -> dict[str, Any]:
    slug = slugify(config.task)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    effective_artifacts_root = config.artifacts_root.resolve()
    artifacts_redirected = False
    if config.channel == "benchmark":
        effective_artifacts_root, artifacts_redirected = ensure_benchmark_artifacts_root(
            config.artifacts_root,
            config.workspace,
            config.run_id,
        )

    session_root = effective_artifacts_root / "outputs" / "runtime" / "vibe-sessions" / config.run_id
    session_root.mkdir(parents=True, exist_ok=True)
    event_recorder = RuntimeEventRecorder(session_root / "runtime-events.jsonl")
    event_recorder.emit(
        actor="system",
        state="RUN_START",
        phase="skeleton_check",
        message="governed runtime session started",
        content_kind="status",
        content=config.task,
    )

    existing = detect_existing_artifacts(effective_artifacts_root)
    skeleton_receipt = {
        "run_id": config.run_id,
        "mode": config.mode,
        "workspace": str(config.workspace),
        "repo_root": str(config.repo_root),
        "requested_artifacts_root": str(config.artifacts_root),
        "effective_artifacts_root": str(effective_artifacts_root),
        "artifacts_redirected": artifacts_redirected,
        "existing": existing,
        "generated_at": utc_now(),
    }
    skeleton_receipt_path = write_json(session_root / "skeleton-receipt.json", skeleton_receipt)
    event_recorder.emit(
        actor="system",
        state="SKELETON_READY",
        phase="skeleton_check",
        message="skeleton check receipt written",
        content_kind="status",
        refs=[str(skeleton_receipt_path)],
    )

    intent = build_intent_contract(config)
    intent_path = write_json(session_root / "intent-contract.json", intent)
    event_recorder.emit(
        actor="system",
        state="INTENT_FROZEN",
        phase="deep_interview",
        message="intent contract frozen",
        content_kind="status",
        refs=[str(intent_path)],
    )

    requirement_doc_path = effective_artifacts_root / "docs" / "requirements" / f"{date}-{slug}.md"
    write_text(requirement_doc_path, build_requirement_doc(config, intent))
    requirement_receipt_path = write_json(
        session_root / "requirement-receipt.json",
        {
            "run_id": config.run_id,
            "requirement_doc_path": str(requirement_doc_path),
            "mode": config.mode,
            "generated_at": utc_now(),
        },
    )
    event_recorder.emit(
        actor="system",
        state="REQUIREMENT_FROZEN",
        phase="requirement_doc",
        message="requirement document written",
        content_kind="status",
        refs=[str(requirement_doc_path), str(requirement_receipt_path)],
    )

    execution_plan_path = effective_artifacts_root / "docs" / "plans" / f"{date}-{slug}-execution-plan.md"
    write_text(execution_plan_path, build_execution_plan(config, intent, requirement_doc_path))
    execution_plan_receipt_path = write_json(
        session_root / "execution-plan-receipt.json",
        {
            "run_id": config.run_id,
            "execution_plan_path": str(execution_plan_path),
            "internal_grade": intent["internal_grade"],
            "generated_at": utc_now(),
        },
    )
    event_recorder.emit(
        actor="system",
        state="PLAN_READY",
        phase="xl_plan",
        message="execution plan written",
        content_kind="status",
        refs=[str(execution_plan_path), str(execution_plan_receipt_path)],
    )

    provider_policy_snapshot_path = None
    if config.channel == "benchmark":
        policy_source = config.repo_root / "config" / "provider-policy.benchmark.json"
        provider_policy_snapshot_path = session_root / "provider-policy-snapshot.json"
        shutil.copy2(policy_source, provider_policy_snapshot_path)

    assistant_policy = load_assistant_policy(config.repo_root, config.channel)
    routing_policy = load_routing_policy(config.repo_root)
    provider_catalog = resolve_assistant_provider_catalog(assistant_policy)
    route = resolve_specialist_route(
        task=config.task,
        channel=config.channel,
        routing_policy=routing_policy,
        assistant_policy=assistant_policy,
        provider_catalog=provider_catalog,
    )
    authoritative_context_refs = [
        str(requirement_doc_path),
        str(execution_plan_path),
        str(session_root / "assistant-policy-snapshot.json"),
        str(session_root / "specialist-routing-receipt.json"),
        str(session_root / "specialists" / "codex-integration-receipt.json"),
    ]
    specialist_artifacts = write_specialist_artifacts(
        config=config,
        session_root=session_root,
        route=route,
        assistant_policy=assistant_policy,
        provider_catalog=provider_catalog,
        authoritative_context_refs=authoritative_context_refs,
        event_recorder=event_recorder,
    )
    runtime_route = deepcopy(route)
    runtime_route["degraded_delegates"] = specialist_artifacts["runtime_degraded_delegates"]
    runtime_route["fallback_warnings"] = specialist_artifacts["warnings"]
    execution_outcome = "degraded_fallback_to_codex" if specialist_artifacts["warnings"] else "normal"

    execute_artifacts: dict[str, Any] = {
        "execute_receipt_path": None,
        "requested_result_json_path": None,
        "result_json_path": None,
        "stdout_path": None,
        "stderr_path": None,
        "status": "receipt_only",
        "exit_code": None,
    }
    if config.channel == "benchmark":
        execute_artifacts = execute_benchmark_task(
            BenchmarkExecutionConfig(
                task=config.task,
                workspace=config.workspace,
                repo_root=config.repo_root,
                session_root=session_root,
                run_id=config.run_id,
                channel=config.channel,
                profile=config.profile,
                mode=config.mode,
                artifacts_root=effective_artifacts_root,
                result_json_path=config.result_json_path,
            )
        )
        execute_receipt_path = Path(execute_artifacts["execute_receipt_path"])
    else:
        execute_receipt_path = write_json(
            session_root / "phase-execute.json",
            {
                "run_id": config.run_id,
                "mode": config.mode,
                "stage_order": FIXED_STAGE_ORDER,
                "internal_grade": intent["internal_grade"],
                "subagent_suffix_required": True,
                "route_kind": route["route_kind"],
                "requested_specialists": [item["assistant_name"] for item in route.get("requested_delegates", [])],
                "execution_outcome": execution_outcome,
                "warning_count": len(specialist_artifacts["warnings"]),
                "warnings": specialist_artifacts["warnings"],
                "generated_at": utc_now(),
            },
        )
    event_recorder.emit(
        actor="codex",
        state="COMPLETED",
        phase="plan_execute",
        message=f"governed execution phase closed with outcome={execution_outcome}",
        content_kind="status",
        refs=[str(execute_receipt_path)],
    )

    cleanup_payload = execute_phase_cleanup(
        repo_root=config.repo_root,
        artifacts_root=effective_artifacts_root,
        session_root=session_root,
        runtime_mode=config.mode,
    )
    cleanup_receipt_path = write_json(
        session_root / "cleanup-receipt.json",
        {
            "run_id": config.run_id,
            **cleanup_payload,
        },
    )
    event_recorder.emit(
        actor="system",
        state="CLEANUP_OK" if cleanup_payload["cleanup_status"] == "ok" else "CLEANUP_DEGRADED",
        phase="phase_cleanup",
        message=(
            "phase cleanup receipt written "
            f"(mode={cleanup_payload['cleanup_mode']}, failures={cleanup_payload['post_cleanup_checks']['failure_count']})"
        ),
        content_kind="status",
        refs=[str(cleanup_receipt_path)],
    )

    summary = {
        "run_id": config.run_id,
        "channel": config.channel,
        "profile": config.profile,
        "mode": config.mode,
        "task": config.task,
        "stage_order": FIXED_STAGE_ORDER,
        "execution_outcome": execution_outcome,
        "warnings": specialist_artifacts["warnings"],
        "artifacts": {
            "requested_artifacts_root": str(config.artifacts_root),
            "effective_artifacts_root": str(effective_artifacts_root),
            "artifacts_redirected": artifacts_redirected,
            "session_root": str(session_root),
            "skeleton_receipt": str(skeleton_receipt_path),
            "intent_contract": str(intent_path),
            "requirement_doc": str(requirement_doc_path),
            "requirement_receipt": str(requirement_receipt_path),
            "execution_plan": str(execution_plan_path),
            "execution_plan_receipt": str(execution_plan_receipt_path),
            "assistant_policy_snapshot": specialist_artifacts["assistant_policy_snapshot"],
            "assistant_provider_snapshot": specialist_artifacts["assistant_provider_snapshot"],
            "specialist_routing_receipt": specialist_artifacts["specialist_routing_receipt"],
            "specialist_task_packets": specialist_artifacts["specialist_task_packets"],
            "specialist_exploration_briefs": specialist_artifacts["specialist_exploration_briefs"],
            "specialist_request_previews": specialist_artifacts["specialist_request_previews"],
            "specialist_results": specialist_artifacts["specialist_results"],
            "capability_proxy_receipt": specialist_artifacts["capability_proxy_receipt"],
            "codex_integration_receipt": specialist_artifacts["codex_integration_receipt"],
            "execute_receipt": str(execute_receipt_path),
            "requested_benchmark_result": execute_artifacts["requested_result_json_path"],
            "effective_benchmark_result": execute_artifacts["result_json_path"],
            "benchmark_result": execute_artifacts["result_json_path"],
            "benchmark_stdout": execute_artifacts["stdout_path"],
            "benchmark_stderr": execute_artifacts["stderr_path"],
            "artifacts_handoff_manifest": None,
            "requested_runtime_summary": None,
            "provider_policy_snapshot": str(provider_policy_snapshot_path) if provider_policy_snapshot_path else None,
            "cleanup_receipt": str(cleanup_receipt_path),
            "runtime_events": str(event_recorder.path),
        },
        "specialist_routing": runtime_route,
        "telemetry": {
            "runtime_events_path": str(event_recorder.path),
            "event_count": event_recorder.seq,
        },
    }
    summary_path = write_json(session_root / "runtime-summary.json", summary)
    handoff_artifacts = None
    if artifacts_redirected:
        handoff_artifacts = materialize_benchmark_artifact_handoff(
            config.artifacts_root.resolve(),
            effective_artifacts_root,
            summary,
            summary_path,
        )
    if handoff_artifacts:
        summary["artifacts"]["artifacts_handoff_manifest"] = handoff_artifacts["manifest_path"]
        summary["artifacts"]["requested_runtime_summary"] = handoff_artifacts["requested_summary_copy"]
        summary_path = write_json(session_root / "runtime-summary.json", summary)
        shutil.copy2(summary_path, handoff_artifacts["requested_summary_copy"])
    summary["summary_path"] = str(summary_path)
    return summary


def build_context_advice(task: str, mode: str, artifacts_root: Path | None = None) -> dict[str, Any]:
    grade = infer_internal_grade(task)
    existing = detect_existing_artifacts(artifacts_root) if artifacts_root else {
        "latest_requirement_doc": None,
        "latest_execution_plan": None,
    }
    return {
        "mode": mode,
        "internal_grade_hint": grade,
        "should_skip_followup_questions": mode == "benchmark_autonomous" and complete_requirement(task),
        "must_append_vibe_suffix": True,
        "stage_order": FIXED_STAGE_ORDER,
        "latest_requirement_doc": existing["latest_requirement_doc"],
        "latest_execution_plan": existing["latest_execution_plan"],
    }


def render_context_block(advice: dict[str, Any]) -> str:
    requirement_doc = advice.get("latest_requirement_doc") or "none"
    execution_plan = advice.get("latest_execution_plan") or "none"
    return "\n".join(
        [
            "EvCode governed runtime context:",
            f"- mode: {advice['mode']}",
            f"- internal grade hint: {advice['internal_grade_hint']}",
            f"- stage order: {', '.join(advice['stage_order'])}",
            f"- latest requirement doc: {requirement_doc}",
            f"- latest execution plan: {execution_plan}",
            f"- skip follow-up questions now: {str(advice['should_skip_followup_questions']).lower()}",
            "- preserve requirement freeze, plan traceability, verification evidence, and phase cleanup",
            "- the active host bridge must keep each governed user turn equivalent to explicit `$vibe`",
            "- if subagents are spawned, child work must remain governed by vibe and end with ` $vibe`",
        ]
    )


def load_task_from_env(default: str = "") -> str:
    return os.environ.get("EVCODE_TASK", default)


def new_run_id(prefix: str = "run") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"
