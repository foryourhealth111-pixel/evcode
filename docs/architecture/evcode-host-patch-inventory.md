# EvCode Host Patch Inventory

## Purpose

This document records every EvCode-specific mutation applied to the selected Codex host.

EvCode is not allowed to accumulate silent host edits.

## Current State

- applied to vendored source: none
- concrete release patch prepared: `subagent-vibe-suffix`
- verification source: `scripts/verify/check_host_bridge.py`

## Decision Rule

1. Prefer native host hook surfaces.
2. Only patch if the ` $vibe` suffix contract cannot be physically guaranteed by hooks.
3. Keep the patch limited to subagent prompt finalization.

## Source-Proven Trigger

The materialized `stellarlinkco/codex` source now proves the trigger condition:

- `docs/hooks.md` states that `SubagentStart` only injects `additionalContext` into the spawned agent context.
- `docs/hooks.md` also states that `updatedInput` is only consumed for `pre_tool_use`.
- `codex-rs/core/src/tools/handlers/multi_agents.rs` collects only `additional_context` from `SubagentStart` hook outcomes.
- `spawn.rs` and `spawn_team.rs` inject hook context and then still submit the original `input_items`.

That combination means hook-only integration can preserve governed context, but cannot physically guarantee the child task text ends with ` $vibe`.

## Required Evidence Before Patch Adoption

- real host hook fixture analysis
- failure proof showing hooks alone are insufficient
- passing verification showing the patch restores the suffix contract

## Concrete Patch Scope

The prepared patch is intentionally narrow:

- add one helper that appends ` $vibe` to the first text input when missing
- call the helper in `spawn_agent`
- call the helper in `spawn_team`
- do not change hook dispatch, session lifecycle, or non-subagent prompt assembly
