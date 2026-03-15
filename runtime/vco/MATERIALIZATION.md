# VCO Runtime Materialization

## Selected Source

- upstream: `foryourhealth111-pixel/vco-skills-codex`
- version target: `v2.3.47`
- materialized snapshot: `runtime/vco/upstream`

## Required Runtime Surfaces

EvCode depends on these runtime families remaining present:

- top-level runtime entry files
- `adapters/`
- `agents/`
- `bundled/`
- `protocols/`
- `config/`
- `core/`
- `dist/`
- `hooks/`
- `mcp/`
- `references/`
- `rules/`
- `schemas/`
- `scripts/common/`
- `scripts/router/`
- `scripts/runtime/`
- `scripts/verify/`
- `docs/`
- `templates/`
- `third_party/`
- `vendor/`

These surfaces are tracked through:

- `runtime/vco/required-runtime-markers.json`
- `runtime/vco/freshness.json`
- `runtime/vco/materialization.json`
