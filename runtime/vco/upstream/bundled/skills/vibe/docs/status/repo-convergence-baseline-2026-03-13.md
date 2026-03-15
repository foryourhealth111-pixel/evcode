# Repo Convergence Baseline (2026-03-13)

## Scope

This document freezes the post-upstream-governance repo state before
convergence repair begins.

The target of this phase is not new functionality. The target is a cleaner,
more auditable repository with no runtime regression.

## Baseline Failures

### Output Artifact Boundary

`outputs/verify/vibe-output-artifact-boundary-gate.json` is `FAIL`.

The failure is narrow and deterministic:

- `outputs/external-corpus/external-corpus-gate.md`
  vs `references/fixtures/external-corpus/external-corpus-gate.md`
- `outputs/external-corpus/vco-suggestions.md`
  vs `references/fixtures/external-corpus/vco-suggestions.md`

All other mirrored pairs already match.

### Version Packaging Parity

`outputs/verify/vibe-version-packaging-gate.json` is `FAIL`.

Current bundled drift is concentrated in `docs/`:

- files only in canonical:
  - `docs/developer-change-governance.md`
  - `docs/plans/2026-03-13-distribution-governance-plan.md`
  - `docs/plans/2026-03-13-post-upstream-governance-developer-entry-plan.md`
  - `docs/plans/2026-03-13-post-upstream-governance-repo-convergence-plan.md`
- files differing between canonical and bundled:
  - `docs/README.md`
  - `docs/plans/README.md`

### Upstream Mirror Freshness

`outputs/verify/vibe-upstream-mirror-freshness-gate.json` is `FAIL`.

The required freshness root exists, but it is missing four manifest slugs:

- `agent-s`
- `browser-use`
- `letta`
- `mem0`

### Router Contract

`outputs/verify/vibe-router-contract-gate.json` was already red before this
phase. It is treated as a standing baseline issue and must not worsen during
convergence.

## Baseline Safety Statement

This phase starts under the following constraints:

- no router rewrites
- no install-flow rewrites
- no runtime ownership transfer
- no feature additions
- only canonical-first cleanup, parity, fixture, registry, and mirror repair

## Expected Convergence Sequence

1. repair external-corpus fixture drift
2. close manifest placeholder heads and mirror inventory gaps
3. sync bundled mirror from canonical
4. rerun repo and runtime proof gates
5. emit closure report with explicit non-regression claims
