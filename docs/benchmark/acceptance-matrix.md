# EvCode Benchmark Acceptance Matrix

## Purpose

This document defines the minimum acceptance matrix for `EvCode Bench`.

## Required Scenarios

| Scenario | Input shape | Expected mode | Expected proof |
| --- | --- | --- | --- |
| One-shot complete task | full requirement | `benchmark_autonomous` | requirement, plan, execute, cleanup receipts |
| One-shot with inferred defaults | mostly complete requirement | `benchmark_autonomous` | requirement doc includes inferred assumptions |
| Existing plan resume | active plan present | `benchmark_autonomous` | execution traces back to existing plan |
| Failure path | task fails mid-phase | `benchmark_autonomous` | failure receipt plus cleanup receipt |

## Hard Gates

- fixed 6-stage order preserved
- no follow-up questioning after complete requirement
- no external MCP dependency for core closure
- verification evidence exists before success claims
- cleanup receipt exists before phase completion claims
