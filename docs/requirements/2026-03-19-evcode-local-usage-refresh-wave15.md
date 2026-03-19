# EvCode Local Usage Refresh Wave15 Requirement

## Goal

Refresh the current repository version of EvCode into the local usage surface so it can be tested directly from the machine command line.

## Deliverable

- Refreshed local standard distribution artifacts, if needed for current checkout usage
- Installed or refreshed local developer wrappers for `evcode` and `evcode-bench`
- Verification evidence showing the local commands resolve to the current checkout and remain runnable

## Constraints

- Do not overwrite unrelated user files outside the documented local wrapper install location.
- Prefer the minimal sufficient update path over a full rebuild if the current host build already exists.
- Preserve current repo-local provider configuration and governed runtime behavior.

## Acceptance Criteria

- `~/.local/bin/evcode` and `~/.local/bin/evcode-bench` point at this checkout.
- The local usage surface can run `evcode status --json` successfully.
- The refreshed local surface is documented with exact test commands.
