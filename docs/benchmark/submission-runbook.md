# EvCode Benchmark Submission Runbook

## Goal

This runbook defines the minimum repeatable path for assembling and smoke-testing the benchmark distribution without polluting the task workspace.

Benchmark is a constrained runtime mode over the same EvCode agent core.
It is not a second agent implementation.

## Core Rules

- the benchmark path must use the same governed runtime core as the normal distribution
- benchmark mode must run as `benchmark_autonomous`
- no human follow-up is allowed once task execution starts
- the core benchmark closure must not require external MCP availability
- benchmark artifacts must live outside the task workspace
- each benchmark run materializes an isolated `CODEX_HOME` with `mcp_servers = {}`
- benchmark policy controls autonomy, isolation, and artifact boundaries
- submission presets control provider, model, reasoning, and auth behavior

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
- `EVCODE_BENCHMARK_MODEL_PROVIDER`: override submission model provider
- `EVCODE_BENCHMARK_MODEL`: override submission model
- `EVCODE_BENCHMARK_REASONING_EFFORT`: override submission reasoning effort
- `EVCODE_BENCH_SOURCE_CODEX_HOME`: source `CODEX_HOME` used to copy config/auth into the isolated benchmark home
- `EVCODE_SUBMISSION_PRESET`: explicit submission preset path; overrides the profile default preset

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
  - let the benchmark profile resolve a submission preset, then copy the needed provider block and auth material from the source `CODEX_HOME`
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
- the bundled `setup.sh` installs an `evcode-bench` wrapper into the first writable path:
  - `/usr/local/bin`, or
  - `~/.local/bin`
- it expects either:
  - `EVCODE_BENCH_ENTRYPOINT`, or
  - `EVCODE_REPO_ROOT`

## Submission Presets

The benchmark profile may point to a default submission preset.

Current default:

- `config/submission-presets/rightcode-gpt-5.4-xhigh.json`

This preset currently resolves to:

- provider: `rightcode`
- model: `gpt-5.4`
- reasoning effort: `xhigh`
- auth strategy: copy `auth.json` from the source `CODEX_HOME`

You can swap presets without changing the benchmark runtime itself.

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
