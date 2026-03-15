# Roadmap

Updated: 2026-03-12

## Positioning

This page is the current sequencing map for the closure program.

It answers:

1. which track is active now;
2. which heavier tracks are explicitly deferred;
3. what must become true before the program can claim closure.

It is not the proof contract, not the guardrail matrix, and not the blocker census.

## Operating Rule

Every cleanup batch is executed under a single rule:

**no proof, no prune**

That means no unproven prune, no tracked output purge, no third-party externalization, and no bulk archive move until the affected replacement path exists and the relevant proof bundle turns green again.

## Active Track

The repository is in **closure mode**, not expansion mode.

That means the current priority is:

1. keep the proof bundle green
2. keep temp/runtime/operator noise at zero
3. collapse active navigation onto the current status spine
4. only reopen heavier cleanup tracks with explicit migration proof

## Current Closure Track

### Closure 1: Docs Spine and Batch Hygiene

Goal: make the current cleanup state readable, bounded, and operator-safe.

- align `config/index.md` and `references/index.md` to the active 2026-03-11 remediation plan
- keep `docs/status/*` as the single live status surface
- standardize phase-end hygiene through `scripts/governance/phase-end-cleanup.ps1`
- write `operator-dry-run.md` and `closure-audit.md`

## Deferred Explicit Tracks

### Batch A: Baseline and Spine

Goal: make the current state explicit and trustworthy before touching runtime structure.

- create `docs/status/*`
- repair `docs/README.md`
- repair `scripts/README.md`
- define the non-regression proof bundle
- record protected capability and path dependency baselines

### Batch B: Nested Compatibility Softening

Goal: turn `nested_bundled` from a permanently tracked mirror into an explicit compatibility layer.

- soften `require_nested_bundled_root`
- update version / packaging / runtime docs and config
- make install / check / runtime flows accept generated-or-optional nested layouts

### Batch C: Output Boundary Completion

Goal: finish the move from tracked legacy outputs to governed fixtures / ledgers.

- restore fixture parity
- close gaps in `migration-map.json`
- remove remaining dual-source ambiguity between `outputs/**` and `references/fixtures/**`
- switch to strict mode only after parity is proven

### Batch D: Third-Party Decoupling

Goal: preserve research / audit flows while shrinking the repo's always-tracked third-party burden.

- parameterize `-SourceRoot`
- resolve source roots from manifest instead of fixed local paths
- keep provenance / license / manifest surfaces tracked
- stop requiring heavy local mirrors for normal repo operation

### Batch E: Archive and Log Normalization

Goal: reduce active file count without losing real history.

- move obsolete dated materials into archive surfaces
- keep only current state, roadmap, and ledgers in the active surface
- normalize repeated report classes into one ledger + one human summary

### Batch F: Proof Re-Green and Dry Run

Goal: prove the repository is cleaner and still behaviorally intact.

- rerun the critical proof bundle
- perform operator dry run from canonical root
- write closure audit

## Current Truth

- the critical proof bundle is green
- the repo is **not** globally zero-dirty
- remaining pressure is still concentrated in managed backlog and high-risk mirror surfaces
- therefore the alpha-to-omega program is **not closed**, but the current closure batch can finish once the status spine and operator receipts are complete

## Cross-Document Boundary

- proof contract lives in [`non-regression-proof-bundle.md`](non-regression-proof-bundle.md)
- guardrail matrix lives in [`protected-capability-baseline.md`](protected-capability-baseline.md)
- blocker map lives in [`path-dependency-census.md`](path-dependency-census.md)
- runtime summary lives in [`current-state.md`](current-state.md)

## Exit Conditions

The program is only closed when all of the following are true:

- the active docs spine is short and trusted
- `nested_bundled` remains an optional topology contract and does not return as a permanent tracked burden
- tracked `outputs/**` are reduced to zero under strict mode
- third-party heavy roots are no longer a default repo burden
- the critical proof bundle is green
