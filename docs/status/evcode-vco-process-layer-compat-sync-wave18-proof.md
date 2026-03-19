# EvCode VCO Process-Layer Compatibility Sync Wave18 Proof

Date: 2026-03-19
Workspace: `/home/lqf/table/table3`

## Requirement And Plan

- Requirement: `docs/requirements/2026-03-19-evcode-vco-process-layer-compat-sync-wave18.md`
- Plan: `docs/plans/2026-03-19-evcode-vco-process-layer-compat-sync-wave18-execution-plan.md`

## Upstream Source Compared

- Embedded runtime previous pin: `241a98d58e066a653c8bac136af3a2ad0e510e45`
- Upstream current main: `50d2de7c2c954919970e8399cee1d9d05e9d4775`
- Remote: `git@github.com-foryourhealth111-pixel:foryourhealth111-pixel/vco-skills-codex.git`

## Synced Runtime Surfaces

The sync updated the embedded runtime mirror under `runtime/vco/upstream` to the newer upstream commit and carried the related metadata forward.

Key surfaces now present locally:

- `runtime/vco/upstream/SKILL.md`
- `runtime/vco/upstream/bundled/skills/vibe/SKILL.md`
- `runtime/vco/upstream/bundled/skills/vibe/bundled/skills/vibe/SKILL.md`
- `runtime/vco/upstream/protocols/runtime.md`
- `runtime/vco/upstream/protocols/think.md`
- `runtime/vco/upstream/config/phase-cleanup-policy.json`
- `runtime/vco/upstream/scripts/common/ProtectedDocumentCleanup.ps1`
- `runtime/vco/upstream/scripts/governance/phase-end-cleanup.ps1`
- `runtime/vco/upstream/docs/document-asset-cleanup-governance.md`
- nested bundled counterparts under `runtime/vco/upstream/bundled/skills/vibe/**`

## EvCode Bridge Alignment

EvCode bridge documentation was aligned to the same ownership split and forbidden outcomes model:

- canonical router owns route authority
- VCO owns governed runtime truth
- host bridge owns hidden hook wiring and artifact persistence
- superpowers and similar layers remain discipline-only
- forbidden outcomes now explicitly include second runtime prompt surface, second requirement freeze surface, second execution-plan surface, and second route authority

## Metadata Updates

Updated files:

- `config/sources.lock.json`
- `runtime/vco/.source.json`
- `runtime/vco/materialization.json`
- `runtime/vco/freshness.json`

Observed synced commit:

- `50d2de7c2c954919970e8399cee1d9d05e9d4775`

## Verification Evidence

### 1. Materialization integrity

Command:

```bash
python3 scripts/verify/check_materialization.py
```

Observed result:

- `materialization checks: ok`

Meaning:

- source lock, runtime materialization receipt, and freshness receipt all agree on the new commit
- required runtime markers still exist after the sync

### 2. Standard distribution reassembly

Command:

```bash
node apps/evcode/bin/evcode.js assemble
```

Observed result:

- standard distribution assembled successfully
- metadata receipt under `.evcode-dist/standard/metadata/runtime/vco/materialization.json` now reports commit `50d2de7c2c954919970e8399cee1d9d05e9d4775`

### 3. Benchmark distribution reassembly

Command:

```bash
node apps/evcode-bench/bin/evcode-bench.js assemble
```

Observed result:

- benchmark distribution assembled successfully

### 4. Staged skill-surface check

Observed facts after reassembly:

- `runtime/vco/upstream/bundled/skills/vibe/SKILL.md` contains `Compatibility With Process Layers`
- `.evcode-dist/standard/codex-home/skills/vibe/SKILL.md` contains the same compatibility section
- `.evcode-dist/benchmark/codex-home/skills/vibe/SKILL.md` contains the same compatibility section

### 5. Cleanup policy check

Observed facts in `runtime/vco/upstream/config/phase-cleanup-policy.json`:

- policy version is `2`
- `cleanup_steps` now include:
  - `snapshot_protected_document_assets`
  - `preview_or_quarantine_protected_tmp_documents`
- `protected_document_policy` exists with protected Office/PDF extensions and quarantine settings

## Remaining Gaps

- This wave did not attempt to retrofit EvCode's Python runtime implementation to execute the upstream PowerShell protected-document cleanup helper directly.
- The sync goal here was to keep the embedded runtime mirror and EvCode bridge contract aligned with upstream truth and to refresh the staged product surfaces accordingly.

## Conclusion

EvCode is now synced to the upstream VCO fix that formalizes process-layer compatibility boundaries and document-safe phase cleanup policy, and the refreshed runtime mirror is materially present in both standard and benchmark assembled distributions.
