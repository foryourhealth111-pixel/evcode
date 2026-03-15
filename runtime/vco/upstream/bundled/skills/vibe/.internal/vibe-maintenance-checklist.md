# Vibe Maintenance Checklist (Internal Only)

Status: Internal maintenance reference only  
Audience: repository maintainers  
Last updated: 2026-02-25

## Internal-Only Handling Rules

1. Do not reference this file from `SKILL.md`, `references/index.md`, or runtime-facing prompt assets.
2. Do not add this path into any routing keyword index or protocol navigation table.
3. Do not quote this file in user-facing runtime instructions.
4. Use this file only during repository maintenance, audits, and release preparation.

This file is intentionally placed under `.internal/` to reduce accidental inclusion in runtime prompt loading flows.

## Goals

1. Provide a low-risk rollout sequence for routing-discipline hardening.
2. Define measurable thresholds before/after each change.
3. Reduce avoidable route drift, config drift, and silent misroutes.
4. Keep user-facing behavior stable while hardening strict-mode behavior.

## Scope

In scope:

1. Strict-mode fallback behavior (`fallback_first_candidate` tightening).
2. Main config vs bundled config parity gate.
3. Canonical convergence for `equivalent` overlap groups.

Out of scope:

1. Replacing the existing grade model (M/L/XL).
2. Changing OpenSpec governance from post-route overlay to route owner.
3. Forcing global hard-fail in non-strict mode.

## Baseline Snapshot (Must Run Before Any Change)

Run:

```powershell
powershell -NoProfile -File scripts\verify\vibe-pack-regression-matrix.ps1
powershell -NoProfile -File scripts\verify\vibe-routing-stability-gate.ps1 -Strict
powershell -NoProfile -File scripts\verify\vibe-openspec-governance-gate.ps1
```

Record baseline metrics:

1. `route_stability`
2. `top1_top2_gap`
3. `fallback_rate`
4. `misroute_rate`
5. `confirm_required_rate` (derived from route-mode counts in audit output)
6. deterministic consistency (same input => same route)

## Low-Risk Implementation Plan

### Phase 1: Config Parity Gate (Do First)

Objective: eliminate main/bundled drift risk before routing behavior changes.

Checklist:

1. Add verification script to compare JSON parity for critical config pairs:
   - `config/pack-manifest.json` vs `bundled/skills/vibe/config/pack-manifest.json`
   - `config/router-thresholds.json` vs `bundled/skills/vibe/config/router-thresholds.json`
   - `config/skill-keyword-index.json` vs `bundled/skills/vibe/config/skill-keyword-index.json`
   - `config/skill-routing-rules.json` vs `bundled/skills/vibe/config/skill-routing-rules.json`
   - `config/openspec-policy.json` vs `bundled/skills/vibe/config/openspec-policy.json`
2. Normalize JSON before compare:
   - key-order normalization
   - ignore metadata-only keys if needed (for example: `updated`, `generated_at`)
3. Fail CI/local gate on parity mismatch.
4. Output diff paths (JSON pointer style), not only hash mismatch.

Thresholds:

1. `parity_critical_files = 100%`
2. `diff_paths_count = 0` for critical files
3. `hash_match_rate = 100%` after normalization

Stop condition:

1. Any critical pair mismatch blocks merge/release.

### Phase 2: Canonical Convergence for Equivalent Groups (Small Batches)

Objective: reduce overlap-induced route variability without deleting capabilities.

Recommended first batch:

1. `code-review` group:
   - `code-review`, `code-reviewer`, `reviewing-code`
2. planning authoring group:
   - `create-plan`, `writing-plans` (keep `planning-with-files` as complementary)
3. OpenAI docs group:
   - `openai-docs`, `openai-knowledge`
4. keep `build-error-resolver -> error-resolver` alias flow stable

Checklist:

1. Mark/verify `equivalent_group` and `canonical_for_task` for each pair.
2. Keep explicit user-requested skill priority unchanged.
3. Keep alias compatibility for historical skill names.
4. Run full regression after each batch; do not merge multiple unrelated groups together.

Thresholds (per batch, compared with baseline):

1. `route_stability` drop <= `0.02`
2. `misroute_rate` increase <= `0.02` absolute
3. `fallback_rate` increase <= `0.05` absolute
4. `confirm_required_rate` increase <= `0.10` absolute
5. deterministic mismatches = `0`

Stop condition:

1. Any threshold violated => revert that batch only, keep other stable batches.

### Phase 3: Strict-Mode Fallback Tightening (Last)

Objective: prevent silent low-confidence routing in strict mode.

Proposed behavior:

1. strict mode:
   - replace `fallback_first_candidate` with `confirm_required`
   - optional CI-only hard-fail path (not default interactive behavior)
2. non-strict mode:
   - keep current behavior unchanged

Checklist:

1. Add strict-only branch in router fallback logic.
2. Preserve existing explicit user-command override semantics.
3. Keep OpenSpec as post-route overlay only.
4. Add targeted regression cases for low-signal prompts and near-gap prompts.

Thresholds:

1. strict `misroute_rate <= 0.10`
2. strict `route_stability >= 0.90`
3. strict `top1_top2_gap >= 0.08`
4. strict `confirm_required_rate` increase <= `0.15` absolute
5. strict `fallback_rate <= 0.20`

Stop condition:

1. If strict confirm rate spikes and blocks normal use, roll back this phase only.

## Unified Release Gate (Any Routing Change)

Mandatory checks:

```powershell
powershell -NoProfile -File scripts\verify\vibe-pack-routing-smoke.ps1
powershell -NoProfile -File scripts\verify\vibe-pack-regression-matrix.ps1
powershell -NoProfile -File scripts\verify\vibe-routing-stability-gate.ps1 -Strict
powershell -NoProfile -File scripts\verify\vibe-openspec-governance-gate.ps1
```

Pass criteria:

1. All scripts exit with code `0`
2. No deterministic mismatch
3. No regression beyond phase thresholds
4. OpenSpec advice still preserves selected route (`preserve_routing_assignment=true`)

## Risk Register

### R1. Main/Bundled Drift

Severity: High  
Symptoms:

1. Local run and installed run route differently.
2. Regression passes on main config but fails after install.

Mitigation:

1. Config parity gate (Phase 1).
2. Include sync step in release checklist.

### R2. Keyword Over-Penalization

Severity: High  
Symptoms:

1. Negative keywords suppress otherwise correct candidates.
2. Sudden increase of `confirm_required` and fallback usage.

Mitigation:

1. Change in small batches.
2. Keep per-group threshold gate.

### R3. Over-Convergence of Equivalent Skills

Severity: Medium  
Symptoms:

1. Semantic nuance lost after canonicalization.
2. User-requested variant behavior becomes harder to trigger.

Mitigation:

1. Preserve explicit requested-skill override.
2. Keep complementary groups out of equivalent convergence.

### R4. Orchestrator Conflict (`vibe` vs `aios-master`)

Severity: High  
Symptoms:

1. Ambiguous orchestration prompts route unpredictably.
2. Double-orchestration patterns appear.

Mitigation:

1. Enforce explicit command priority.
2. Keep conflict pair handling from overlap matrix and routing rules.

### R5. Governance-Layer Leakage Into Route Assignment

Severity: High  
Symptoms:

1. OpenSpec logic starts changing selected pack/skill.
2. Governance mode change alters routing baseline.

Mitigation:

1. Keep OpenSpec as post-route metadata only.
2. Require governance gate pass before release.

### R6. Hook Coexistence Side Effects

Severity: Medium  
Symptoms:

1. Different plugin hooks alter tool timing/order.
2. Non-reproducible behavior in long sessions.

Mitigation:

1. Keep fallback chains explicit.
2. Prefer deterministic script-based verification.

## Maintenance Do/Do-Not Checklist

Do:

1. Change one dimension at a time (parity, then convergence, then strict fallback).
2. Save baseline metrics before edits.
3. Keep compatibility aliases until equivalent convergence stabilizes.
4. Verify both route correctness and governance non-interference.

Do not:

1. Mix threshold tuning and keyword rewrites in one large commit.
2. Merge strict fallback change before parity gate is in place.
3. Edit main config without mirrored bundled update.
4. Promote complementary or conflicting pairs to equivalent without audit evidence.

## Suggested Commit Partitioning

1. Commit A: parity gate script + docs + no routing behavior change.
2. Commit B: equivalent canonical convergence (one group batch only).
3. Commit C: strict fallback tightening + strict-mode tests.
4. Commit D: threshold adjustment (only if metrics justify).

## Emergency Backout Rules

1. Back out only the latest phase commit; do not rollback unrelated stable phases.
2. Keep release notes explicit about reverted metric threshold.
3. Re-run full gate suite after backout.

## Quick Maintenance Session Template

1. Capture baseline.
2. Apply exactly one scoped change.
3. Run full gate suite.
4. Compare metrics vs thresholds.
5. Decide: merge, patch, or phase-only backout.
6. Document in `references/changelog.md` with metric deltas.

