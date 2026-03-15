# Codex Host Upstream

## Selected Source

- upstream: `stellarlinkco/codex`
- remote: `https://github.com/stellarlinkco/codex`
- branch: `main`

## Materialization Policy

EvCode does not treat this host as an opaque binary dependency.
It materializes a pinned upstream snapshot under:

- `vendor/codex-host/upstream`

The selected source commit is tracked in:

- `config/sources.lock.json`
- `vendor/codex-host/materialization.json`

## Why This Host

- it exposes native hook surfaces
- it preserves Codex-native UX
- it reduces the amount of EvCode-specific host patching required
