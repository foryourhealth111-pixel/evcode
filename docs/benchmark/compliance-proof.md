# EvCode Benchmark Compliance Proof

## Goal

This document defines the benchmark compliance proof target for `EvCode Bench`.

## Compliance Boundaries

- execution stays inside the benchmark-provided environment
- no hidden second orchestrator
- no human intervention after benchmark task start
- no timeout or resource mutation by the adapter
- no requirement for external MCP availability for core closure

## Required Evidence

- adapter summary
- requirement document
- execution plan
- execute receipt
- cleanup receipt
- provider policy snapshot
- materialization receipt proving the benchmark build uses the pinned host/runtime sources

## Non-Compliant Conditions

- benchmark run widens scope without requirement update
- benchmark run skips requirement freeze
- benchmark run skips cleanup
- benchmark run depends on undeclared external transport for core completion
- benchmark build silently swaps host or runtime sources without updating source lock
