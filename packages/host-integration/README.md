# Host Integration

This package owns the bridge between the host hook surfaces and the EvCode governed runtime.

Responsibilities:

- map host events to runtime stages
- attach hidden governance context
- wire subagent suffix policy
- preserve host-native UX

Real integration note:

- host-level bridge validation must prefer real host payload fixtures over invented local payloads
- any physical ` $vibe` suffix enforcement gap must be recorded in the host patch inventory
- the Python helper `packages/host-integration/python/upstream_bridge.py` performs source-level seam analysis against the materialized host
