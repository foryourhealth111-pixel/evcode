# EvCode Real Host Bridge Proof

## Goal

Freeze the real `stellarlinkco/codex` host seam analysis into a release-auditable design proof.

## Materialized Source

- host: `vendor/codex-host/upstream`
- commit: `82a925f8d366754ecddad8bba56f2bf74de3f2c0`

## Verified Facts

1. `SubagentStart` hooks inject additional context into the child thread.
2. `updatedInput` is only honored for `pre_tool_use`, not for `SubagentStart`.
3. The multi-agent hook dispatcher aggregates only `additional_context` values from `SubagentStart`.
4. `spawn_agent` injects hook context and then sends the original `input_items`.
5. `spawn_team` injects hook context and then sends the original member task input.

## Engineering Consequence

This proves three things simultaneously:

- hook-only integration is sufficient for governed context propagation
- hook-only integration is insufficient for physical child prompt mutation
- the smallest correct EvCode host patch is a subagent prompt finalization patch

## Required Patch

Prepared patch:

- `vendor/codex-host/patches/subagent-vibe-suffix.patch`

Scope:

- add one helper that appends ` $vibe` if missing
- use it in `spawn_agent`
- use it in `spawn_team`

Non-goals:

- no new outer REPL
- no second orchestrator
- no mutation of top-level user prompt behavior
- no change to host resume, yolo, worktree, or team lifecycle semantics

## Verification

Authoritative verification entrypoint:

- `python3 scripts/verify/check_host_bridge.py`

This verification proves:

- the materialized host still has the analyzed seam
- the EvCode host contract is aligned with that seam
- the prepared patch is concrete rather than placeholder text
