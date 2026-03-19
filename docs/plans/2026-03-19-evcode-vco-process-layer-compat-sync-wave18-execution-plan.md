# EvCode VCO Process-Layer Compatibility Sync Wave18 Execution Plan

## Requirement Source

- `docs/requirements/2026-03-19-evcode-vco-process-layer-compat-sync-wave18.md`

## Internal Grade

- `M`

## Waves

1. Compare the current embedded VCO materialization pin with the upstream commit that contains the compatibility-layer fix.
2. Sync the changed upstream runtime files into `runtime/vco/upstream`, including canonical, bundled, and nested bundled surfaces, plus cleanup-safety docs/scripts/fixtures.
3. Update runtime materialization receipts and source-lock metadata to the synced upstream commit.
4. Align EvCode host-bridge documentation with the same ownership split to prevent semantic drift between EvCode and the embedded runtime.
5. Run targeted verification for materialization integrity and inspect the resulting diff for unintended spillover.
6. Emit proof documentation summarizing the synced commit, changed surfaces, and verification evidence.

## Verification Commands

- `python3 scripts/verify/check_materialization.py`
- `git diff -- runtime/vco config/sources.lock.json docs/architecture/evcode-host-runtime-bridge.md`
- targeted content inspection for `Compatibility With Process Layers` and protected document cleanup policy

## Rollback Rules

- If the upstream sync introduces unrelated drift, revert only the newly synced runtime files and metadata touched by this wave.
- If materialization verification fails, do not claim sync completion; restore metadata/file parity before closing the run.

## Phase Cleanup Expectations

- Preserve synced runtime artifacts, requirement/plan docs, and proof docs.
- Do not delete protected document fixtures introduced by the upstream sync.
