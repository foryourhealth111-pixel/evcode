# EvCode Architecture

## Authoritative Definition

EvCode is not a wrapper-centric governance tool.

EvCode is:

- a Codex-native distribution or fork
- with the full Vibe ecosystem embedded
- plus one native per-turn governance hook

The authoritative reset document is:

- [docs/plans/2026-03-14-evcode-reset-native-fork.md](/home/lqf/table/table3/docs/plans/2026-03-14-evcode-reset-native-fork.md)
- [docs/architecture/evcode-host-runtime-bridge.md](/home/lqf/table/table3/docs/architecture/evcode-host-runtime-bridge.md)
- [docs/architecture/evcode-dual-distribution.md](/home/lqf/table/table3/docs/architecture/evcode-dual-distribution.md)
- [docs/architecture/evcode-benchmark-adapter.md](/home/lqf/table/table3/docs/architecture/evcode-benchmark-adapter.md)
- [docs/architecture/evcode-upstream-materialization-and-bridge.md](/home/lqf/table/table3/docs/architecture/evcode-upstream-materialization-and-bridge.md)
- [docs/architecture/evcode-distribution-assembly.md](/home/lqf/table/table3/docs/architecture/evcode-distribution-assembly.md)

## Core Principle

The intended product is:

- `Codex core`
- `EvCode native patch layer`
- `embedded Vibe runtime`

not:

- `outer wrapper`
- `fake managed shell`
- `adapter-first hook product`

## What Stays Native

These should remain Codex-identical unless the native hook intentionally changes hidden prompt context:

- TUI
- session model
- resume
- fork
- yolo / full-auto semantics
- MCP loading
- native team orchestration
- base CLI behavior

## What EvCode Adds

EvCode adds exactly three product-level behaviors:

1. A native `UserPromptSubmit` hook
   - runs on every user turn
   - inspects workspace and user message
   - compiles minimal Vibe governance overlay

2. A native `SubagentStart` governance seam plus one minimal host patch
   - hook path carries governed context into child work
   - patch path appends ` $vibe` to every child-task prompt before send

3. An embedded full Vibe runtime
   - skills
   - rules
   - agents
   - MCP profiles
   - workflow contracts

## Current Host Decision

The current preferred host baseline is a hook-rich Codex host rather than a wrapper-first shim.

The active bridge and distribution design now assumes:

- a selected Codex host fork with native hook surfaces
- embedded VCO governed runtime `v2.3.43`
- one runtime core with two release channels:
  - standard
  - benchmark

See:

- [docs/architecture/evcode-host-runtime-bridge.md](/home/lqf/table/table3/docs/architecture/evcode-host-runtime-bridge.md)
- [docs/architecture/evcode-dual-distribution.md](/home/lqf/table/table3/docs/architecture/evcode-dual-distribution.md)
- [docs/architecture/evcode-benchmark-adapter.md](/home/lqf/table/table3/docs/architecture/evcode-benchmark-adapter.md)
- [docs/architecture/evcode-upstream-materialization-and-bridge.md](/home/lqf/table/table3/docs/architecture/evcode-upstream-materialization-and-bridge.md)

## What Is No Longer The Product Direction

The following are no longer considered primary architecture:

- managed wrapper shell as the main path
- hookify-only governance
- session-log inference as proof of hook execution
- external scheduler thinking layered above Codex native team

They may exist temporarily during migration, but they are not the target system.

## Implementation Priority

1. Rebase EvCode around the native prompt hook patch point.
2. Rebase child-task prompt building around source-proven ` $vibe` suffix enforcement.
3. Embed full Vibe assets into the runtime contract.
4. Remove or demote wrapper-first behavior to debug-only fallback.
5. Replace inferred observability with receipts emitted by the real native hook.
