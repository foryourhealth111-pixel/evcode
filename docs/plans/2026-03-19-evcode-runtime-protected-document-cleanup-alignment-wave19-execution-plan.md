# EvCode Runtime Protected Document Cleanup Alignment Wave19 Execution Plan

## Requirement Source

- `docs/requirements/2026-03-19-evcode-runtime-protected-document-cleanup-alignment-wave19.md`

## Internal Grade

- `M`

## Waves

1. Inspect the current Python `phase_cleanup` implementation and isolate the gap against the synced upstream policy and helper semantics.
2. Implement a minimal policy reader plus protected-document manifest, quarantine, and post-check helpers in `scripts/runtime/runtime_lib.py`.
3. Replace the placeholder cleanup receipt generation with a real cleanup result that records mode, counts, assertions, and evidence paths.
4. Add targeted unit coverage for protected documents under `.tmp` and for retained protected assets outside `.tmp`.
5. Run focused tests plus broader regression checks for the governed runtime bridge.
6. Write a proof artifact summarizing the behavior alignment and verification evidence.

## Verification Commands

- `python3 -m unittest tests.test_runtime_bridge`
- `python3 -m unittest tests.test_app_entrypoints`
- `python3 scripts/verify/check_materialization.py`

## Rollback Rules

- If cleanup behavior risks deleting non-temporary protected documents, stop and revert only this wave's cleanup changes.
- If the new cleanup evidence shape breaks existing runtime consumers, preserve the old receipt keys while extending the payload.
- If tests expose ambiguity in the policy mapping, prefer weaker `preview/quarantine` behavior over stronger destructive cleanup.

## Phase Cleanup Expectations

- Preserve the new requirement, plan, and proof artifacts.
- Do not delete or mutate upstream fixture baselines under `runtime/vco/upstream/scripts/verify/fixtures/document-cleanup-safety`.
- Treat `.tmp` protected documents as quarantine candidates, not destructive purge targets.
