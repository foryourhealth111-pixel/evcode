# EvCode Hook Runtime Architecture

## Problem Statement

The current EvCode design is still too wrapper-centric.

It has two structural flaws:

1. It treats governance as an outer shell concern.
2. It injects prompt policy either through a fake managed loop or by passing visible startup text into Codex.

That is the wrong abstraction.

The desired product is not "a Codex wrapper that sometimes prepends text".
It is "a Codex-native governance layer that reacts to each user interaction through hooks, compiles the minimum turn policy, and keeps the native UI intact".

## Design Goal

Build EvCode as a hook-driven Codex modification layer with these properties:

- native Codex remains the host UI/runtime
- governance is triggered on each user interaction, not by a visible wrapper prompt
- prompt policy is compiled per turn from workspace state plus current user message
- subagent prompts are automatically rewritten to append ` $vibe`
- cleanup and telemetry run as lifecycle hooks, not as ad hoc wrapper logic
- the native screen remains the primary UX

## Core Design Principle

EvCode should move from:

- `CLI wrapper -> prompt prepend -> codex`

to:

- `codex host -> EvCode hook runtime -> policy compiler -> native execution`

This means EvCode becomes a runtime pack installed into Codex's hook/config environment, rather than a fake chat shell.

## Target Architecture

### 1. Host Layer

Codex remains the host:

- native TUI
- native session model
- native team runtime
- native MCP loading
- native resume/fork/history behavior

EvCode does not replace these.

### 2. Hook Runtime Layer

EvCode installs a hook runtime under the Codex hook/config root and registers lifecycle handlers.

Target hook categories:

- `SessionStart`
  - detect workspace
  - detect VCO skeleton / requirement / plan state
  - initialize EvCode state for the session

- `UserPromptSubmit`
  - intercept the user message before the model sees it
  - classify whether the message is clear, ambiguous, execution-ready, or follow-up
  - compile the minimum governance overlay for this turn
  - attach the overlay invisibly to the request context

- `SubagentPromptBuild`
  - append ` $vibe` to all child-task prompts
  - add team/runtime metadata

- `PostAssistantTurn`
  - persist turn outcome
  - update requirement/plan/execution state
  - detect whether a stage boundary completed

- `PostStage`
  - cleanup zombie node processes attributable to EvCode work
  - cleanup temp artifacts
  - emit audit receipt

- `SessionEnd`
  - finalize audit state
  - compress transcript metadata

### 3. Governance Compiler

The governance system should not inject one giant static prompt on every turn.

Instead, it should compile a turn-scoped overlay:

- workspace facts
- current state machine state
- current user message classification
- action policy for this turn only

This compiler produces one of several overlay classes:

- `overlay.none`
  - trivial greeting / no task / no governance needed

- `overlay.interview`
  - user intent exists but requirement is underspecified
  - bounded to max 3 interview turns

- `overlay.plan`
  - requirements are sufficiently clear
  - no confirmed plan exists

- `overlay.execute`
  - confirmed plan exists
  - continue wave/batch/phase execution

- `overlay.resume`
  - follow-up message in an active governed execution flow

This is materially better than repeating the full policy block every turn.

## Turn Policy Model

### Phase A: Turn Classification

Given the current user message plus stored session/workspace state, EvCode computes:

- `has_explicit_task`
- `is_smalltalk`
- `is_requirement_complete`
- `has_requirement_doc`
- `has_confirmed_plan`
- `is_plan_followup`
- `needs_interview`
- `can_skip_interview`

Important rule:

- if the user has already provided a complete, compound, execution-ready task description, interview is forbidden and the compiler must emit `overlay.plan` or `overlay.execute`

### Phase B: Overlay Assembly

Instead of a monolithic text wall, assemble:

1. invariant rule block
2. workspace state block
3. turn policy block
4. subagent policy block

The invariant block contains rules such as:

- use Codex native team only
- append ` $vibe` to subagent prompts
- run stage cleanup at stage boundaries

The turn policy block is short and specific:

- `Skip interview. User requirement is already explicit. Generate plan.`
- `Plan exists. Continue execution from next phase.`
- `Interview user directly. Max remaining interview turns: 2.`

This preserves intelligence while reducing visible and token-heavy repetition.

## State Machine

EvCode should own a strict state machine outside the model text.

### States

- `idle`
- `skeleton_missing`
- `requirements_missing`
- `interview_active`
- `requirements_confirm_pending`
- `plan_missing`
- `plan_confirm_pending`
- `execution_active`
- `execution_paused`
- `completed`

### Stored State

Per session:

- session id
- workspace path
- current state
- interview turn count
- requirement doc path
- plan path
- latest completed stage
- latest cleanup receipt

Per workspace:

- VCO skeleton status
- latest requirement doc
- latest plan doc
- last execution receipt

## Why This Is Better

### What the current design gets wrong

- wrapper shell owns the conversation
- native mode previously leaked visible startup prompt text
- governance logic is text-first instead of runtime-first
- prompt policy is too coarse and too static

### What the hook design fixes

- governance becomes invisible and event-driven
- Codex native UX stays intact
- per-turn behavior is triggered by actual user interactions
- prompt injection is minimal and contextual
- execution state becomes deterministic instead of prompt-only

## Concrete Runtime Components

Recommended structure:

- `src/hook-runtime/registry.ts`
- `src/hook-runtime/session-start.ts`
- `src/hook-runtime/user-prompt-submit.ts`
- `src/hook-runtime/subagent-prompt-build.ts`
- `src/hook-runtime/post-assistant-turn.ts`
- `src/hook-runtime/post-stage.ts`
- `src/hook-runtime/session-end.ts`
- `src/governance/turn-classifier.ts`
- `src/governance/overlay-compiler.ts`
- `src/governance/state-store.ts`
- `src/governance/stage-detector.ts`
- `src/integration/codex-hooks.ts`
- `src/integration/hookify-adapter.ts`

## Hook Integration Strategy

There are two deployment modes.

### Mode 1: True Native Hook Mode

Use Codex-native hook points if they exist or are exposed through the local runtime/plugins.

This is the ideal mode.

### Mode 2: Hook Adapter Mode

If Codex does not expose the needed prompt-submission hooks directly, install a low-level adapter through the local hook/plugin stack that:

- intercepts outbound prompt payloads
- adds turn overlay metadata
- preserves native TUI ownership

This is still acceptable because the hook behavior remains invisible to the user and is not implemented as a fake REPL.

### Explicit Non-Goal

Do not implement per-turn governance by reintroducing a wrapper-owned readline chat shell.

That is a fallback only, not the product architecture.

## Product Surface After Redesign

- `evcode`
  - install/use hook-governed Codex mode

- `evcode native`
  - pure native Codex, no EvCode governance hooks

- `evcode hook status`
  - inspect registered hook runtime state

- `evcode hook install`
  - materialize hook runtime into Codex hook/config roots

- `evcode hook doctor`
  - verify hook wiring and compatibility

- `evcode audit`
  - inspect per-turn governance receipts and state transitions

## Implementation Waves

### Wave 1: Runtime Separation

- separate current wrapper logic from target hook runtime logic
- keep current managed shell only as fallback/dev mode
- stop describing wrapper mode as the primary architecture

### Wave 2: Turn Classifier + Overlay Compiler

- implement deterministic per-turn classification
- compile short, stateful overlays instead of static text walls

### Wave 3: Hook Runtime Adapter

- wire session-start / user-prompt-submit / post-turn hooks
- integrate with Codex settings + local hook runtime

### Wave 4: Subagent Governance

- move `$vibe` suffix append into a dedicated subagent hook
- remove duplicate text-based suffix logic where possible

### Wave 5: Lifecycle Governance

- post-stage cleanup
- receipts
- audit replay
- workspace/session state restore

## Decision

EvCode should no longer be treated as a "smart prompt wrapper".

It should be redesigned as:

- a Codex-native hook runtime
- with per-turn governance compilation
- invisible injection
- explicit state machine
- native UI preservation

That is the architecture consistent with the product you are actually asking for.
