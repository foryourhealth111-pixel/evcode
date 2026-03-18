# EvCode Portable Paths And Hybrid Baseline Design

## Problem Statement

EvCode is no longer just a local repo convenience wrapper. It is becoming a distributable, governed agent CLI that users should be able to install and run from different machines, directories, and operating systems without inheriting the original developer's filesystem layout.

The current repository already proves the multi-assistant control model is viable, but the primary user surfaces are still too repo-centric:

- provider setup is documented around a repo-local env file
- JS and Python entrypoints still lean on repo-relative distribution roots and `~/.codex` fallbacks
- benchmark mode protects workspace safety by redirecting artifacts into `/tmp`, but the current contract is surprising to callers

At the same time, the product now needs a formal baseline for mixed-assistant behavior. The current production validation proved that Claude and Gemini can be routed live under VCO governance, but that capability is still tested as an operator exercise, not as a first-class baseline lane.

## Design Goals

- Preserve one governed control plane.
- Keep Codex as final execution and verification authority.
- Make path behavior portable and explainable.
- Preserve safe developer-local repo workflows without making them the only workflow.
- Add hybrid baseline coverage without weakening the core benchmark lane.

## Approaches Considered

### Approach A: Keep repo-relative defaults and add more environment overrides

This is the lowest-effort path. The repo remains the main home for local config and distribution state, and portability is handled by documenting more env vars.

Pros:

- minimal code movement
- low migration cost for current contributors
- preserves current local habits

Cons:

- still too dependent on checkout layout
- still produces confusing behavior for packaged or moved installs
- shifts too much burden onto user documentation and shell discipline

Verdict: not recommended as the primary design.

### Approach B: Introduce a portable path model with explicit roots and a compatibility layer

This separates immutable install assets from mutable user state. The CLI resolves a portable state root and config root using OS conventions, while still allowing repo-local overrides for development.

Pros:

- correct mental model for a distributable CLI
- supports packaging and broad reuse cleanly
- lets benchmark and standard modes share the same path contract language
- keeps current repo workflows through explicit compatibility overrides

Cons:

- requires a shared path resolver across JS and Python entrypoints
- needs migration logic and documentation updates
- requires tests that simulate multiple machine layouts

Verdict: recommended.

### Approach C: Full runtime registry or daemon-backed environment manager

This would centralize install metadata, active profiles, runtime directories, and artifact bookkeeping in a richer global state system.

Pros:

- strongest long-term operator model
- more space for future packaging and multi-install support

Cons:

- too large for the current correction scope
- high implementation and rollout risk
- unnecessary before the simpler portable-root model is stabilized

Verdict: defer.

## Recommended Design

Adopt Approach B.

EvCode should define five explicit path domains:

1. Install root: immutable product assets and packaged binaries
2. State root: mutable EvCode-owned runtime state on the local machine
3. Config root: user-editable configuration stored under the state root or a matching OS config directory
4. Workspace root: the repository or task directory the agent is operating on
5. Artifacts root: the run-specific output location for proofs, logs, and benchmark receipts

These must stop being implicitly conflated.

## Path Contract

### 1. Install Root

The install root is where EvCode itself lives. In source mode this may still be the repository. In packaged mode it is the installed CLI distribution.

The install root must never be used as the default location for mutable secrets, receipts, or cross-run state.

### 2. State Root

The state root is the portable home for mutable EvCode runtime state.

Recommended default:

- Linux: XDG-style path under the user's config/state home
- macOS: Application Support-style path
- Windows: AppData-style path

Override precedence should remain explicit:

- CLI flag
- env var
- portable default resolver

### 3. Config Root

The config root should hold the primary user-facing assistant/provider setup surface.

Recommendation:

- move the portable primary setup target out of `repo/config/...`
- keep repo-local `config/assistant-providers.env.local` as a development override only
- document a single portable config file containing key, URL, model, and optional feature flags

This preserves contributor convenience while fixing the broad-distribution user story.

### 4. Workspace Root

Workspace root stays task-specific and may be a repo checkout, arbitrary project folder, or benchmark task directory.

A portable CLI must not assume the workspace is also the product home.

### 5. Artifacts Root

Artifacts root must become explicit and predictable.

The current benchmark redirection is defensible for safety, but the contract is weak because the caller asks for one path and receives another without a stable on-disk handoff at the requested location.

Recommended correction:

- execution may still use an external safe temp root when required
- but the user-requested output path must receive a stable handoff artifact after execution completes
- that handoff should be a copied result or a manifest file, not a silent disappearance into `/tmp`
- the same contract should be documented for both `--artifacts-root` and `--result-json`

## Config Resolution Model

Recommended precedence:

1. explicit CLI flags
2. explicit shell environment variables
3. portable user config file in config root
4. repo-local development override file when running from source mode
5. tracked policy defaults

This keeps one portable story for users while preserving repo-local contributor ergonomics.

## Hybrid Baseline Test Model

The current benchmark lane should not be overloaded to do everything.

EvCode should instead formalize two baseline families:

### Family A: Core Baseline

Purpose:

- deterministic regression checks
- Codex-primary benchmark discipline
- no dependency on specialist availability

Expected properties:

- benchmark channel
- Codex-only execution or explicit specialist suppression
- no live network dependency by default
- suitable for CI gating

### Family B: Hybrid Governed Baseline

Purpose:

- prove that multi-assistant governance actually works
- validate routing decisions and contract receipts
- prove that Claude and Gemini can contribute without bypassing Codex authority

Expected properties:

- primarily standard governed mode
- route assertions plus receipt assertions
- offline contract tests first, live opt-in smoke tests second
- separated reporting so non-deterministic live provider issues do not corrupt core benchmark conclusions

## Hybrid Baseline Coverage Matrix

Minimum baseline scenarios:

- Codex-only scenario: backend/runtime or verification task should remain Codex-owned
- Claude scenario: planning/documentation task should route to Claude advisory mode
- Gemini scenario: frontend-visual task should route to Gemini advisory mode
- Suppression scenario: benchmark mode should suppress Claude and Gemini unless an explicit future rollout changes policy
- Contract scenario: all specialist runs must emit routing, packet, result, integration, and cleanup receipts

## Verification Strategy

### Offline verification

- unit tests for path resolution precedence
- unit tests for portable config discovery
- unit tests for benchmark artifact handoff semantics
- routing tests for Codex / Claude / Gemini / suppression cases
- contract snapshot tests for standard and benchmark summaries

### Live opt-in verification

- portable provider probe using configured user config root
- one Claude-routed standard smoke task
- one Gemini-routed standard smoke task
- one benchmark Codex-only smoke task

Live validation should remain opt-in and never be the only release gate.

## Rollout Strategy

### Phase 1: Portable path layer

- add shared resolver primitives
- introduce config/state/artifact path terminology
- preserve current repo-local behavior behind compatibility fallback

### Phase 2: Contract correction

- make benchmark artifact handoff explicit
- update status and doctor surfaces so they describe portable and repo-local resolution clearly

### Phase 3: Baseline expansion

- add hybrid governed baseline family
- keep core benchmark family separate in docs and reporting

### Phase 4: Distribution hardening

- validate source-mode, moved-checkout, and packaged-install scenarios
- verify Windows/macOS/Linux path behavior

## Recommendation Summary

The right fix is not to keep piling env vars onto repo-relative assumptions.
The right fix is to make EvCode path domains explicit, move the primary user configuration story to a portable state/config root, retain repo-local overrides only as development compatibility, and split baseline validation into a deterministic core lane plus a governed hybrid lane.
