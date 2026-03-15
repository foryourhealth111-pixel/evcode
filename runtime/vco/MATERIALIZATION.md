# VCO Runtime Materialization

## Selected Source

- upstream: `foryourhealth111-pixel/vco-skills-codex`
- version target: `v2.3.43`
- materialized snapshot: `runtime/vco/upstream`

## Required Runtime Surfaces

EvCode depends on these runtime families remaining present:

- `protocols/`
- `config/`
- `scripts/runtime/`
- `scripts/verify/`
- `docs/releases/`
- `docs/requirements/`

These surfaces are tracked through:

- `runtime/vco/required-runtime-markers.json`
- `runtime/vco/freshness.json`
- `runtime/vco/materialization.json`
