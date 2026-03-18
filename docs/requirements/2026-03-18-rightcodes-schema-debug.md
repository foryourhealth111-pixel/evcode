# Governed Requirement

## Goal

直接排查 RightCodes API 与 EvCode specialist adapter 之间的 schema 兼容问题，优先使用 `https://right.codes/codex/v1` 与 `model=gpt-5.4` 做最小请求实验，确认服务端实际接受的请求形态。

## Deliverable

- 一组最小请求实验结果
- 对 `responses` 与 `chat/completions` 的兼容判断
- 对 EvCode 当前 adapter 差异的定位结论
- 明确的修复建议

## Constraints

- 不把 API key 写入仓库文件
- 只做最小必要网络请求，不做大规模调用
- 保留 governed runtime 证据链
- phase cleanup 必须完成

## Acceptance Criteria

- 至少验证 `gpt-5.4` 在 RightCodes codex 端点上的最小请求表现
- 至少比较两种 schema：`/responses` 与 `/chat/completions`
- 输出服务端返回码、关键响应体和结论
- 明确指出 EvCode 当前 adapter 是否用错 schema

## Non-Goals

- 本轮不直接提交完整 adapter 修复
- 不做 UI specialist 功能扩展
- 不做长时间稳定性压测

## Assumptions

- 用户提供的 key 允许最小 smoke 请求
- RightCodes 兼容层可能并不完整支持 OpenAI Responses API

## Runtime Mode

- mode: `interactive_governed`
- scope: `provider_schema_debug`
