# EvCode Claude Haiku Live Probe Wave12 Execution Plan

## Requirement Source

- `docs/requirements/2026-03-19-evcode-claude-haiku-live-probe-wave12.md`

## Internal Grade

- `M`

## Waves

1. Preserve current local provider configuration as baseline context.
2. Override `EVCODE_CLAUDE_MODEL=claude-haiku-4-5` for one probe invocation only.
3. Run `probe-providers --json --live` and inspect the Claude result.
4. Compare against the prior `claude-opus-4-6` result and emit proof artifacts.

## Verification Commands

- `EVCODE_CLAUDE_MODEL=claude-haiku-4-5 node apps/evcode/bin/evcode.js probe-providers --json --live`
- `npm run check:proof`

## Rollback Rules

- No persistent config rollback required because the model override is process-local.

## Phase Cleanup Expectations

- No temp artifacts beyond proof docs and optional scratch JSON under `/tmp`.
