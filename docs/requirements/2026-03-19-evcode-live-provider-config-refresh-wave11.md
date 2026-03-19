# EvCode Live Provider Config Refresh Wave11 Requirement

## Goal

Refresh the local provider configuration to reflect the current live RightCodes reality: Gemini is available, and Claude should use `https://right.codes/claude-aws` instead of the older Claude endpoint.

## Deliverable

- A repo-local provider override file for source-mode development
- Updated tracked example and setup documentation so the recommended Claude URL matches the current live endpoint
- Fresh status and provider probe evidence describing the post-refresh machine state

## Constraints

- Preserve Codex as the final executor and keep specialists advisory-only.
- Do not commit secrets.
- Use repo-local or portable env surfaces only; do not hardcode live credentials into tracked JSON policy files.
- Verification must be evidence-backed.

## Acceptance Criteria

- `config/assistant-providers.env.local` exists and enables live specialists without exposing a real key in git history.
- Tracked setup guidance points Claude at `https://right.codes/claude-aws`.
- `status` reflects the local env source after refresh.
- `probe-providers` is rerun and its outcome is documented, including any remaining blocker if no key is present.

## Non-Goals

- No change to authority tier policy.
- No benchmark policy changes.
- No claim of live compatibility without a successful authenticated probe.
