# EvCode Benchmark Adapter

## Status

- Status: Proposed benchmark integration design
- Date: 2026-03-15
- Scope: Harness adapter, compliance boundaries, and proof model

## 1. Purpose

This document defines how EvCode Bench should present itself to benchmark systems while preserving the same governed runtime core used by the normal distribution.

The safest public integration path is a `BaseAgent`-style adapter surface.

The benchmark adapter exists to:

- receive benchmark task input
- enter `benchmark_autonomous`
- run the governed runtime closure
- emit auditable receipts

It does not exist to create a separate benchmark-only orchestrator.

## 2. Adapter Principle

External benchmark systems should see:

- one agent class
- one task entry method
- one controlled execution surface

Internally, the adapter may invoke:

- EvCode host runtime
- embedded VCO runtime
- benchmark-safe capability runtime

The adapter must remain thin.

## 3. Public Contract

The adapter should expose a single task entry contract compatible with benchmark harness expectations.

Expected shape:

- receive task description
- receive benchmark-managed session or terminal
- execute through the provided environment
- return completion result plus proof artifacts

The adapter must not:

- bypass the benchmark environment
- create hidden external execution planes
- rely on human intervention

## 4. Runtime Entry

On benchmark task submission, the adapter must:

1. create run id
2. set default mode to `benchmark_autonomous`
3. initialize benchmark-safe capability policy
4. call the same governed runtime bridge used by the normal distribution
5. collect artifacts and receipts

The adapter must not skip:

- requirement freezing
- plan generation
- verification
- cleanup

## 5. Compliance Boundaries

The adapter must satisfy these hard boundaries:

### 5.1 Environment boundary

All execution must occur within the benchmark-provided session or environment.

### 5.2 Resource boundary

The adapter must not alter benchmark timeout or resource contracts unless explicitly allowed by benchmark rules.

### 5.3 Capability boundary

The benchmark channel must not require external MCP server availability to complete the core path.

### 5.4 Memory boundary

The benchmark channel must not depend on hidden task-specific external memory not available inside the benchmark environment.

### 5.5 Human boundary

No human-in-the-loop fallback is allowed once benchmark execution starts.

## 6. Capability Policy For Benchmark

Allowed baseline:

- embedded runtime surfaces
- benchmark-safe local tools
- provider paths explicitly allowed by benchmark policy

Restricted by default:

- optional MCP transports
- non-local hidden service dependencies
- environment-specific convenience surfaces that cannot be reproduced by evaluators

## 7. Proof Artifacts

Every benchmark run should leave behind a minimal proof bundle:

- skeleton receipt
- intent contract
- requirement doc
- execution plan
- execute receipt
- cleanup receipt
- benchmark adapter summary

Recommended additional artifacts:

- verification command ledger
- no-regression summary
- assumption ledger

## 8. Stability Proof

The benchmark adapter is considered stable only when:

- benchmark mode always preserves 6-stage order
- receipts are emitted for all runs
- incomplete runs still emit failure receipts
- capability policy decisions are visible in the summary

## 9. Usability Proof

The benchmark adapter is considered usable only when:

- a one-shot requirement can close the loop without further questioning
- requirement and plan outputs remain readable
- artifact locations are deterministic
- harness integration does not require ad hoc manual patching per task

## 10. Intelligence Proof

The benchmark adapter is considered intelligent only when:

- it can infer missing but necessary assumptions
- those assumptions are recorded, not hidden
- execution remains traceable to requirement and plan artifacts
- verification evidence exists before completion claims

## 11. Test Matrix

Required benchmark-adapter test families:

### Contract tests

- adapter enters `benchmark_autonomous`
- adapter preserves governed runtime stage order
- adapter writes expected artifact families

### Compliance tests

- no external MCP dependency for core path
- no unauthorized provider activation
- no timeout or resource mutation

### Scenario tests

- complete one-shot requirement
- incomplete but recoverable requirement with explicit inferred assumptions
- execution failure that still emits receipts
- cleanup-triggered completion path

### Replay tests

- same scenario can be replayed with comparable artifact structure

## 12. Packaging Consequence

The benchmark adapter should live in its own package boundary, for example:

- `packages/benchmark-adapter`

This package should depend on:

- host integration
- governed runtime bridge
- capability runtime
- receipt schema package

It should not reimplement any of them.
