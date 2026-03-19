# EvCode Host Runtime Bridge

## Status

- Status: Proposed authoritative bridge design
- Date: 2026-03-15
- Scope: Host hook integration and governed runtime embedding

## 1. Purpose

This document defines how EvCode embeds the latest VCO governed runtime into the selected Codex host.

The product goal is not:

- an outer wrapper shell
- a second orchestrator beside Codex
- visible startup prompt injection

The product goal is:

- a Codex-native host
- with embedded VCO runtime truth
- connected through real host hook surfaces

## 2. Selected Host Baseline

EvCode should use `stellarlinkco/codex` as the host baseline.

Reason:

- it already exposes native hook surfaces
- it already supports agent-team-oriented host behavior
- it reduces the amount of custom patching EvCode must carry

This changes the implementation strategy from:

- "patch upstream Codex until it has usable hooks"

to:

- "adopt a hook-rich Codex host, then bridge VCO into it with the smallest possible EvCode patch layer"

## 3. Governed Runtime Source Of Truth

The embedded VCO runtime source of truth is `vco-skills-codex` governed runtime family `v2.3.47`.

EvCode must preserve the following VCO invariants:

1. one governed entry contract for `vibe`
2. fixed 6-stage runtime order
3. requirement freeze before execution
4. XL-style plan generation before execution
5. mandatory verification and phase cleanup
6. `interactive_governed` and `benchmark_autonomous` as runtime modes, not separate products

The runtime stages are:

1. `skeleton_check`
2. `deep_interview`
3. `requirement_doc`
4. `xl_plan`
5. `plan_execute`
6. `phase_cleanup`

## 4. Integration Principle

EvCode does not create a second router.

The canonical VCO router remains authoritative for route and confirmation behavior.
EvCode host integration only provides:

- host event interception
- runtime state bridging
- hidden governance context attachment
- artifact persistence
- cleanup triggering

The core rule is:

- VCO owns governed runtime truth
- Codex host owns UI and execution shell
- EvCode owns the bridge between them

Compatibility note:

- superpowers or similar workflow layers may shape process discipline,
- but they must feed the existing governed runtime rather than creating a parallel runtime surface.

Required ownership split:

- canonical router: route authority
- VCO governed runtime: stage order, requirement freeze, plan traceability, execution receipts, cleanup receipts
- host bridge: hidden hook wiring and artifact persistence
- superpowers or similar workflow layers: discipline and workflow advice only

Forbidden outcomes:

- a second visible startup/runtime prompt surface
- a second requirement freeze surface
- a second execution-plan surface
- a second route authority

## 5. Hook Mapping

### 5.1 `user_prompt_submit`

This is the primary bridge point.

On every user turn, EvCode should:

1. load workspace state
2. detect active requirement and plan artifacts
3. select runtime mode
4. invoke the governed runtime compiler
5. attach minimal hidden governance context to the host request

This hook must not emit a visible startup prompt.

### 5.2 `subagent_start`

This is the child-task governance point.

EvCode should:

1. attach governed runtime metadata to every spawned subagent
2. inject the active requirement and plan references
3. ensure subagent prompts end with ` $vibe`

If the host hook surface cannot physically mutate the subagent prompt suffix, EvCode may carry one minimal host patch for prompt-build mutation.

That patch must remain:

- narrow
- auditable
- limited to subagent prompt finalization

### 5.3 `task_completed` or post-turn equivalent

This hook updates phase receipts and execution traceability:

- phase progress
- verification receipts
- execution receipts
- plan alignment markers

### 5.4 `stop` or stage-boundary equivalent

This hook triggers `phase_cleanup`.

Minimum required work:

- temp artifact cleanup
- repo hygiene receipt
- node audit or cleanup
- cleanup receipt persistence

## 6. Runtime Mode Selection

EvCode exposes one governed runtime core and chooses mode per entry surface.

### Normal distribution default

- mode: `interactive_governed`
- user-facing behavior: collaborative, approval-aware, governed

### Benchmark distribution default

- mode: `benchmark_autonomous`
- user-facing behavior: closed-loop, no-follow-up, receipt-driven

This mode selection happens before requirement freezing.
It does not change the stage sequence.

## 7. Artifact Layout

EvCode must preserve VCO artifact truth and make paths predictable.

Required artifact families:

- `outputs/runtime/vibe-sessions/<run-id>/skeleton-receipt.json`
- `outputs/runtime/vibe-sessions/<run-id>/intent-contract.json`
- `docs/requirements/YYYY-MM-DD-<topic>.md`
- `docs/plans/YYYY-MM-DD-<topic>-execution-plan.md`
- `outputs/runtime/vibe-sessions/<run-id>/phase-*.json`
- `outputs/runtime/vibe-sessions/<run-id>/cleanup-receipt.json`

EvCode may add host-local receipts, but it must not replace these canonical runtime artifacts with host-only state.

## 8. Host Responsibilities

The host is responsible for:

- native TUI behavior
- session lifecycle
- native team execution
- resume and fork behavior
- command parsing and transport

EvCode must avoid replacing these surfaces with custom shell logic.

## 9. EvCode Patch Layer Responsibilities

EvCode patch layer is allowed to own:

- hook registration
- governed runtime bridge code
- runtime mode selection defaults
- artifact directory wiring
- observability receipts
- stage cleanup execution

EvCode patch layer is not allowed to own:

- a second chat loop
- a second route authority
- a wrapper-first execution model
- a second visible requirement / plan truth surface

## 10. Failure And Degradation Rules

If optional enhancements are unavailable, EvCode must degrade without violating governed runtime truth.

Allowed degradation:

- optional MCP enhancement unavailable
- optional memory enhancement unavailable
- optional provider unavailable

Not allowed:

- skipping requirement doc
- skipping plan generation
- skipping cleanup
- claiming success without verification evidence

## 11. Implementation Consequence

This bridge design implies the following package boundaries:

- `vendor/codex-host`
- `runtime/vco`
- `packages/host-integration`
- `packages/governed-runtime-bridge`
- `packages/receipts`
- `packages/cleanup`

The bridge is the product seam.
It should be implemented first, because every later capability depends on it.
