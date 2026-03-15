# External Tooling Boundary

- Docs root: [`../README.md`](../README.md)
- Repo root: [`../../README.md`](../../README.md)

## What Lives Here

`docs/external-tooling/` 是 background boundary surface。这里解释 VCO 与外部工具面的职责边界：哪些能力应该做成 skill，哪些能力应该走 MCP，哪些能力仍然保持 manual or operator 路径。

## Start Here

### Boundary Entry

| File | Purpose |
| --- | --- |
| [`mcp-vs-skill-vs-manual.md`](mcp-vs-skill-vs-manual.md) | 解释 MCP / skill / manual 三类扩展面的职责边界与选型规则 |

### Cross-Layer Handoff

- [`../README.md`](../README.md): docs 三段式总入口
- [`../../references/index.md`](../../references/index.md): long-lived contracts, matrices, ledgers, and overlays
- [`../../scripts/README.md`](../../scripts/README.md): executable operator surface

## Rules

- 新增 external-tooling 说明时，优先写“边界与选型”，不要把具体 wave 执行记录堆到这里
- 这里属于 background / governance boundary，不承担 current runtime summary 或 release receipt 入口
- 若某篇 external-tooling 文档影响路由或治理合同，必须补到 `docs/README.md` 与相关 `config/` / `scripts/` 锚点
