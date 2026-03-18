# EvCode Gate Integration And Live Hybrid Validation Execution Plan

## Requirement Source

- `docs/requirements/2026-03-18-evcode-gate-integration-live-hybrid-wave2.md`

## Internal Grade

- `M`

## Waves

1. Update contract/gate entrypoints to include offline baseline-family and distribution-portability validators.
2. Add a dedicated live hybrid validation script and corresponding offline test coverage.
3. Update docs and operator surfaces for the new gate/live entrypoints.
4. Run targeted tests, gate-level commands, and opt-in live validation.
5. Emit proof and cleanup receipts.

## Verification Commands

- `python3 -m pytest tests/test_live_hybrid_validation.py tests/test_hybrid_baseline.py tests/test_distribution_portability.py tests/test_contracts.py tests/test_app_entrypoints.py -q`
- `python3 scripts/verify/check_contracts.py`
- `python3 scripts/verify/run_hybrid_baseline.py --repo-root /home/lqf/table/table3 --json`
- `python3 scripts/verify/validate_distribution_portability.py --repo-root /home/lqf/table/table3 --json`
- `python3 scripts/verify/run_live_hybrid_validation.py --repo-root /home/lqf/table/table3 --json` (with explicit live env only)

## Rollback Rules

- If gate integration introduces flakiness, keep the new validators callable via `package.json` scripts first and leave CI wiring minimal.
- If live validation cannot prove stable behavior with current provider env, keep the script but report degraded/skip status instead of forcing a false pass.

## Phase Cleanup Expectations

- Remove temp validation roots created outside the repo after preserving proof artifacts.
- Preserve repo-owned logs and receipts.
- Audit node/codex processes; do not kill long-lived sessions.
