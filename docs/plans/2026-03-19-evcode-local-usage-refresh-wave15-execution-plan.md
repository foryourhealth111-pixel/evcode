# EvCode Local Usage Refresh Wave15 Execution Plan

## Requirement Source

- `docs/requirements/2026-03-19-evcode-local-usage-refresh-wave15.md`

## Internal Grade

- `M`

## Waves

1. Confirm whether an existing bundled host and assembled distribution already exist.
2. Refresh the standard assembled distribution from the current checkout without forcing an unnecessary host rebuild.
3. Install local developer wrappers into `~/.local/bin` so `evcode` resolves to this repository.
4. Run status and basic wrapper checks to prove the local usage surface is current and runnable.

## Verification Commands

- `node apps/evcode/bin/evcode.js assemble`
- `bash scripts/install/install_local_wrappers.sh`
- `~/.local/bin/evcode status --json`
- `~/.local/bin/evcode-bench status --json`

## Rollback Rules

- If wrapper installation is incorrect, rewrite the wrappers by re-running the install script.
- No repo cleanup should revert user changes.

## Phase Cleanup Expectations

- No temp artifacts beyond governed proof docs.
- No extra process cleanup expected.
