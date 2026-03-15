# Host Patch Inventory

This directory holds EvCode-specific host patches when native hook surfaces are insufficient.

Rules:

- every patch must have a clear non-goal
- every patch must be referenced in `PATCHES.md`
- every patch must have a matching verification statement

No production patch should be added here without an explicit inventory entry.

Current concrete patch:

- `subagent-vibe-suffix.patch`

Patch scope:

- add one helper that appends ` $vibe` to the first text input if missing
- call that helper in `spawn_agent`
- call that helper in `spawn_team`
- do not alter any unrelated host behavior
