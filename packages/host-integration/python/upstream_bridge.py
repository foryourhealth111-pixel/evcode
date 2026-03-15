from __future__ import annotations

import json
from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Evidence:
    path: str
    line: int
    statement: str


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _line_number(text: str, needle: str) -> int:
    for index, line in enumerate(text.splitlines(), start=1):
        if needle in line:
            return index
    raise ValueError(f"needle not found: {needle}")


def _evidence(path: Path, needle: str, statement: str) -> Evidence:
    text = _read(path)
    return Evidence(
        path=str(path),
        line=_line_number(text, needle),
        statement=statement,
    )


def analyze_materialized_host(repo_root: Path) -> dict:
    repo_root = Path(repo_root).resolve()
    source_lock = json.loads((repo_root / "config" / "sources.lock.json").read_text(encoding="utf-8"))
    host_root = repo_root / source_lock["host"]["vendored_dir"] / source_lock["host"]["materialized_subdir"]
    host_hooks_doc = host_root / "docs" / "hooks.md"
    codex_path = host_root / "codex-rs" / "core" / "src" / "codex.rs"
    multi_agents_path = host_root / "codex-rs" / "core" / "src" / "tools" / "handlers" / "multi_agents.rs"
    spawn_path = host_root / "codex-rs" / "core" / "src" / "tools" / "handlers" / "multi_agents" / "spawn.rs"
    spawn_team_path = host_root / "codex-rs" / "core" / "src" / "tools" / "handlers" / "multi_agents" / "spawn_team.rs"

    hooks_text = _read(host_hooks_doc)
    codex_text = _read(codex_path)
    multi_agents_text = _read(multi_agents_path)
    spawn_text = _read(spawn_path)
    spawn_team_text = _read(spawn_team_path)

    supports_additional_context = "additionalContext` output is injected into the spawned agent" in hooks_text
    updated_input_is_pre_tool_use_only = "`updatedInput` is only consumed for `pre_tool_use`." in hooks_text
    user_prompt_submit_receives_prompt_snapshot = "hook_event: HookEvent::UserPromptSubmit { prompt }" in codex_text
    user_prompt_submit_records_context_only = "self.record_hook_context(turn_context, &additional_context)" in codex_text
    user_turn_uses_original_items_after_hook = (
        ".dispatch_user_prompt_submit_hook(current_context.as_ref(), &items)" in codex_text
        and "sess.steer_input(items, None).await" in codex_text
    )
    dispatcher_collects_context_only = "additional_context.extend(result.additional_context);" in multi_agents_text
    spawn_agent_injects_context_before_send = (
        ".inject_developer_message_without_turn(agent_id, injected)" in spawn_text
        and ".send_spawn_input(agent_id, input_items, notification_source)" in spawn_text
    )
    spawn_team_injects_context_before_send = (
        ".inject_developer_message_without_turn(agent_id, injected)" in spawn_team_text
        and ".send_spawn_input(agent_id, input_items, notification_source)" in spawn_team_text
    )

    requires_host_patch_for_physical_suffix = all(
        [
            supports_additional_context,
            updated_input_is_pre_tool_use_only,
            user_prompt_submit_receives_prompt_snapshot,
            user_prompt_submit_records_context_only,
            user_turn_uses_original_items_after_hook,
            dispatcher_collects_context_only,
            spawn_agent_injects_context_before_send,
            spawn_team_injects_context_before_send,
        ]
    )

    evidence = [
        _evidence(
            host_hooks_doc,
            "additionalContext` output is injected into the spawned agent",
            "SubagentStart hooks can inject context into the child thread, but the contract only promises context injection.",
        ),
        _evidence(
            host_hooks_doc,
            "`updatedInput` is only consumed for `pre_tool_use`.",
            "The hook contract does not permit prompt rewriting for UserPromptSubmit or SubagentStart.",
        ),
        _evidence(
            codex_path,
            "hook_event: HookEvent::UserPromptSubmit { prompt }",
            "UserPromptSubmit hooks receive a prompt snapshot, not a mutable input handle.",
        ),
        _evidence(
            codex_path,
            "self.record_hook_context(turn_context, &additional_context)",
            "UserPromptSubmit dispatch records injected context but does not rewrite the pending turn items.",
        ),
        _evidence(
            codex_path,
            ".dispatch_user_prompt_submit_hook(current_context.as_ref(), &items)",
            "The live turn still passes the original items into the UserPromptSubmit hook.",
        ),
        _evidence(
            codex_path,
            "sess.steer_input(items, None).await",
            "After the hook returns, Codex continues with the original items unless the host is patched.",
        ),
        _evidence(
            multi_agents_path,
            "additional_context.extend(result.additional_context);",
            "The multi-agent hook dispatcher collects only additional_context from SubagentStart outcomes.",
        ),
        _evidence(
            spawn_path,
            ".inject_developer_message_without_turn(agent_id, injected)",
            "spawn_agent injects hook context as a developer message before sending child input.",
        ),
        _evidence(
            spawn_path,
            ".send_spawn_input(agent_id, input_items, notification_source)",
            "spawn_agent still submits the original input_items after hook injection.",
        ),
        _evidence(
            spawn_team_path,
            ".inject_developer_message_without_turn(agent_id, injected)",
            "spawn_team injects hook context as a developer message before sending member task input.",
        ),
        _evidence(
            spawn_team_path,
            ".send_spawn_input(agent_id, input_items, notification_source)",
            "spawn_team still submits the original member task text after hook injection.",
        ),
    ]

    return {
        "host": source_lock["host"]["id"],
        "commit": source_lock["host"]["commit"],
        "materialized_host_root": str(host_root),
        "user_prompt_submit": {
            "hook_receives_prompt_snapshot": user_prompt_submit_receives_prompt_snapshot,
            "hook_updated_input_is_pre_tool_use_only": updated_input_is_pre_tool_use_only,
            "dispatcher_records_context_only": user_prompt_submit_records_context_only,
            "turn_uses_original_items_after_hook": user_turn_uses_original_items_after_hook,
            "requires_host_patch_for_physical_suffix": requires_host_patch_for_physical_suffix,
            "recommended_patch": "vendor/codex-host/patches/subagent-vibe-suffix.patch",
        },
        "subagent_start": {
            "hook_supports_additional_context": supports_additional_context,
            "hook_updated_input_is_pre_tool_use_only": updated_input_is_pre_tool_use_only,
            "dispatcher_collects_context_only": dispatcher_collects_context_only,
            "spawn_agent_injects_context_before_send": spawn_agent_injects_context_before_send,
            "spawn_team_injects_context_before_send": spawn_team_injects_context_before_send,
            "requires_host_patch_for_physical_suffix": requires_host_patch_for_physical_suffix,
            "recommended_patch": "vendor/codex-host/patches/subagent-vibe-suffix.patch",
        },
        "evidence": [asdict(item) for item in evidence],
    }
