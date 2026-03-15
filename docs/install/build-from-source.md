# Build From Source

EvCode is now source-build-first.

The primary supported audience is:

- developers working on the host/runtime bridge
- benchmark users who want a reproducible local build
- advanced users who want to inspect or reproduce the host patch

This path does **not** require a preinstalled `codex`.

## What Source Build Produces

Source build does two things:

1. builds the patched EvCode host binary from vendored Codex upstream
2. assembles an embedded EvCode distribution that points at the bundled host

For the standard channel, the final launcher is:

```bash
.evcode-dist/standard/bin/evcode
```

## Required Dependencies

At minimum:

- `bash`
- `python3`
- `node`
- `git`
- `rustc`
- `cargo`

Linux also requires:

- `pkg-config`
- `libcap-dev`

Validate dependencies before building:

```bash
scripts/install/check_build_deps.sh --channel standard
```

## Build The Standard Channel

One command:

```bash
scripts/install/build_from_source.sh
```

This builds:

- patched host: `.evcode-build/host/codex`
- assembled standard dist: `.evcode-dist/standard`

## Manual Build Steps

If you want the lower-level steps:

```bash
python3 scripts/build/build_patched_host.py --output .evcode-build/host/codex
python3 scripts/build/assemble_distribution.py \
  --channel standard \
  --output-root .evcode-dist \
  --bundled-host-binary .evcode-build/host/codex
```

## Run The Built Standard Channel

Direct launcher:

```bash
.evcode-dist/standard/bin/evcode
```

Or through the repository app shim:

```bash
node apps/evcode/bin/evcode.js native
```

## Notes

- The standard source build is the canonical local install path.
- Release tarballs are convenience artifacts, not the primary installation contract.
- If you are building for benchmark reproduction, use the dedicated benchmark build path instead of the standard one.
