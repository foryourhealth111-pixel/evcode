# EvCode Local Commit And Refresh Wave7 Requirement

## Goal

将已经整理完成的 EvCode 多助手增强改动提交到本地 Git 仓库，并刷新本机实际使用的 EvCode 版本，使用户能够基于最新本地构建直接测试。

## Deliverable

- 一个本地 Git 提交，包含当前整理后的增强改动
- 一次本地 EvCode 安装/分发刷新，使 CLI 实际使用最新代码
- 新鲜的启动或版本验证证据
- 本轮 governed proof/report 与 cleanup receipt

## Constraints

- 不推送远端，只提交到本地仓库。
- 不回滚用户未要求撤销的改动。
- 刷新本地使用版本必须走仓库正式的本地安装/assemble 路径，而不是临时脚本替换。
- 在提交前确认工作树内容仍通过既有验证基线。

## Acceptance Criteria

- 本地仓库出现新的提交记录。
- 本地使用的 EvCode 入口已刷新到本次提交对应版本。
- 至少有一条新鲜命令证明本地刷新后的 EvCode 可启动。
- 输出本轮 proof/report 与 cleanup receipt。

## Non-Goals

- 推送 GitHub 远端。
- 额外引入新的功能改动。
- 修复 RightCodes Claude 提供方外部稳定性问题。
