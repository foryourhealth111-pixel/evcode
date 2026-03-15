# Repo Cleanliness Baseline

Updated: 2026-03-12

## Positioning

This page is a dated baseline snapshot for improvement tracking.

It is not the live cleanliness dashboard.

Use it to answer:

1. what the last frozen inventory looked like;
2. what categories dominated cleanup pressure at that time; and
3. how to compare later improvements against that frozen point.

For current truth, always use the latest gate receipt at [`../../outputs/verify/vibe-repo-cleanliness-gate.json`](../../outputs/verify/vibe-repo-cleanliness-gate.json).

## Frozen Inventory Baseline

The current frozen baseline comes from:

- file: [`../../outputs/governance/repo-cleanliness-inventory.json`](../../outputs/governance/repo-cleanliness-inventory.json)
- companion report: [`../../outputs/governance/repo-cleanliness-inventory.md`](../../outputs/governance/repo-cleanliness-inventory.md)
- generated at: `2026-03-11T19:00:51`
- operator: `powershell -NoProfile -File scripts/governance/export-repo-cleanliness-inventory.ps1 -WriteArtifacts`

## Frozen Snapshot Summary

| Metric | Count |
| --- | --- |
| total dirty paths | `908` |
| modified tracked | `225` |
| untracked | `683` |

## Plane Split

| Plane | Total | Modified | Untracked |
| --- | --- | --- | --- |
| canonical | `417` | `103` | `314` |
| mirror:bundled | `426` | `99` | `327` |
| mirror:nested | `65` | `23` | `42` |

## Bucket Split

| Bucket | Count | Meaning |
| --- | --- | --- |
| local_noise | `8` | local scratch / operator residue |
| runtime_generated | `2` | runtime-only generated artifacts |
| managed_workset | `406` | canonical governed backlog |
| high_risk_managed | `491` | mirror and other high-risk governed backlog |
| other_dirty | `1` | uncategorized residue that should be eliminated |

## Top Dirty Prefixes

| Prefix | Count |
| --- | --- |
| `bundled` | `491` |
| `scripts` | `123` |
| `docs` | `102` |
| `references` | `94` |
| `config` | `64` |
| `third_party` | `15` |

## Current Gate-Backed View

The latest authoritative cleanliness receipt is [`../../outputs/verify/vibe-repo-cleanliness-gate.json`](../../outputs/verify/vibe-repo-cleanliness-gate.json), generated at `2026-03-12T19:35:08`.

Current summary fields from that receipt:

| Metric | Count |
| --- | --- |
| changed paths | `1164` |
| local noise visible | `0` |
| runtime generated visible | `0` |
| managed workset visible | `475` |
| high-risk managed visible | `689` |
| other dirty visible | `0` |
| repo zero-dirty | `false` |

## Reading Rule

These two views answer different questions:

- the frozen inventory explains the historical workload shape, including plane split and top dirty prefixes;
- the gate receipt explains whether current local hygiene is acceptable and how much governed backlog is still visible.

That means the repo can simultaneously be:

- `PASS` on the cleanliness gate, because local noise and runtime residue are already closed; and
- `repo_zero_dirty = false`, because the governed workset itself is still mid-migration.

## Interpretation

That means:

- removing `.serena/` or scratch files is not enough;
- the main closure work remains inside governed surfaces such as `bundled/`, `scripts/`, `docs/`, `references/`, `config/`;
- mirror pressure is still the single largest cleanup cost center;
- the old `mirror:nested` plane is a historical part of the frozen baseline and may disappear from future inventories once optional-topology cleanup fully lands.

## Authority Rule

Until the next inventory export is taken, this document remains the authoritative baseline for measuring improvement deltas. It does not replace the latest gate receipt for current-state judgments.

Ad hoc `git status` counts are useful for local awareness, but they do not replace either:

- the exported inventory split by plane and bucket; or
- the latest cleanliness gate receipt used by `current-state.md`.
