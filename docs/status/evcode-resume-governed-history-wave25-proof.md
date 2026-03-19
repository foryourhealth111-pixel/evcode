# EvCode Resume Governed History Wave25 Proof

Date: 2026-03-19
Workspace: `/home/lqf/table/table3`
Manual verification artifacts root: `/tmp/evcode-resume-check`

## Implemented Behavior

EvCode now handles `resume` as a governed internal command in the local wrapper instead of silently delegating it to the host CLI.

Supported surfaces:

- `evcode resume`
- `evcode resume <run-id>`
- `evcode resume --artifacts-root PATH`
- `evcode native resume ...` for explicit host-native passthrough

## Files Changed

- `apps/evcode/bin/evcode.js`
- `apps/evcode/lib/runtime_display.js`
- `apps/evcode/README.md`
- `tests/test_app_entrypoints.py`

## Root Cause

`resume` was not registered as an EvCode internal command in `apps/evcode/bin/evcode.js`.

Because of that, `evcode resume` followed the same fallback path as unknown commands and was forwarded to the assembled host launcher. That path cannot restore EvCode-governed history stored under `outputs/runtime/vibe-sessions/<run-id>/...`.

## Verified Behavior

### Local Wrapper Semantics

- `resume` is now part of the EvCode internal command set.
- Without a run id, EvCode restores the most recent governed session that contains `runtime-summary.json`.
- With a run id, EvCode restores that exact governed session.
- Output uses the same runtime display surface as `trace`.
- Missing governed history now returns a clear error: `No governed runtime sessions found for EvCode resume`.

### Manual Governed Run

Created governed run:

- run id: `resume-verification-001`
- artifacts root: `/tmp/evcode-resume-check`
- session root: `/tmp/evcode-resume-check/outputs/runtime/vibe-sessions/resume-verification-001`

Observed generated artifacts include:

- `runtime-summary.json`
- `runtime-events.jsonl`
- `cleanup-receipt.json`

### Manual Resume Verification

Command:

```bash
node apps/evcode/bin/evcode.js resume --artifacts-root /tmp/evcode-resume-check
```

Observed output included:

- `EvCode Governed Run`
- `run_id: resume-verification-001`
- `route: codex_only`
- actor board rows for `CODX`, `CLAU`, `GEMI`
- timeline entries sourced from governed runtime events
- artifacts footer pointing at the saved session root and runtime event log

### Manual Named Resume Verification

Command:

```bash
node apps/evcode/bin/evcode.js resume resume-verification-001 --artifacts-root /tmp/evcode-resume-check --json
```

Observed output included:

- `summary.run_id = "resume-verification-001"`
- `events[0..]` populated from governed runtime event history
- `summary.artifacts.cleanup_receipt = "/tmp/evcode-resume-check/outputs/runtime/vibe-sessions/resume-verification-001/cleanup-receipt.json"`

## Automated Verification

Focused regression verification:

```bash
python3 -m unittest \
  tests.test_app_entrypoints.AppEntrypointTests.test_standard_resume_restores_latest_governed_session \
  tests.test_app_entrypoints.AppEntrypointTests.test_standard_resume_errors_clearly_when_no_governed_session_exists \
  tests.test_distribution_assembly.DistributionAssemblyTests.test_standard_distribution_assembles_and_launches \
  tests.test_distribution_assembly.DistributionAssemblyTests.test_standard_distribution_prefers_bundled_host_binary
```

Result:

- `Ran 4 tests in 0.294s`
- `OK`

Broader regression verification:

```bash
python3 -m unittest tests.test_app_entrypoints tests.test_distribution_assembly tests.test_runtime_bridge tests.test_specialist_routing tests.test_assistant_adapters
python3 scripts/verify/check_materialization.py
```

Result:

- `Ran 46 tests in 2.016s`
- `OK`
- `materialization checks: ok`

## Result

Wave25 proves that `evcode resume` now restores EvCode-governed history directly from governed artifacts, while explicit host passthrough remains available through `evcode native resume ...`.
