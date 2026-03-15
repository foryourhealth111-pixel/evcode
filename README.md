# EvCode

EvCode is intended to be:

- Codex itself
- with the full Vibe ecosystem embedded
- plus one native per-turn governance hook

It is **not** intended to be a wrapper-owned shell or an external governance sidecar.

## Product Baseline

The current authoritative architecture is defined in:

- [docs/architecture.md](/home/lqf/table/table3/docs/architecture.md)
- [docs/plans/2026-03-14-evcode-reset-native-fork.md](/home/lqf/table/table3/docs/plans/2026-03-14-evcode-reset-native-fork.md)
- [docs/architecture/evcode-host-runtime-bridge.md](/home/lqf/table/table3/docs/architecture/evcode-host-runtime-bridge.md)
- [docs/architecture/evcode-dual-distribution.md](/home/lqf/table/table3/docs/architecture/evcode-dual-distribution.md)
- [docs/architecture/evcode-benchmark-adapter.md](/home/lqf/table/table3/docs/architecture/evcode-benchmark-adapter.md)
- [docs/architecture/evcode-upstream-materialization-and-bridge.md](/home/lqf/table/table3/docs/architecture/evcode-upstream-materialization-and-bridge.md)
- [docs/plans/2026-03-15-evcode-vco-benchmark-integration-plan.md](/home/lqf/table/table3/docs/plans/2026-03-15-evcode-vco-benchmark-integration-plan.md)
- [docs/plans/2026-03-15-evcode-upstream-materialization-and-bridge-plan.md](/home/lqf/table/table3/docs/plans/2026-03-15-evcode-upstream-materialization-and-bridge-plan.md)

## Target Behaviors

- launching `evcode` should feel like launching Codex
- full Vibe skills/rules/agents/MCP assets should be embedded into the runtime
- every user turn should be physically normalized to the same effect as explicit `$vibe`
- every child-task prompt should end with ` $vibe`
- `resume`, `fork`, `yolo`, MCP, and native team behavior should remain Codex-compatible

## Current Reality

The repository contains transitional code from an earlier wrapper-first direction.

That direction is now considered obsolete.

The next implementation waves should:

1. rebase around a real native prompt hook patch point
2. embed the full Vibe ecosystem as first-class runtime content
3. demote wrapper-managed behavior to temporary debug-only fallback
4. replace inferred observability with receipts emitted by the real native hook

## Current Direction

The current design direction is:

- hook-rich Codex host as the runtime base
- embedded VCO governed runtime as the control-plane truth
- one shared runtime core
- two release channels:
  - `EvCode`
  - `EvCode Bench`

## Current Local Usage

Standard channel:

```bash
node apps/evcode/bin/evcode.js
node apps/evcode/bin/evcode.js resume --yolo
node apps/evcode/bin/evcode.js assemble
node apps/evcode/bin/evcode.js host-build --output .evcode-build/host/codex
node apps/evcode/bin/evcode.js assemble --bundled-host-binary .evcode-build/host/codex
```

Benchmark channel:

```bash
node apps/evcode-bench/bin/evcode-bench.js
node apps/evcode-bench/bin/evcode-bench.js assemble
```

Release packages:

```bash
python3 scripts/release/build_release_packages.py
python3 scripts/release/build_release_packages.py --allow-system-host
```

What these commands now do:

- assemble a real EvCode distribution directory under `.evcode-dist/`
- set `CODEX_HOME` to the assembled profile and embedded skills/runtime payload
- prefer an EvCode-bundled patched host binary when present, otherwise fall back to the configured/system `codex`
- keep standard and benchmark channels on the same governed runtime truth
- emit releasable `standard` and `benchmark` tarballs through the release builder

Formal release note:

- official release packages are expected to be self-contained and should be built without `--allow-system-host`
- `--allow-system-host` exists only for local development when Rust/cargo is unavailable

Hard-equivalence note:

- hook scripts alone only inject governed context
- true per-turn equivalence to explicit `$vibe` requires the patched host binary built from `scripts/build/build_patched_host.py`
- that host patch also enforces ` $vibe` on spawned child tasks
