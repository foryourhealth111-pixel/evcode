# Benchmark Build

`EvCode Bench` is the benchmark-oriented source build path.

Use this when you want:

- benchmark-safe defaults
- autonomous governed runtime mode
- a local build that reflects the benchmark channel rather than the standard interactive channel

## Check Dependencies

```bash
scripts/install/check_build_deps.sh --channel benchmark
```

The dependency surface is currently the same as the standard source build because both channels reuse the same patched host build.

## Build The Benchmark Channel

```bash
scripts/install/build_benchmark_from_source.sh
```

This produces:

- patched host: `.evcode-build/host/codex`
- assembled benchmark dist: `.evcode-dist/benchmark`

## Run The Built Benchmark Channel

Direct launcher:

```bash
.evcode-dist/benchmark/bin/evcode-bench
```

Or through the repository app shim:

```bash
node apps/evcode-bench/bin/evcode-bench.js native
```

## Manual Build Steps

```bash
python3 scripts/build/build_patched_host.py --output .evcode-build/host/codex
python3 scripts/build/assemble_distribution.py \
  --channel benchmark \
  --output-root .evcode-dist \
  --bundled-host-binary .evcode-build/host/codex
```

## Why Benchmark Users Should Prefer Source Build

Source build is the stronger path for benchmark users because it is:

- auditable
- reproducible
- easy to patch locally
- closer to the exact host/runtime combination used during evaluation
