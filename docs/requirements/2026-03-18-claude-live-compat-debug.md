# Governed Requirement

## Goal

定位并修复 EvCode 在 RightCodes Claude live specialist 路线上仍然超时/失败的问题，重点排查为什么同一端点在最小 curl 场景下可返回，而 Python adapter 路径不稳定。

## Deliverable

- 传输层差异分析
- 最小修复方案
- 对应测试与真实回归结果
- 清晰的成功/失败边界

## Constraints

- 不把密钥写入仓库
- 保持 Codex 最终执行权不变
- phase cleanup 必须完成
- 优先做最小修复，不扩大无关范围

## Acceptance Criteria

- 至少比较 curl 与 Python adapter 所走请求路径的差异
- 若能修复，则 EvCode 真实 Claude run 至少一次达到 `completed_live_advisory`
- 若仍不能修复，则必须拿到可归因的失败证据，而不是模糊超时描述

## Non-Goals

- 不重构整个 provider runtime
- 不同时处理无关的 Gemini/Codex 路线

## Assumptions

- RightCodes Claude endpoint 在部分请求形态下是可用的
- 当前问题更可能出在传输/请求构造层，而非治理层

## Runtime Mode

- mode: `interactive_governed`
- scope: `claude_provider_debug`
