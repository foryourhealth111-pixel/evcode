# Benchmark Adapter

This package exposes a thin benchmark-facing adapter over the shared EvCode governed runtime.

Goals:

- enter `benchmark_autonomous`
- preserve the fixed 6-stage order
- emit requirement, plan, execute, cleanup receipts, and benchmark `result.json`
- avoid creating a second orchestrator

Thin adapter entrypoints:

- `python/evcode_benchmark_adapter.py`
- `python/harbor_evcode_agent.py`
- `python/terminal_bench_evcode_agent.py`
