# EvCode Gemini Live Verification Wave13 Requirement

## Goal

Verify the Gemini side specifically under the current live configuration.

## Deliverable

- Fresh Gemini live-probe evidence
- A governed `frontend_visual` run artifact showing whether Gemini is requested and/or active in specialist routing
- A concise conclusion about Gemini provider health and Gemini routing visibility

## Constraints

- Ignore Claude for this wave unless it appears as a suppressed or failed non-target delegate.
- Keep Codex as final executor and Gemini advisory-only.
- Preserve governed traceability and proof artifacts.

## Acceptance Criteria

- `probe-providers --json --live` confirms the current Gemini provider state.
- `evcode run --task ... --json` for a frontend-visual task produces machine-readable routing evidence.
- The final proof states whether Gemini is merely configured, truly live-compatible, and visibly requested/active in a governed run.
