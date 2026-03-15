# EvCode Reset: Native Fork Baseline

## Status

- Status: Authoritative Reset Baseline
- Date: 2026-03-14
- Priority: Highest
- Scope: Product definition reset

## 1. Reset Statement

The current EvCode implementation drifted away from the intended product.

It became too focused on:

- outer wrappers
- external runtime management
- declarative hook adapters
- audit layers that do not correspond to a real prompt-submit patch point

That is not the desired product.

The intended product is much simpler and much stricter:

> EvCode is Codex itself, with the full Vibe ecosystem embedded, plus one added native per-turn hook.

Everything else should remain as close to upstream Codex behavior as possible.

## 2. Product Definition

EvCode must be treated as:

- a Codex-native distribution or fork
- with full Vibe skills, rules, agents, MCP profiles, and supporting assets embedded into the Codex home/runtime contract
- with exactly one new core runtime patch:
  - a native per-turn prompt hook before request assembly

EvCode must **not** be treated as:

- a wrapper-owned REPL
- a managed shell
- a hookify-first adapter product
- an external governance orchestrator layered beside Codex
- a sidecar CLI that tries to simulate native behavior

## 3. The One Allowed Magic Modification

The only essential magic modification is:

- add a prompt-submit hook point inside the Codex interaction pipeline

That hook runs on every user message and does exactly four things:

1. load workspace-level Vibe context
2. inspect project state
3. compile the minimal per-turn governance overlay
4. append invisible governance context before the model request is assembled

This hook is native to EvCode itself, not dependent on external declarative plugin behavior.

## 4. Full Vibe Ecosystem Embedding

EvCode should ship with the full Vibe ecosystem embedded as first-class runtime content:

- `skills/`
- `rules/`
- `agents/`
- `mcp/` profiles/templates
- VCO bootstrap assets
- protocol and planning assets

Embedding means:

- EvCode runtime knows where these assets live
- the host can resolve them exactly like Codex resolves its own local assets
- users do not need a second external governance product to activate the ecosystem

This should feel like:

- "Codex, but with Vibe built in"

not:

- "Codex, plus an external tool that tries to manage Vibe around it"

## 5. Behavioral Contract

The per-turn native hook must implement the following contract:

### 5.1 Turn Trigger

Trigger on every user message.

Not:

- startup only
- session-start only
- wrapper loop only
- manual `/vibe` only

### 5.2 State Inspection

On each turn, inspect:

- current workspace path
- whether VCO skeleton exists
- whether requirement doc exists
- whether plan exists
- whether the current message is a complete executable task
- whether the current message is a follow-up to an active plan

### 5.3 Turn Outcomes

The hook compiles one of these outcomes:

- `none`
- `interview`
- `plan`
- `execute`
- `resume`

### 5.4 Subagent Rule

Whenever Codex native team spawns child tasks, EvCode must append:

- ` $vibe`

to every subagent prompt.

This must happen inside the native task-building path, not by asking the model politely to remember it.

## 6. What Must Stay Identical To Codex

All of these should behave like Codex unless the single hook intentionally alters prompt context:

- native TUI
- input model
- history
- resume
- fork
- yolo / full-auto semantics
- MCP loading
- native team orchestration
- session handling
- base command semantics

The product principle is:

- same Codex surface
- one native governance hook
- full Vibe runtime baked in

## 7. What Must Be Removed Or Demoted

The following ideas are now considered wrong-path or secondary:

### 7.1 Wrapper-Owned Managed Mode As Product Core

This must not be the primary architecture.

At most, it can remain as a temporary debug-only fallback while the native patch is under construction.

### 7.2 Hookify-Only Governance

Declarative `hookify-configs` may still be useful for auxiliary rules, but they are not sufficient to implement the core EvCode product.

Core per-turn governance cannot depend on a surface that may or may not execute custom runtime logic.

### 7.3 Fake Proof Systems

Anything that merely infers behavior from session logs without owning the real patch point is not the product.

Observability is useful, but it must sit on top of a real native hook, not replace it.

### 7.4 External Scheduler Thinking

EvCode must not introduce a second scheduler above Codex native team.

Vibe coordinates behavior and prompt policy; Codex remains the execution runtime.

## 8. Correct Internal Architecture

The correct architecture is:

- `upstream codex core`
- `evcode native patch layer`
- `embedded vibe runtime`

### 8.1 Upstream Codex Core

Unmodified or minimally modified upstream runtime:

- UI
- command parser
- model transport
- session store
- native team runtime

### 8.2 EvCode Native Patch Layer

Only patch the smallest possible set of internal seams:

- user prompt pre-request hook
- child task prompt builder hook
- optional stage-finish cleanup hook

### 8.3 Embedded Vibe Runtime

Baked-in asset pack:

- skills
- rules
- agents
- MCP profiles
- workflow contracts

## 9. Required Patch Points

EvCode should patch inside Codex internals at these seams:

### Patch A: `UserPromptSubmit`

Before model request assembly:

- inspect workspace
- inspect user message
- compile minimal overlay
- merge into system or hidden context

### Patch B: `SubagentPromptBuild`

Before child task dispatch:

- append ` $vibe`
- optionally attach execution metadata

### Patch C: `StageBoundary`

After a meaningful execution stage:

- cleanup temp files
- cleanup zombie node processes attributable to the session

Patch A is mandatory.
Patch B is mandatory.
Patch C is recommended.

## 10. New Implementation Waves

### Wave 1: Product Reset

- mark wrapper-first architecture as obsolete
- define native-fork baseline as authoritative
- remove adapter-first language from architecture docs

### Wave 2: Runtime Rebase

- identify the precise upstream Codex input pipeline seam
- patch native `UserPromptSubmit`
- patch native subagent prompt builder

### Wave 3: Embedded Ecosystem

- move full Vibe assets into the EvCode runtime contract
- resolve skills/rules/agents from embedded paths by default

### Wave 4: Compatibility Preservation

- ensure `resume`, `fork`, `yolo`, native MCP, and team behavior remain Codex-identical
- verify no wrapper shell remains on the default path

### Wave 5: Observability

- add real hook receipts generated by the native hook itself
- remove any fake or inferential proof paths that do not correspond to the real patch

## 11. Acceptance Criteria

EvCode is correct only if all of the following are true:

- launching `evcode` feels like launching Codex
- full Vibe ecosystem is available without external sidecar activation
- every user turn passes through a real native EvCode hook
- every child task prompt ends with ` $vibe`
- `resume`, `fork`, `yolo`, MCP, and native team still behave like Codex
- the implementation does not depend on wrapper-owned chat control
- observability reflects real native patch execution, not guesses

## 12. Final Rule

When architecture tradeoffs appear, prefer:

- less wrapper
- less sidecar logic
- less fake orchestration
- less prompt theater
- more native patching
- more upstream compatibility
- more embedded Vibe runtime

That is the correct EvCode direction.
