# EvCode Gemini CLI Display Simulation Wave14 Execution Plan

## Requirement Source

- `docs/requirements/2026-03-19-evcode-gemini-cli-display-simulation-wave14.md`

## Internal Grade

- `M`

## Waves

1. Launch a real TTY run for a frontend-visual task expected to activate Gemini.
2. Capture terminal output from the interactive actor surface.
3. Compare that output with runtime summary, trace, and routing receipts.
4. Emit proof/report with a direct statement about CLI display correctness.

## Verification Commands

- `node apps/evcode/bin/evcode.js run --task "Design a responsive frontend landing page with typography, spacing, motion, and visual polish" --run-id wave14-gemini-cli-display`
- `node apps/evcode/bin/evcode.js trace wave14-gemini-cli-display`
- `npm run check:proof`

## Rollback Rules

- No persistent config changes are required.

## Phase Cleanup Expectations

- Preserve the generated wave14 session directory as evidence.
