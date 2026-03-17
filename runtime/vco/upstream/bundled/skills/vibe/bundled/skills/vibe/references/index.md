# VCO References Index

Navigation guide for VCO long-lived contracts, registries, matrices, ledgers, scenarios, fixtures, and overlay reference packs. This page is the contract and reference layer, not the operator console.

## Start Here

### Contract Entrypoints

| Asset | Purpose |
| --- | --- |
| [unified-task-contract.md](./unified-task-contract.md) | cleanup-first 任务合同与跨平面执行边界 |
| [tool-rule-contract.md](./tool-rule-contract.md) | 工具、规则、允许/禁止项合同 |
| [mirror-topology.md](./mirror-topology.md) | canonical、bundled、nested topology invariants |
| [release-evidence-bundle-contract.md](./release-evidence-bundle-contract.md) | 什么构成 release 或 closure proof 的证据合同 |
| [reference-asset-taxonomy.md](./reference-asset-taxonomy.md) | `references/` 的正式分类、命名约定与维护规则 |

### Evidence Entrypoints

| Asset | Purpose |
| --- | --- |
| [release-ledger.jsonl](./release-ledger.jsonl) | release ledger |
| [cross-plane-replay-ledger.md](./cross-plane-replay-ledger.md) | replay 证据账本 |
| [connector-action-ledger.md](./connector-action-ledger.md) | connector action ledger |
| [upstream-value-ledger.md](./upstream-value-ledger.md) | upstream value extraction ledger |
| [changelog.md](./changelog.md) | reference 层变更账本与长期演进轨迹 |

### Adjacent Runtime / Execution Context

这些入口保留可达性，但它们属于运行态、操作态或时间绑定上下文，不属于 `references/` 的 spine：

- [`../docs/status/current-state.md`](../docs/status/current-state.md)
- [`../docs/status/non-regression-proof-bundle.md`](../docs/status/non-regression-proof-bundle.md)
- [`../scripts/verify/gate-family-index.md`](../scripts/verify/gate-family-index.md)
- [`../docs/plans/README.md`](../docs/plans/README.md)

## Contracts / Handbooks

| Asset | Purpose |
| --- | --- |
| [unified-task-contract.md](./unified-task-contract.md) | VCO 统一任务合同 |
| [tool-rule-contract.md](./tool-rule-contract.md) | 工具 / 规则约束合同 |
| [memory-block-contract.md](./memory-block-contract.md) | memory block / tier 结构合同 |
| [memory-runtime-v3-contract.md](./memory-runtime-v3-contract.md) | memory runtime v3 合同 |
| [browser-task-contract.md](./browser-task-contract.md) | browser task contract |
| [openworld-task-contract.md](./openworld-task-contract.md) | open-world runtime task contract |
| [gate-keyword-alias-contract.md](./gate-keyword-alias-contract.md) | gate/document keyword alias contract |
| [eval-replay-ledger-contract.md](./eval-replay-ledger-contract.md) | replay / audit ledger contract |
| [conflict-rules.md](./conflict-rules.md) | 跨平面冲突仲裁手册 |
| [manual-apply-checklist.md](./manual-apply-checklist.md) | 手工 apply / exception checklist |

## Registries / Catalogs

| Asset | Purpose |
| --- | --- |
| [tool-registry.md](./tool-registry.md) | VCO tool registry |
| [capability-catalog.md](./capability-catalog.md) | capability surface 总目录 |
| [role-pack-catalog.md](./role-pack-catalog.md) | role-pack v1 catalog |
| [role-pack-catalog-v2.md](./role-pack-catalog-v2.md) | role-pack v2 catalog |
| [discovery-intake-watchlist.md](./discovery-intake-watchlist.md) | discovery intake watchlist |
| [connector-capability-matrix.md](./connector-capability-matrix.md) | connector 与 capability 的映射入口 |
| [`../templates/ORIGIN.md.tmpl`](../templates/ORIGIN.md.tmpl) | repo-local upstream provenance template |

## Matrices / Scorecards

| Asset | Purpose |
| --- | --- |
| [connector-admission-matrix.md](./connector-admission-matrix.md) | connector admission 决策矩阵 |
| [capability-dedup-matrix.md](./capability-dedup-matrix.md) | capability overlap / owner / dedup 基线 |
| [capability-lifecycle-matrix.md](./capability-lifecycle-matrix.md) | capability lifecycle 状态矩阵 |
| [candidate-quality-scorecards.md](./candidate-quality-scorecards.md) | candidate 质量评分 |
| [browser-provider-scorecard.md](./browser-provider-scorecard.md) | browser provider 评分卡 |
| [plane-scorecards.md](./plane-scorecards.md) | memory / browser / desktop / document 等平面评分卡 |
| [subagent-pattern-scorecard.md](./subagent-pattern-scorecard.md) | subagent pattern 质量评分 |
| [skill-distillation-scorecard.md](./skill-distillation-scorecard.md) | skill distillation 评分标准 |
| [upstream-reaudit-matrix-v2.md](./upstream-reaudit-matrix-v2.md) | upstream re-audit 矩阵 |

## Ledgers / Evidence / Changelog

| Asset | Purpose |
| --- | --- |
| [release-ledger.jsonl](./release-ledger.jsonl) | release ledger |
| [release-evidence-bundle-contract.md](./release-evidence-bundle-contract.md) | release evidence bundle contract |
| [changelog.md](./changelog.md) | append-only reference changelog |
| [connector-action-ledger.md](./connector-action-ledger.md) | connector action ledger |
| [cross-plane-replay-ledger.md](./cross-plane-replay-ledger.md) | replay 证据账本 |
| [upstream-value-ledger.md](./upstream-value-ledger.md) | upstream value extraction ledger |
| [rollout-proposal-contract.md](./rollout-proposal-contract.md) | rollout proposal contract |

## Validation / Playbooks

| Asset | Purpose |
| --- | --- |
| [memory-eval-scenarios.md](./memory-eval-scenarios.md) | memory quality / replay 场景 |
| [prompt-eval-scenarios.md](./prompt-eval-scenarios.md) | prompt intelligence 场景 |
| [openworld-eval-scenarios.md](./openworld-eval-scenarios.md) | open-world runtime 评测场景 |
| [connector-simulation-scenarios.md](./connector-simulation-scenarios.md) | connector sandbox / simulation 场景 |
| [document-golden-corpus.md](./document-golden-corpus.md) | 文档平面 golden corpus |
| [document-failure-taxonomy.md](./document-failure-taxonomy.md) | document failure taxonomy |
| [prompt-pattern-cards.md](./prompt-pattern-cards.md) | prompt pattern cards |
| [prompt-risk-checklist.md](./prompt-risk-checklist.md) | prompt risk checklist |
| [upstream-distillation-quality-bar.md](./upstream-distillation-quality-bar.md) | upstream distillation quality bar |
| [fixtures/README.md](./fixtures/README.md) | fixture migration stage2 的 baseline / migration map 入口 |

## Overlay Packs

| Folder | Purpose |
| --- | --- |
| [overlays/turix-cua](./overlays/turix-cua) | BrowserOps / CUA foundation 与 runbook |
| [overlays/gitnexus](./overlays/gitnexus) | GitNexus foundation / architecture / impact / detect-changes |
| [overlays/ruc-nlpir](./overlays/ruc-nlpir) | FlashRAG / WebThinker / DeepAgent overlay references |
| [overlays/agency](./overlays/agency) | agency-style role overlays |

## Wave Execution Backlog Anchors

| Wave Set | Primary Assets |
| --- | --- |
| Wave19-30 | [../docs/plans/2026-03-07-vco-full-spectrum-integration-plan.md](../docs/plans/2026-03-07-vco-full-spectrum-integration-plan.md) |
| Wave31-39 | [../docs/plans/2026-03-07-vco-deep-value-extraction-drift-closure-plan.md](../docs/plans/2026-03-07-vco-deep-value-extraction-drift-closure-plan.md) |
| Wave40-63 | [../docs/plans/2026-03-07-vco-wave40-63-execution-plan.md](../docs/plans/2026-03-07-vco-wave40-63-execution-plan.md), [../config/wave40-63-execution-board.json](../config/wave40-63-execution-board.json) |
| Wave64-82 | [../docs/plans/2026-03-07-vco-wave64-82-execution-plan.md](../docs/plans/2026-03-07-vco-wave64-82-execution-plan.md), [../config/wave64-82-planning-board.json](../config/wave64-82-planning-board.json) |
| Wave83-100 | [../docs/plans/2026-03-07-vco-wave83-100-execution-plan.md](../docs/plans/2026-03-07-vco-wave83-100-execution-plan.md), [../docs/plans/2026-03-07-vco-wave83-100-execution-status.md](../docs/plans/2026-03-07-vco-wave83-100-execution-status.md) |

## Reading Order

1. 先看 [unified-task-contract.md](./unified-task-contract.md)、[tool-rule-contract.md](./tool-rule-contract.md)、[mirror-topology.md](./mirror-topology.md) 建立 contract-first 边界。
2. 再看 [tool-registry.md](./tool-registry.md) 与 [capability-catalog.md](./capability-catalog.md) 理解能力面。
3. 然后进入 matrix / scorecard 判断 admission、dedup、quality。
4. 接着进入 ledger / evidence 读取长期证明链。
5. 最后按 validation / playbooks / overlays 深读具体场景与实现参考。

## Maintenance Rules

- 新增 reference 资产必须进入本 index。
- 新增 ledger / scorecard / contract 时，需至少补一个对应的 docs 或 gate 锚点。
- 不把 wave 执行正文塞进 `references/`；时间绑定正文继续放 `docs/plans/` 或 `docs/status/`。
