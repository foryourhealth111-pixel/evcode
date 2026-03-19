# EvCode

EvCode is now **source-build-first**.This is not ready to use.

The primary audience is:

- developers
- benchmark users
- users who want to reproduce and inspect the host patch locally

EvCode is intended to be:

- Codex itself
- with the full Vibe ecosystem embedded
- plus one native per-turn governance hook

It is **not** intended to be a wrapper-owned shell or an external governance sidecar.

## Primary Install Path

EvCode does **not** require a preinstalled `codex`.

The canonical local install path is:

1. install source-build dependencies
2. build the patched host from vendored upstream
3. assemble a local EvCode distribution that embeds the bundled host

Start here:

```bash
scripts/install/check_build_deps.sh --channel standard
scripts/install/build_from_source.sh
```

Benchmark users should use:

```bash
scripts/install/check_build_deps.sh --channel benchmark
scripts/install/build_benchmark_from_source.sh
```

Install references:

- [docs/install/build-from-source.md](docs/install/build-from-source.md)
- [docs/install/benchmark-build.md](docs/install/benchmark-build.md)
- [docs/install/system-deps.md](docs/install/system-deps.md)
- [docs/benchmark/submission-runbook.md](docs/benchmark/submission-runbook.md)

## Assistant Provider Setup

EvCode now exposes one canonical setup surface for assistant-provider overrides:

- setup guide: [docs/configuration/openai-compatible-provider-setup.md](docs/configuration/openai-compatible-provider-setup.md)
- tracked example: `config/assistant-providers.env.example`
- local untracked file: `config/assistant-providers.env.local`

Compatibility note:

- EvCode currently treats OpenAI-style `chat/completions` as the primary portable wire format for Codex / Claude / Gemini specialist routing.
- `responses` remains adapter-tolerant, but provider behavior still varies and should not be assumed interchangeable without verification.


## Baseline Verification

EvCode now distinguishes two formal baseline families:

- `hybrid_governed`: standard-channel governed routing proof for Codex + advisory specialists
- `core_benchmark`: benchmark-channel Codex-only safety proof

Offline verification commands:

```bash
python3 scripts/verify/run_hybrid_baseline.py --repo-root . --json
python3 scripts/verify/validate_distribution_portability.py --repo-root . --json
```

Live opt-in operator verification:

```bash
EVCODE_ENABLE_LIVE_SPECIALISTS=1 EVCODE_RIGHTCODES_API_KEY=... \
python3 scripts/verify/run_live_hybrid_validation.py --repo-root . --json
```

The live validator is intentionally separate from default `check` and CI so benchmark-safe offline verification remains deterministic.

## Product Preview

The static marketing preview used by repository-level smoke tests lives at:

- `apps/site/index.html`

Open it directly in a browser when you need a lightweight product surface for demos, release packaging checks, or visual review without starting a dev server.

## Product Baseline

The current authoritative architecture is defined in:

- [docs/architecture.md](docs/architecture.md)
- [docs/plans/2026-03-14-evcode-reset-native-fork.md](docs/plans/2026-03-14-evcode-reset-native-fork.md)
- [docs/architecture/evcode-host-runtime-bridge.md](docs/architecture/evcode-host-runtime-bridge.md)
- [docs/architecture/evcode-dual-distribution.md](docs/architecture/evcode-dual-distribution.md)
- [docs/architecture/evcode-benchmark-adapter.md](docs/architecture/evcode-benchmark-adapter.md)
- [docs/architecture/evcode-upstream-materialization-and-bridge.md](docs/architecture/evcode-upstream-materialization-and-bridge.md)
- [docs/plans/2026-03-15-evcode-vco-benchmark-integration-plan.md](docs/plans/2026-03-15-evcode-vco-benchmark-integration-plan.md)
- [docs/plans/2026-03-15-evcode-upstream-materialization-and-bridge-plan.md](docs/plans/2026-03-15-evcode-upstream-materialization-and-bridge-plan.md)

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

## Repository Usage

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
node apps/evcode-bench/bin/evcode-bench.js run --task "..." --result-json ./result.json
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

- official release packages are convenience artifacts
- source build remains the primary installation contract for advanced users
- formal release packages are still expected to be self-contained and should be built without `--allow-system-host`
- `--allow-system-host` exists only for local development when Rust/cargo is unavailable

Hard-equivalence note:

- hook scripts alone only inject governed context
- true per-turn equivalence to explicit `$vibe` requires the patched host binary built from `scripts/build/build_patched_host.py`
- that host patch also enforces ` $vibe` on spawned child tasks
