# Provider Runtime

This package owns provider-family policy and distribution-specific defaults.

MCP is treated as a capability transport, not as a second orchestrator.

It also owns assistant-provider defaults for the Codex/Claude/Gemini specialist pipeline without storing live credentials in tracked files.

Canonical user setup surface:

- guide: `docs/configuration/openai-compatible-provider-setup.md`
- portable config filename: `assistant-providers.env`
- repo example file: `config/assistant-providers.env.example`
- repo-local development override: `config/assistant-providers.env.local`

Portable user configuration is resolved outside the repo checkout by default. The repo-local file remains a source-mode compatibility override for contributors.
