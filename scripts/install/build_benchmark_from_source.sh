#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"

HOST_OUTPUT="$REPO_ROOT/.evcode-build/host/codex"
DIST_OUTPUT_ROOT="$REPO_ROOT/.evcode-dist"
SKIP_DEPS=0

usage() {
  cat <<'EOF'
Usage: scripts/install/build_benchmark_from_source.sh [options]

Builds the patched EvCode host from source and assembles the benchmark channel.

Options:
  --host-output PATH       Output path for the patched host binary
  --dist-output-root PATH  Distribution output root (default: .evcode-dist)
  --skip-deps-check        Skip dependency validation
  -h, --help               Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --host-output)
      HOST_OUTPUT="${2:-}"
      shift 2
      ;;
    --dist-output-root)
      DIST_OUTPUT_ROOT="${2:-}"
      shift 2
      ;;
    --skip-deps-check)
      SKIP_DEPS=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

cd "$REPO_ROOT"

if [[ $SKIP_DEPS -ne 1 ]]; then
  "$SCRIPT_DIR/check_build_deps.sh" --channel benchmark
fi

python3 scripts/build/build_patched_host.py --output "$HOST_OUTPUT"
python3 scripts/build/assemble_distribution.py \
  --channel benchmark \
  --output-root "$DIST_OUTPUT_ROOT" \
  --bundled-host-binary "$HOST_OUTPUT"

cat <<EOF
EvCode benchmark source build complete.
host: $HOST_OUTPUT
dist: $DIST_OUTPUT_ROOT/benchmark

Try:
  $DIST_OUTPUT_ROOT/benchmark/bin/evcode-bench --help
  node apps/evcode-bench/bin/evcode-bench.js native
EOF
