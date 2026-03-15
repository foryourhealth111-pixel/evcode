# Developer Entry Closure Report (2026-03-13)

## Scope

This report closes the developer-entry phase only.

It does not claim final installed-runtime freshness closure.
It does not claim final GitHub sync closure.
It does not claim router-contract repair.

The purpose of this phase was to convert the post-upstream-governance rules into
an explicit contributor-entry system with:

- a root contributor entry
- safe-zone and proof-burden decision surfaces
- GitHub issue / PR templates for governed change intake
- a dedicated developer-entry verification gate
- a canary contributor journey proving the path is usable

## Completed in This Phase

- established `CONTRIBUTING.md` as the root contributor entry surface
- added explicit zone and proof references so contributors can classify change
  risk before touching runtime-critical areas
- added developer-facing GitHub templates under `.github/`
- added `references/developer-entry-contract.md` and
  `scripts/verify/vibe-developer-entry-gate.ps1`
- added baseline and canary reports for the developer-entry rollout
- kept canonical-first governance intact so bundled parity can still be synced
  from canonical after contributor-surface changes

## Verified Results

### Developer Entry Gate

- Command:
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify\vibe-developer-entry-gate.ps1 -WriteArtifacts`
- Output:
  `gate_result = PASS`, `summary.failures = 0`
- Claim:
  the contributor-entry contract is now wired end-to-end: root README links to
  `CONTRIBUTING.md`, the contributor guide links to zone/proof/governance
  surfaces, and the required marker groups are present

### Contributor Journey Canary

- Evidence:
  `docs/status/developer-entry-canary-report-2026-03-13.md`
- Output:
  all recorded canary steps are `PASS`
- Claim:
  a contributor can now discover the default safe contribution path without
  relying on maintainer folklore

### GitHub Template Surface

- Command:
  `python -c "from pathlib import Path; import yaml; [yaml.safe_load(p.read_text(encoding='utf-8')) for p in Path('.github/ISSUE_TEMPLATE').glob('*.yml')]; print('issue-template-yaml=PASS')"`
- Output:
  `issue-template-yaml=PASS`
- Claim:
  the structured issue intake forms are syntactically valid and ready to act as
  governed contributor-entry surfaces

### Output Artifact Boundary

- Command:
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify\vibe-output-artifact-boundary-gate.ps1 -WriteArtifacts`
- Output:
  `gate_result = PASS`
- Claim:
  the developer-entry work did not reintroduce fixture/output drift

### Version Packaging Parity

- Command:
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify\vibe-version-packaging-gate.ps1 -WriteArtifacts`
- Output:
  `gate_result = PASS`
- Claim:
  developer-entry changes preserved packaging parity expectations

### Nested Bundled Parity

- Command:
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify\vibe-nested-bundled-parity-gate.ps1 -WriteArtifacts`
- Output:
  `gate_result = PASS`
- Claim:
  the nested bundled mirror stayed aligned after the contributor-entry rollout

### Release / Install / Runtime Coherence

- Command:
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify\vibe-release-install-runtime-coherence-gate.ps1 -WriteArtifacts`
- Output:
  `gate_result = PASS`
- Claim:
  the contributor-entry additions did not break the documented release/install
  contract

### Upstream Governance Gates

- Commands:
  - `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify\vibe-upstream-corpus-manifest-gate.ps1 -WriteArtifacts`
  - `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify\vibe-upstream-mirror-freshness-gate.ps1 -WriteArtifacts`
- Output:
  both gates report `PASS`
- Claim:
  developer-entry work did not regress the upstream-governance closure achieved
  in prior phases

## Expected Red Items Still Open

### Router Contract

- Command:
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify\vibe-router-contract-gate.ps1 -WriteArtifacts`
- Output:
  `gate_passed = false`, `strict_equality_rate = 0.9000`, only mismatch case =
  `low-signal`
- Claim:
  router-contract remains a pre-existing baseline red item and has not been
  widened by developer-entry work

### Installed Runtime Freshness

- Command:
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify\vibe-installed-runtime-freshness-gate.ps1 -WriteArtifacts`
- Output:
  `gate_result = FAIL`
- Claim:
  installed runtime freshness is still intentionally deferred to the final
  version-governance and sync phase; this report does not claim that the local
  installed copy is already updated

### Repo Cleanliness

- Command:
  `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify\vibe-repo-cleanliness-gate.ps1 -WriteArtifacts`
- Output:
  `gate_result = FAIL`
- Claim:
  cleanliness remains intentionally red while the governed changes are still
  uncommitted in the worktree; final version-governance closure must convert the
  managed workset into a clean committed state

## Stability Verdict

Current verdict: `entry_surface_closed_runtime_sync_deferred`

This verdict is justified because:

- the contributor-facing entry path is now explicit and machine-verifiable
- the new contributor surfaces did not break packaging, output, or upstream
  governance gates
- remaining red items are explicitly deferred to the final version-governance
  phase rather than hidden as accidental drift

## Hand-off to Final Version-Governance Phase

The final phase after this report must:

- sync canonical changes into bundled mirrors again after any final doc edits
- update the installed runtime under `C:\Users\羽裳\.codex\skills\vibe`
- turn `vibe-installed-runtime-freshness-gate` green
- convert the managed workset into a clean committed state
- push the resulting latest governed state to GitHub so repo, installed runtime,
  and remote latest are unified
