# EvCode Resume Governed History Wave25 Execution Plan

Date: 2026-03-19
Requirement: `docs/requirements/2026-03-19-evcode-resume-governed-history-wave25.md`
Internal grade: `M`

## Scope

Implement EvCode-managed resume semantics in the standard CLI wrapper while preserving explicit host-native passthrough through `evcode native ...`.

## Steps

1. Add failing tests for `resume` selecting the latest governed session and restoring a named run id.
2. Add failing tests for clear error handling when no governed session exists.
3. Update the CLI wrapper so `resume` becomes an EvCode internal command instead of an implicit host passthrough.
4. Reuse runtime display and summary loading instead of inventing a second history format.
5. Keep explicit host-native passthrough available via `evcode native resume ...`.
6. Run focused and suite-level verification plus materialization checks.

## Verification Commands

```bash
python3 -m unittest tests.test_app_entrypoints tests.test_distribution_assembly tests.test_runtime_bridge tests.test_specialist_routing tests.test_assistant_adapters
python3 scripts/verify/check_materialization.py
node apps/evcode/bin/evcode.js run --task "diagnostic specialist visibility" --trace --artifacts-root /tmp/evcode-resume-check --run-id resume-check-demo --specialist-test claude
node apps/evcode/bin/evcode.js resume --artifacts-root /tmp/evcode-resume-check
```

## Rollback Rules

- Do not break `evcode native ...` host passthrough.
- Do not create a second history storage surface.
- Do not mutate governed session artifacts during resume.
