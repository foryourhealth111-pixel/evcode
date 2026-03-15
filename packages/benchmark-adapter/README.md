# Benchmark Adapter

This package exposes a thin benchmark-facing adapter over the shared EvCode governed runtime.

Goals:

- enter `benchmark_autonomous`
- preserve the fixed 6-stage order
- emit requirement, plan, execute, and cleanup receipts
- avoid creating a second orchestrator
