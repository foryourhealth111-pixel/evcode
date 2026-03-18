# EvCode Specialist Pipeline

## Status

- Status: Proposed authoritative architecture
- Date: 2026-03-18
- Scope: Codex-led specialist pipeline with Claude planning and Gemini visual design

## 1. Architecture Decision

EvCode should adopt a Codex-led specialist pipeline, not a broad autonomous multi-assistant execution model.

The architecture should be:

- Codex as engineering spine
- Claude as planner and product/UX strategist
- Gemini as visual and front-end design specialist
- VCO as sole control-plane truth

This preserves EvCode's strongest current properties while adding specialist value where Codex is weakest.

## 2. Role Model

### 2.1 Codex

Codex remains the only assistant allowed to:

- own final engineering execution
- modify high-risk code paths
- integrate across packages and layers
- resolve front-end/back-end coupling
- run verification and declare completion

Codex is not just one specialist among others.
It is the execution authority.

### 2.2 Claude

Claude should be restricted to planning intelligence.

Claude outputs may include:

- requirement refinement
- product framing
- UX and interaction structure
- design rationale
- implementation plan suggestions
- acceptance criteria refinements
- reports, summaries, documentation, and paper-style writing artifacts
- early-stage user-need interpretation and overall project-design briefs

Claude should not directly land repository code in the initial design.

### 2.3 Gemini

Gemini should be restricted to visual and front-end intelligence.

Gemini outputs may include:

- visual direction and mood
- component styling plans
- typography, spacing, color, and motion guidance
- isolated front-end candidate implementations
- presentational component proposals
- screenshot-oriented target states

Gemini should not own backend logic, integration logic, or final repository merges.

## 3. Control-Plane Rule

All specialist work must remain subordinate to the existing governed runtime.

That means:

- route authority stays with the canonical EvCode + VCO runtime
- requirement freezing happens before specialist execution
- execution planning happens before specialist delegation
- specialist routing is a `plan_execute` concern only
- completion still requires Codex-led verification and cleanup

## 4. Specialist Invocation Model

### 4.1 Claude Invocation

Claude is invoked when the task is primarily about:

- ambiguity reduction
- product structure
- UX flow
- interaction hierarchy
- reframing an uninspired but technically safe design direction
- writing reports, summaries, documentation, or paper-like artifacts
- understanding user requirements and shaping overall project design before engineering execution

Claude result type:

- structured plan artifact
- not executable repository truth

Claude exploration modes:

- `autonomous`: Claude receives a light mission brief, explores the repository itself, and writes the document or design artifact
- `packetized`: Claude receives a structured task packet when stronger auditability or tighter scope control is required

The default for documentation, requirements understanding, and overall project design should be `autonomous`.
Codex still translates Claude output into engineering practice and execution plans.


### 4.2 Gemini Invocation

Gemini is invoked when the task is primarily about:

- visual quality
- front-end aesthetics
- layout feel
- design-system styling direction
- component polish
- landing-page tone and presentation

Gemini result type:

- visual plan or isolated UI candidate diff
- not final integrated repository truth

### 4.3 Codex Integration Step

After Claude and/or Gemini produce outputs, Codex must:

- reconcile them with real repository constraints
- convert them into an engineering plan
- normalize candidate edits into repo-safe patches
- repair front-end/back-end coupling
- run all required verification
- write final execution and cleanup receipts

## 5. Trust Tiers

### Tier A: Advisory Only

Claude and Gemini return plans, rationale, and candidate ideas only.
Codex applies everything manually or semi-manually.

This should be the first rollout phase.

### Tier B: Isolated Candidate Apply

Gemini may produce candidate UI code in an isolated worktree.
Codex reviews and selectively integrates.

Claude may later produce structured front-end skeleton proposals in an isolated worktree, but still without final authority.

### Tier C: Narrow Direct Apply

This is optional and only for low-risk presentational scopes.
It should not exist in the first stable release.

## 6. Task Packet Contract

EvCode should never pass raw conversation fragments directly into specialists.
It should compile a normalized task packet.

### Required fields

- task id
- run id
- repository path summary
- file scope
- task goal
- constraints
- acceptance criteria
- non-goals
- current architecture notes
- design-system notes
- allowed authority tier
- expected output type

### Optional fields

- current screenshots
- component inventory
- route or page references
- backend API constraints
- existing style-token references

## 7. Result Contract

Every specialist response should be normalized into a result packet.

### Required fields

- specialist name
- task id
- summary
- assumptions
- proposed actions
- files touched or proposed
- confidence level
- unresolved risks
- recommended next actor

### Optional fields

- patch text
- component code
- design tokens
- screenshot references
- alternate variants

## 8. Receipt Model

Each specialist delegation should emit:

- routing receipt
- task packet receipt
- specialist result receipt
- Codex integration receipt
- final verification receipt

This is necessary to preserve traceability and prevent model-shopping drift.

## 9. RightCodes Provider Design

The first provider surface should be RightCodes.

### Canonical endpoints

- Codex endpoint: `https://right.codes/codex/v1`
- Codex model: `gpt5.4`
- Claude endpoint: `https://right.codes/claude/v1`
- Claude model: `claude-opus-4-6`
- Gemini endpoint: `https://right.codes/gemini/v1`
- Gemini model: `gemini-3.1-pro-preview`

### Secret handling

Do not write the live API key into tracked repository config.
Use one of:

- `env.local`
- shell environment
- local untracked provider config materialized during assembly

Recommended variable names:

- `EVCODE_RIGHTCODES_API_KEY`
- `EVCODE_CODEX_BASE_URL`
- `EVCODE_CLAUDE_BASE_URL`
- `EVCODE_GEMINI_BASE_URL`

The assembly/runtime layer may derive provider-specific configs from these variables.

## 10. Standard And Benchmark Policy

### Standard channel

Allowed behavior:

- Claude advisory planning
- Gemini advisory design
- Gemini isolated UI candidate apply for low-risk scopes after proof
- Codex final integration

### Benchmark channel

Default behavior:

- Codex only
- no external specialist dependency in the critical path
- optional specialist advisory mode only if explicitly proven reproducible

Benchmark mode must stay conservative.

## 11. Package Layout

Recommended new packages:

- `packages/specialist-routing`
- `packages/assistant-adapters`
- `packages/delegation-contracts`

Existing packages to extend:

- `packages/provider-runtime`
- `packages/capability-runtime`
- `packages/governed-runtime-bridge`

## 12. Failure Handling

### Claude failure

Fallback:

- continue with Codex-only planning
- record specialist-unavailable receipt

### Gemini failure

Fallback:

- continue with Codex-only engineering path
- optionally keep visual requirements as unmet and visible in artifacts

### Codex integration rejection

If Codex determines a Claude or Gemini output is unsafe or incoherent:

- reject candidate output
- write rejection rationale into receipts
- continue with Codex-authored implementation path

## 13. Why This Architecture Is Correct For EvCode

This design accepts a hard truth:

- the best design intelligence and the best engineering discipline do not necessarily come from the same model

But it also preserves another hard truth:

- EvCode's value comes from governed execution, not from model plurality alone

So the architecture must optimize for both:

- specialist quality where appropriate
- Codex-led engineering control everywhere that matters
