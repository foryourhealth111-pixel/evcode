# EvCode Production User Journey Testing

## Goal

Perform real production-like user-operation testing against EvCode itself, not just unit tests, to determine whether legacy and primary user-facing features still work under current repository state.

## Scope

This validation targets the actual committed product surface available in this repository:

- `evcode` CLI
- `evcode-bench` CLI
- host passthrough surfaces still expected to feel Codex-compatible
- governed runtime entry surfaces
- provider probe and status surfaces
- at least one real standard-channel smoke run
- at least one benchmark-path smoke run if it completes within a reasonable execution window

## Constraints

- Preserve the dirty worktree; do not revert unrelated changes.
- Treat existing long-lived repo Node processes as audit-only unless they were started by this validation run.
- Keep requirement/plan/proof/cleanup artifacts traceable.
- Use realistic user commands instead of synthetic function-only validation.
- Do not invent a standalone web frontend if the repository does not actually ship one.

## Acceptance Criteria

- A governed requirement doc and execution plan exist for this validation turn.
- Real user-facing commands are executed and recorded.
- Old/legacy user-visible surfaces are checked for breakage.
- Findings are written with evidence, not guesses.
- Cleanup artifacts are emitted before completion is claimed.

## Non-Goals

- Building a new marketing site during this testing turn.
- Rebaselining release packaging or source-build pipelines.
- Killing unknown external Node workloads.
