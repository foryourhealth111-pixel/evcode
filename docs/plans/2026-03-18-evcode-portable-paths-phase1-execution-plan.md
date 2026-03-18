# EvCode Portable Paths Phase 1 Execution Plan

## Requirement Source

- `docs/requirements/2026-03-18-evcode-portable-paths-phase1.md`

## Internal Grade

- `M`

## Waves

1. Add failing regression tests for portable config resolution, benchmark artifact handoff, and `run --help` behavior.
2. Implement a shared portable config-path resolver plus benchmark handoff semantics.
3. Re-run focused tests, then real CLI smoke commands.
4. Emit proof and cleanup receipts.

## Verification Commands

- `python3 -m pytest tests/test_portable_paths.py tests/test_app_entrypoints.py tests/test_runtime_bridge.py tests/test_contracts.py -q`
- `node apps/evcode/bin/evcode.js run --help`
- `node apps/evcode-bench/bin/evcode-bench.js run --help`
- `node apps/evcode-bench/bin/evcode-bench.js run --task '...' --workspace ... --artifacts-root ... --run-id ...`

## Rollback Rules

- If portable config resolution breaks source-mode flows, keep the portable root as opt-in fallback while preserving the resolver API.
- If benchmark handoff becomes ambiguous, fail loudly rather than silently redirecting.

## Phase Cleanup Expectations

- remove temp files created by focused tests or smoke runs
- preserve repo-owned evidence artifacts
- audit but do not kill pre-existing long-lived agent sessions
