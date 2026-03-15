# EvCode Native/Managed Convergence Plan

## Goal

Build a mature EvCode CLI that:

- preserves `codex` native interactive experience as the primary shell
- supports native compatibility features such as `resume`, `fork`, `mcp`, and power-user flags such as `--full-auto` and dangerous bypass aliases
- provides a governed managed mode for per-turn Vibe injection, requirement interview, planning confirmation, and staged execution
- stores session state, plan state, and requirement state predictably
- offers a slightly refined UI without breaking native Codex expectations

This plan explicitly avoids introducing an external team scheduler. `codex native team` remains the only team runtime.

## Core Diagnosis

The current implementation has three structural issues:

1. It mixes two incompatible goals into one entrypoint:
   - native Codex TUI compatibility
   - wrapper-owned per-turn prompt interception

2. It currently relies on a custom managed loop for per-turn governance, which makes the experience feel less mature than native Codex.

3. It does not yet define a hard state machine for:
   - unclear requirements
   - confirmed requirement document
   - confirmed implementation plan
   - governed execution after confirmation

## Architectural Decision

EvCode should converge to a dual-mode architecture with one stable compatibility core.

### Mode A: Native Mode

`evcode` should default to a native-first path whenever the user wants:

- Codex-like TUI interaction
- `resume` / `fork`
- native interactive scrolling and rendering
- minimal wrapper overhead

Responsibilities:

- normalize CLI arguments
- map EvCode config to native Codex options
- pass through supported native commands and flags
- add light UI framing only when safe
- keep native screen behavior intact

Governance model:

- session-start injection only
- no fake per-turn interception
- no wrapper-owned readline loop

### Mode B: Managed Mode

`evcode managed` should own the governed conversation loop when the user explicitly needs:

- per-turn governance injection
- requirement interviews
- requirement confirmation before document write
- plan confirmation before plan persistence
- staged governed execution after plan confirmation

Responsibilities:

- per-turn contract injection
- transcript persistence
- requirement/plan state machine
- stage cleanup
- auditability

Governance model:

- every user turn is wrapped
- explicit managed session files
- explicit confirmation boundaries

### Compatibility Core

Both modes share:

- argument normalization
- runtime/profile/mcp management
- requirement detection
- plan detection
- audit and doctor views
- cleanup tools

## Product Surface

### Primary Commands

- `evcode`
  - native-first interactive mode
- `evcode managed`
  - governed per-turn mode
- `evcode exec "<prompt>"`
  - non-interactive governed execution
- `evcode raw`
  - raw native Codex passthrough
- `evcode resume`
  - passthrough with EvCode context restoration when available
- `evcode fork`
  - passthrough with EvCode context restoration when available
- `evcode doctor`
  - health and compatibility checks
- `evcode status`
  - compact state view
- `evcode audit`
  - detailed state, receipts, contract versions, and managed session state
- `evcode runtime ...`
  - runtime management
- `evcode profile ...`
  - profile management

### Flag Strategy

EvCode must stop hard-coding a partial flag model. Instead:

- native-interactive commands should preserve native Codex flags transparently
- exec-only flags must be separated from interactive-only flags
- wrapper-only flags must be namespaced and documented

Rules:

- `resume`, `fork`, and top-level interactive flows must support native-compatible flag forwarding
- `exec` must only pass flags that `codex exec --help` actually accepts
- `--full-auto` should map directly when user requests yolo-like flow
- if a user uses a wrapper alias such as `--yolo`, EvCode should normalize it into a supported native flag set

## UI Strategy

UI changes should be incremental, not a replacement.

### Native UI Layer

Allowed enhancements:

- lightweight preflight banner before entering native Codex
- optional one-line status strip with:
  - mode
  - active profile
  - governance state
  - requirement state
  - plan state

Not allowed:

- replacing the Codex TUI rendering model
- rewriting native screen management
- wrapping native interactive mode inside a fake chat shell

### Managed UI Layer

Managed mode may have its own UI because it is explicitly a wrapper-owned loop.

Recommended elements:

- compact top banner
- current mode badge: `managed`
- requirement state badge
- plan state badge
- turn counter
- current session id
- explicit `/confirm`, `/save`, `/plan`, `/audit`, `/exit` commands

## Governance State Machine

EvCode needs a deterministic state machine rather than prompt-only behavior.

### States

1. `skeleton_missing`
2. `needs_requirement_interview`
3. `requirement_ready_unconfirmed`
4. `requirement_confirmed`
5. `plan_missing`
6. `plan_ready_unconfirmed`
7. `plan_confirmed`
8. `governed_execution`

### Transitions

- if skeleton missing: initialize skeleton first
- if user intent exists but requirement is unclear and no requirement doc exists: enter interview mode
- interview mode must terminate within 3 turns
- after requirement synthesis: require explicit user confirmation before saving
- after requirement confirmed and no plan exists: generate plan
- after plan synthesis: require explicit user confirmation before saving
- after plan confirmed: enter governed execution

### Persistence

Persist the state machine in EvCode-controlled files:

- `~/.evcode/sessions/<id>.jsonl`
- `~/.evcode/sessions/<id>.state.json`
- optional workspace-local requirement document
- optional workspace-local plan document

## File Layout Changes

Recommended additions:

- `src/ui/native-entry.ts`
- `src/ui/managed-shell.ts`
- `src/ui/status-strip.ts`
- `src/compat/native-flags.ts`
- `src/compat/native-commands.ts`
- `src/governance/requirements-state.ts`
- `src/governance/plan-state.ts`
- `src/governance/interview.ts`
- `src/session/managed-session.ts`
- `src/session/native-session-map.ts`

## Execution Plan

## Wave 1: Compatibility Kernel

### Batch 1.1: Native command/flag inventory

- derive a machine-readable compatibility map from `codex --help` and `codex exec --help`
- separate:
  - interactive flags
  - exec flags
  - passthrough commands
  - wrapper-only aliases

### Batch 1.2: Argument normalization

- replace ad hoc argument builder with command-aware mapping
- support:
  - `resume`
  - `fork`
  - `mcp`
  - `review`
  - top-level interactive prompt
- add wrapper aliases:
  - `--yolo` -> native-supported auto mode mapping

### Batch 1.3: Compatibility tests

- snapshot the actual supported flags
- add regression tests for forbidden flags on `exec`
- add passthrough tests for `resume` and `fork`

## Wave 2: Native-First Interactive Shell

### Batch 2.1: Remove fake default REPL

- make `evcode` default to native-first mode
- keep managed mode behind explicit command

### Batch 2.2: Lightweight UI overlay

- add optional one-line preflight summary
- add optional inline status strip
- preserve native TUI screen ownership

### Batch 2.3: Resume-aware context restoration

- store EvCode metadata linked to Codex session id
- allow `evcode resume` to recover:
  - governance state
  - requirement state
  - plan state
  - active workspace context

## Wave 3: Managed Governance Engine

### Batch 3.1: Requirement detection and interview state

- detect requirement docs
- detect ambiguous intent
- enter interview mode only when needed
- enforce max 3 interview turns

### Batch 3.2: Requirement persistence and confirmation

- synthesize requirement doc candidate
- require explicit user confirmation before write
- default to single-file output unless unnecessary

### Batch 3.3: Plan persistence and confirmation

- synthesize plan candidate
- require explicit user confirmation before write
- preserve current `docs/plans/` compatibility

### Batch 3.4: Governed execution state

- only after confirmed plan
- per-turn injection remains managed-mode only

## Wave 4: Session Persistence and Audit

### Batch 4.1: Managed session persistence

- JSONL transcript
- state sidecar
- requirement and plan linkage

### Batch 4.2: Native session map

- map native Codex session ids to EvCode metadata
- support `resume` and `fork`

### Batch 4.3: Audit expansion

- current mode
- current native session id or managed session id
- requirement state
- plan state
- confirmation state
- last successful cleanup

## Wave 5: UX and Release Hardening

### Batch 5.1: UI polish

- banner copy
- mode badges
- compact status strip
- clearer errors for config/profile/provider mismatches

### Batch 5.2: Failure handling

- missing API key
- non-git repo
- unknown profile
- invalid resume target
- incompatible flag combination

### Batch 5.3: Release preparation

- packaging
- smoke scripts
- migration notes
- operator guide

## Testing Plan

### Unit Tests

- native flag normalization
- interactive vs exec argument separation
- requirement detector
- plan detector
- interview turn cap
- confirmation state transitions
- session persistence

### Integration Tests

- `evcode` native-first launch
- `evcode resume`
- `evcode fork`
- `evcode exec`
- `evcode managed`
- `evcode raw`
- `evcode audit`

### PTY Smoke Tests

Use PTY-based automation for:

- startup banner correctness
- native screen ownership preservation
- `/exit` in managed mode
- transcript persistence
- resume flow continuity

### Fault Injection Tests

- missing provider auth
- unsupported flag
- missing runtime
- corrupted session sidecar
- missing requirement doc
- ambiguous requirement requiring interview

## Quantitative Acceptance Criteria

### Stability

- 100/100 native launch smoke runs complete without wrapper crash
- 100/100 managed launch smoke runs complete without transcript corruption
- 0 unsupported flags forwarded to `codex exec` in compatibility test matrix
- 0 zombie EvCode-owned node processes after cleanup stage tests

### Availability

- native-mode startup overhead <= 120 ms over raw Codex median
- managed-mode startup overhead <= 400 ms before first prompt
- `resume` success rate >= 99% in controlled smoke tests

### Usability

- user can distinguish native vs managed mode within 1 glance
- requirement interview terminates within 3 turns in 100% of bounded interview fixtures
- plan confirmation requires explicit positive confirmation in 100% of plan-save tests

### Intelligence

- requirement ambiguity fixtures correctly enter interview mode >= 95%
- clear requirement fixtures skip interview mode >= 95%
- confirmed-plan fixtures route directly to governed execution >= 99%

## Proof Strategy

The design is considered correctly landed only if all four evidence layers are satisfied:

1. **Static proof**
   - typed command map
   - no invalid interactive/exec flag overlap

2. **Deterministic proof**
   - state machine fixtures
   - snapshot tests for routing outcomes

3. **Runtime proof**
   - PTY-based smoke tests
   - resume/fork continuity tests
   - provider/config failure tests

4. **Operational proof**
   - audit output includes mode, session, requirement state, and plan state
   - cleanup receipts are visible
   - managed transcript files are replayable

## Risks and Mitigations

### Risk: Native TUI and per-turn interception remain in conflict

Mitigation:

- keep native-first and managed mode separate
- do not pretend one mode can safely do both

### Risk: Resume metadata drifts from Codex native sessions

Mitigation:

- link by native session id
- add repair and orphan detection in `audit`

### Risk: User perceives managed mode as inferior chat shell

Mitigation:

- only use managed mode when governance needs require it
- keep native mode as default premium path

### Risk: Requirement interview becomes noisy

Mitigation:

- maximum 3 rounds
- explicit interview state
- focused interview templates

## Recommended Next Implementation Order

1. fix compatibility kernel and command-aware flag mapping
2. make `evcode` native-first again
3. move per-turn governance into explicit `evcode managed`
4. add requirement/plan confirmation state machine
5. add resume/fork metadata mapping
6. polish UI and finalize release hardening
