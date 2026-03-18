# EvCode Governed Specialist Repair Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Repair EvCode's specialist architecture so skills, MCP, memory, and specialist delegation remain governed by one VCO control plane while Claude and Gemini contribute real specialist value.

**Architecture:** Keep VCO as the only control plane, Codex as the only engineering authority, and introduce skill-capsule compilation plus MCP proxy mediation for specialist workers. Roll out advisory-only first, then isolated apply for low-risk UI scopes only after proof.

**Tech Stack:** Node.js CLI entrypoints, JSON policy/config files, provider runtime, capability runtime, governed runtime bridge, Python verification scripts, pytest contract tests, artifact-backed receipts.

---

## Requirement Source

- `docs/requirements/2026-03-18-evcode-governed-specialist-repair.md`

## Internal Grade

- `L` for implementation program design
- expected rollout execution: `L -> XL` if parallelized later

## Wave 1: Freeze governance contracts

### Task 1: Codify control-plane ownership

**Files:**
- Modify: `docs/architecture/evcode-specialist-pipeline.md`
- Modify: `docs/architecture/evcode-multi-assistant-routing.md`
- Modify: `docs/architecture/evcode-multi-assistant-risk-review.md`
- Create: `docs/architecture/evcode-governed-specialist-repair.md`

**Steps:**
1. Document that VCO owns governance, skills, MCP authority, memory truth, receipts, and cleanup.
2. Document that Codex alone owns engineering execution, integration, verification, and completion claims.
3. Document that Claude and Gemini are governed workers, not peer orchestrators.
4. Add explicit rejection of per-CLI native control-plane duplication for the first stable rollout.

**Verification:**
- `rg -n "control plane|skill capsule|MCP|completion authority" docs/architecture`

### Task 2: Freeze authority-tier policy

**Files:**
- Modify: `config/assistant-policy.standard.json`
- Modify: `config/assistant-policy.benchmark.json`
- Modify: `config/specialist-routing.json`
- Modify: `profiles/standard/profile.json`
- Modify: `profiles/benchmark/profile.json`

**Steps:**
1. Encode `advisory_only` as the standard initial authority for Claude and Gemini.
2. Encode benchmark suppression or strict narrowing rules.
3. Add explicit policy fields for `codex_only_mutations`, `proxy_only_capabilities`, and `specialist_read_only_capabilities`.
4. Ensure status surfaces can explain these settings deterministically.

**Verification:**
- `python3 scripts/verify/check_contracts.py`
- `python3 -m pytest tests/test_contracts.py tests/test_app_entrypoints.py -q`

## Wave 2: Add skill-capsule compilation

### Task 3: Define skill-capsule schema

**Files:**
- Modify: `packages/delegation-contracts/src/index.ts`
- Modify: `packages/delegation-contracts/README.md` if present
- Modify: `tests/test_delegation_contracts.py`

**Steps:**
1. Add schema types for `skill_capsule`, `control_plane_only_rules`, `compiled_guidance`, and `tool_bound_constraints`.
2. Add validation rules that prevent control-plane-only skills from being delegated as executable authority.
3. Add contract tests for representative Claude and Gemini packets.

**Verification:**
- `python3 -m pytest tests/test_delegation_contracts.py -q`

### Task 4: Implement capsule compiler entrypoint

**Files:**
- Modify: `packages/capability-runtime/src/index.ts`
- Modify: `packages/capability-runtime/README.md`
- Modify: `tests/test_contracts.py`
- Modify: `tests/test_runtime_bridge.py`

**Steps:**
1. Add a deterministic function that maps routing context plus selected skills to a compact specialist capsule.
2. Ensure capsules include constraints, output schema expectations, and prohibited actions.
3. Record capsule generation in delegation receipts.

**Verification:**
- `python3 -m pytest tests/test_contracts.py tests/test_runtime_bridge.py -q`

## Wave 3: Repair memory ownership

### Task 5: Define authoritative memory surfaces

**Files:**
- Modify: `packages/governed-runtime-bridge/src/index.ts`
- Modify: `packages/governed-runtime-bridge/README.md`
- Modify: `scripts/runtime/runtime_lib.py`
- Modify: `tests/test_runtime_bridge.py`

**Steps:**
1. Explicitly model requirement docs, plans, config, and receipts as authoritative context layers.
2. Mark specialist-local memory as ephemeral in runtime bridge metadata.
3. Ensure task packet assembly pulls from governed artifacts rather than ad hoc conversation fragments.

**Verification:**
- `python3 -m pytest tests/test_runtime_bridge.py tests/test_hooks.py -q`

## Wave 4: Repair MCP placement

### Task 6: Add MCP authority model

**Files:**
- Modify: `packages/capability-runtime/src/index.ts`
- Modify: `packages/governed-runtime-bridge/src/index.ts`
- Modify: `config/host-integration.json`
- Modify: `tests/test_contracts.py`
- Modify: `tests/test_runtime_bridge.py`

**Steps:**
1. Introduce capability classes: `codex_only`, `proxy_mediated`, `specialist_read_only`.
2. Prevent write-side capabilities from being exposed directly to specialists by default.
3. Add result normalization for proxy-mediated capability responses.
4. Ensure MCP absence degrades cleanly without violating runtime truth.

**Verification:**
- `python3 -m pytest tests/test_contracts.py tests/test_runtime_bridge.py -q`

### Task 7: Add operator-facing MCP policy visibility

**Files:**
- Modify: `apps/evcode/bin/evcode.js`
- Modify: `apps/evcode-bench/bin/evcode-bench.js`
- Modify: `README.md`
- Modify: `docs/configuration/openai-compatible-provider-setup.md`

**Steps:**
1. Expose concise status output showing specialist authority tier and MCP policy class.
2. Document that MCP is a capability transport, not a second orchestrator.
3. Document how capability proxying works and what is intentionally withheld from specialists.

**Verification:**
- `node apps/evcode/bin/evcode.js status --json`
- `node apps/evcode-bench/bin/evcode-bench.js status --json`

## Wave 5: Strengthen routing and result mediation

### Task 8: Extend routing context for governance-aware delegation

**Files:**
- Modify: `packages/specialist-routing/src/index.ts`
- Modify: `packages/assistant-adapters/src/index.ts`
- Modify: `tests/test_specialist_routing.py`
- Modify: `tests/test_assistant_adapters.py`

**Steps:**
1. Add routing inputs for authority tier, required skill capsule types, capability needs, and benchmark suppression.
2. Ensure planning-heavy work favors Claude, visual-heavy work favors Gemini, and risky or cross-cutting work returns to Codex.
3. Normalize specialist outputs into result packets that include capability requests and unresolved risks.

**Verification:**
- `python3 -m pytest tests/test_specialist_routing.py tests/test_assistant_adapters.py -q`

### Task 9: Add failure and degradation tests

**Files:**
- Modify: `tests/test_assistant_adapters.py`
- Modify: `tests/test_specialist_routing.py`
- Modify: `tests/test_app_entrypoints.py`

**Steps:**
1. Test provider unavailability for one specialist while others remain usable.
2. Test policy-denied capability requests.
3. Test benchmark suppression and Codex-only fallback.
4. Test missing MCP enhancement as allowed degradation.

**Verification:**
- `python3 -m pytest tests/test_assistant_adapters.py tests/test_specialist_routing.py tests/test_app_entrypoints.py -q`

## Wave 6: Realistic proof and operator simulation

### Task 10: Build proof scenarios

**Files:**
- Modify: `scripts/verify/probe_assistant_providers.py`
- Create: `docs/status/evcode-governed-specialist-repair-proof.md`
- Create: `docs/status/evcode-governed-specialist-repair-report.json`

**Steps:**
1. Add probe coverage for authority tier and capability class reporting.
2. Run realistic planning, visual, mixed UI, backend-safe, and benchmark scenarios.
3. Record whether routing, skills, capability proxying, and receipts behaved as intended.
4. Sanitize outputs and save proof artifacts.

**Verification:**
- `node apps/evcode/bin/evcode.js probe-providers --json --live`
- `node apps/evcode/bin/evcode.js status --json`
- `node apps/evcode-bench/bin/evcode-bench.js status --json`

### Task 11: Simulate operator journeys

**Files:**
- Create: `docs/status/evcode-governed-specialist-repair-operator-simulation.md`

**Steps:**
1. Simulate a documentation task routed to Claude.
2. Simulate a premium visual task routed to Gemini with Codex integration ownership.
3. Simulate a mixed full-stack task where specialists advise but Codex remains final executor.
4. Simulate a denied specialist write-capability request and verify operator-visible explanation.

**Verification:**
- manual trace review of generated receipts and status artifacts
- optional `python3 -m pytest tests/test_hooks.py tests/test_runtime_bridge.py -q`

## Rollout Gates

### Gate A: Documentation and policy complete

Required evidence:
- updated architecture docs
- updated policy/config docs
- contract tests passing

### Gate B: Capsule and MCP mediation stable

Required evidence:
- contract and runtime tests passing
- status surfaces show authority and capability policy clearly
- degradation tests passing

### Gate C: Advisory production qualification

Required evidence:
- real provider probe passes in standard channel
- benchmark suppression still passes
- proof artifacts show specialists never own completion

### Gate D: Isolated apply pilot qualification

Required evidence:
- all prior gates green
- candidate apply limited to low-risk UI scopes
- Codex integration and rollback proof exists

## Rollback Rules

- if routing begins to behave like a second control plane, disable specialist delegation and return to Codex-only execution
- if specialists require direct write-side MCP to remain useful, stop rollout and redesign the task decomposition instead of widening permissions casually
- if specialist-local memory becomes necessary for correctness, move the missing context into governed artifacts or capsules
- if benchmark reproducibility weakens, restore strict benchmark suppression immediately

## Phase Cleanup Expectations

- no secrets written to tracked files
- no temporary packet files left outside governed artifacts
- no unmanaged Node processes created by the rollout tasks
- every proof run emits routing, result, verification, and cleanup receipts
- failed specialist or MCP calls leave deterministic failure artifacts rather than silent drops

## Recommended Execution Order

1. Finish Wave 1 before changing runtime behavior.
2. Finish Waves 2 and 3 before widening specialist responsibilities.
3. Finish Wave 4 before exposing any new specialist tool access.
4. Finish Wave 5 before trusting live advisory flows.
5. Finish Wave 6 before claiming production readiness.

## Suggested First Implementation Slice

If the team wants the smallest high-value start, implement this slice first:

1. authority-tier policy fields in config
2. skill-capsule schema and compiler skeleton
3. MCP capability classes with proxy-only specialist behavior
4. status/doctor output that explains the resulting governance state

This slice improves architecture honesty immediately without overcommitting to autonomous specialist behavior.
