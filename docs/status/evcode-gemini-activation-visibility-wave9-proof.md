# EvCode Gemini Activation Visibility Wave9 Proof

## Fresh Evidence

A fresh governed run using the task:

`Design a responsive frontend landing page with typography, spacing, motion, and visual polish`

produced a runtime summary showing:

- `specialist_routing.classification.domain = frontend_visual`
- `specialist_routing.route_kind = codex_with_specialists`
- `specialist_routing.requested_delegates[0].assistant_name = gemini`
- `specialist_routing.active_delegates = []`
- `specialist_routing.degraded_delegates[0].assistant_name = gemini`
- degraded reason: live specialist invocation is not enabled, so Codex remains the execution path

Current local status also shows:

- `provider_setup.active_env_source = none`
- `assistant_provider_resolution.gemini.api_key_present = false`

Therefore:

1. Gemini is activated by task classification, not by merely mentioning the word “Gemini”.
2. The correct visibility surface is the governed run JSON under `specialist_routing` and the generated specialist artifacts.
3. This machine currently proves request/degraded visibility, but not live Gemini execution, because provider env is not active.
