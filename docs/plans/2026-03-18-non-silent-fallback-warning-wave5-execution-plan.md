# Non-Silent Fallback Warning Wave5 Execution Plan

## Requirement Source

- `docs/requirements/2026-03-18-non-silent-fallback-warning-wave5.md`

## Internal Grade

- `M`

## Waves

1. Inspect the current fallback path and user-visible outputs.
2. Implement explicit fallback warning/telemetry when specialist/provider failure occurs.
3. Add or adjust targeted tests.
4. Run fresh fallback execution and verify visible warning behavior.
5. Emit proof and cleanup receipts.

## Verification Commands

- `python3 -m pytest <targeted tests> -q`
- `node apps/evcode/bin/evcode.js run --task "Plan the product architecture and UX workflow for an ambiguous redesign" --artifacts-root <temp> --run-id <id> --json`

## Rollback Rules

- If the warning path breaks execution, revert to the last known safe fallback behavior and report the regression.
- If summary/receipt changes are user-visible but not yet fully covered by tests, do not claim completion until fresh execution evidence confirms them.

## Phase Cleanup Expectations

- Archive fresh run artifacts into the repo-owned session directory.
- Remove temp roots after archiving.
- Audit processes without touching unrelated long-lived sessions.
