# EvCode Portable Paths And Hybrid Baseline Requirement

## Goal

Make EvCode safe to distribute and use broadly as a general agent CLI by removing machine-specific path assumptions from the primary user experience, while also introducing a governed baseline test surface that can validate mixed-assistant behavior without collapsing the existing Codex-primary benchmark discipline.

## Deliverable

A production-ready architecture and implementation plan for:

- path portability across different machines and install locations
- a stable, predictable user configuration surface for keys, URLs, models, and runtime roots
- portable artifact and state handling across standard and benchmark channels
- a hybrid-agent baseline validation lane that proves Claude and Gemini routing works under VCO governance
- preservation of Codex as final executor and benchmark safety authority

## Constraints

- EvCode remains one governed product with one VCO control plane.
- Codex remains the final executor for repository mutation, verification, and completion claims.
- Claude and Gemini remain governed specialists unless a stricter future rollout explicitly changes that.
- No broad-distribution workflow may depend on a repository checkout living at a fixed absolute path.
- No broad-distribution workflow may require a user to keep secrets in tracked repo files.
- Developer-local workflows may keep repo-relative overrides, but those must not be the primary portable user surface.
- Benchmark automation must preserve determinism and safety; hybrid validation must not silently weaken the core benchmark contract.
- Path redirection rules must be explicit and machine-agnostic.
- The resulting design must support Linux, macOS, and Windows conventions.

## Acceptance Criteria

- EvCode has a clearly defined path model separating install root, state root, workspace root, config root, and artifacts root.
- The primary user configuration surface for key, URL, and model setup is portable across machines and independent of repo checkout location.
- Repo-local configuration remains a supported development override, not the default portable surface.
- Standard and benchmark channels have a documented artifact contract that avoids surprising silent path behavior.
- The testing strategy distinguishes between core deterministic baseline coverage and hybrid governed specialist coverage.
- Hybrid baseline coverage includes at least one Codex-only expectation, one Claude-routed expectation, and one Gemini-routed expectation.
- Live provider validation remains opt-in and never becomes the only proof mechanism.
- Verification criteria and rollout gates are documented before implementation starts.

## Non-Goals

- Turning EvCode into an ungoverned model switchboard.
- Granting direct repository mutation authority to Claude or Gemini.
- Making live provider traffic mandatory for local development or CI.
- Replacing the current benchmark fast path with a specialist-first benchmark.
- Solving all packaging and installer concerns in this single planning turn.

## Current Evidence Driving This Requirement

- The current provider setup document centers a repo-local file at `config/assistant-providers.env.local`, which is fine for contributors but too repo-bound for a broadly distributed CLI.
- Current standard and benchmark entrypoints still assume repo-local `.evcode-dist` and `~/.codex` fallback behavior.
- The latest production user-journey proof found that benchmark runs silently redirect requested in-workspace artifact paths into `/tmp`, which is safe internally but weak as a portable user contract.
- The latest production user-journey proof also confirmed that Claude and Gemini can be live-routed successfully in governed standard mode, so hybrid-agent baseline coverage is now worth formalizing rather than keeping purely ad hoc.

## Assumptions

- The next implementation phase may introduce a small runtime-path resolver module shared by JS and Python entrypoints.
- A portable state/config root based on OS conventions is acceptable as the default user-facing model.
- Core benchmark and hybrid baseline validation should be reported separately to avoid metric contamination.
- The immediate next step is design plus implementation planning, not full rollout in this turn.

## Runtime Mode

- mode: `interactive_governed`
- requested outcome: `design + implementation plan`
- internal grade target: `L`
