# EvCode Benchmark Submission Runbook

## Goal

This runbook defines the minimum repeatable path for assembling and smoke-testing the benchmark distribution.

## Core Rules

- the benchmark path must use the same governed runtime core as the normal distribution
- benchmark mode must run as `benchmark_autonomous`
- no human follow-up is allowed once task execution starts
- the core benchmark closure must not require external MCP availability

## Required Environment

- `python3`
- `node`
- a codex-compatible host binary or a bundled EvCode host
- provider credentials required by the chosen execution backend

Optional benchmark execution overrides:

- `EVCODE_BENCH_HOST_BIN`: explicit host binary path
- `EVCODE_BENCHMARK_EXECUTOR`: shell-style command template used instead of the default host path
- `EVCODE_BENCHMARK_EXEC_TIMEOUT_SEC`: execution timeout for the benchmark bridge

Supported placeholders inside `EVCODE_BENCHMARK_EXECUTOR`:

- `{task_file}`
- `{prompt_file}`
- `{workspace}`
- `{result_json}`
- `{run_dir}`
- `{host_bin}`

## Assemble

```bash
python3 scripts/build/assemble_distribution.py \
  --channel benchmark \
  --output-root .evcode-dist \
  --bundled-host-binary .evcode-build/host/codex
```

## Local Smoke

```bash
node apps/evcode-bench/bin/evcode-bench.js run \
  --task "Solve the benchmark task end-to-end without asking follow-up questions." \
  --workspace "$PWD" \
  --artifacts-root "$PWD/.bench-artifacts" \
  --result-json "$PWD/.bench-artifacts/result.json"
```

Expected outputs:

- `docs/requirements/...`
- `docs/plans/...`
- `outputs/runtime/vibe-sessions/<run-id>/phase-execute.json`
- `outputs/runtime/vibe-sessions/<run-id>/cleanup-receipt.json`
- benchmark `result.json`

## Harbor / Terminal-Bench Import Paths

- `packages.benchmark-adapter.python.harbor_evcode_agent:HarborEvCodeAgent`
- `packages.benchmark-adapter.python.terminal_bench_evcode_agent:TerminalBenchEvCodeAgent`

## Proof Ladder

1. smoke: 1 task with result file generation
2. mini: 3-5 tasks with no human intervention
3. partial: 20+ tasks with failure taxonomy
4. full: submission-like full suite

## Failure Taxonomy

- `completed`
- `executor_failed`
- `timeout`
- `runtime_error`

Each failure mode must still emit:

- execute receipt
- result file
- cleanup receipt
