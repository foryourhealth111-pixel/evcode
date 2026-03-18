# Governed Requirement

## Goal

对 EvCode 的多助手专家设计做一次实体化、仿真的可用性验证，模拟真实用户通过 CLI 使用 `evcode` / `evcode-bench`，确认标准通道、benchmark 通道、Claude autonomous 探查、Gemini packetized 设计建议，以及 Codex 最终执行权这条链路能正常工作。

## Deliverable

- 一组可重复执行的仿真验证场景
- 对应的运行证据与结果判定
- 对异常/边界的风险说明
- 更新后的 proof 文档

## Constraints

- 必须保留 VCO 六阶段治理语义
- 不创建第二套路由器
- 不把 specialist advisory 误判为最终执行完成
- 验证需要覆盖 deterministic mock 场景，必要时追加真实 provider smoke
- 不在仓库里写入明文密钥
- phase cleanup 必须完成并留下证据

## Acceptance Criteria

- `evcode status` / `evcode-bench status` 可正常返回状态信息
- standard 通道 CLI run 能生成 governed runtime artifact
- benchmark 通道 CLI run 能保持 specialist suppression 且不污染 workspace
- 通过 mock provider 可验证 Claude autonomous brief 与 Gemini packetized packet 的真实 HTTP 调用链路
- 若执行真实 provider smoke，能证明 live specialist 在 RightCodes 上至少完成一次最小 advisory 往返
- 所有验证都有命令、退出码、关键 artifact 或输出作为证据

## Non-Goals

- 不在本轮实现新的 specialist 能力
- 不把 advisory 结果自动转成大规模代码修改
- 不做性能压测或长时间 soak test

## Assumptions

- 当前仓库中的 specialist pipeline 改动为待验收对象
- 本地环境允许启动临时 HTTP 服务用于 mock provider
- benchmark 使用 fake codex host 即可证明其治理语义

## Runtime Mode

- mode: `interactive_governed`
- scope: `validation_and_proof`
