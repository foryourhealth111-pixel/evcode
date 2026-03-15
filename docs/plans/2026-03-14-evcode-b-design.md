# EvCode 方案 B 详细设计文档

## 文档状态

- 状态：Draft v2
- 日期：2026-03-14
- 方案：B，原生兼容代理
- 默认治理：`vibe-on`
- 默认工作流等级：`XL`
- 目标读者：产品设计者、CLI 实现者、VCO runtime 维护者

---

## 1. 背景与目标

### 1.1 背景

EvCode 的目标不是做一个 `codex` 的薄别名，也不是 fork 出一套新的独立推理运行时，而是在现有 `codex` CLI 之上构建一个新的代理工具 `evcode`。这个工具需要满足四个核心条件：

1. 底层继续使用 `codex` 作为执行器与会话宿主。
2. 每次新对话默认进入 VCO 治理态，相当于自动启用 `$vibe`。
3. 每次新对话默认按 `XL` 级工作流理解与推进任务。
4. 在保持与原生 Codex 用户心智相近的前提下，将 VCO runtime 管理、计划检查、native team 前置包装、阶段清理做成产品内建规范。

从用户视角看，`evcode` 应该是一个“开箱即带 Vibe 治理和 XL 工作流”的 Codex 变体；从工程实现看，`evcode` 应该是一个“对 Codex 进行会话前导注入、workflow 编排和 runtime 管理的控制层”。

### 1.2 产品目标

EvCode 首版需要实现以下核心目标：

- 提供一个新的主命令入口 `evcode`。
- 让每个新会话默认处于 `vibe` 已启用的治理上下文中。
- 让每个新会话默认按 `XL` 级任务流处理，并优先把执行委托给 `codex` native team。
- 在会话启动时先检查项目目录、VCO 骨架、计划文件状态。
- 如果 VCO 骨架未初始化，先初始化骨架。
- 如果没有计划，进入 `XL planning mode`，先完成全面规划再进入实现。
- 如果已有计划，进入 `XL` 原生团队执行模式，并强制所有子代理在 prompt 末尾追加 `$vibe`。
- 在阶段完成后自动执行僵尸 Node 清理、临时文件清理、仓库整洁性维护。
- 保留与原生 `codex` 相近的操作心智，包括交互式会话、非交互执行、MCP 管理、profile 管理与会话恢复。
- 以 `vco-skills-codex` 作为上层 runtime payload，而不是在 EvCode 内部复制一份 VCO 逻辑。
- 支持安装、校验、同步、升级、回滚与环境诊断。

### 1.3 非目标

首版明确不做以下事情：

- 不 fork `codex` 模型调用协议。
- 不重写 `vco-skills-codex` 的路由、协议、overlay 规则。
- 不试图完全复制官方 Codex 未公开的内部 agent 管理实现。
- 不把所有 prompt 层能力都做成 GUI。
- 不因为默认 `XL` 而移除 raw escape、显式关闭治理或手动降级能力。

---

## 2. 产品定位

EvCode 的产品定位如下：

> 一个基于 Codex Runtime 的原生兼容代理工具，在每次新会话启动时自动注入 Vibe Code Orchestrator 启动上下文，默认以 `XL` 工作流组织任务，并以受控 runtime 的方式管理 skills、protocols、MCP profile、native team 前置包装和阶段清理。

这个定位包含四层含义：

- `codex` 是执行底座，不被替换。
- `vco-skills-codex` 是治理 runtime，不被重写。
- `evcode` 是 native team 的前置包装层，负责默认启用 Vibe/XL、管理配置与保证一致性。
- `workflow spec` 是产品合同，不是口头建议。

EvCode 的差异化价值不在模型能力，而在“默认治理”和“受控交付”：

- 默认 Vibe：不需要每次手动输入 `$vibe`。
- 默认 `XL`：不需要每次手动声明“这是 XL 级任务”。
- 受控交付：用户得到的是一个可安装、可升级、可诊断、可回滚、可清理的治理代理。

---

## 3. 方案 B 的核心原则

### 3.1 原生兼容优先

EvCode 应优先复用原生 `codex` 的命令语义与配置结构。只要 `codex` 已具备对应能力，EvCode 就做包装，不重新发明一套独立接口。

### 3.2 会话前导注入，而不是每轮污染

EvCode 的关键魔改点是“新会话启动时的 Vibe bootstrap 注入”。这应该在会话创建阶段完成，而不是在每轮用户消息前重新拼接长 prompt。

### 3.3 默认 XL，而不是按信号推荐 XL

EvCode 的设计不是“根据任务信号经常推荐 XL”，而是“默认按 XL 启动，再由用户显式切换到 raw 或治理关闭模式”。这是一条产品级约束。

### 3.4 运行时解耦

EvCode 控制层与 VCO runtime 必须解耦。升级 `vco-skills-codex` 时，不应该要求修改 `evcode` 主程序；升级 `evcode` 时，也不应强制改动 VCO 规则。

### 3.5 默认启用，保留逃生口

EvCode 默认开启 Vibe 启动包装，并默认按 `XL` 级工作流组织任务，但必须保留明确的原生逃生口，例如 `evcode raw` 或 `--governance off`。没有逃生口的“强制包装”会在简单任务场景中显著降低体验。

### 3.6 阶段完成必须清理

仓库整洁、内存精简和阶段后清理不是“最佳实践建议”，而是 workflow contract 的一部分。每个阶段完成后都必须执行一次资源整理。

---

## 4. 用户心智模型

### 4.1 对用户的统一表达

用户理解 EvCode 时，只需要记住一句话：

> `evcode` 是默认带 Vibe 治理和 XL 工作流的 Codex。

### 4.2 用户不需要理解的内部细节

用户不需要直接理解：

- bootstrap contract 的具体格式
- runtime pin 与 payload 镜像细节
- VCO overlay 在本地的物化方式
- 子代理 prompt suffix 的注入机制

这些应该由 `evcode doctor`、`evcode audit` 与 `evcode status` 提供必要可见性，而不是要求用户手工介入。

### 4.3 三种主要使用方式

1. 默认治理会话
   - 用户执行 `evcode`
   - 新会话自动进入 VCO 治理态
   - 默认按 `XL` 工作流执行

2. 治理的非交互执行
   - 用户执行 `evcode exec "任务描述"`
   - 该任务在 VCO 治理上下文中执行
   - 默认按 `XL` 工作流执行

3. 原生绕过
   - 用户执行 `evcode raw`
   - 不注入 Vibe，行为更接近原生 `codex`

---

## 5. 系统总体架构

EvCode 建议采用四层架构。

### 5.1 CLI Facade Layer

职责：

- 暴露 `evcode` 命令入口
- 解析子命令、flags、profile 选择与工作目录
- 负责输出统一帮助文案、状态与错误信息

边界：

- 不直接承载 VCO 规则
- 不直接存储业务 runtime 内容

### 5.2 Session Bootstrap Layer

职责：

- 在每次会话创建时注入 Vibe bootstrap contract
- 维护治理状态，例如 `vibe-on`、`vibe-off`
- 维护默认工作流等级，例如 `XL`
- 根据启动检查决定是否初始化骨架、生成计划、或把执行交给 native team
- 管理显式 command priority、raw escape、子代理 prompt suffix、阶段清理

这层是 EvCode 的核心差异化能力，但它不是 team scheduler。

### 5.3 Native Compatibility Layer

职责：

- 把 `evcode` 命令映射到 `codex` 原生命令
- 保持对 `exec`、`mcp`、`resume`、`fork` 和 native team 等能力的兼容
- 为不可直接透传的部分提供最薄包装

这层要尽量小，避免 EvCode 演化成“另一个自定义代理协议”。

### 5.4 VCO Runtime Layer

职责：

- 承载 `vco-skills-codex` 的 skills、protocols、config、bootstrap、verify 脚本
- 为 EvCode 提供治理知识与 runtime payload
- 支持 pin、同步、升级与回滚

这层不属于 EvCode 主程序逻辑，而是 EvCode 管理的 payload。

### 5.5 Native Team Boundary

EvCode 必须明确遵守以下边界：

- `codex` native team 是唯一的 team orchestration authority
- EvCode 不新增 wave、batch 或 scheduler 层
- EvCode 只负责启动前置包装、子任务 prompt 后缀注入、runtime/profile/mcp 默认状态与阶段清理

---

## 6. Session-Start Vibe 注入设计

### 6.1 设计目标

EvCode 需要保证“每次新对话都会自动调用 vibe”的产品语义，并进一步保证“每次新对话默认采用 XL 级工作流”的产品语义，但工程上不应采用粗糙的字符串前缀拼接方式。

### 6.2 推荐实现

在启动新会话时，由 Session Bootstrap Layer 构造一份压缩版 bootstrap contract，并作为会话初始上下文注入。

这份 contract 应包含以下语义：

- 当前会话默认启用 Vibe 启动注入。
- 当前会话默认按 `XL` 工作流理解和推进任务。
- 当前会话必须先查看项目目录。
- 当前会话必须先检查 VCO 骨架是否初始化。
- 当前会话必须先检查计划文件是否存在。
- 用户显式技能命令拥有更高优先级。
- 未启用工具必须惰性探测并按 fallback 处理。
- 在具备计划时优先进入无人值守、多子代理、高并发执行。
- 每个子代理任务 prompt 尾部必须附加 `$vibe`。
- 每阶段结束必须执行仓库清理、临时文件清理、僵尸 Node 清理。

### 6.3 默认系统提示词合同

EvCode 首版应将以下内容固化为默认 session-start system prompt contract 的核心语义：

1. 请先查看项目目录。
2. 请查看 VCO 骨架是否初始化。
3. 请查看计划是否已经生成。
4. 如果 VCO 骨架未初始化，请先初始化骨架。
5. 如果没有计划：
   - 请采用 `XL` 级任务流理解任务类型。
   - 保证高效完成任务实现。
   - 全面规划落地计划、注意事项、具体设计。
   - 进一步规划执行步骤、测试项目。
   - 说明如何保证设计正确落地。
   - 严格证明设计落地的稳定性、可用性和智能性。
6. 如果有计划：
   - 请基于计划完成后续所有的 wave、batch、阶段。
   - 在这条执行指令后追加 `$vibe`。
   - 这是 `XL` 级任务。
   - 接下来将在无人值守模式下完成。
   - 每个子代理执行时，都要在任务 prompt 最后加入 `$vibe` 后缀。
   - 在保证质量前提下尽可能提高并发度。
   - 严谨、细致、简洁明了地完成任务。
   - 保持全流程执行、监测、推进、调试、分析。
   - 把方案细致地完成和落实。
7. 在每次运行完一个阶段后：
   - 清除僵尸 Node 对内存的占用。
   - 清理为了完成任务产生的临时文件。
   - 保持仓库整洁。
   - 保持内存使用精简。

这个合同在产品上应视为“默认治理人格”，不是普通提示词模板。用户不需要每次重新输入。

### 6.4 为什么不直接注入整份 `SKILL.md`

整份 `SKILL.md` 太长，且包含大量对当前回合并不必要的细节。每次完整注入会导致：

- 上下文浪费
- 对话冗长
- 每轮重复成本过高

更合理的方式是：

- 会话启动时注入精简治理合同
- 需要具体协议时，再按需引导载入 `protocols/*`
- 需要具体 skill 行为时，再按需触发相应 skill

### 6.5 启动时的项目检查顺序

EvCode 在创建新会话后，应先执行一个固定的启动检查序列：

1. 检查当前项目目录是否可读。
2. 检查是否存在 VCO 骨架标志文件或目录。
3. 检查是否存在可识别的计划文件。
4. 根据检查结果决定是进入“骨架初始化”、“XL 规划生成”，还是“XL 无人值守执行”。

建议定义两个检测器：

- `skeleton detector`
  - 用于判断当前仓库是否已完成 EvCode/VCO 最小骨架初始化
- `plan detector`
  - 用于判断当前仓库是否已有计划文档，例如 `docs/plans/*.md`

### 6.6 注入模式

EvCode 首版应至少支持两种治理模式：

- `vibe-on`
  - 所有新会话默认启用 VCO bootstrap
  - 所有新会话默认工作流等级为 `XL`
- `vibe-off`
  - 不注入 VCO，行为接近原生 `codex`

### 6.7 原生逃生路径

建议提供两个绕过入口：

- `evcode raw`
- `evcode --governance off`

这两个入口应是显式语义，不应依赖环境变量黑箱切换。

---

## 7. 工作流规范

### 7.1 默认工作流等级

EvCode 的默认工作流等级应设为 `XL`。这不是“根据任务信号推荐 XL”，而是“默认以 XL 的治理标准启动，再根据显式命令或 raw 模式降级”。

### 7.2 无计划时的行为

如果启动检查发现没有计划文件，EvCode 应进入 `XL planning mode`：

- 先理解任务类型
- 生成全面计划
- 明确注意事项、具体设计、执行步骤、测试项目
- 明确如何证明设计的稳定性、可用性和智能性

此时不应直接跳过规划进入实现。

### 7.3 有计划时的行为

如果启动检查发现已有计划文件，EvCode 应进入 `XL native-team execution mode`：

- 默认无人值守推进
- 尽可能启用高并发子代理
- 每个子代理 prompt 尾部追加 `$vibe`，这是子任务使用 vibe skills 的实际触发机制
- 严格按计划推进、监测、调试、分析和清理

### 7.4 子代理约束

所有由 EvCode 派生的子代理 prompt 在执行阶段都必须满足：

- 保留当前任务上下文
- 在 prompt 末尾追加 `$vibe`
- 优先使用 VCO 的 XL 团队执行心智

### 7.5 阶段结束清理

每个阶段结束后必须执行一次清理动作，至少包括：

- 清除僵尸 Node 进程
- 清理任务产生的临时文件
- 维持仓库目录整洁
- 释放不必要的内存占用

这部分规范应作为 workflow contract 的一部分落地，而不是开发者自觉遵守的口头约定。

---

## 8. 命令面设计

### 8.1 一级命令

建议首版支持以下一级命令：

- `evcode`
- `evcode exec`
- `evcode raw`
- `evcode resume`
- `evcode fork`
- `evcode doctor`
- `evcode status`
- `evcode audit`
- `evcode governance`
- `evcode mcp`
- `evcode profile`
- `evcode runtime`

### 8.2 命令说明

#### `evcode`

启动新的交互式会话，默认启用 `vibe-on`，默认使用 `XL` 工作流。

#### `evcode exec "<prompt>"`

启动治理态的非交互执行流程，默认使用 `XL` 工作流。

#### `evcode raw`

启动不注入 Vibe 的原生兼容会话。

#### `evcode doctor`

聚合检查以下信息：

- `codex` 可执行文件状态
- 当前 EvCode 配置完整性
- 当前 runtime pin
- `vco-skills-codex` payload 是否存在
- MCP profile 是否已物化
- 必要的 provider/env 是否齐全
- 默认 `XL` 工作流策略是否已生效
- skeleton detector 与 plan detector 是否可执行
- 阶段清理器是否可执行

#### `evcode status`

输出当前默认 profile、治理模式、工作流等级、runtime 版本、MCP profile 等状态。

#### `evcode audit`

输出更细粒度的审计视图：

- runtime receipt
- pinned commit/release
- overlay 启用状态
- 当前 bootstrap contract 版本
- 默认系统提示词合同版本
- 最近一次 doctor/verify 结果

#### `evcode governance on|off|status`

建议首版只支持 `on`、`off`、`status`。

这里的 `governance` 仅表示“是否默认注入 Vibe 启动合同”的开关，不表示额外的 team 编排器。

- `on`
  - 默认启用 Vibe
  - 默认工作流等级为 `XL`
- `off`
  - 关闭默认 Vibe 启动注入
- `status`
  - 查看当前治理状态

#### `evcode mcp ...`

优先透传到底层 `codex mcp`，必要时附加 EvCode runtime 的默认 profile 或 materialization 能力。

#### `evcode profile ...`

管理 EvCode profile，包括：

- 默认模型
- provider/base URL
- MCP profile
- governance mode
- workflow grade

#### `evcode runtime sync|update|rollback|pin|status`

管理 VCO payload runtime。

---

## 9. 与原生 Codex 的兼容边界

### 9.1 兼容目标

EvCode 需要与原生 Codex 保持以下层面的兼容：

- 命令习惯
- 配置心智
- 工作目录与会话运行方式
- MCP 管理入口

### 9.2 不做 1:1 内部复制

EvCode 不应该承诺以下事情：

- 完全复制官方内部 agent object model
- 复制所有未公开或不稳定的本地状态结构
- 覆盖或替代 `codex` 的底层协议更新节奏

### 9.3 推荐兼容策略

- 已存在的原生命令：直接转发或轻包装
- 需要新增的治理命令：明确标注为 EvCode 扩展
- 原生兼容字段：放在 `codex` 配置命名空间
- EvCode 扩展字段：放在 `evcode` 配置命名空间

---

## 10. 配置模型

### 10.1 设计原则

EvCode 配置需要同时满足两个目标：

- 对原生 `codex` 尽可能兼容
- 对 EvCode 的治理策略足够明确

### 10.2 建议结构

```json
{
  "codex": {
    "model": "gpt-5",
    "profile": "default",
    "sandbox": "workspace-write",
    "approval": "on-request",
    "mcp_profile": "full"
  },
  "evcode": {
    "governance": "vibe-on",
    "inject_mode": "session-start",
    "raw_escape": true,
    "default_workflow_grade": "XL",
    "unattended_when_plan_exists": true,
    "subagent_prompt_suffix": " $vibe",
    "stage_cleanup": {
      "kill_zombie_node": true,
      "clean_temp_files": true,
      "keep_repo_tidy": true
    },
    "runtime": {
      "source": "pinned-release",
      "version": "bb98ece"
    }
  }
}
```

### 10.3 Provider 与 Endpoint 策略

EvCode 不应把上游模板中的 `OPENAI_BASE_URL` 或其他私有 endpoint 直接写死为产品默认。更合理的做法是将 provider 做成 profile 选择：

- `official-openai`
- `custom-openai-compatible`
- `ark-hybrid`

用户可以在 `init` 或 `profile use` 时选择。

---

## 11. 运行时与目录布局

### 11.1 设计原则

EvCode 不应直接把所有治理状态写到用户现有 `~/.codex` 下。建议使用独立根目录承载 EvCode 的控制状态与 runtime payload。

### 11.2 建议目录

```text
~/.evcode/
  config/
    default.json
    profiles/
  runtime/
    vco/
  sessions/
  logs/
  receipts/
  cache/
```

仓库内建议目录：

```text
src/
  commands/
  governance/
  runtime/
  cleanup/
  codex/
  profiles/
  doctor/
tests/
docs/
  plans/
```

### 11.3 与 `~/.codex` 的关系

- EvCode 自身治理状态：保存在 `~/.evcode`
- 与 `codex` 兼容的 settings/materialized MCP：按需桥接
- 用户原有 `~/.codex`：不应被静默污染

如果需要 adopt 模式，可后续增加：

- `evcode runtime adopt-codex-home`

---

## 12. VCO Runtime 集成策略

### 12.1 集成原则

EvCode 直接复用 `vco-skills-codex` 的以下内容：

- `config/`
- `protocols/`
- `mcp/`
- `scripts/bootstrap/`
- `scripts/setup/`
- `install.*`
- `check.*`

### 12.2 不复制原则

EvCode 不在主仓库里手工复制 VCO 规则文本。它应通过以下方式之一消费上游：

- pin 到指定 commit
- 下载 release artifact
- 开发态本地引用

### 12.3 推荐首版策略

首版建议使用 pin 到上游 commit 的方式，理由如下：

- 透明可审计
- 易于对齐上游更新
- 回滚简单

需要记录的信息：

- 上游源地址
- commit hash
- 安装时间
- 校验结果

---

## 13. 状态、诊断与可观测性

### 13.1 `evcode doctor`

`doctor` 应覆盖以下诊断项：

- `codex` 可执行性
- EvCode 配置可读性
- VCO runtime 是否存在
- runtime pin 是否完整
- MCP active profile 是否存在
- 关键环境变量是否满足当前 profile
- 当前治理模式是否有效
- 默认 `XL` 工作流策略是否生效
- skeleton detector 与 plan detector 是否可用
- 阶段清理器是否可执行

### 13.2 `evcode status`

建议输出：

- governance mode
- workflow grade
- current profile
- runtime source
- runtime version
- mcp profile
- codex binary path

### 13.3 `evcode audit`

建议输出：

- runtime receipt
- pinned commit/release
- overlay 启用状态
- 当前 bootstrap contract 版本
- 默认系统提示词合同版本
- 最近一次 doctor/verify 结果

---

## 14. 失败模式与风控

### 14.1 默认 XL 带来的执行开销

风险：

- 简单任务也按 `XL` 规则启动
- 子代理并发过多导致资源浪费
- 无人值守模式可能在骨架或计划缺失时做出错误推进

缓解：

- 明确保留 `raw`
- 明确提供 `governance off`
- 启动时强制执行骨架与计划探测
- 将并发度纳入资源与健康约束，而不是无限放大

### 14.2 治理注入过重

风险：

- 对话过长
- 简单任务处理成本过高

缓解：

- 提供 `raw`
- 在 bootstrap contract 中引入显式绕过机制

### 14.3 与原生 Codex 演化脱节

风险：

- EvCode 过度包裹原生命令
- 版本升级后兼容性断裂

缓解：

- Compatibility Layer 尽量薄
- 避免依赖未公开内部状态
- 所有桥接逻辑都可通过 `doctor` 自检

### 14.4 上游 runtime 更新破坏稳定性

风险：

- `vco-skills-codex` 更新后行为变化
- 现有 profile/overlay 失配

缓解：

- 使用 pin
- 更新前执行 runtime verify
- 保留 rollback

### 14.5 环境污染

风险：

- 修改用户原有 `~/.codex`
- 不同 provider/profile 互相覆盖

缓解：

- EvCode 状态与 runtime 独立落地
- 对 `~/.codex` 的同步必须是显式动作

---

## 15. 实施阶段

### P1：最小可用产品

目标：让用户真正能“打开 EvCode 就进入 Vibe 且默认进入 XL”。

范围：

- CLI scaffold
- `evcode`
- `evcode exec`
- `evcode raw`
- session-start governance injection
- 默认系统提示词合同落地
- skeleton detector
- plan detector
- 默认 `XL` 工作流模式
- runtime pin 与最小 `doctor`

### P2：治理与 runtime 管理

目标：让 EvCode 成为可维护的治理代理。

范围：

- `governance on/off/status`
- `runtime sync/update/rollback/status`
- `profile` 基础管理
- `mcp` 兼容包装
- receipt 与 runtime 验证
- 无人值守推进策略
- 子代理 prompt suffix 注入
- 阶段结束清理器

### P3：产品化与发布

目标：可长期维护、升级与分发。

范围：

- bootstrap/install UX
- 审计视图
- adopt 模式
- 发布流程
- 文档与回归验证

---

## 16. 首版仓库建议

建议采用 TypeScript CLI 工程，原因如下：

- 调用 `codex` 子进程简单
- 处理 JSON 配置与文件系统方便
- 跨平台分发成本低于自研 Rust/Go 首版
- 与上游 shell/PowerShell/Python 脚本可良好共存

建议初始结构：

```text
docs/plans/
src/
  commands/
    run.ts
    exec.ts
    raw.ts
    doctor.ts
    governance.ts
    profile.ts
    runtime.ts
  codex/
    spawn.ts
    args.ts
  governance/
    bootstrap.ts
    policy.ts
    session-mode.ts
    skeleton-detector.ts
    plan-detector.ts
    workflow-spec.ts
  runtime/
    sync.ts
    verify.ts
    receipts.ts
  cleanup/
    node-zombies.ts
    temp-files.ts
    stage-cleaner.ts
  config/
    load.ts
    schema.ts
tests/
```

---

## 17. 待决策项

以下问题在实现前需要最终确认：

1. 骨架初始化的最小标志文件集合是什么。
2. “已有计划”的识别规则是否只认 `docs/plans/*.md`。
3. 子代理最大并发数是否由系统资源动态约束。
4. `~/.evcode` 与 `~/.codex` 的桥接策略是否允许自动同步。
5. runtime 来源是否采用 git pin 还是 release artifact。

---

## 18. 结论

方案 B 的本质不是重新造一个模型代理，而是在 `codex` 之上增加一个“常驻 Vibe 治理的会话控制层”，并将 `XL` 级工作流作为默认执行规范。EvCode 的核心成功标准只有三个：

- 用户打开 `evcode` 就天然处在 VCO 治理态。
- 用户打开 `evcode` 就默认进入 `XL` 工作流。
- 用户仍然感觉自己在使用一套与原生 Codex 高度兼容的工具。

只要坚持“会话前导注入、默认 XL、运行时解耦、原生兼容优先、默认治理但可逃生”这五条原则，EvCode 就能以较低风险演进成一个真正可用的 Codex 魔改代理工具。
