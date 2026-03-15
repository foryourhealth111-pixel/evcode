---
name: auto-plugin-discovery
enabled: true
event: prompt
pattern: .+
action: warn
---

**Auto Plugin Discovery Reminder**

Before starting this task, analyze the user's request and determine if any specialized tools or plugins could help.

**Step 1: Classify the task type**
Identify keywords and intent: coding, testing, review, documentation, git, database, UI, deployment, debugging, data analysis, etc.

**Step 2: Search for relevant tools**
Use `ToolSearch` with relevant keywords to discover available MCP tools that match the task. Examples:
- Coding/implementation: search for language-specific or framework tools
- Git/PR operations: search "github" tools
- Testing/E2E: search "playwright" or test-related tools
- Documentation: search "context7" for library docs
- Code analysis: search "serena" for semantic code tools
- UI development: search "playwright" for browser tools

**Step 3: Decide whether to use discovered tools**
Only invoke discovered tools if they genuinely add value to the current task. Skip ToolSearch if:
- The task is a simple question or conversation
- You already know which tools to use
- The task does not involve any tool-assisted operations

**Available plugin categories for reference:**
- `github` - GitHub operations (PRs, issues, code search)
- `context7` - Library documentation lookup
- `playwright` - Browser automation and E2E testing
- `serena` - Semantic code analysis, symbol navigation, project memory
- `ide` - IDE diagnostics and code execution

Be smart about this. Do not force ToolSearch when it is not needed, but do proactively discover tools when the task could benefit from specialized capabilities.
