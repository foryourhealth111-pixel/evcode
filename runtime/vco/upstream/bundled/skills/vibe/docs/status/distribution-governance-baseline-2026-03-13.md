# Distribution Governance Baseline (2026-03-13)

## Scope

This document freezes the pre-rollout baseline for distribution governance work.

It records the measured state before registry/disclosure/provenance closure changes are applied.

## Measured Truth Surfaces

- `config/upstream-lock.json`
  - runtime/distribution upstream registry
  - 22 dependencies
- `config/upstream-corpus-manifest.json`
  - corpus/value-extraction registry
  - 19 entries
- `THIRD_PARTY_LICENSES.md`
  - public disclosure surface
  - 13 listed upstreams before closure

Union count across these surfaces: 39 upstream sources.

## Verified Gaps

### Disclosure Drift

`THIRD_PARTY_LICENSES.md` was missing multiple upstreams already present in `config/upstream-lock.json`, which meant public disclosure lagged behind the canonical runtime/distribution registry.

### Non-Canonicalized Public Sources

These sources were disclosed publicly but were not represented in the canonical registries:

- `SynkraAI/aios-core`
- `x1xhlol/system-prompts-and-models-of-ai-tools`
- `muratcankoylan/Agent-Skills-for-Context-Engineering`

### Provenance Gap

Before this rollout:

- there was no `ORIGIN.md` template
- there was no `vendor/**` contract
- there was no provenance gate

### Freshness Placeholder Gap

`config/upstream-corpus-manifest.json` still contained `HEAD_FROM_UPSTREAM_LOCK` placeholder values for:

- `agent-s`
- `browser-use`
- `letta`
- `mem0`

These are left for the repo-convergence phase to close because they affect cross-surface closure and bundled parity sequencing.

## Runtime Freeze Statement

This baseline was captured under a runtime freeze:

- no router contract changes
- no install/check behavior changes
- no bundled runtime ownership changes

## Evidence Paths

- `outputs/verify/vibe-upstream-corpus-manifest-gate.json`
- `outputs/verify/vibe-version-packaging-gate.json`
- `outputs/verify/vibe-repo-cleanliness-gate.json`
- `outputs/verify/vibe-output-artifact-boundary-gate.json`
