# 安装路径：推荐满血（标准推荐安装）

这条路是 **大多数用户的默认推荐安装路径**。

它的目标不是“第一次安装就把整个生态所有面全部装满”，而是：

- 把仓库真正负责的面尽量一次装好
- 把 deep doctor / coherence / packaging 跑通
- 把剩余缺口诚实暴露出来

换句话说，这条路追求的是 **repo-governed closure + truth-first disclosure**。

对应分发面：

- `dist/manifests/vibeskills-codex.json`
- `dist/manifests/vibeskills-core.json`

## 标准推荐安装适合谁

- 想稳定把 VibeSkills 用起来的重度 AI 用户
- 想先验证这套治理面是否值得团队推广的负责人
- 想拿到比“最小可用”更完整的 doctor / gate 结果，但暂时不需要企业级审计和回滚流程的人

如果你是第一次认真使用这个仓库，**默认就应该先走这条路**。

## 这条路承诺什么

这条路承诺尽可能闭环 **仓库自己拥有的面**：

- shipped runtime payload
- bundled mirrors
- active MCP profile 物化
- deep doctor / runtime coherence 路径
- repo 侧治理文档、脚本和验证入口

## 这条路不承诺什么

这条路**不应该被误读为**：

- 自动安装所有宿主插件
- 自动在宿主平台里注册所有 MCP
- 自动补齐所有 provider secrets
- Windows、Linux、Claude Code、Generic Host 全部已经等价

因此，当这些宿主侧条件还没补齐时，`manual_actions_pending` 不是失败，而是**标准推荐安装的诚实结果**。

## 平台与宿主的真实边界

根据 `docs/universalization/host-capability-matrix.md` 与 `docs/universalization/platform-parity-contract.md`：

- Codex 是当前最强参考 lane，但仍然有 host-managed surfaces
- Windows 是当前权威参考路径
- Linux 只有在具备 `pwsh` 且能跑 PowerShell gates 时，才接近权威路径
- Linux 没有 `pwsh` 时属于 `degraded-but-supported`
- Claude Code 仍是 `preview`
- Generic Host 仍是 `advisory-only`

所以，**标准推荐安装 != 跨平台等价承诺**。

## 推荐命令（Codex lane）

这条默认链路现在会把 `scrapling` 视作 `full` profile 的默认本地 scraping surface；如果 Python 打包链路可用，安装脚本会尝试直接把它装上。

### Windows

```powershell
pwsh -File .\scripts\bootstrap\one-shot-setup.ps1
pwsh -File .\check.ps1 -Profile full -Deep
```

### Linux / macOS

```bash
bash ./scripts/bootstrap/one-shot-setup.sh
bash ./check.sh --profile full --deep
```

Truth-first 提示：

- Linux / macOS 如果没有 `pwsh`，出现 `authoritative PowerShell gates skipped` / `warn_and_skip` 类提示是预期降级行为
- 不要把“bash 这条链能跑”表述成“与 Windows 权威路径完全等价”

## 什么叫“标准推荐安装已经完成”

在当前标准里，完成状态除了看 one-shot 和 doctor，还要看三层默认面是否被正确表达：

- `scrapling`：应当被视作默认 full-profile 本地能力面
- `Cognee`：应当被视作默认长程图记忆 enhancement lane
- `Composio / Activepieces`：应当被视作 prewired 但 setup-required 的 external action surfaces

对多数用户，完成的标准是：

- one-shot bootstrap 跑通
- deep doctor 跑通
- repo-governed surfaces 已闭环
- 剩余缺口被清晰列出来，而不是被静默吞掉

因此，这条路合理的完成状态有两个：

- `fully_ready`
- `manual_actions_pending`

真正应当阻塞继续使用的是：

- `core_install_incomplete`

## 你仍然需要宿主侧完成的事

即使这条路执行成功，以下仍可能属于宿主侧 responsibility：

- plugin provisioning / enablement
- MCP registration 与授权，尤其是 plugin-backed MCP surfaces
- `OPENAI_API_KEY` 等 provider secrets 的安全存储与可用性
- 某些外部 CLI 的安装与版本治理

## 如果你想进一步增强，按这条顺序加

这里最重要的不是“多装”，而是不要把不同层次的面混在一起：

- `scrapling` 是默认本地 runtime 面
- `Cognee` 是默认长程增强面
- `Composio / Activepieces` 是默认预接线但 setup-required 的外部操作面

不要一开始全加。更稳的增强路线是：

### 第一层：先补在线能力

- 配置你实际需要的 provider secrets
- 例如 `OPENAI_API_KEY`

### 第二层：先补默认推荐的宿主插件

优先：

- `superpowers`
- `hookify`

这是对多数用户最值得优先增加的宿主增强面。

### 第三层：再补 plugin-backed MCP surfaces

在进入 plugin-backed MCP 之前，先确认一件事：

- `Cognee` 应该只承担 long-term graph memory
- 它不是第二个 `state_store`
- 如果你只是想补长程图记忆增强，先保持这个边界，而不是引入新的 session truth

例如：

- `github`
- `context7`
- `serena`

只有你确实要用这些能力时再补，不要为了“看起来完整”而全开。

### 第四层：其余宿主插件按真实缺口补

`Composio / Activepieces` 不属于“默认自动打开的第四层增强”。它们更适合被理解为：

- repo 已经预接线并提供治理语义
- 但默认仍然 setup-required
- 只有在你确实需要外部操作能力时，再补 secret、endpoint 与 host registration

默认延后：

- `everything-claude-code`
- `claude-code-settings`
- `ralph-loop`

只有在 doctor 仍然明确指向这些缺口时，再补这三项。

### 第五层：最后补可选 CLI / 工具链增强

例如：

- `claude-flow`
- `xan`
- `ivy`

这些都属于增强项，不属于标准推荐安装的默认前置。

## 什么时候该升级到企业治理路径

当你需要下面这些能力时，就不该停留在标准推荐安装：

- 固定版本审计
- 安装证据留存
- 宿主侧责任人分配
- 回滚准备
- 团队级交付口径

这时请进入：

- [`enterprise-governed-path.md`](./enterprise-governed-path.md)

## 什么时候不该走这条路

- 你只想尽快看一下仓库能不能跑
  这时先走 [`minimal-path.md`](./minimal-path.md)
- 你需要团队级、可审计、可回滚的安装交付
  这时直接走 [`enterprise-governed-path.md`](./enterprise-governed-path.md)
- 你在 Claude Code / Generic Host 上，却期待当前仓库提供与 Codex 等价的安装闭环
  目前不成立
