# EvCode Local Commit And Refresh Wave7 Execution Plan

## Requirement Source

- `docs/requirements/2026-03-18-evcode-local-commit-refresh-wave7.md`

## Internal Grade

- `M`

## Waves

1. Freeze governed artifacts for this local commit/refresh wave.
2. Confirm the canonical local install path and final commit scope.
3. Stage and create a local Git commit for the prepared enhancement set.
4. Refresh the locally used EvCode installation via the repository-supported install/assemble/wrapper flow.
5. Run fresh startup/version validation and emit proof/report/cleanup receipts.

## Verification Commands

- `git log -1 --stat --oneline`
- `bash scripts/install/build_from_source.sh`
- `bash scripts/install/install_local_wrappers.sh`
- `evcode --version`
- `evcode status --json`

## Rollback Rules

- If the local install refresh fails after commit, do not rewrite history; diagnose and report the failing install step.
- If wrapper refresh changes system-facing paths unexpectedly, stop and report before attempting further host-level changes.

## Phase Cleanup Expectations

- Capture install/refresh logs in the repo-owned session directory.
- Remove any caches or transient byproducts created during verification if they land in the repo.
- Audit, but do not terminate, unrelated external Node processes.
