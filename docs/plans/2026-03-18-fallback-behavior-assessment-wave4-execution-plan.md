# Fallback Behavior Assessment Wave4 Execution Plan

## Requirement Source

- `docs/requirements/2026-03-18-fallback-behavior-assessment-wave4.md`

## Internal Grade

- `M`

## Waves

1. Prepare repo-owned log directory and fresh governed run id.
2. Execute one standard-channel task that requests Claude under live env.
3. Inspect routing, specialist result, and Codex integration receipts.
4. Write proof and cleanup receipts.

## Verification Commands

- `node apps/evcode/bin/evcode.js run --task "Plan the product architecture and UX workflow for an ambiguous redesign" --artifacts-root <temp> --run-id <id>`
- `python3 - <<PY ...` to extract fallback fields from generated artifacts

## Rollback Rules

- If the run no longer degrades cleanly, report that regression explicitly.
- If Claude still fails but Codex remains final executor, report fallback as working but degraded.

## Phase Cleanup Expectations

- Archive fresh temp artifacts into the repo-owned session directory.
- Remove temp directories after archiving.
- Audit node/codex processes without terminating unrelated sessions.
