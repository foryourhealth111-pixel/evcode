# Current State

Updated: 2026-03-12

## What This Page Is

This page is the runtime-entry summary for the current closure batch.

It exists to answer three questions only:

1. current truth lives where;
2. this batch is trying to finish what;
3. the next operator hop is where.

It is not the canonical contract layer, and it is not the place to restate long-lived governance text.

## Authority

This page is a live summary, not the source of truth.

Authoritative receipts for the current closure batch:

- repo cleanliness: [`../../outputs/verify/vibe-repo-cleanliness-gate.json`](../../outputs/verify/vibe-repo-cleanliness-gate.json)
- other gate receipts: `../../outputs/verify/*.json`
- latest node/process hygiene audits: [`../../outputs/runtime/process-health/audits/`](../../outputs/runtime/process-health/audits/)
- latest node/process cleanup receipts: [`../../outputs/runtime/process-health/cleanups/`](../../outputs/runtime/process-health/cleanups/)

## Mission

当前仓库仍处于 `non-regression-first cleanup` 收口期。目标已经从“继续扩展治理面”切换为“压缩入口、收敛叙事、保持 proof 绿色”，也就是把已修复的 routing、packaging、mirror、runtime、cleanliness 结果稳定固化下来。

## Runtime Handoff

- current execution entry: [`../plans/README.md`](../plans/README.md)
- active remediation plan: [`../plans/2026-03-11-vco-repo-simplification-remediation-plan.md`](../plans/2026-03-11-vco-repo-simplification-remediation-plan.md)
- closure proof contract: [`non-regression-proof-bundle.md`](non-regression-proof-bundle.md)
- operator script surface: [`../../scripts/README.md`](../../scripts/README.md)
- verify family navigation: [`../../scripts/verify/gate-family-index.md`](../../scripts/verify/gate-family-index.md)

## Canonical Background Contracts

- repo cleanliness: [`../repo-cleanliness-governance.md`](../repo-cleanliness-governance.md)
- version / packaging / mirror topology: [`../version-packaging-governance.md`](../version-packaging-governance.md)
- outputs boundary: [`../output-artifact-boundary-governance.md`](../output-artifact-boundary-governance.md)
- docs IA: [`../docs-information-architecture.md`](../docs-information-architecture.md)

## Live Snapshot

Current cleanliness authority is the receipt at [`../../outputs/verify/vibe-repo-cleanliness-gate.json`](../../outputs/verify/vibe-repo-cleanliness-gate.json), generated at `2026-03-12T20:27:28`.

Key summary fields from that receipt:

- changed paths: `1164`
- local noise visible: `0`
- runtime generated visible: `0`
- managed workset visible: `475`
- high-risk managed visible: `689`
- repo zero-dirty: `false`

Interpretation:

- 当前 pressure 主要来自 governed managed workset，不是操作者垃圾或运行时残留。
- `nested_bundled` 现在应被视为 optional compatibility topology surface，而不是必须常驻的物理 payload。
- `outputs/**` 继续承担 evidence 职责；这里不再重复抄写每个 gate 的详细结果。

## Proof Surface

当前 closure batch 的核心 proof surface 由以下 gate receipts组成：

- `vibe-upstream-corpus-manifest-gate`
- `vibe-upstream-mirror-freshness-gate`
- `vibe-mirror-edit-hygiene-gate`
- `vibe-nested-bundled-parity-gate`
- `vibe-version-packaging-gate`
- `vibe-installed-runtime-freshness-gate`
- `vibe-release-install-runtime-coherence-gate`
- `vibe-repo-cleanliness-gate`

这些 gate 的最新 PASS/FAIL 以 `../../outputs/verify/*.json` 为准，不再在本页维护手写状态表。

## Primary Blockers

1. 文档入口仍然过宽。
   - 虽然 `status/` supporting baselines 已经分层，但 `plans/`、`releases/`、历史报告面仍有继续压缩的空间，避免“当前入口”和“背景材料”继续并列暴露。

2. worktree 仍然处于高压 managed state。
   - 虽然 cleanliness gate 通过，但 `managed_workset_visible` 与 `high_risk_managed_visible` 仍然很高，只能按受管 backlog 波次继续收口，不能做 blanket deletion。

3. phase-end hygiene 必须持续 attribution-safe。
   - 最新 node/process 审计显示 `cleanup_candidate_count = 0`，所以本轮只能继续使用 report-only cleanup，而不是误杀外部 Node 进程。

## Current Closure Focus

1. 压缩 `docs/`、`status/`、`plans/`、`releases/`、`references/` 的入口面，不改变治理合同与运行时行为。
2. 让 `current-state`、README、索引页统一回指 authoritative artifacts，停止手工复制快照数字。
3. 每完成一个批次都执行 canonical -> bundled 同步、proof bundle 复验，以及 phase-end hygiene。

Compatibility-layer stabilization、larger prune windows、以及更大范围的 archive/move/delete 仍然是后续显式波次，不在本页隐式推进。
