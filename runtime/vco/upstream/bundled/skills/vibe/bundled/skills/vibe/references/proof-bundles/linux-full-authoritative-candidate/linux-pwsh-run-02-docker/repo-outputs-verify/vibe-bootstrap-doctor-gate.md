# VCO Bootstrap Doctor Gate

- Gate Result: **PASS**
- Readiness State: **manual_actions_pending**
- Blocking Issues: `0`
- Manual Actions Pending: `9`
- Warnings: `0`
- Target Root: `/tmp/vco-linux-proof-run2/target-root`
- MCP Profile: `full`
- MCP Active File Exists: `True`

## Settings

- `OPENAI_API_KEY`: `placeholder`
- `ARK_API_KEY`: `placeholder`

## Plugin Readiness

- `superpowers`: status=`platform_plugin_required` install_mode=`manual-codex` next_step=`Provision via Codex-native MCP/plugin tooling (no Claude CLI command).`
- `everything-claude-code`: status=`platform_plugin_required` install_mode=`manual-codex` next_step=`Provision via Codex-native MCP/plugin tooling (no Claude CLI command).`
- `claude-code-settings`: status=`platform_plugin_required` install_mode=`manual-codex` next_step=`Provision via Codex-native MCP/plugin tooling (no Claude CLI command).`
- `hookify`: status=`platform_plugin_required` install_mode=`manual-codex` next_step=`Provision via Codex-native MCP/plugin tooling (no Claude CLI command).`
- `ralph-loop`: status=`platform_plugin_required` install_mode=`manual-codex` next_step=`Provision via Codex-native MCP/plugin tooling (no Claude CLI command).`
- `serena`: status=`platform_plugin_required` install_mode=`manual-codex` next_step=`Provision via Codex-native MCP/plugin tooling (no Claude CLI command).`
- `context7`: status=`platform_plugin_required` install_mode=`manual-codex` next_step=`Provision via Codex-native MCP/plugin tooling (no Claude CLI command).`
- `github`: status=`platform_plugin_required` install_mode=`manual-codex` next_step=`Provision via Codex-native MCP/plugin tooling (no Claude CLI command).`
- `prompts-chat`: status=`platform_plugin_required` install_mode=`manual-codex` next_step=`Provision prompts.chat MCP/API integration in Codex runtime; optional, used by prompt-lookup/prompt-overlay.`
- `claude-flow`: status=`ready` install_mode=`scripted` next_step=`none`
- `xan`: status=`platform_plugin_required` install_mode=`manual-codex` next_step=`Provision xan CLI manually (recommended on Windows: scoop install xan) for large CSV acceleration.`
- `fuck-u-code`: status=`platform_plugin_required` install_mode=`manual-codex` next_step=`Optional quality-debt analyzer for quality-debt-overlay; install manually if you want external analyzer hints beyond built-in risk scoring.`
- `ivy`: status=`platform_plugin_required` install_mode=`manual-codex` next_step=`Optional framework-interop backend for framework-interop-overlay; install manually in Python environment (for example: pip install ivy).`
- `leetcuda`: status=`platform_plugin_required` install_mode=`manual-codex` next_step=`Optional methodology source for cuda-kernel-overlay; no runtime dependency required. Keep GPL-3.0 boundary: do not vendor upstream code.`

## External Tools

- `git`: present=`True` required_for=`bootstrap`
- `npm`: present=`True` required_for=`claude-flow, ralph-wiggum`
- `python`: present=`False` required_for=`scrapling, ivy`
- `claude-flow`: present=`True` required_for=`mcp:claude-flow`
- `scrapling`: present=`False` required_for=`mcp:scrapling`
- `xan`: present=`False` required_for=`csv-acceleration`

## MCP Servers

- `github`: mode=`plugin` status=`platform_plugin_required` next_step=`Provision the corresponding Codex plugin in the host runtime.`
- `context7`: mode=`plugin` status=`platform_plugin_required` next_step=`Provision the corresponding Codex plugin in the host runtime.`
- `serena`: mode=`plugin` status=`platform_plugin_required` next_step=`Provision the corresponding Codex plugin in the host runtime.`
- `claude-flow`: mode=`stdio` status=`ready` next_step=`none`

## Secret Surfaces

- `ACTIVEPIECES_MCP_TOKEN`: status=`not_configured` storage=`environment, vault`
- `COMPOSIO_API_KEY`: status=`not_configured` storage=`environment, vault`
- `COMPOSIO_SESSION_MCP_URL`: status=`runtime_not_set` storage=`runtime`

