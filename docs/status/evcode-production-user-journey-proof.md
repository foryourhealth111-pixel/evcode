# EvCode Production User Journey Proof

## Scope

This proof simulates a real user operating the committed EvCode product surfaces in this repository on 2026-03-18.
The tested surfaces were the CLI entrypoints, legacy Codex passthrough commands, health/probe commands, one standard governed run that routed to Claude, one standard governed run that routed to Gemini, and one benchmark autonomous run.

## Verdict

Core production journeys are usable.
EvCode currently preserves its legacy Codex-compatible help surfaces, standard governed execution works, live Claude and Gemini advisory delegation both work behind the VCO control plane, and benchmark mode remains Codex-primary as designed.
The run is not clean enough to call issue-free because two operator-facing problems remain: `run --help` is broken on both CLIs, and benchmark output paths are silently redirected to `/tmp` when the caller points them inside the workspace.

## Commands Executed

- `node apps/evcode/bin/evcode.js --help` -> exit 0 | evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-help.log`
- `node apps/evcode-bench/bin/evcode-bench.js --help` -> exit 0 | evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-bench-help.log`
- `node apps/evcode/bin/evcode.js native --help` -> exit 0 | evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-native-help.log`
- `node apps/evcode/bin/evcode.js resume --help` -> exit 0 | evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-resume-help.log`
- `node apps/evcode/bin/evcode.js mcp --help` -> exit 0 | evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-mcp-help.log`
- `node apps/evcode/bin/evcode.js run --help` -> exit 1 | evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-run-help.log`
- `node apps/evcode-bench/bin/evcode-bench.js run --help` -> exit 1 | evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-bench-run-help.log`
- `node apps/evcode/bin/evcode.js status --json` -> exit 0 | evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-status.json`
- `node apps/evcode-bench/bin/evcode-bench.js status --json` -> exit 0 | evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-bench-status.json`
- `node apps/evcode/bin/evcode.js doctor` -> exit 0 | evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-doctor.log`
- `node apps/evcode/bin/evcode.js probe-providers --json` -> exit 0 | evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-probe.json`
- `node apps/evcode-bench/bin/evcode-bench.js probe-providers --json` -> exit 0 | evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-bench-probe.json`
- `EVCODE_RIGHTCODES_API_KEY=*** EVCODE_ENABLE_LIVE_SPECIALISTS=1 node apps/evcode/bin/evcode.js probe-providers --json --live` -> exit 0 | evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-probe-live.json`
- `EVCODE_RIGHTCODES_API_KEY=*** EVCODE_ENABLE_LIVE_SPECIALISTS=1 node apps/evcode/bin/evcode.js run --task '<planning advisory>' --run-id prod-user-standard-smoke --artifacts-root ...` -> exit 0 | evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-standard-run.log`
- `EVCODE_RIGHTCODES_API_KEY=*** EVCODE_ENABLE_LIVE_SPECIALISTS=1 node apps/evcode/bin/evcode.js run --task '<frontend visual advisory>' --run-id prod-user-gemini-smoke --artifacts-root ...` -> exit 0 | evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-gemini-run.log`
- `EVCODE_RIGHTCODES_API_KEY=*** EVCODE_ENABLE_LIVE_SPECIALISTS=1 node apps/evcode-bench/bin/evcode-bench.js run --task '<benchmark smoke>' --run-id prod-user-benchmark-smoke --artifacts-root ... --result-json ...` -> exit 0 | evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-benchmark-run.log`

## What Passed

- Legacy passthrough still works. The standard, benchmark, native, resume, and mcp help surfaces all opened Codex-compatible help text rather than failing. Evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-help.log`, `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-bench-help.log`, `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-native-help.log`, `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-resume-help.log`, `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-mcp-help.log`.
- Standard product health surfaces work. `status --json`, `doctor`, and offline `probe-providers --json` all returned structured output. Evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-status.json`, `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-doctor.log`, `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-probe.json`.
- Benchmark health surfaces work. `status --json` and offline provider probing completed, and specialist suppression is visible in the benchmark channel. Evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-bench-status.json`, `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-bench-probe.json`.
- Live RightCodes provider compatibility is real, not just configured. With `EVCODE_RIGHTCODES_API_KEY` set, Codex, Claude, and Gemini all returned `live_compatible`. Evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-probe-live.json`.
- A real standard governed run routed planning work to Claude while preserving Codex final authority. Evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/tmp/standard-run/outputs/runtime/vibe-sessions/prod-user-standard-smoke/runtime-summary.json` and `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/tmp/standard-run/outputs/runtime/vibe-sessions/prod-user-standard-smoke/specialists/claude-result.json`.
- A real standard governed run routed a frontend-visual task to Gemini while preserving Codex final authority. Evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/tmp/gemini-run/outputs/runtime/vibe-sessions/prod-user-gemini-smoke/runtime-summary.json` and `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/tmp/gemini-run/outputs/runtime/vibe-sessions/prod-user-gemini-smoke/specialists/gemini-result.json`.
- A real benchmark run completed in autonomous mode with `route_kind = codex_only_benchmark`, explicitly suppressing Claude and Gemini. Evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/captured/benchmark-smoke/runtime-summary.json` and `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/captured/benchmark-smoke/assistant-last-message.txt`.

## Findings

### 1. Medium: `run --help` is broken

Both `node apps/evcode/bin/evcode.js run --help` and `node apps/evcode-bench/bin/evcode-bench.js run --help` exit with code 1 and print `Missing --task for run`.
That is a real user-facing CLI regression because normal help discovery no longer works on the `run` subcommand.
Implementation evidence points to the custom `run()` handlers requiring `--task` before any help path is considered in [evcode.js](/home/lqf/table/table3/apps/evcode/bin/evcode.js:225) and [evcode-bench.js](/home/lqf/table/table3/apps/evcode-bench/bin/evcode-bench.js:120).
Runtime evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-run-help.log` and `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-bench-run-help.log`.

### 2. Medium: benchmark path contracts are surprising and brittle

The benchmark smoke run succeeded, but the runtime replaced the requested in-repo `--artifacts-root` with a temp directory under `/tmp`, and it also redirected the requested `--result-json` to another temp path.
This behavior is explicit in the implementation: workspace-internal benchmark artifacts are redirected by [runtime_lib.py](/home/lqf/table/table3/scripts/runtime/runtime_lib.py:110), and workspace-internal result JSON is redirected by [execute_benchmark_task.py](/home/lqf/table/table3/scripts/runtime/execute_benchmark_task.py:77) and [execute_benchmark_task.py](/home/lqf/table/table3/scripts/runtime/execute_benchmark_task.py:341).
The CLI therefore completes successfully, but automation cannot rely on the path it asked for unless it parses the returned runtime summary JSON. Evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-benchmark-run.log` and `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/captured/benchmark-smoke/runtime-summary.json`.

### 3. Low: benchmark stderr is noisy because Codex home lives under `/tmp`

The benchmark run emitted `Refusing to create helper binaries under temporary dir "/tmp"` in stderr, even though the run completed and produced the expected final sentence.
This is not a correctness failure in this session, but it is operationally noisy and could confuse any wrapper that treats stderr warnings as a degraded outcome.
Evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/captured/benchmark-smoke/benchmark.stderr.txt`.

### 4. Low: provider env status is technically accurate but not very operator-friendly

The standard status and doctor output show `provider_setup.local_env_present = false` while the assembled distribution reports `env_local_present = true`.
That difference is possible, but the surface does not explain it, so a user can easily read the status as "provider env missing" even when the built distribution still contains one.
Evidence: `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-status.json` and `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/logs/evcode-doctor.log`.

## Cleanup And Artifact Preservation

- Benchmark artifacts were copied back into the repo session folder at `/home/lqf/table/table3/outputs/runtime/vibe-sessions/2026-03-18-evcode-production-user-journey-testing/captured/benchmark-smoke` before temp cleanup.
- The benchmark temp roots that were created outside the repo were removed after the key evidence files were copied back into the repo session folder.
- Existing long-lived `codex resume --yolo` and `evcode.js --yolo` processes were audited only and intentionally left untouched.
