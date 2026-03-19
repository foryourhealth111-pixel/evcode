# EvCode CLI Actor Visibility Requirement

## Status

- Status: Frozen requirement
- Date: 2026-03-19
- Scope: Real CLI-visible assistant activity for Codex, Claude, and Gemini under governed runtime

## Goal

EvCode must expose real assistant activity directly in the CLI interaction surface so the user can tell, during a governed run, whether Codex, Claude, or Gemini is currently participating, what state that actor is in, and what work content has been produced without reading raw JSON artifacts.

## Problem Statement

The current governed runtime records truthful specialist-routing and result artifacts, but the interactive CLI does not surface them in a user-readable way. Users can inspect `runtime-summary.json`, routing receipts, task packets, and result packets after a run, but cannot reliably see:

- which actor is currently active
- whether a specialist was only requested or truly live
- whether the run degraded back to Codex-only execution
- what advisory content or integration content was actually produced

This creates an observability gap between runtime truth and CLI experience.

## Scope

This requirement covers the standard EvCode CLI surface and the shared governed runtime truth it depends on.

Included:

- a CLI actor board visible during `evcode run`
- a real event model backed by runtime artifacts
- a `--trace` mode for richer event and content visibility
- a `trace <run-id>` replay surface for completed runs
- architecture, testing, proof, and cleanup artifacts

Excluded:

- web dashboard work
- changing route authority away from VCO
- allowing Claude or Gemini to become final executor
- fake or inferred live status when no runtime evidence exists
- token-by-token provider streaming unless the provider transport actually supports it

## Core User Outcomes

The user must be able to answer these questions from the CLI alone:

1. Which assistant is working right now?
2. Is that assistant truly active, only requested, degraded, or suppressed?
3. What content has it actually produced so far?
4. Has Codex taken over integration or fallback execution?
5. Where are the underlying proof artifacts if deeper inspection is needed?

## Trust Rules

The CLI must remain evidence-backed.

Mandatory rules:

- never show `STREAMING` unless live provider activity is truly in flight or content is being received from a live invocation path
- never present stub or degraded results as live output
- always preserve `codex` as final executor in the display model
- always display fallback or degraded specialist states non-silently
- ensure every visible status is reconstructible from runtime events or artifacts

## Functional Requirements

### 1. Actor Board

`evcode run` must display a compact actor board showing `codex`, `claude`, and `gemini` with current state and short status text.

Supported states:

- `IDLE`
- `REQUESTED`
- `DISPATCHING`
- `ACTIVE`
- `COMPLETED`
- `DEGRADED`
- `SUPPRESSED`
- `INTEGRATING`

### 2. Runtime Event Ledger

The governed runtime must emit an append-only event stream for each run under the session artifact root.

Required event properties:

- timestamp
- sequence number
- actor
- phase
- state
- message
- optional content kind
- optional content snippet
- optional artifact references

### 3. Recent Activity View

The default CLI surface must show recent activity lines reflecting the latest runtime events in human-readable form.

### 4. Trace Mode

`evcode run --trace` must expose a more detailed event log, including advisory result snippets and Codex integration notes when available.

### 5. Trace Replay

`evcode trace <run-id>` must replay the actor timeline from saved runtime artifacts.

### 6. JSON Compatibility

`evcode run --json` must remain machine-readable and must not mix human UI output into stdout.

### 7. Non-Silent Fallback

If Claude or Gemini fails or degrades, the CLI must state that fact explicitly and show that Codex continues in degraded mode.

## UX Requirements

- The default view must be readable in a normal terminal without becoming noisy.
- The layout should look deliberate and polished rather than like a raw log dump.
- The display must degrade cleanly when color or TTY capabilities are unavailable.
- Non-interactive output should remain line-based and deterministic for logs and tests.

## Artifact Requirements

This feature must generate or maintain:

- requirement doc
- execution plan doc
- architecture doc
- proof/status doc
- runtime events ledger
- runtime summary references to the events ledger

## Acceptance Criteria

The implementation is acceptable only if all of the following are true:

1. A standard `evcode run` on a frontend-visual task visibly shows Gemini being requested and either activated or degraded.
2. A planning or documentation task visibly shows Claude being requested and either activated or degraded.
3. A Codex-only backend task does not falsely show Claude or Gemini as active.
4. `evcode trace <run-id>` reproduces the actor timeline from artifacts.
5. `--json` output remains valid JSON.
6. Tests cover state emission, CLI rendering, degraded fallback visibility, and trace replay.
7. Proof documentation cites concrete runtime artifacts and verification commands.

## Non-Goals

- full-screen terminal UI framework migration
- live token streaming for providers that do not support incremental transport
- replacing current routing policy with UI-driven routing
- hiding degraded specialist failures behind generic success language
