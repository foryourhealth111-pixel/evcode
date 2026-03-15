# Developer Entry Baseline (2026-03-13)

## Scope

This document freezes the contributor-facing entry state before the
post-upstream-governance developer-entry documentation slice is applied.

This baseline is documentation-only. It does not claim runtime drift, only
discoverability and contributor workflow gaps.

## Observed Gaps

### Missing Root Contributor Entry

Before this slice:

- there was no `CONTRIBUTING.md`
- the root `README.md` did not provide a formal contributor entrypoint
- the repo exposed governance documents, but not a guided contributor path

### No Contributor Decision Compression

Before this slice:

- there was no contributor-facing zone decision table
- there was no contributor-facing proof matrix
- change-control expectations lived mainly inside governance prose

### No Developer Journey Evidence

Before this slice:

- there was no developer-entry baseline report
- there was no developer-entry canary report
- there was no explicit "README -> contributor guide -> zone/proof decision"
  path recorded as evidence

## Measured Starting State

- contributor entry file: missing
- contributor zone table: missing
- change proof matrix: missing
- developer-entry status artifacts: missing

## Slice Boundary

This owner slice is limited to contributor-facing documentation surfaces.

It does not claim completion of:

- GitHub PR template enforcement
- GitHub issue template routing
- a dedicated developer-entry gate script

Those are separate enforcement surfaces outside the current write scope.

## Safety Statement

This baseline starts under a runtime freeze:

- no router rewrites
- no install-flow rewrites
- no bundled mirror rewrites
- no runtime ownership transfer

The only target of this slice is a cleaner, faster, safer contributor entry
surface.
