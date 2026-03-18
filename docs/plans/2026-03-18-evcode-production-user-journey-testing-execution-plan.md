# EvCode Production User Journey Testing Execution Plan

## Requirement Source

- `docs/requirements/2026-03-18-evcode-production-user-journey-testing.md`

## Internal Grade

- `M`

## Wave 1: Entry surface checks

### Task 1: Verify CLI and passthrough discovery surfaces

Commands:

- `node apps/evcode/bin/evcode.js --help`
- `node apps/evcode-bench/bin/evcode-bench.js --help`
- `node apps/evcode/bin/evcode.js native --help`
- `node apps/evcode/bin/evcode.js resume --help`
- `node apps/evcode/bin/evcode.js mcp --help`

Verification:

- commands exit cleanly and expose expected Codex-compatible verbs

## Wave 2: Product health surfaces

### Task 2: Verify standard and benchmark status/doctor/probe surfaces

Commands:

- `node apps/evcode/bin/evcode.js status --json`
- `node apps/evcode-bench/bin/evcode-bench.js status --json`
- `node apps/evcode/bin/evcode.js doctor`
- `node apps/evcode/bin/evcode.js probe-providers --json`
- `node apps/evcode-bench/bin/evcode-bench.js probe-providers --json`
- `node apps/evcode/bin/evcode.js probe-providers --json --live` with provider env opt-in

Verification:

- governance surfaces are present
- benchmark suppression remains visible
- live provider probe behavior is explicit and bounded

## Wave 3: Real user smoke operations

### Task 3: Standard-channel real run

Command:

- `node apps/evcode/bin/evcode.js run --task "..." --run-id ... --artifacts-root ...`

Verification:

- run completes
- governed artifacts exist
- user-visible route and result surfaces remain coherent

### Task 4: Benchmark-path real smoke run

Command:

- `node apps/evcode-bench/bin/evcode-bench.js run --task "..." --run-id ... --artifacts-root ... --result-json ...`

Verification:

- benchmark path either completes or fails in an explicit bounded way
- specialist suppression remains intact

## Wave 4: Evidence and cleanup

### Task 5: Write proof and report

Artifacts:

- `docs/status/evcode-production-user-journey-proof.md`
- `docs/status/evcode-production-user-journey-report.json`

### Task 6: Cleanup

- remove temp artifacts created outside repo
- audit repo-related Node processes without touching unknown long-lived sessions
- write cleanup receipt
