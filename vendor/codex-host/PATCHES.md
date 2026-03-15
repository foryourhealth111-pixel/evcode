# EvCode Host Patch Policy

This file inventories any EvCode-specific host patch carried on top of the selected Codex host.

## Current Policy

- prefer hook-level integration first
- only patch the host when a contract cannot be guaranteed through native hooks
- keep patches narrow, auditable, and attributable

## Current Patch Inventory

Applied-to-vendored-source: none.

Concrete release patch prepared:

- `vendor/codex-host/patches/subagent-vibe-suffix.patch`

Why it exists:

- `SubagentStart` hooks can inject context, but cannot rewrite child prompt text
- EvCode requires a physical ` $vibe` suffix on spawned child tasks
- the patch stays limited to subagent prompt finalization before `send_spawn_input(...)`

See:

- `vendor/codex-host/patches/README.md`
- `docs/architecture/evcode-host-patch-inventory.md`
- `scripts/verify/check_host_bridge.py`
