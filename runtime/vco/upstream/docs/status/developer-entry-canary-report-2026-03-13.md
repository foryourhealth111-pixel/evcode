# Developer Entry Canary Report (2026-03-13)

## Scope

This canary validates the contributor-facing documentation slice only.

It proves that a contributor can now discover the safe contribution path and the
required decision surfaces without touching runtime behavior.

## Canary Journey

### Step 1: Root README to Contributor Guide

Result: `PASS`

The root `README.md` now links directly to `CONTRIBUTING.md`, so contributor
entry is reachable in one hop from the repo root.

### Step 2: Contributor Guide to Zone and Proof Decisions

Result: `PASS`

`CONTRIBUTING.md` links directly to:

- `references/contributor-zone-decision-table.md`
- `references/change-proof-matrix.md`
- `docs/developer-change-governance.md`

That means a contributor can classify both path risk and proof burden without
reading the entire docs tree first.

### Step 3: Docs Index to Contributor Path

Result: `PASS`

`docs/README.md` now exposes the contributor entry path explicitly instead of
only exposing the full governance spine.

### Step 4: Safe-Zone Identification

Result: `PASS`

The contributor path now states the default safe zones clearly:

- `docs/**`
- `references/**` except fixtures
- `scripts/governance/**`
- `scripts/verify/**`
- `templates/**`

### Step 5: Frozen-Surface Escalation Clarity

Result: `PASS`

The contributor path now states that the following are not casual edit targets:

- `install.*`
- `check.*`
- `SKILL.md`
- `protocols/**`
- `scripts/router/**`
- `bundled/**`
- tracked `outputs/**`
- `third_party/**`
- `vendor/**`

### Step 6: Plan Trigger Clarity

Result: `PASS`

The contributor guide and governance doc now say that a plan is required before
editing frozen, cross-zone, runtime-affecting, vendored, mirrored, or
provenance-sensitive surfaces.

## What This Canary Proves

- contributor entry is now explicit
- path risk is compressible into a single decision table
- proof burden is compressible into a single matrix
- the repo no longer depends on unwritten maintainer folklore for the first
  contributor decision

## What This Canary Does Not Claim

This report does not claim completion of:

- GitHub PR template enforcement
- GitHub issue template enforcement
- automated developer-entry gating

Those enforcement surfaces are outside the current owner write scope.
