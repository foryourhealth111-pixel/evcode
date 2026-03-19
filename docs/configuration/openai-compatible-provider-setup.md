# OpenAI-Compatible Provider Setup

## What This Setup Covers

EvCode supports a governed, OpenAI-style assistant-provider surface for:

- Codex as the final executor
- Claude as an advisory specialist for documentation, requirements, and project design
- Gemini as an advisory specialist for visual and front-end design

The current portability claim remains intentionally bounded:

- primary wire format: `chat/completions`
- secondary support: tolerant parsing for `responses`-style payloads when a provider actually behaves that way
- currently live-validated scope: RightCodes Codex / Claude / Gemini endpoints configured through EvCode

Do not read this as a blanket guarantee that every OpenAI-compatible vendor behaves identically. EvCode keeps governed defaults and verification because provider-specific differences still exist.

## Primary User Setup Surface

For broad distribution and cross-machine use, the primary user config is now a portable file outside the repo checkout.

Default portable config roots:

- Linux: `${XDG_CONFIG_HOME:-~/.config}/evcode/assistant-providers.env`
- macOS: `~/Library/Application Support/EvCode/assistant-providers.env`
- Windows: `%APPDATA%/EvCode/assistant-providers.env`

Optional override:

- set `EVCODE_CONFIG_ROOT` to choose a different portable config directory
- set `EVCODE_PROVIDER_ENV_FILE` to point at one exact env file

## Source-Mode Development Override

Repo-local config is still supported for contributors running EvCode from source:

- repo-local development override: `config/assistant-providers.env.local`
- example file: `config/assistant-providers.env.example`

This repo-local file is now a compatibility override for source-mode development, not the primary user-facing portable setup surface.

## Precedence Rules

Resolution order is:

1. explicit shell environment variables
2. `EVCODE_PROVIDER_ENV_FILE`
3. portable user config file under the resolved config root
4. repo-local `config/assistant-providers.env.local`
5. tracked defaults in `config/assistant-policy.standard.json` or `config/assistant-policy.benchmark.json`

This keeps secrets out of tracked files while avoiding any requirement that the product live in one fixed checkout path.

## Recommended Portable File

```env
# Enable live advisory specialists in the standard channel.
EVCODE_ENABLE_LIVE_SPECIALISTS=1

# Shared credential for the current RightCodes distributor paths.
EVCODE_RIGHTCODES_API_KEY=replace-with-live-key

# Codex executor
EVCODE_CODEX_BASE_URL=https://right.codes/codex/v1
EVCODE_CODEX_MODEL=gpt-5.4

# Claude advisory specialist
EVCODE_CLAUDE_BASE_URL=https://right.codes/claude-aws
EVCODE_CLAUDE_MODEL=claude-opus-4-6

# Gemini advisory specialist
EVCODE_GEMINI_BASE_URL=https://right.codes/gemini/v1
EVCODE_GEMINI_MODEL=gemini-2.5-pro
```

## Status And Discovery

To inspect the resolved setup surface:

```bash
node apps/evcode/bin/evcode.js status --json
node apps/evcode/bin/evcode.js doctor
node apps/evcode-bench/bin/evcode-bench.js status --json
```

These surfaces now expose:

- the repo-local compatibility file path
- the portable config root
- the portable env file path
- the resolved file actually used for the run
- the active env source kind
- whether the selected file was loaded
- which keys came from the selected file
- the current assistant API compatibility summary
- the resolved base URL and model for each assistant

## Probe Command

Use the built-in probe when you want a compact compatibility check against the currently resolved provider settings.

```bash
node apps/evcode/bin/evcode.js probe-providers --json
node apps/evcode/bin/evcode.js probe-providers --json --live
node apps/evcode-bench/bin/evcode-bench.js probe-providers --json
```

Behavior:

- without `--live`, the command reports whether each assistant is configured, gated, or suppressed
- with `--live`, the command performs a minimal advisory request against assistants whose configuration is sufficient for live probing
- benchmark output still reflects benchmark policy suppression for advisory specialists

## Safety Notes

- Do not commit `config/assistant-providers.env.local`.
- Do not put live keys into markdown, JSON policy files, or tracked test fixtures.
- Keep Codex as the final executor even when Claude or Gemini are live-enabled.
- Benchmark rollout policy may still suppress advisory specialists even when local credentials are present.
