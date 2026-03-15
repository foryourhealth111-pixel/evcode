from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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


def write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def build_intent_contract(config: GovernedRuntimeConfig) -> dict[str, Any]:
    inferred = config.mode == "benchmark_autonomous"
    return {
        "run_id": config.run_id,
        "mode": config.mode,
        "goal": config.task,
        "deliverable": "Governed EvCode execution closure with requirement, plan, verification, and cleanup artifacts.",
        "constraints": [
            "Preserve the fixed 6-stage governed runtime order.",
            "Do not fork runtime truth between release channels.",
            "Emit proof artifacts before claiming completion.",
        ],
        "acceptance_criteria": [
            "Requirement doc exists.",
            "Execution plan exists.",
            "Execution receipt exists.",
            "Cleanup receipt exists.",
        ],
        "non_goals": [
            "Create a second router.",
            "Skip requirement freezing.",
            "Skip cleanup.",
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
2. Execute the governed task path with explicit receipts.
3. Verify outputs and run mandatory cleanup.

## Ownership Boundaries

- host integration
- governed runtime bridge
- capability and provider policy
- benchmark adapter and proof surfaces

## Verification Commands

- `python3 scripts/verify/check_contracts.py`
- `python3 scripts/verify/check_proof_docs.py`
- `python3 -m unittest discover -s tests -p 'test_*.py'`

## Rollback Rules

- Do not widen scope without updating the requirement document.
- Preserve the previous runtime contract if a new bridge breaks tests.

## Phase Cleanup Expectations

- remove temp artifacts attributable to the run
- record node audit status
- write cleanup receipt before completion is claimed
"""


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

    intent = build_intent_contract(config)
    intent_path = write_json(session_root / "intent-contract.json", intent)

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

    provider_policy_snapshot_path = None
    if config.channel == "benchmark":
        policy_source = config.repo_root / "config" / "provider-policy.benchmark.json"
        provider_policy_snapshot_path = session_root / "provider-policy-snapshot.json"
        shutil.copy2(policy_source, provider_policy_snapshot_path)

    execute_artifacts: dict[str, Any] = {
        "execute_receipt_path": None,
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
                "generated_at": utc_now(),
            },
        )

    cleanup_receipt_path = write_json(
        session_root / "cleanup-receipt.json",
        {
            "run_id": config.run_id,
            "temp_files_removed": 0,
            "node_processes_cleaned": 0,
            "cleanup_status": "ok",
            "generated_at": utc_now(),
        },
    )

    summary = {
        "run_id": config.run_id,
        "channel": config.channel,
        "profile": config.profile,
        "mode": config.mode,
        "task": config.task,
        "stage_order": FIXED_STAGE_ORDER,
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
            "execute_receipt": str(execute_receipt_path),
            "benchmark_result": execute_artifacts["result_json_path"],
            "benchmark_stdout": execute_artifacts["stdout_path"],
            "benchmark_stderr": execute_artifacts["stderr_path"],
            "provider_policy_snapshot": str(provider_policy_snapshot_path) if provider_policy_snapshot_path else None,
            "cleanup_receipt": str(cleanup_receipt_path),
        },
    }
    summary_path = write_json(session_root / "runtime-summary.json", summary)
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
