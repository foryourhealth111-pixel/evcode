# EvCode Login Prompt Fix Wave17 Execution Plan

## Requirement Source

- `docs/requirements/2026-03-19-evcode-login-prompt-fix-wave17.md`

## Internal Grade

- `L`

## Waves

1. Patch source Codex home resolution so assembly ignores self-referential dist `CODEX_HOME` values.
2. Reassemble the standard distribution from the corrected source selection.
3. Verify the assembled `config.toml` now includes model provider information adopted from the real source Codex home.
4. Launch `evcode` in a real TTY and inspect whether startup proceeds into EvCode/Codex runtime rather than the generic login prompt.
5. Emit proof/report and run targeted verification.

## Verification Commands

- `node apps/evcode/bin/evcode.js assemble`
- `~/.local/bin/evcode status --json`
- `sed -n '1,220p' .evcode-dist/standard/codex-home/config.toml`
- `~/.local/bin/evcode`
- `npm test -- tests/test_app_entrypoints.py tests/test_runtime_bridge.py` if test scope changes require it

## Rollback Rules

- If the fix misresolves source config, revert to the previous resolution logic.
- Reassemble after rollback to restore launcher behavior.

## Phase Cleanup Expectations

- Preserve refreshed distribution artifacts and proof docs.
- No extra process cleanup expected beyond standard session cleanup.
