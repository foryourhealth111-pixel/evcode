# EvCode Portable Paths Phase 1 Requirement

## Goal

Implement the first concrete repair wave for EvCode portability and broad distribution safety by fixing the primary path model, benchmark artifact contract, and CLI help ergonomics.

## Deliverable

Code changes plus verification coverage for:

- portable provider/config path resolution
- explicit benchmark artifact handoff semantics
- standard `run --help` behavior on both CLIs

## Constraints

- Preserve the current governed runtime contract.
- Keep Codex as final execution authority.
- Do not break repo-local contributor workflows; demote them to compatibility behavior instead.
- Do not weaken benchmark safety isolation.
- Keep changes compatible with current source-mode execution from this repository.

## Acceptance Criteria

- A portable config root is discoverable without relying on the repo checkout path.
- Repo-local `config/assistant-providers.env.local` remains supported as a development override.
- Benchmark runs that redirect execution artifacts still leave a stable user-visible handoff at requested paths.
- `evcode run --help` and `evcode-bench run --help` return usage/help instead of `Missing --task for run`.
- Focused regression tests cover the new behavior.

## Non-Goals

- Full hybrid baseline implementation in this turn.
- New packaging installers.
- Direct specialist mutation authority.

## Source Design

- `docs/plans/2026-03-18-evcode-portable-paths-hybrid-baseline-design.md`
- `docs/plans/2026-03-18-evcode-portable-paths-hybrid-baseline-execution-plan.md`
