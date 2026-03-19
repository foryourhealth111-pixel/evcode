# EvCode Gemini Live Verification Wave13 Proof

Gemini was verified on two surfaces.

## 1. Provider Live Probe

`node apps/evcode/bin/evcode.js probe-providers --json --live` reports:

- `codex`: `live_compatible`
- `gemini`: `live_compatible`
- `claude`: `live_probe_failed` with `provider_http_error:403:error code: 1010`

This confirms Gemini is live-compatible on the current machine and key.

## 2. Governed Frontend-Visual Run

A real governed run was executed with run id `wave13-gemini-demo` for the task:

`Design a responsive frontend landing page with typography, spacing, motion, and visual polish`

Top-level run JSON shows:

- `classification.domain`: `frontend_visual`
- `route_kind`: `codex_with_specialists`
- `requested_delegates`: includes `gemini`
- `active_delegates`: includes `gemini`
- active Gemini delegate status: `live_advisory_available`
- `degraded_delegates`: empty
- `suppressed_delegates`: Claude only, with reason `task_not_plan_heavy_enough`

The run also emitted Gemini-specific artifacts:

- `specialists/gemini-task-packet.json`
- `specialists/gemini-request-preview.json`
- `specialists/gemini-result.json`
- `specialists/codex-integration-receipt.json`

Therefore Gemini is not only configured and probe-compatible, but visibly active inside a governed EvCode frontend-visual run on this machine.
