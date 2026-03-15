# EvCode Benchmark Submission Runbook

## Goal

This runbook defines the minimum repeatable path for assembling and smoke-testing the benchmark distribution without polluting the task workspace.

## Core Rules

- the benchmark path must use the same governed runtime core as the normal distribution
- benchmark mode must run as `benchmark_autonomous`
- no human follow-up is allowed once task execution starts
- the core benchmark closure must not require external MCP availability
- benchmark artifacts must live outside the task workspace
- each benchmark run materializes an isolated `CODEX_HOME` with `mcp_servers = {}`

## Required Environment

- `python3`
- `node`
- a codex-compatible host binary or a bundled EvCode host
- provider credentials required by the chosen execution backend

Optional benchmark execution overrides:

- `EVCODE_BENCH_HOST_BIN`: explicit host binary path
- `EVCODE_BENCHMARK_EXECUTOR`: shell-style command template used instead of the default host path
- `EVCODE_BENCHMARK_EXEC_TIMEOUT_SEC`: execution timeout for the benchmark bridge
- `EVCODE_BENCH_ENTRYPOINT`: installed-agent wrapper override for `evcode-bench`

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
ARTIFACTS_ROOT="$(mktemp -d /tmp/evcode-bench-artifacts-XXXXXX)"

node apps/evcode-bench/bin/evcode-bench.js run \
  --task "Solve the benchmark task end-to-end without asking follow-up questions." \
  --workspace "$PWD" \
  --artifacts-root "$ARTIFACTS_ROOT" \
  --result-json "$ARTIFACTS_ROOT/result.json"
```

Expected outputs:

- external `docs/requirements/...`
- external `docs/plans/...`
- external `outputs/runtime/vibe-sessions/<run-id>/phase-execute.json`
- external `outputs/runtime/vibe-sessions/<run-id>/cleanup-receipt.json`
- external benchmark `result.json`
- no `docs/` or `outputs/` directories created in the task workspace

## Official Mode vs Debug Mode

- Official mode:
  - use the default `codex exec` path
  - let EvCode create its per-run isolated `CODEX_HOME`
  - point `--artifacts-root` to a directory outside the task workspace
  - do not enable MCP or workstation-specific config
- Debug mode:
  - optionally set `EVCODE_BENCH_HOST_BIN` to a local host build
  - optionally set `EVCODE_BENCHMARK_EXECUTOR` to a custom wrapper
  - keep debug-only traces under a separate external artifacts directory

## Harbor / Terminal-Bench Import Paths

- `packages.benchmark-adapter.python.harbor_evcode_agent:HarborEvCodeAgent`
- `packages.benchmark-adapter.python.terminal_bench_evcode_agent:TerminalBenchEvCodeAgent`

Harbor route:

- `HarborEvCodeAgent` is the preferred first submission path
- it is shaped to subclass a Harbor / Terminal-Bench `BaseAgent` when the official package is installed
- it uses `logging_dir` or `artifacts_root` as the external artifact directory

Terminal-Bench installed-agent route:

- `TerminalBenchEvCodeAgent` exposes `_install_agent_script_path`, `_run_agent_commands`, and `_env`
- the bundled `setup.sh` installs an `evcode-bench` wrapper and expects either:
  - `EVCODE_BENCH_ENTRYPOINT`, or
  - `EVCODE_REPO_ROOT`

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
