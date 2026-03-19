# EvCode Live Provider Config Refresh Wave11 Proof

The machine now resolves provider configuration from the repo-local override file `config/assistant-providers.env.local`.

Observed post-refresh state:

- `active_env_source` is `repo_local_override`
- live specialist opt-in is loaded from file
- the local provider env now includes the shared RightCodes API key
- Claude resolves to `https://right.codes/claude-aws`
- Gemini resolves to `https://right.codes/gemini/v1`

Authenticated verification results:

- `codex`: `live_compatible`
- `gemini`: `live_compatible`
- `claude`: `live_probe_failed` with `provider_http_error:403:error code: 1010`

Therefore Gemini is confirmed live-compatible on this machine under the current settings. The remaining provider-level issue is limited to Claude on the `claude-aws` endpoint under the supplied key and probe path.
