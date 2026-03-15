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

Development-only fallback to system host:

```bash
python3 scripts/release/build_release_packages.py --allow-system-host
```

Publish the GitHub release after the tag exists:

```bash
VERSION=$(python3 scripts/release/print_version.py)
python3 scripts/release/publish_github_release.py \
  --owner foryourhealth111-pixel \
  --repo evcode \
  --tag v$VERSION \
  --asset dist/releases/evcode-v$VERSION/artifacts/evcode-standard-v$VERSION.tar.gz \
  --asset dist/releases/evcode-v$VERSION/artifacts/evcode-benchmark-v$VERSION.tar.gz
```

The script reads the GitHub token from stdin so it does not need to be stored in the repository.

## Patched Host Behavior

Formal release packages are self-contained by default.

That means the builder must:

1. build the patched host from vendored Codex upstream
2. bundle that host into both channels
3. make the launcher prefer the bundled host over system `codex`
4. assemble release directories in `copy` mode so tarballs do not contain repo-local symlinks

If `cargo` is unavailable, the default release build now fails.

Only explicit development builds may fall back to the configured/system host, and they must opt in with `--allow-system-host`.

## Release Validation

Validate that archives are portable and self-contained:

```bash
VERSION=$(python3 scripts/release/print_version.py)
python3 scripts/verify/check_release_packages.py --manifest dist/releases/evcode-v$VERSION/artifacts/release-manifest.json
```

The validator checks:

- each archive contains `host/bin/codex`
- no tarball contains symlinks that escape back into the build machine

## Channel Defaults

- standard package:
  - binary: `evcode`
  - mode: `interactive_governed`
- benchmark package:
  - binary: `evcode-bench`
  - mode: `benchmark_autonomous`

The benchmark package defaults to benchmark-safe governance automatically.
