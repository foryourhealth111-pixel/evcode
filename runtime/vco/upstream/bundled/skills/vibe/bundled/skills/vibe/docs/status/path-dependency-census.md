# Path Dependency Census

Updated: 2026-03-12

## Positioning

This page is a transitional blocker map for the current cleanup program.

It is not a long-term contract surface. It exists to answer one question only:

Which dependency clusters still make blanket delete / move / archive operations unsafe right now?

## Blocker Summary

The repository still contains four dependency clusters that block safe cleanup:

1. nested mirror compatibility
2. tracked output to fixture parity
3. third-party local source roots
4. multi-index docs and script navigation

## Dependency Table

| Dependency Cluster | Current Consumers | Risk | Current Constraint | Safe Migration Direction |
| --- | --- | --- | --- | --- |
| `bundled/skills/vibe/bundled/skills/vibe` | `config/version-governance.json`, `scripts/common/vibe-governance-helpers.ps1`, `scripts/verify/vibe-nested-bundled-parity-gate.ps1`, mirror topology docs | high | runtime contract already allows absence; physical payload has been removed and the remaining constraint is topology-safe absence semantics | keep the optional topology contract, and only materialize on demand if legacy compatibility actually needs it |
| tracked `outputs/**` | `config/outputs-boundary-policy.json`, `references/fixtures/migration-map.json`, `scripts/verify/vibe-output-artifact-boundary-gate.ps1` | high | repo is still `stage2_mirrored`; tracked allowlist parity is currently proven, but strict-mode zero-tracked-outputs has not been adopted | keep mirrored parity green, then enable strict mode only after explicit migration decision |
| `third_party/system-prompts-mirror` | `scripts/research/extract-prompt-signals.ps1`, `scripts/research/generate-vco-suggestions.ps1`, docs examples | high | scripts default to a fixed local mirror path | make source root manifest-driven and parameterizable |
| `third_party/vco-ecosystem-mirror` | `config/upstream-corpus-manifest.json`, registry / curation metadata, mirror-path references, some research flows | medium-high | local mirror is treated as the default evidence source | preserve provenance and manifest, allow external checkout / audit-time fetch |
| docs spine entry files | `docs/README.md`, `docs/plans/README.md`, `docs/releases/README.md`, `config/index.md`, `scripts/README.md`, `scripts/verify/gate-family-index.md`, `references/index.md`, `docs/status/*` | medium | the primary spine has been shortened, but contract pages, receipt pages, and transition pages still need clearer separation | keep collapsing to a shorter canonical spine with clear subordinate indexes |
| dated plan / report materials | `docs/plans/**`, `docs/releases/**`, status and closure history | medium | historical material still shares visibility with active material | move history to archive surfaces while keeping active state in `docs/status/` |

## Notable Hard References

### Nested Mirror

Observed hard references include:

- `config/version-governance.json`
- `scripts/common/vibe-governance-helpers.ps1`
- `scripts/verify/vibe-installed-runtime-freshness-gate.ps1`
- `scripts/verify/vibe-nested-bundled-parity-gate.ps1`
- `config/repo-cleanliness-policy.json`
- `config/execution-context-status.json`

This used to make nested mirror deletion unsafe. With `require_nested_bundled_root = false`, optional `presence_policy`, and absence-aware gates, the physical payload can now stay absent without regressing runtime/install/release behavior.

### Outputs Boundary

Observed hard references include:

- `config/outputs-boundary-policy.json`
- `references/fixtures/migration-map.json`
- `scripts/verify/vibe-output-artifact-boundary-gate.ps1`
- `references/fixtures/README.md`
- `docs/output-artifact-boundary-governance.md`

This is why `outputs/**` cannot be zeroed until policy is explicitly moved out of `stage2_mirrored`.

### Third-Party Source Roots

Observed hard references include:

- `scripts/research/extract-prompt-signals.ps1`
- `scripts/research/generate-vco-suggestions.ps1`
- `config/upstream-corpus-manifest.json`
- `config/candidate-curation-policy.json`
- `config/tool-registry.json` mirror-path metadata
- docs and verify README examples that still point to local mirrors

This is why third-party shrinkage must be parameterized, not just deleted.

## Current Migration Order

The order below is a current recommendation for safe sequencing. It is not a standing contract and may change once the next blocker is cleared.

1. docs and status spine completion
2. operator dry run + closure audit
3. nested compatibility contract stabilization
4. third-party source-root parameterization
5. outputs strict-mode decision
6. archive / prune window

## Cross-Document Boundary

- blocker sequencing lives in [`roadmap.md`](roadmap.md)
- proof requirements live in [`non-regression-proof-bundle.md`](non-regression-proof-bundle.md)
- protected surfaces live in [`protected-capability-baseline.md`](protected-capability-baseline.md)
- runtime summary lives in [`current-state.md`](current-state.md)
