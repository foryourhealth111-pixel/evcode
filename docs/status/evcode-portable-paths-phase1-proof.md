# EvCode Portable Paths Phase 1 Proof

## Scope

This proof closes the phase-1 repair wave for EvCode portability on 2026-03-18.
The verified behaviors were portable provider configuration resolution, `run --help` ergonomics on both CLIs, and benchmark artifact handoff stability when the caller requests workspace-local output paths.

## Verdict

Phase-1 is verified.
Fresh smoke evidence and fresh regression evidence both confirm that the implemented repairs behave as required: the standard CLI can resolve provider configuration from a portable config root, both `run --help` surfaces now return usage with exit code 0, and benchmark execution still redirects unsafe workspace-local execution to `/tmp` while materializing stable handoff artifacts back at the user-requested paths.

## Commands Executed

- `XDG_CONFIG_HOME=<session tmp> node apps/evcode/bin/evcode.js status --json` -> exit 0 | evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-portable-paths-phase1/logs/portable-status.json`
- `node apps/evcode/bin/evcode.js run --help` -> exit 0 | evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-portable-paths-phase1/logs/evcode-run-help.log`
- `node apps/evcode-bench/bin/evcode-bench.js run --help` -> exit 0 | evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-portable-paths-phase1/logs/evcode-bench-run-help.log`
- `EVCODE_BENCH_HOST_BIN=<session fake host> node apps/evcode-bench/bin/evcode-bench.js run --task 'Verify benchmark artifact handoff semantics' --workspace <session tmp> --artifacts-root <session tmp> --result-json <session tmp> --run-id portable-paths-phase1-bench-smoke` -> exit 0 | evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-portable-paths-phase1/logs/benchmark-smoke.json`
- `python3 -m pytest tests/test_portable_paths.py tests/test_benchmark_artifact_contract.py tests/test_app_entrypoints.py tests/test_benchmark_execution_bridge.py tests/test_runtime_bridge.py tests/test_contracts.py -q` -> exit 0 | evidence: `22 passed in 1.31s`

## What Passed

- Portable provider configuration is now portable-first. With `XDG_CONFIG_HOME` set to a session-local config root, the CLI reported `active_env_source = portable_user_config` and resolved the env file from the portable location while honoring the configured portable models. Evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-portable-paths-phase1/logs/portable-status.json`.
- `run --help` is fixed on both CLIs. The standard CLI prints `Usage: evcode run ...`, and the benchmark CLI prints `Usage: evcode-bench run ...`, both without the old `Missing --task` failure. Evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-portable-paths-phase1/logs/evcode-run-help.log` and `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-portable-paths-phase1/logs/evcode-bench-run-help.log`.
- Benchmark artifact handoff is stable. The benchmark smoke still redirected its effective execution root to `/tmp`, but it copied the runtime summary and result JSON back to the caller-requested workspace paths and wrote a handoff manifest that links requested and effective locations. Evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-portable-paths-phase1/logs/benchmark-smoke.json`, `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-portable-paths-phase1/tmp/bench-workspace/requested-output/result.json`, and `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-portable-paths-phase1/tmp/bench-workspace/requested-artifacts/benchmark-artifact-handoff.json`.
- Fresh regression coverage is green across the new portability tests and the impacted runtime/contract suites. Evidence: local pytest run with `22 passed in 1.31s`.

## Residual Notes

- Benchmark execution remains intentionally redirect-to-temp for safety when requested paths live inside the workspace. Phase-1 does not remove that safety behavior; it makes it observable and stable for callers.
- This phase does not implement the broader hybrid baseline family. That remains the next design/execution wave.

## Cleanup And Artifact Preservation

- Requested-path evidence was preserved under `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-portable-paths-phase1`.
- External benchmark execution roots under `/tmp` created by this smoke were removed after the requested-path handoff files were confirmed.
- Existing `node` and `codex` processes were audited only and intentionally left untouched. Evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-portable-paths-phase1/node-process-audit.txt`.
