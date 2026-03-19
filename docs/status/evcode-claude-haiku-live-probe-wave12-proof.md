# EvCode Claude Haiku Live Probe Wave12 Proof

A temporary process-local override was used:

- `EVCODE_CLAUDE_MODEL=claude-haiku-4-5`
- endpoint remained `https://right.codes/claude-aws`
- shared RightCodes API key remained unchanged

Authenticated live probe result:

- `codex`: `live_compatible`
- `gemini`: `live_compatible`
- `claude`: `live_probe_failed` with `provider_http_error:403:error code: 1010`

Comparison to the prior `claude-opus-4-6` run shows the same Claude failure mode and same error code.

Therefore the current Claude live-probe failure is not explained by the `claude-opus-4-6` model choice alone. Under the current endpoint, key, and probe path, the failure persists when switching to `claude-haiku-4-5`.
