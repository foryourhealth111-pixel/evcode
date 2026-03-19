# EvCode Portable API Config Wave16 Requirement

## Goal

Configure the EvCode API/provider settings into the machine-local portable config surface so local usage does not depend solely on the repository-local env override.

## Deliverable

- A populated portable provider env file under the resolved EvCode config root
- Verification that `evcode` resolves provider settings from the portable surface
- Proof artifacts documenting the configured machine-local API surface

## Constraints

- Do not commit secrets into tracked files.
- Preserve the existing provider values that were already verified locally.
- Keep the repo-local file intact unless a later cleanup explicitly removes it.

## Acceptance Criteria

- `~/.config/evcode/assistant-providers.env` exists.
- `evcode status --json` shows the portable config path is present and selected by precedence.
- `evcode probe-providers --json --live` still confirms the same live provider behavior.
