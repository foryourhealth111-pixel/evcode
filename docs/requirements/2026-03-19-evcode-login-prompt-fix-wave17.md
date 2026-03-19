# EvCode Login Prompt Fix Wave17 Requirement

## Goal

Fix the current local EvCode standard launcher so running `evcode` does not incorrectly fall through to the Codex login prompt when valid local provider configuration and a usable source Codex config already exist.

## Deliverable

- A root-cause fix for the self-referential source `CODEX_HOME` adoption bug during assembly
- A refreshed standard distribution using the corrected source Codex config
- Verification that the assembled `codex-home/config.toml` carries model provider settings instead of a hooks-only config
- Evidence from a real default launcher invocation or equivalent startup proof

## Constraints

- Apply the smallest fix that addresses the identified root cause.
- Do not remove existing governed runtime hooks.
- Preserve local provider configuration already verified for Gemini/Codex.

## Acceptance Criteria

- The assembly path no longer prefers the current `.evcode-dist/.../codex-home` as the source configuration seed when that would self-copy an incomplete config.
- Reassembled `codex-home/config.toml` includes model/provider settings.
- Default `evcode` startup no longer drops immediately into the generic Codex sign-in screen under the current local setup.
