# EvCode Upstream Materialization And Host-Level Bridge

## Status

- Status: Proposed authoritative materialization design
- Date: 2026-03-15
- Scope: Real upstream ingestion, host-level bridge integration, and proof model

## 1. Purpose

This document defines how EvCode moves from:

- local contract skeleton
- local governed runtime bridge
- local benchmark adapter scaffold

to:

- real host upstream materialization
- real embedded VCO runtime materialization
- real host-level hook bridge integration

The goal is not to keep simulating the final system with repo-local stand-ins.
The goal is to converge the current skeleton into a real distributable product.

## 2. Authoritative Inputs

EvCode now has three authoritative inputs:

1. selected host baseline
   - `stellarlinkco/codex`
2. selected governed runtime truth
   - `vco-skills-codex` governed runtime `v2.3.47`
3. EvCode local contracts
   - dual-distribution model
   - benchmark adapter boundary
   - fixed 6-stage runtime contract

The materialization and bridge work must preserve all three.

## 3. Materialization Goals

### 3.1 Host materialization

EvCode must materialize the real Codex host under:

- `vendor/codex-host`

This is not only a source mirror.
It is the authoritative host baseline from which EvCode release artifacts are built.

### 3.2 Runtime materialization

EvCode must materialize the real VCO runtime under:

- `runtime/vco`

This materialized runtime must include:

- governed runtime contracts
- scripts
- templates
- policies
- protocol references
- required skill and bundle surfaces

### 3.3 Bridge materialization

EvCode must replace the current repo-local pseudo-bridge with a host-coupled bridge that:

- consumes real host hook payloads
- writes governed runtime artifacts
- attaches hidden governance context
- preserves host-native UX

## 4. Materialization Architecture

The product should be treated as four stacked layers:

1. `vendor/codex-host`
2. `runtime/vco`
3. `packages/host-integration`
4. `apps/evcode` and `apps/evcode-bench`

### 4.1 Host layer

Responsibilities:

- TUI
- session lifecycle
- command parsing
- native team execution
- native hook dispatch
- resume and fork

### 4.2 Runtime layer

Responsibilities:

- governed runtime truth
- requirement freeze semantics
- plan generation semantics
- benchmark mode semantics
- protocol and policy truth

### 4.3 Bridge layer

Responsibilities:

- hook-to-runtime mapping
- artifact path reconciliation
- mode defaulting
- channel-specific policy attachment
- subagent suffix enforcement

### 4.4 App layer

Responsibilities:

- channel packaging
- profile defaults
- release metadata
- benchmark adapter surface

## 5. Host-Level Bridge Design

### 5.1 Required host hook surfaces

The bridge should bind to these host events:

- `user_prompt_submit`
- `subagent_start`
- `task_completed`
- `stop`

Secondary surfaces may be used later:

- `session_start`
- `session_end`
- `worktree_create`
- `worktree_remove`

### 5.2 `user_prompt_submit` bridge

This becomes the primary runtime seam.

Required behavior:

1. inspect workspace and existing artifacts
2. determine distribution channel and runtime mode
3. build minimal hidden governed context
4. attach requirement and plan references when they exist
5. preserve blank-start UX until the first user turn

### 5.3 `subagent_start` bridge

This becomes the subagent control seam.

Required behavior:

1. carry requirement and plan references into child work
2. attach governed runtime metadata
3. ensure prompt finalization preserves the ` $vibe` suffix contract

If the host hook API cannot guarantee physical prompt suffix mutation, EvCode may carry one narrow host patch in prompt build finalization.

### 5.4 `task_completed` bridge

Required behavior:

- write execution and verification receipts
- update phase traceability state
- preserve requirement-to-plan-to-execution lineage

### 5.5 `stop` bridge

Required behavior:

- trigger cleanup
- write cleanup receipt
- persist node audit result

## 6. Upstream Ingestion Strategy

### 6.1 Host ingestion

Recommended strategy:

- pin remote and branch in `config/sources.lock.json`
- clone a clean upstream snapshot into `vendor/codex-host`
- carry EvCode patches separately, not as undocumented edits

Recommended supporting files:

- `vendor/codex-host/PATCHES.md`
- `vendor/codex-host/UPSTREAM.md`
- `vendor/codex-host/patches/*.patch`

### 6.2 Runtime ingestion

Recommended strategy:

- pin runtime source and version in `config/sources.lock.json`
- materialize required runtime surfaces into `runtime/vco`
- keep receipt markers proving freshness and parity

Recommended supporting files:

- `runtime/vco/MATERIALIZATION.md`
- `runtime/vco/freshness.json`
- `runtime/vco/required-runtime-markers.json`

### 6.3 Patch discipline

Patch discipline must be explicit:

- host upstream remains attributable
- runtime upstream remains attributable
- EvCode-only modifications are isolated
- no silent direct edits inside vendored code

## 7. Distribution-Specific Wiring

### Standard channel

- mode default: `interactive_governed`
- broader capability allowlist
- collaboration-friendly pauses remain enabled

### Benchmark channel

- mode default: `benchmark_autonomous`
- benchmark-safe provider policy
- no dependency on external MCP for core closure
- thin benchmark adapter only

Both channels must still consume the same materialized host and runtime.

## 8. Testing Strategy

### 8.1 Materialization tests

Verify:

- host source exists and is pinned
- runtime source exists and is pinned
- freshness markers match expected source lock
- required runtime files are present

### 8.2 Hook integration tests

Verify:

- `user_prompt_submit` receives real host payloads
- `subagent_start` receives real child-work payloads
- `stop` path writes cleanup receipts
- no visible startup prompt pollution occurs
- host seam analysis proves whether hook-only integration is sufficient or a narrow host patch is required

### 8.3 End-to-end runtime tests

Verify:

- standard channel completes governed runs
- benchmark channel completes governed runs
- real host bridge preserves stage order
- real host bridge preserves artifact locations

### 8.4 Distribution diff tests

Verify:

- standard and benchmark channels share runtime truth
- only approved policy and packaging surfaces differ

### 8.5 Compliance tests

Verify:

- benchmark channel does not require external MCP for core closure
- no second orchestrator has been introduced
- benchmark adapter stays within the declared boundary

## 9. Stability, Usability, And Intelligence Proof

### Stability

Prove:

- same host and runtime pins across channels
- same stage order across channels
- same receipt schema across channels
- degradation does not remove governed closure

### Usability

Prove:

- standard channel preserves host-native ergonomics
- benchmark channel closes one-shot tasks without follow-up questioning
- artifacts are deterministic and inspectable

### Intelligence

Prove:

- requirement inference is recorded in benchmark mode
- plans remain traceable to frozen requirements
- cleanup remains mandatory and evidenced
- subagent governance remains enforced

## 10. Real Host-Level Seam Result

After materializing `stellarlinkco/codex`, EvCode can now prove the actual bridge boundary:

- `user_prompt_submit` is a viable per-turn governance seam
- `subagent_start` is a viable child-context seam
- `subagent_start` is not a viable child-prompt-rewrite seam

The key source fact is that the host injects `SubagentStart` hook output as an extra developer message and then sends the original child `input_items`.
Because the host contract limits `updatedInput` to `pre_tool_use`, a hook alone cannot physically enforce the required child-task suffix.

Therefore the real integration design is:

1. keep hook-driven governance for per-turn and child-context injection
2. keep host-native UX untouched
3. carry one minimal release patch for child prompt finalization only

The prepared patch lives at:

- `vendor/codex-host/patches/subagent-vibe-suffix.patch`

And the proof entrypoint lives at:

- `scripts/verify/check_host_bridge.py`

## 11. Risks

### Risk 1: vendor drift

If upstream host or runtime changes silently, local contracts may stop matching reality.

Mitigation:

- source lock pinning
- freshness markers
- materialization tests

### Risk 2: hidden patch sprawl

If EvCode edits vendored host files directly without patch discipline, long-term maintenance will fail.

Mitigation:

- isolated patch manifests
- explicit host patch inventory

### Risk 3: hook semantic mismatch

The host hook payload may differ from the assumptions in the current local bridge.

Mitigation:

- capture payload fixtures from the real host
- convert pseudo-hook tests into real fixture-driven tests

### Risk 4: benchmark drift into second product

If benchmark channel begins carrying unique runtime logic, dual-distribution truth is lost.

Mitigation:

- shared-core release diff gate
- adapter thinness tests

## 12. Completion Standard

This phase is complete only when:

1. host source is materialized
2. runtime source is materialized
3. bridge uses real host hook payloads
4. patch inventory is explicit
5. materialization, bridge, and compliance tests pass
6. proof documents are updated from simulated bridge evidence to real host evidence
