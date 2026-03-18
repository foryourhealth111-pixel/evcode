# EvCode Gate Integration And Live Hybrid Validation Requirement

## Goal

Promote the new offline baseline-family and distributed-install validators into EvCode's formal verification gate, while adding a separate live-opt-in hybrid validation surface that can prove real governed Claude/Gemini collaboration without contaminating the default benchmark-safe CI path.

## Deliverable

Code, tests, docs, and proof artifacts for:

- integrating offline baseline-family and distribution-portability validation into formal check/release verification entrypoints
- extending contract checks so baseline-family invariants are enforced centrally
- adding a dedicated live hybrid validation script that exercises real governed standard-channel routing when API configuration is supplied
- preserving offline-first CI and Codex-only benchmark semantics

## Constraints

- Keep benchmark CI deterministic and specialist-suppressed by default.
- Do not make live provider traffic mandatory in `check` or GitHub Actions.
- Preserve Codex as final executor and verifier.
- Preserve dirty worktree state and unrelated user changes.
- Keep live validation opt-in via explicit env and/or flag.

## Acceptance Criteria

- `package.json` and release workflow formal verification surfaces include offline baseline-family and distribution-portability validators.
- `scripts/verify/check_contracts.py` enforces baseline-family config/profile invariants and the presence of new verification scripts.
- A live validation script exists for governed standard-channel hybrid validation and returns structured JSON.
- The live script degrades cleanly when live env is absent and can execute real validation when env is provided.
- Fresh regression tests and gate-level command runs pass.

## Non-Goals

- Running live validation in default CI.
- Enabling specialists in benchmark mode.
- Changing RightCodes provider compatibility behavior.

## Source Design

- `docs/requirements/2026-03-18-evcode-hybrid-baseline-distribution-wave1.md`
- `docs/plans/2026-03-18-evcode-hybrid-baseline-distribution-wave1-execution-plan.md`
- `docs/status/evcode-hybrid-baseline-distribution-wave1-proof.md`
- `docs/status/evcode-real-collab-validation-proof.md`
