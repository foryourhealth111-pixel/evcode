# Repo Convergence Closure Report (2026-03-13)

## Scope

This report closes the repo-convergence phase only.

It does not claim full repository completion.
It does not claim installed runtime freshness closure.
It does not claim developer-entry completion.

The purpose of this phase was to repair the canonical navigation surface,
close already-identified fixture and upstream-governance gaps, sync bundled
mirrors from canonical, and prove that those repairs did not introduce a new
runtime-facing regression.

## Completed in This Phase

- repaired the canonical documentation and script navigation surfaces so the
  main repo entry points are readable and discoverable again
- repaired the broken `references/index.md` planning-board link by pointing it
  at the real execution-board artifact
- closed the external-corpus fixture drift so output/fixture mirrored pairs are
  hash-aligned again
- closed upstream manifest and mirror freshness gaps so the upstream corpus
  registry is now fully canonicalized at the manifest/gate layer
- synced the bundled mirrors from canonical so version packaging parity is
  green before developer-entry work continues

## Verified Results

### Output Artifact Boundary

- Command:
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify\vibe-output-artifact-boundary-gate.ps1 -WriteArtifacts`
- Output:
  `gate_result = PASS`, `fixture_hash_mismatches = 0`, `failures = 0`
- Claim:
  output and fixture mirrors are aligned again; the previously failing
  external-corpus markdown drift has been closed

### Version Packaging Parity

- Command:
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify\vibe-version-packaging-gate.ps1 -WriteArtifacts`
- Output:
  `gate_result = PASS`, `assertions.failed = 0`
- Claim:
  canonical and bundled packaging surfaces are in parity for the release
  contract checked by this gate

### Nested Bundled Parity

- Command:
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify\vibe-nested-bundled-parity-gate.ps1 -WriteArtifacts`
- Output:
  `gate_result = PASS`
- Claim:
  the nested bundled mirror remained aligned after the canonical-first edits

### Upstream Corpus Manifest

- Command:
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify\vibe-upstream-corpus-manifest-gate.ps1 -WriteArtifacts`
- Output:
  `gate_result = PASS`, `summary.expected_entries = 19`,
  `summary.actual_entries = 19`, `summary.failure_count = 0`
- Claim:
  upstream corpus registry closure is now in place at the manifest layer;
  the earlier placeholder-head and registry closure concerns are no longer red
  in this gate

### Upstream Mirror Freshness

- Command:
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify\vibe-upstream-mirror-freshness-gate.ps1 -WriteArtifacts`
- Output:
  `gate_result = PASS`, `failed_assertions = 0`
- Claim:
  the required freshness root is fully covered and head-aligned for the
  manifest inventory used by this gate

### Pack Routing Smoke

- Command:
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify\vibe-pack-routing-smoke.ps1 -WriteArtifacts`
- Output:
  summary artifact written with no recorded failure
- Claim:
  convergence-phase documentation, fixture, and governance cleanup did not
  break the routing smoke surface

### Release/Install Runtime Coherence

- Command:
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify\vibe-release-install-runtime-coherence-gate.ps1 -WriteArtifacts`
- Output:
  `gate_result = PASS`
- Claim:
  the release/install/runtime coherence contract checked by this gate did not
  regress during repo convergence

## Expected Red Items Still Open

### Router Contract

- Command:
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify\vibe-router-contract-gate.ps1 -WriteArtifacts`
- Output:
  `gate_passed = false`, `strict_equality_rate = 0.9000`,
  only mismatch case = `low-signal`
- Claim:
  router-contract remains a pre-existing baseline red item; repo convergence
  did not close it and did not widen it beyond the known low-signal mismatch

### Installed Runtime Freshness

- Command:
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify\vibe-installed-runtime-freshness-gate.ps1 -WriteArtifacts`
- Output:
  `gate_result = FAIL`
- Claim:
  installed runtime freshness is intentionally deferred to the final
  version-governance and sync phase; this report makes no claim that local
  installed runtime is already converged to repo latest

### Repo Cleanliness

- Command:
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify\vibe-repo-cleanliness-gate.ps1 -WriteArtifacts`
- Output:
  `gate_result = FAIL`, `managed_workset_visible = 32`,
  `high_risk_managed_visible = 60`, `other_dirty_visible = 4`
- Claim:
  repo cleanliness is still intentionally red because the next phases remain
  open and four provenance-skeleton paths are still uncategorized:
  `templates/ORIGIN.md.tmpl`, `vendor/README.md`, `vendor/mirrors/.gitkeep`,
  `vendor/upstreams/.gitkeep`

## Stability Verdict

Current verdict: `stable_with_deferred_nonruntime_backlog`

This verdict is justified because:

- the canonical convergence repairs that were in scope are now green on their
  direct gates
- packaging parity and release/install/runtime coherence gates remained green
- no new runtime-facing regression was introduced by the repo-convergence edits
- remaining red items are explicit, bounded, and already assigned to later
  phases rather than being hidden as accidental drift

## Next Phase Hand-off

The next phase is developer-entry implementation.

That phase must:

- convert governance rules into a formal contributor-facing entry system
- add templates and a developer-entry verification gate
- absorb the remaining provenance skeleton paths into governed repo state
- keep routing/runtime/install proof at least as strong as it is at the end of
  this report

The final version-governance phase after that must:

- synchronize local repo, local installed runtime, and GitHub latest
- turn `vibe-installed-runtime-freshness-gate` green
- complete the repo cleanliness closure
