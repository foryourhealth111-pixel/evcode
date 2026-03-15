# EvCode Distribution Assembly

## Goal

Define how EvCode turns the materialized host, embedded VCO runtime, hooks, and patch inventory into a runnable local distribution.

## Assembly Model

EvCode now assembles a distribution directory instead of pretending the repository root is the product.

Per channel, the assembler creates:

- `bin/<channel-binary>`
- `codex-home/config.toml`
- `codex-home/skills/*`
- `evcode-runtime/hooks/*`
- `evcode-runtime/runtime/*`
- `evcode-runtime/config/*`
- `evcode-runtime/protocols/*`
- `metadata/assembly-manifest.json`
- `vendor/codex-host/patches/subagent-vibe-suffix.patch`

## Why This Matters

This closes the gap between:

- architecture and proof documents
- local runtime scripts
- a launchable Codex-native host profile

The launcher does not create a second REPL.
It sets `CODEX_HOME` to the assembled profile and then execs the host `codex` binary with native argument passthrough.

## Standard Channel

- binary: `evcode`
- mode: `interactive_governed`
- profile: `standard`

## Benchmark Channel

- binary: `evcode-bench`
- mode: `benchmark_autonomous`
- profile: `benchmark`

## Local Dev vs Release Packaging

The assembler supports two staging modes:

- `symlink`: fast local development
- `copy`: release-style materialization

The runtime truth remains the same in both modes.

## Patch Boundary

The assembler stages the physical child-suffix patch as a first-class release artifact.
It can also stage a patched host source tree when requested, but the patch remains isolated and auditable.

## Verification

Primary verification entrypoints:

- `python3 scripts/verify/check_distribution_assembly.py`
- `python3 -m unittest discover -s tests -p 'test_*.py'`
