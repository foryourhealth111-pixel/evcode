# EvCode Hybrid Baseline Family And Distributed Install Validation Requirement

## Goal

Implement a formal hybrid baseline family for EvCode so governed mixed-assistant behavior becomes a first-class baseline surface, while preserving the existing Codex-only benchmark safety lane and validating that EvCode remains usable across moved paths, external workspaces, and broad-distribution style installs.

## Deliverable

Code, tests, verification runners, and proof artifacts for:

- a formal baseline-family definition that distinguishes deterministic core benchmark coverage from hybrid governed specialist coverage
- a repeatable hybrid baseline runner with offline assertions and optional live specialist smoke validation
- channel/profile/status surfaces that expose baseline-family membership clearly
- distribution-style portability validation that proves EvCode can start outside the repo root and resolve portable unified configuration from an external config root
- governed proof and cleanup receipts for this wave

## Constraints

- Preserve one governed VCO control plane.
- Preserve Codex as final executor, verifier, and mutation authority.
- Do not enable Claude or Gemini in the benchmark channel by default.
- Do not make live provider traffic mandatory for baseline or portability validation.
- Preserve dirty worktree state and do not revert unrelated user changes.
- Keep the implementation lean; prefer formalizing existing behavior over adding a heavy new packaging subsystem.

## Acceptance Criteria

- A formal baseline-family contract exists in-repo and distinguishes at least `core_benchmark` and `hybrid_governed`.
- The benchmark profile remains mapped to a Codex-only baseline family and still suppresses specialists.
- The standard profile exposes hybrid governed baseline membership without implying specialist mutation authority.
- A repeatable hybrid baseline runner can verify at minimum: Codex-only backend routing, Claude planning routing, Gemini frontend routing, and benchmark suppression.
- Hybrid baseline reporting is separate from the core benchmark lane.
- Distribution-style validation proves that assembled launchers can start from an external workspace outside the repo path.
- Portable unified configuration can still be resolved from an external config root when the CLI is run from an external cwd.
- Fresh tests cover the baseline-family contract and external-path validation.

## Non-Goals

- Replacing the benchmark channel with a hybrid lane.
- Granting direct filesystem or shell mutation power to Claude or Gemini.
- Shipping a platform-specific installer in this wave.
- Reworking the live provider adapter protocol beyond what is required for baseline reporting.

## Source Design

- `docs/requirements/2026-03-18-evcode-portable-paths-hybrid-baseline.md`
- `docs/plans/2026-03-18-evcode-portable-paths-hybrid-baseline-design.md`
- `docs/plans/2026-03-18-evcode-portable-paths-hybrid-baseline-execution-plan.md`
