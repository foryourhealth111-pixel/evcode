# EvCode VCO Benchmark Integration Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build EvCode as a host-native Codex distribution that embeds the VCO governed runtime, ships both standard and benchmark release channels from one core, and proves the design with contract, integration, compliance, and proof-bundle testing.

**Architecture:** EvCode adopts a hook-rich Codex host, embeds VCO `v2.3.43` governed runtime as the control-plane truth, and bridges host hooks into the fixed 6-stage governed runtime. The product ships one codebase and one runtime core, then emits two release channels: `EvCode` with `interactive_governed` defaults and `EvCode Bench` with `benchmark_autonomous` defaults plus a benchmark-safe adapter.

**Tech Stack:** Codex host fork, embedded VCO runtime assets, host hook integration, benchmark-safe adapter layer, JSON receipts, Markdown requirements and plans, verification gates, package-based dual distribution.

---

## 1. Authoritative Decisions

1. Host baseline: `stellarlinkco/codex`
2. Embedded governance truth: `vco-skills-codex` governed runtime `v2.3.43`
3. Product model: one codebase, one runtime core, two release channels
4. Standard default mode: `interactive_governed`
5. Benchmark default mode: `benchmark_autonomous`
6. Benchmark public surface: thin `BaseAgent`-style adapter
7. MCP remains a capability transport, not a second orchestrator

## 2. Success Criteria

The plan is complete only when:

1. EvCode launches through the selected host without a wrapper-owned REPL.
2. User turns are governed through real host hook surfaces.
3. Subagent prompts end with ` $vibe`.
4. Standard and benchmark channels share the same governed runtime core.
5. Benchmark tasks can complete through the adapter without interactive questioning after a complete requirement is given.
6. Requirement, plan, execution, verification, and cleanup artifacts are emitted for both channels.
7. Stability, usability, and intelligence are proved with explicit receipts and test evidence.

## 3. Repository Structure Target

Recommended target layout:

- `apps/evcode`
- `apps/evcode-bench`
- `vendor/codex-host`
- `runtime/vco`
- `packages/host-integration`
- `packages/governed-runtime-bridge`
- `packages/capability-runtime`
- `packages/provider-runtime`
- `packages/benchmark-adapter`
- `packages/receipts`
- `packages/cleanup`
- `profiles/standard`
- `profiles/benchmark`

## 4. Wave Plan

### Wave 1: Freeze Product Truth

**Objective:** align all local docs around the selected host, embedded VCO governed runtime, and dual-distribution model.

**Files:**
- Create: `docs/architecture/evcode-host-runtime-bridge.md`
- Create: `docs/architecture/evcode-dual-distribution.md`
- Create: `docs/architecture/evcode-benchmark-adapter.md`
- Modify: `docs/architecture.md`
- Modify: `README.md`

**Step 1: Add host/runtime bridge document**

Write the host-hook mapping and bridge invariants.

**Step 2: Add dual-distribution document**

Define shared core, allowed differences, and channel defaults.

**Step 3: Add benchmark adapter document**

Define compliance boundaries and proof artifacts.

**Step 4: Update top-level architecture pointers**

Point `README.md` and `docs/architecture.md` to the new authoritative docs.

**Step 5: Review for contradiction**

Check that the new docs do not conflict with the existing reset baseline.

### Wave 2: Vendor The Host And Runtime

**Objective:** establish the physical repo structure for the selected host and embedded VCO runtime.

**Files:**
- Create: `vendor/codex-host/README.md`
- Create: `runtime/vco/README.md`
- Create: `profiles/standard/README.md`
- Create: `profiles/benchmark/README.md`

**Step 1: Vendor host boundary**

Define how the host fork is brought into the repo and pinned.

**Step 2: Vendor runtime boundary**

Define how VCO assets are mirrored or pinned under `runtime/vco`.

**Step 3: Freeze profile defaults**

Record the mode and capability policy defaults for both channels.

**Step 4: Add freshness markers**

Define markers that prove host/runtime parity for install and release.

### Wave 3: Build Host Integration

**Objective:** connect host hooks to the governed runtime bridge.

**Files:**
- Create: `packages/host-integration/README.md`
- Create: `packages/governed-runtime-bridge/README.md`
- Create: `packages/receipts/README.md`
- Create: `packages/cleanup/README.md`

**Step 1: Define `user_prompt_submit` bridge**

Map host user-turn events into governed runtime mode selection and context attachment.

**Step 2: Define `subagent_start` bridge**

Ensure child tasks inherit requirement, plan, and ` $vibe` suffix policy.

**Step 3: Define phase receipt bridge**

Map execution and cleanup receipts into stable artifact paths.

**Step 4: Define hook observability**

Add receipt-backed evidence for hook execution, not inferred log guesses.

### Wave 4: Build Dual Release Channels

**Objective:** create standard and benchmark release packaging without forking runtime truth.

**Files:**
- Create: `apps/evcode/README.md`
- Create: `apps/evcode-bench/README.md`
- Create: `packages/provider-runtime/README.md`
- Create: `packages/capability-runtime/README.md`

**Step 1: Standard channel packaging**

Set `interactive_governed` and standard provider policy defaults.

**Step 2: Benchmark channel packaging**

Set `benchmark_autonomous` and benchmark-safe provider policy defaults.

**Step 3: Shared runtime imports**

Ensure both channels load the same governed runtime core.

**Step 4: Package diff audit**

Prove only the allowed differences exist between channels.

### Wave 5: Implement Benchmark Adapter

**Objective:** expose a thin benchmark-facing adapter on top of the shared runtime.

**Files:**
- Create: `packages/benchmark-adapter/README.md`
- Create: `docs/benchmark/acceptance-matrix.md`
- Create: `docs/benchmark/compliance-proof.md`

**Step 1: Define adapter entry contract**

Map benchmark task input to governed runtime invocation.

**Step 2: Define compliance policy**

Lock down capability use, external dependencies, and harness boundaries.

**Step 3: Define proof bundle**

Specify benchmark run artifacts and success/failure receipts.

### Wave 6: Prove Stability, Usability, And Intelligence

**Objective:** establish evidence that the design is stable, usable, and intelligent.

**Files:**
- Create: `docs/status/stability-proof.md`
- Create: `docs/status/usability-proof.md`
- Create: `docs/status/intelligence-proof.md`

**Step 1: Stability proof**

Define contract, replay, degradation, and release stability evidence.

**Step 2: Usability proof**

Define onboarding, run-closure, artifact readability, and degraded-host usability evidence.

**Step 3: Intelligence proof**

Define requirement completeness, plan traceability, execution alignment, and cleanup completion evidence.

## 5. Test Plan

### 5.1 Contract Tests

Verify:

- fixed 6-stage order
- mode default correctness
- receipt path correctness
- requirement and plan traceability

### 5.2 Hook Integration Tests

Verify:

- native start remains blank until user input
- first user prompt triggers governance
- subagent start triggers child governance context
- cleanup hook triggers phase cleanup and receipts

### 5.3 Scenario Tests

Required scenarios:

- unclear task in standard mode
- complete one-shot task in standard mode
- complete one-shot task in benchmark mode
- existing requirement without plan
- existing plan resume
- XL parallelizable task
- execution failure with cleanup receipts

### 5.4 Compliance Tests

Verify:

- benchmark channel does not require external MCP servers for core closure
- provider allowlist is enforced
- no unauthorized resource mutation
- no hidden human intervention path

### 5.5 Release Diff Tests

Verify:

- standard and benchmark channels share the same runtime contract
- channel-specific differences are limited to approved policy and packaging surfaces

## 6. Stability Proof Model

EvCode is stable only when:

- the runtime contract does not drift between channels
- replay produces the same artifact family shape
- degraded optional dependencies do not break governed closure
- release upgrades do not silently change stage order or receipt schemas

## 7. Usability Proof Model

EvCode is usable only when:

- normal channel feels host-native
- no startup prompt pollution exists
- benchmark channel can close a one-shot task without extra questions
- artifacts are readable by operators and evaluators

## 8. Intelligence Proof Model

EvCode is intelligent only when:

- it extracts a complete intent contract from user input or benchmark inference
- it freezes a requirement doc before execution
- it writes an actionable XL-style plan
- execution remains traceable to requirement and plan artifacts
- cleanup is treated as part of task intelligence, not an afterthought

## 9. Risks

### Risk 1: Host hook surface is insufficient for subagent suffix mutation

Mitigation:

- allow one narrow prompt-build patch in the host layer

### Risk 2: Benchmark channel accidentally depends on optional MCP surfaces

Mitigation:

- enforce benchmark provider allowlist in policy and tests

### Risk 3: Standard and benchmark distributions drift over time

Mitigation:

- release diff tests and shared runtime version pinning

### Risk 4: Documentation truth drifts from implementation

Mitigation:

- every wave adds tests or proof artifacts tied to the documented contract

## 10. Completion Gate

Do not claim this plan implemented until all of the following are true:

1. host and runtime are vendored or pinned
2. hook bridge exists
3. dual distribution packaging exists
4. benchmark adapter exists
5. test families exist
6. proof documents exist
7. receipts demonstrate runtime truth instead of inferred behavior
