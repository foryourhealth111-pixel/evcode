# Release Packages

EvCode ships as two distribution channels from one repository:

- `standard`: normal governed CLI
- `benchmark`: benchmark-first governed CLI

## Outputs

The release builder emits:

- one assembled distribution directory per channel
- one `.tar.gz` archive per channel
- one release manifest

Default output root:

```bash
dist/releases/
```

## Build

Basic release build:

```bash
python3 scripts/release/build_release_packages.py
```

Require a bundled patched host:

```bash
python3 scripts/release/build_release_packages.py --require-patched-host
```

Publish the GitHub release after the tag exists:

```bash
python3 scripts/release/publish_github_release.py \
  --owner foryourhealth111-pixel \
  --repo evcode \
  --tag v0.1.0 \
  --asset dist/releases/evcode-v0.1.0/artifacts/evcode-standard-v0.1.0.tar.gz \
  --asset dist/releases/evcode-v0.1.0/artifacts/evcode-benchmark-v0.1.0.tar.gz
```

The script reads the GitHub token from stdin so it does not need to be stored in the repository.

## Patched Host Behavior

If `cargo` is available, the release builder will:

1. build the patched host from vendored Codex upstream
2. bundle that host into both channels
3. make the launcher prefer the bundled host over system `codex`

If `cargo` is unavailable, the builder still emits both channel packages, but they fall back to the configured/system host at runtime.

## Channel Defaults

- standard package:
  - binary: `evcode`
  - mode: `interactive_governed`
- benchmark package:
  - binary: `evcode-bench`
  - mode: `benchmark_autonomous`

The benchmark package defaults to benchmark-safe governance automatically.
