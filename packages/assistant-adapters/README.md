# Assistant Adapters

This package resolves assistant-provider settings, sanitizes provider snapshots, and optionally invokes advisory specialists.

Safety rules:

- never persist live API keys in tracked files
- advisory specialists are opt-in for live calls
- benchmark channel remains suppressible by policy
- Codex remains the only final executor
