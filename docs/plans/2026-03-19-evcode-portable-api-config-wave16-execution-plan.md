# EvCode Portable API Config Wave16 Execution Plan

## Requirement Source

- `docs/requirements/2026-03-19-evcode-portable-api-config-wave16.md`

## Internal Grade

- `M`

## Waves

1. Create the portable EvCode config directory if missing.
2. Write the current verified provider settings into `~/.config/evcode/assistant-providers.env`.
3. Run `evcode status --json` to confirm the portable surface wins over repo-local fallback.
4. Run a live probe to confirm provider behavior remains stable.

## Verification Commands

- `~/.local/bin/evcode status --json`
- `~/.local/bin/evcode probe-providers --json --live`
- `npm run check:proof`

## Rollback Rules

- If the portable file is malformed, overwrite it with a corrected env file.
- Do not remove the repo-local provider file during this wave.

## Phase Cleanup Expectations

- No temp artifacts beyond proof docs.
- No process cleanup expected.
