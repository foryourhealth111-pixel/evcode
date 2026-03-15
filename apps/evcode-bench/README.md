# EvCode Bench App

This package is the benchmark-oriented EvCode release channel.

Defaults:

- channel: `benchmark`
- mode: `benchmark_autonomous`
- profile: `benchmark`

This app is intended to wrap the same governed runtime core behind benchmark-safe defaults and a thin harness adapter.

Current commands:

- `evcode-bench`
- `evcode-bench assemble`
- `evcode-bench run --task "..."`

Execution bridge notes:

- `evcode-bench run` now executes a benchmark bridge instead of only writing static execute receipts
- use `--result-json PATH` to force the benchmark result artifact location
- use `EVCODE_BENCHMARK_EXECUTOR` to inject a harness-compatible thin execution backend
