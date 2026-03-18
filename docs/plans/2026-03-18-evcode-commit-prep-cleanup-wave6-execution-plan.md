# EvCode Commit Prep Cleanup Wave6 Execution Plan

## Requirement Source

- `docs/requirements/2026-03-18-evcode-commit-prep-cleanup-wave6.md`

## Internal Grade

- `M`

## Waves

1. Freeze governed artifacts for this cleanup wave.
2. Audit modified/untracked files and classify commit-worthy deliverables versus transient artifacts.
3. Remove caches and temporary test/runtime byproducts without touching durable outputs.
4. Run fresh verification on the retained change set.
5. Emit proof/report and cleanup receipt for commit readiness.

## Verification Commands

- `python3 -m pytest tests/test_app_entrypoints.py tests/test_runtime_bridge.py tests/test_specialist_routing.py -q`
- `python3 scripts/verify/check_contracts.py`
- `npm run check`

## Rollback Rules

- If cleanup removes files required by tests or runtime validation, restore only the minimal required artifacts.
- If full verification exposes regressions, stop at evidence collection and do not claim commit readiness.

## Phase Cleanup Expectations

- Delete repo-local caches such as `__pycache__`, `.pytest_cache`, and stray `.pyc` files.
- Avoid touching unrelated external processes; audit only.
- Keep repo-owned proof docs and only keep runtime session receipts needed for governed traceability.
