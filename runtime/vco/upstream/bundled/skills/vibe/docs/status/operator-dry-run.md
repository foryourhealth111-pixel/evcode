# Operator Dry Run

Updated: 2026-03-12

## Summary

This page is the latest human-readable phase-end receipt.

Authoritative gate outcomes still live in `outputs/verify/*.json`, and authoritative process receipts live in `outputs/runtime/process-health/**`.

## Command

Canonical batch-close entrypoint used for this receipt:

```powershell
powershell -NoProfile -File scripts/governance/phase-end-cleanup.ps1 -WriteArtifacts -IncludeMirrorGates
```

## Receipt Snapshot

Observed on `2026-03-12T12:30:03Z`.

- overall result: `PASS`
- mode: mirror-aware, write-artifacts, report-only node cleanup
- wrapper steps passed: `10/10`
- `.tmp/` purge: `removed = false`
- local exclude refresh: `PASS`
- cleanliness inventory export: `PASS`
- cleanliness gate: `PASS`
- output artifact boundary gate: `PASS`
- mirror edit hygiene gate: `PASS`
- nested bundled parity gate: `PASS`
- version packaging gate: `PASS`
- node process audit: `PASS`
- node zombie cleanup: `PASS` in report-only mode

## Key Metrics

- repo cleanliness remains governed rather than globally clean
  - changed paths: `1164`
  - local noise visible: `0`
  - runtime generated visible: `0`
  - managed workset visible: `475`
  - high-risk managed visible: `689`
- output boundary remains stable under `stage2_mirrored`
  - tracked outputs: `21`
  - tracked allowlist parity: `PASS`
- node audit remained attribution-safe
  - audited node processes: `222`
  - classified external / audit-only: `222`
  - cleanup candidates: `0`
  - managed termination applied: `false`

## Evidence Anchors

- `outputs/verify/vibe-repo-cleanliness-gate.json`
- `outputs/verify/vibe-output-artifact-boundary-gate.json`
- `outputs/verify/vibe-mirror-edit-hygiene-gate.json`
- `outputs/verify/vibe-nested-bundled-parity-gate.json`
- `outputs/verify/vibe-version-packaging-gate.json`
- `outputs/runtime/process-health/audits/node-process-audit-20260312-203003.json`
- `outputs/runtime/process-health/cleanups/node-process-cleanup-20260312-203003.json`

## Next Hop

- runtime summary: [`current-state.md`](current-state.md)
- batch closure assessment: [`closure-audit.md`](closure-audit.md)
- verify family navigation: [`../../scripts/verify/gate-family-index.md`](../../scripts/verify/gate-family-index.md)

## Boundaries

This receipt proves only that the current phase-end closure wrapper can purge temp state, refresh local excludes, rerun bounded non-regression gates, and audit node processes without unsafe broad termination.

It does **not** prove that the repository is globally zero-dirty, that `nested_bundled` is removable, that tracked `outputs/**` can already be hard-pruned, or that third-party mirror roots can already be deleted.
