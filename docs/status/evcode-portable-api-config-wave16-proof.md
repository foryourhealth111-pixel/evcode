# EvCode Portable API Config Wave16 Proof

The machine-local portable provider config was created at:

- `~/.config/evcode/assistant-providers.env`

The file was written with the current verified provider settings and locked to user-only permissions (`0600`).

Configured portable surface:

- live specialists opt-in enabled
- Codex base URL: `https://right.codes/codex/v1`
- Claude base URL: `https://right.codes/claude-aws`
- Gemini base URL: `https://right.codes/gemini/v1`

Verification through the local `evcode` command shows the portable file now wins precedence over the repo-local fallback:

- `active_env_source`: `portable_user_config`
- `resolved_local_env_path`: `/home/lqf/.config/evcode/assistant-providers.env`

Authenticated live probe through the local command surface reports:

- `codex`: `live_compatible`
- `gemini`: `live_compatible`
- `claude`: `live_probe_failed` with `provider_http_error:403:error code: 1010`

Therefore the API is now configured in the machine-local EvCode usage surface, not only inside the repository-local development override.
