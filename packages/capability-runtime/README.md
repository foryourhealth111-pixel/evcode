# Capability Runtime

This package owns capability selection across shared EvCode release channels.

Provider families:

- `embedded`
- `api`
- `mcp`

Release channels share this runtime and differ only by policy.

Specialist capability selection stays subordinate to governed routing and never bypasses Codex as final executor.
