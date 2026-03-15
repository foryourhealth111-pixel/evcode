# System Dependencies

This document lists the minimum system packages needed to build EvCode from source.

## Core Tooling

Required on all supported source-build setups:

- `bash`
- `python3`
- `node`
- `git`
- `rustc`
- `cargo`

## Linux

Required packages:

- `pkg-config`
- `libcap-dev`

Why `libcap-dev` matters:

- EvCode builds a patched Codex host
- the Linux host path compiles `codex-linux-sandbox`
- that build compiles vendored `bubblewrap`
- vendored `bubblewrap` needs `libcap` headers exposed through `pkg-config`

Ubuntu/Debian example:

```bash
sudo apt-get update
sudo apt-get install -y pkg-config libcap-dev
```

## macOS

Current state:

- source build may work for non-Linux-specific paths
- the Linux sandbox path is not the primary validated target

Recommended starting point:

```bash
brew install pkg-config
brew install rustup-init
```

Then install a Rust toolchain with `rustup`.

## CI / GitHub Actions

The GitHub release workflow also needs Linux build dependencies.

Current workflow expectation:

```bash
sudo apt-get update
sudo apt-get install -y libcap-dev pkg-config
```
