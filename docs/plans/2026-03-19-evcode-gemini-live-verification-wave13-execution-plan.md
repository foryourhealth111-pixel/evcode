# EvCode Gemini Live Verification Wave13 Execution Plan

## Requirement Source

- `docs/requirements/2026-03-19-evcode-gemini-live-verification-wave13.md`

## Internal Grade

- `M`

## Waves

1. Run a fresh live provider probe and capture the Gemini result.
2. Execute one governed `frontend_visual` scenario through `evcode run --task ... --json`.
3. Inspect top-level routing JSON plus saved runtime artifacts for Gemini-specific evidence.
4. Emit proof/report and re-run proof doc validation.

## Verification Commands

- `node apps/evcode/bin/evcode.js probe-providers --json --live`
- `node apps/evcode/bin/evcode.js run --task "Design a responsive frontend landing page with typography, spacing, motion, and visual polish" --json`
- `npm run check:proof`

## Rollback Rules

- No persistent config changes are required for this wave.

## Phase Cleanup Expectations

- Keep generated run artifacts as evidence.
- No manual node cleanup expected unless residue is observed.
