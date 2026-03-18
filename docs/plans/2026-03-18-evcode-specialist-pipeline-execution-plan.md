# EvCode Specialist Pipeline Execution Plan

Date: 2026-03-18

## Internal Grade

L

This is a cross-cutting product program that changes architecture, policy, capability routing, verification, and proof strategy while preserving one governed runtime core.

## Wave 1: Architecture And Contract Freeze

- finalize assistant roles and authority boundaries
- define the specialist task packet schema
- define the specialist result schema
- define delegation receipt requirements
- define benchmark restrictions and override policy

## Wave 2: Provider And Adapter Foundation

- add a RightCodes-backed provider config surface for Codex, Claude, and Gemini
- implement assistant adapters under a shared contract
- define secure secret handling through environment variables and local non-tracked config only
- add availability checks and deterministic failure modes

## Wave 3: Specialist Routing Runtime

- introduce specialist routing inside `plan_execute`
- classify tasks by domain, risk, ambiguity, and evidence needs
- route planning-heavy tasks to Claude in advisory mode
- route visual-front-end tasks to Gemini in advisory or isolated-apply mode
- keep Codex as final engineering executor and verifier

## Wave 4: Engineering Integration Gate

- convert Claude plans into executable engineering plans
- normalize Gemini candidate UI diffs into repository-safe changes
- resolve front-end/back-end coupling in Codex-owned integration steps
- require Codex review before any candidate diff is accepted

## Wave 5: Verification And Proof

- add routing and policy unit tests
- add adapter contract tests with deterministic mocks
- add isolated candidate-diff integration tests
- add screenshot and artifact verification for Gemini-driven work
- add stability, usability, and intelligence proof receipts

## Wave 6: Controlled Rollout

- standard channel: enable advisory-only Claude and Gemini first
- standard channel: graduate Gemini to isolated apply for low-risk UI scopes only after proof
- benchmark channel: remain Codex-primary by default
- collect failure receipts and rollback when specialist routing weakens governance

## Suggested Repository Changes

- add `packages/specialist-routing`
- add `packages/assistant-adapters`
- add `packages/delegation-contracts`
- extend `packages/provider-runtime`
- extend `packages/capability-runtime`
- extend `packages/governed-runtime-bridge`
- add `config/assistant-policy.standard.json`
- add `config/assistant-policy.benchmark.json`
- add `config/specialist-routing.json`

## Verification Commands For Later Implementation

```bash
python3 scripts/verify/check_contracts.py
python3 scripts/verify/check_host_bridge.py
python3 -m pytest tests/test_runtime_bridge.py tests/test_contracts.py tests/test_distribution_assembly.py tests/test_hooks.py
python3 -m pytest tests/test_app_entrypoints.py
python3 -m pytest tests/test_specialist_routing.py tests/test_assistant_adapters.py tests/test_delegation_contracts.py
```

## Rollback Rule

If specialist routing begins to override the governed runtime's control-plane authority or weakens Codex-led verification, reduce the system to advisory-only specialist output and disable apply paths.

## Cleanup Expectation

- no tracked files may contain live API secrets
- every specialist delegation must leave a routing receipt and result receipt
- failed specialist calls must emit deterministic failure artifacts
- cleanup remains mandatory even when delegation fails midway
