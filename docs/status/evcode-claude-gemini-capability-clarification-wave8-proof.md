# EvCode Claude Gemini Capability Clarification Wave8 Proof

Fresh local evidence shows that EvCode is configured to route work to Claude and Gemini as governed advisory specialists, but those providers are part of the EvCode runtime layer rather than native built-in tools of the current Codex chat environment.

Key facts established in this wave:

1. `evcode status --json` reports assistants `codex`, `claude`, and `gemini` and exposes provider routing metadata.
2. The standard assistant policy enables Claude and Gemini with advisory-only authority and OpenAI-style chat-completions transport.
3. The CLI bridges `evcode run` into the governed Python runtime rather than exposing Claude/Gemini as direct top-level tools of this chat session.
4. Current local provider setup is not live-ready because `provider_setup.active_env_source = none` and `api_key_present = false` in the fresh status output.

Therefore the earlier answer was describing the current assistant session boundary, not the EvCode product runtime boundary.
