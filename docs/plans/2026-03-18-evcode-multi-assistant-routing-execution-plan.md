# EvCode Multi-Assistant Routing Execution Plan

Date: 2026-03-18

## Internal Grade

L

This is a cross-cutting design and implementation program. It affects routing, capability policy, provider runtime, bridge behavior, and proof strategy, but it should still be executed under one product and one governed runtime core.

## Wave 1: Architecture Freeze

- define the multi-assistant control-plane model
- define the assistant capability matrix
- define trust boundaries for Codex, Claude Code, and Gemini CLI
- define the routing heuristics and override rules

## Wave 2: Adapter Layer

- introduce assistant adapters for Codex, Claude Code, and Gemini CLI
- define a normalized task packet format and normalized result contract
- add configuration for assistant availability, capability tags, and risk policy

## Wave 3: Delegation Runtime

- add a specialist delegation runtime under the existing governed runtime bridge
- ensure delegation occurs inside `plan_execute`, not as a new route authority
- persist assistant selection receipts and delegation artifacts

## Wave 4: Verification And Review

- add correctness verification for code-producing specialists
- add visual verification surfaces for design-heavy specialists
- require Codex-led final integration for high-risk repository modifications

## Wave 5: Channel Policy

- keep standard channel delegation-rich and collaborative
- keep benchmark channel conservative and reproducible
- explicitly gate any external specialist dependency inside benchmark mode

## Suggested Package Evolution

- `packages/specialist-routing`
- `packages/assistant-adapters`
- `packages/delegation-contracts`
- extend `packages/capability-runtime`
- extend `packages/provider-runtime`
- extend `packages/governed-runtime-bridge`

## Verification Commands For Later Implementation

```bash
python3 scripts/verify/check_contracts.py
python3 scripts/verify/check_host_bridge.py
python3 -m pytest tests/test_runtime_bridge.py tests/test_contracts.py tests/test_distribution_assembly.py tests/test_hooks.py
python3 -m pytest tests/test_app_entrypoints.py
```

## Rollback Rule

If multi-assistant routing begins to compete with the governed runtime router or weakens verification authority, remove assistant autonomy and keep only advisory-mode delegation until the trust boundary is corrected.

## Cleanup Expectation

- no hidden assistant state outside EvCode artifacts
- no silent prompt rewriting without receipts
- no design-only delegation path that can claim completion without engineering verification
