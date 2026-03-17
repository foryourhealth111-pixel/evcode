# Contributing to VCO Skills Codex

This repository is open to contributions, but it is not an "edit anywhere"
repo.

`vco-skills-codex` contains runtime entrypoints, routing policy, bundled
mirrors, provenance records, release evidence, and contributor-safe governance
surfaces. The first job of a contributor is to choose the correct surface
before making a change.

## Start Here

1. Read the zone table:
   [`references/contributor-zone-decision-table.md`](references/contributor-zone-decision-table.md)
2. Classify your change with the proof matrix:
   [`references/change-proof-matrix.md`](references/change-proof-matrix.md)
3. Read the formal change-control rules if your change is not obviously
   docs-only:
   [`docs/developer-change-governance.md`](docs/developer-change-governance.md)
4. If your change touches a frozen or guarded surface, stop and write or attach
   a plan before editing:
   [`docs/plans/2026-03-13-post-upstream-governance-developer-entry-plan.md`](docs/plans/2026-03-13-post-upstream-governance-developer-entry-plan.md)

## Default Safe Contribution Path

If you are not sure where to work, stay in the additive contributor-safe zones:

- `docs/**`
- `references/**`, except `references/fixtures/**`
- `scripts/governance/**`
- `scripts/verify/**`
- `templates/**`

These surfaces are the preferred place to add documentation, governance
contracts, verification gates, and operator guidance without changing runtime
behavior.

## Do Not Edit These Surfaces Casually

Do not directly edit these paths unless your change explicitly owns the plan and
proof burden:

- `install.ps1`
- `install.sh`
- `check.ps1`
- `check.sh`
- `SKILL.md`
- `protocols/**`
- `scripts/router/**`
- `bundled/**`
- tracked `outputs/**`
- `third_party/**`
- `vendor/**`

Those areas either control runtime behavior directly or represent mirrored,
generated, vendored, or compliance-sensitive content.

## Choose Your Change Class

### Docs-only

Use this class when you are changing explanatory docs, reference guides, plans,
or governance text without changing runtime behavior.

Start with:

- [`docs/README.md`](docs/README.md)
- [`references/contributor-zone-decision-table.md`](references/contributor-zone-decision-table.md)
- [`references/change-proof-matrix.md`](references/change-proof-matrix.md)

### Governance or Policy

Use this class when you change public promises, repo rules, gate definitions, or
machine-readable policy surfaces.

Always read:

- [`docs/developer-change-governance.md`](docs/developer-change-governance.md)
- [`docs/distribution-governance.md`](docs/distribution-governance.md)
- [`docs/repo-cleanliness-governance.md`](docs/repo-cleanliness-governance.md)

### Mirror, Fixture, Provenance, or Compliance

Use this class when you touch:

- `bundled/**`
- `references/fixtures/**`
- tracked `outputs/**`
- `third_party/**`
- `vendor/**`

These changes are never mirror-first. The canonical source must change first,
then sync and proof must follow.

### Runtime-affecting

Use this class when you touch install flow, routing, protocols, packaged
behavior, or anything that changes default runtime ownership.

These changes require a plan before implementation and a stronger proof bundle
before completion.

## When a Plan Is Mandatory

Write or attach a plan before editing if any of the following are true:

- you are changing a `Z0` frozen control-plane file
- you are changing multiple zones in one task
- you are changing install, check, router, protocol, or packaging behavior
- you are changing vendored, mirrored, provenance, or disclosure surfaces
- you cannot explain the required proof set before you start editing

The current program plan for developer entry is:

- [`docs/plans/2026-03-13-post-upstream-governance-developer-entry-plan.md`](docs/plans/2026-03-13-post-upstream-governance-developer-entry-plan.md)

## Minimum Proof Expectation

Use the proof matrix for the exact path, but the default floor is:

- docs-only changes: `git diff --check` plus link and navigation sanity
- governance changes: relevant gates plus updated documentation
- guarded or runtime-sensitive changes: explicit proof bundle with
  `Command -> Output -> Claim` evidence

The matrix is here:

- [`references/change-proof-matrix.md`](references/change-proof-matrix.md)

## Stop and Escalate

Stop and escalate instead of guessing if any of these are true:

- you are about to edit `bundled/**` as if it were the source of truth
- you are about to hand-edit tracked `outputs/**`
- you cannot identify the canonical source for a mirrored file
- you are touching `third_party/**` or `vendor/**` without provenance and
  disclosure updates
- you do not know which gates must pass before you claim non-regression

## Useful Navigation

- repo docs index:
  [`docs/README.md`](docs/README.md)
- formal change-control rules:
  [`docs/developer-change-governance.md`](docs/developer-change-governance.md)
- contributor zone table:
  [`references/contributor-zone-decision-table.md`](references/contributor-zone-decision-table.md)
- change proof matrix:
  [`references/change-proof-matrix.md`](references/change-proof-matrix.md)
- developer entry baseline:
  [`docs/status/developer-entry-baseline-2026-03-13.md`](docs/status/developer-entry-baseline-2026-03-13.md)
- developer entry canary:
  [`docs/status/developer-entry-canary-report-2026-03-13.md`](docs/status/developer-entry-canary-report-2026-03-13.md)
- developer entry closure:
  [`docs/status/developer-entry-closure-report-2026-03-13.md`](docs/status/developer-entry-closure-report-2026-03-13.md)

## Scope Note

This contributor guide is the human entry surface for the developer-entry
rollout. Formal enforcement evidence for templates, gating, and non-regression
proof lives in the dated status reports under `docs/status/`.
