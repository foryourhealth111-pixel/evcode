# EvCode Runtime Protected Document Cleanup Alignment Wave19 Proof

Date: 2026-03-19
Workspace: `/home/lqf/table/table3`

## Requirement And Plan

- Requirement: `docs/requirements/2026-03-19-evcode-runtime-protected-document-cleanup-alignment-wave19.md`
- Plan: `docs/plans/2026-03-19-evcode-runtime-protected-document-cleanup-alignment-wave19-execution-plan.md`

## Goal Closed In This Wave

This wave closes the remaining gap left by Wave18:

- Wave18 synced the upstream VCO protected-document cleanup contract into EvCode's embedded runtime mirror and metadata.
- Wave19 aligns EvCode's Python governed runtime behavior with that contract so `phase_cleanup` receipts now represent real protected-document handling rather than a placeholder success stub.

## Implemented Runtime Behavior

Updated runtime behavior in `scripts/runtime/runtime_lib.py` now:

- loads the embedded VCO cleanup policy from `runtime/vco/upstream/config/phase-cleanup-policy.json`
- snapshots protected `.docx`, `.xlsx`, `.pptx`, and `.pdf` assets across the policy-declared snapshot roots under the active artifacts root
- detects protected document assets under `.tmp`
- quarantines protected tmp documents into `outputs/runtime/process-health/quarantine/protected-documents`
- removes the remaining `.tmp` tree after quarantine
- verifies that retained protected assets outside `.tmp` still exist and quarantined assets still exist in quarantine
- emits cleanup receipts with cleanup mode, protected document summary, post-cleanup assertions, and evidence paths

## Supporting Robustness Fixes

Two small support fixes were applied so verification stays deterministic in the local environment:

- `scripts/build/assemble_distribution.py` now falls back to a builtin/vendor TOML reader instead of depending solely on the user-site `toml` package
- EvCode entrypoints now treat any `standard/codex-home` or `benchmark/codex-home` target as self-managed so source-config adoption correctly falls back to `HOME/.codex`
- probe/trace tests were pinned to explicit non-live provider env so they do not depend on the operator's local API-key state

## Verification Evidence

### 1. Targeted runtime cleanup tests

Command:

```bash
python3 -m unittest tests.test_runtime_bridge
```

Observed result:

- `Ran 6 tests ... OK`
- includes direct coverage for:
  - protected tmp documents quarantined before cleanup
  - preview-only mode preserving protected tmp assets
  - governed standard run still writing enriched cleanup receipts

### 2. App entrypoint regression coverage

Command:

```bash
python3 -m unittest tests.test_app_entrypoints
```

Observed result:

- `Ran 13 tests ... OK`
- confirms:
  - standard and benchmark entrypoints still assemble and adopt source config correctly
  - provider probe behavior remains deterministic under isolated env
  - trace flows still render governed runtime actor timelines

### 3. Materialization integrity

Command:

```bash
python3 scripts/verify/check_materialization.py
```

Observed result:

- `materialization checks: ok`

Meaning:

- runtime materialization metadata still matches the synced embedded VCO mirror after the runtime-behavior update

### 4. Standard and benchmark distribution assembly

Commands:

```bash
node apps/evcode/bin/evcode.js assemble
node apps/evcode-bench/bin/evcode-bench.js assemble
```

Observed result:

- standard distribution assembled successfully
- benchmark distribution assembled successfully

## Key Changed Surfaces

- `scripts/runtime/runtime_lib.py`
- `scripts/build/assemble_distribution.py`
- `apps/evcode/bin/evcode.js`
- `apps/evcode-bench/bin/evcode-bench.js`
- `tests/test_runtime_bridge.py`
- `tests/test_app_entrypoints.py`

## Conclusion

EvCode now has behavior-level protected-document cleanup alignment with the synced upstream VCO policy: protected Office/PDF assets inside `.tmp` are quarantined before tmp cleanup, retained protected assets outside `.tmp` are preserved, and governed cleanup receipts now carry the evidence needed to support the claim.
