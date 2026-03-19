# EvCode Claude Haiku Live Probe Wave12 Requirement

## Goal

Test whether the Claude live probe succeeds on the `https://right.codes/claude-aws` endpoint when the Claude model is temporarily switched from `claude-opus-4-6` to `claude-haiku-4-5`.

## Deliverable

- A controlled live probe result for Claude using `claude-haiku-4-5`
- A comparison against the prior `claude-opus-4-6` result
- Governed proof artifacts for this validation turn

## Constraints

- Do not change the tracked assistant policy for this experiment.
- Do not persist the haiku model override into tracked files unless explicitly requested.
- Keep Codex as final executor and specialists advisory-only.

## Acceptance Criteria

- The probe is run with a temporary Claude model override.
- The resulting Claude status and reason are recorded.
- The conclusion clearly states whether the issue is model-specific or persists across Claude models on the current endpoint.
