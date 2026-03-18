# EvCode Multi-Assistant Routing

## Status

- Status: Proposed architecture
- Date: 2026-03-18
- Scope: Specialist delegation for Codex, Claude Code, and Gemini CLI

## 1. Design Intent

EvCode should remain one governed product with one runtime truth, while becoming more honest about which assistant is best suited for a given class of work.

The key product idea is:

- Codex remains the host-native engineering backbone
- Claude Code and Gemini CLI become governed specialists
- EvCode chooses among them inside a controlled delegation layer
- VCO remains the only control-plane authority

This design deliberately avoids turning EvCode into a model switchboard with no governance.

## 2. Core Principle

EvCode must distinguish between:

- control-plane authority
- specialist execution authority

### 2.1 Control-plane authority

This remains unchanged and belongs to the existing EvCode + VCO runtime stack.

It owns:

- stage order
- requirement freezing
- plan generation
- delegation approval rules
- verification rules
- cleanup rules
- artifact persistence

### 2.2 Specialist execution authority

This is new.
It decides which assistant should contribute to a task or subtask.

It does not own:

- route truth
- completion claims
- benchmark policy
- final repository correctness claims

## 3. Assistant Roles

### 3.1 Codex

Codex should remain:

- the default assistant
- the final engineering integrator
- the backend and systems lead
- the correctness verifier
- the high-risk code owner

Codex is best for:

- backend implementation
- repository-wide refactors
- tests and verification
- migration discipline
- integration logic
- cross-file engineering coherence

Codex should own the final say on whether repository code is safe to land.

### 3.2 Claude Code

Claude Code should be positioned as:

- product and UX architecture specialist
- design-interpretation specialist
- ambiguity-resolution specialist
- front-end structure and interaction reasoning specialist

Claude Code is best for:

- reframing vague user intent into better product structure
- designing flows, hierarchy, and interaction models
- generating richer front-end direction than Codex tends to produce
- critiquing narrow engineering-driven UI proposals

Claude Code should not be treated as the final verifier for low-level repository correctness.

### 3.3 Gemini CLI

Gemini CLI should be positioned as:

- visual design and aesthetics specialist
- front-end styling and polish specialist
- layout, look-and-feel, and visual exploration specialist

Gemini is best for:

- visual concepts
- typography direction
- color systems
- spacing rhythm
- landing-page feel
- component styling exploration
- visual alternatives when Codex output is technically sound but aesthetically weak

Gemini should not be trusted as the primary owner of backend or integration logic.

## 4. Recommended Trust Model

The safest model is not “all three assistants edit the repo freely”.
The safest model is a layered trust system.

### Tier A: Advisory Mode

Assistant returns:

- proposal
- patch sketch
- design rationale
- component structure
- styling direction

Codex then decides whether and how to apply it.

This should be the default initial rollout for Claude Code and Gemini CLI.

### Tier B: Isolated Apply Mode

Assistant may edit code only inside an isolated worktree or delegation sandbox.
Its output is treated as a candidate diff, not an accepted change.

Codex must review, normalize, and verify before merge.

### Tier C: Direct Apply Mode

This should be rare and narrowly scoped.
It should only be allowed for low-risk file classes such as:

- isolated presentational components
- static copy
- design-token files with strong guardrails

Even here, final verification remains mandatory.

## 5. Routing Dimensions

EvCode should route by explicit dimensions instead of naive keyword matching.

### 5.1 Domain dimension

Possible domains:

- backend
- frontend-structural
- frontend-visual
- design-system
- UX-flow
- content/copy
- mixed full-stack
- verification

### 5.2 Risk dimension

Possible risks:

- low: style-only, copy-only, isolated component polish
- medium: UI component logic, front-end state interactions, design-system changes
- high: backend, auth, data flow, migrations, security-sensitive logic, cross-package refactors

### 5.3 Ambiguity dimension

Possible ambiguity levels:

- low: exact implementation request
- medium: partially specified behavior
- high: vague desired feel, taste, or product direction

### 5.4 Evidence dimension

Possible evidence requirements:

- code correctness evidence
- screenshot or visual evidence
- design rationale evidence
- benchmark or regression evidence

## 6. Routing Rules

### Rule 1: Codex-first default

If no strong specialist signal exists, route to Codex.

### Rule 2: Claude-first for design reasoning

If the task is primarily about:

- user flow
- UX architecture
- product framing
- ambiguous front-end direction
- critique of a technically safe but uninspired UI plan

then Claude Code should be consulted before implementation is frozen.

### Rule 3: Gemini-first for visual generation

If the task is primarily about:

- aesthetics
- visual polish
- landing-page styling
- typography
- palette
- motion tone
- component look and feel

then Gemini CLI should be used as the visual specialist.

### Rule 4: Codex finalizes any mixed or risky work

If a task affects:

- backend logic
- shared state semantics
- build system
- tests
- deployment
- auth or security
- cross-package integration

Codex must own final integration and verification even if Claude or Gemini drafted part of the solution.

### Rule 5: Dual-specialist flow for premium front-end work

For high-value front-end work, the best path is often:

1. Claude Code refines product and interaction direction
2. Gemini CLI proposes or edits the visual layer
3. Codex integrates, fixes edge cases, and verifies

This gives EvCode both taste and engineering discipline.

## 7. Normalized Delegation Contract

EvCode should not send raw chat fragments into external assistants.
It should send a normalized task packet.

### Input packet

Must include:

- task goal
- file scope
- constraints
- acceptance criteria
- non-goals
- repository context summary
- current design/system conventions
- allowed edit authority level
- expected output type

### Output contract

Assistant must return:

- proposed action summary
- changed files or intended files
- patch or patch-like artifact
- assumptions made
- unresolved uncertainties
- self-reported confidence
- specialist rationale

Optional:

- screenshots
- design token proposal
- alternative variants

## 8. Where Delegation Belongs In The Runtime

Delegation should happen inside `plan_execute`.
It should not happen in:

- route selection
- requirement freezing
- plan generation authority

Reason:

- VCO should still freeze the requirement and plan before choosing an execution specialist
- the user should be able to inspect why delegation happened
- benchmark mode should be able to disable or narrow delegation without rewriting the whole runtime

## 9. Repository Shape

Recommended package additions:

- `packages/specialist-routing`
  - task classification
  - assistant selection
  - override rules
- `packages/assistant-adapters`
  - Codex adapter
  - Claude Code CLI adapter
  - Gemini CLI adapter
- `packages/delegation-contracts`
  - task packet schema
  - result schema
  - receipt schema

Recommended config additions:

- `config/assistant-policy.standard.json`
- `config/assistant-policy.benchmark.json`
- `config/specialist-routing.json`

Possible profile additions:

- standard profile enables specialist delegation
- benchmark profile defaults to Codex-only unless explicitly proven reproducible

## 10. Verification Strategy

### 10.1 For Codex work

Existing engineering verification remains primary:

- tests
- build
- lint
- contract checks

### 10.2 For Claude Code work

Require:

- rationale review
- implementation coherence review by Codex
- follow-up engineering verification

### 10.3 For Gemini work

Require:

- visual evidence such as screenshots or screenshot diffs
- style-token review
- front-end build and interaction verification
- Codex integration review before completion claims

### 10.4 For mixed front-end work

Require both:

- visual quality proof
- engineering correctness proof

A pretty interface that breaks behavior is a failed result.
A technically safe interface that obviously misses the design goal is also a failed result.

## 11. Benchmark Policy

Benchmark mode should start conservative.

Recommended benchmark behavior:

- Codex remains primary
- Claude/Gemini delegation disabled by default
- optional advisory-only delegation can be enabled later behind explicit policy
- no benchmark-critical path should depend on external specialist availability unless benchmark rules allow it

This keeps benchmark reproducibility intact.

## 12. Failure Modes To Avoid

### 12.1 Second router failure

If specialist routing becomes a hidden second route authority, the design has failed.

### 12.2 Aesthetic authority without verification

If Gemini can land visually ambitious code without build and interaction proof, the design has failed.

### 12.3 Creative reframing without traceability

If Claude can substantially reinterpret the task without updating requirement/plan lineage, the design has failed.

### 12.4 Model shopping

If EvCode repeatedly retries different assistants until one agrees, with no receipt trail, the design has failed.

## 13. Recommended Rollout

### Phase 1

- advisory-only Claude and Gemini
- Codex applies and verifies all accepted changes

### Phase 2

- isolated apply mode for low-risk front-end scopes
- Codex remains final integrator

### Phase 3

- selective automatic delegation for premium front-end work
- visual verification and receipting become mandatory

## 14. Final Recommendation

The strongest EvCode evolution is not:

- “replace Codex when it feels weak”

It is:

- “keep Codex as the engineering spine, then add Claude Code and Gemini CLI as governed specialists with explicit contracts, explicit trust limits, and Codex-led final verification”

This gives EvCode:

- taste without losing rigor
- creativity without losing traceability
- better front-end quality without weakening backend safety


## 8. Baseline Families

EvCode should distinguish baseline families explicitly instead of collapsing every check into the benchmark lane.

### 8.1 `core_benchmark`

This is the deterministic safety lane.

- channel: `benchmark`
- executor posture: Codex-only
- specialist posture: suppressed by policy
- intended use: CI-safe regression checks, submission/benchmark discipline, safety invariants

### 8.2 `hybrid_governed`

This is the governed mixed-assistant lane.

- channel: `standard`
- executor posture: Codex final authority with advisory specialists
- specialist posture: Claude and Gemini can be requested by routing policy, but remain read-only/advisory
- intended use: prove that governed routing, delegation packets, and family-specific receipts work without weakening the benchmark lane

The important product rule is separation, not replacement: the hybrid family expands proof coverage, but it does not redefine benchmark truth.
