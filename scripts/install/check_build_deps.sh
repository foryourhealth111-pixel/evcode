#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"

CHANNEL="standard"
QUIET=0

usage() {
  cat <<'EOF'
Usage: scripts/install/check_build_deps.sh [--channel standard|benchmark] [--quiet]

Checks the minimum local dependencies required to build EvCode from source.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --channel)
      CHANNEL="${2:-}"
      shift 2
      ;;
    --quiet)
      QUIET=1
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

if [[ "$CHANNEL" != "standard" && "$CHANNEL" != "benchmark" ]]; then
  echo "Unsupported channel: $CHANNEL" >&2
  exit 1
fi

declare -a missing=()
declare -a notes=()

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    missing+=("$cmd")
  fi
}

require_cmd bash
require_cmd python3
require_cmd node
require_cmd git
require_cmd rustc
require_cmd cargo

os_name="$(uname -s)"
case "$os_name" in
  Linux)
    require_cmd pkg-config
    if ! pkg-config --exists libcap 2>/dev/null; then
      missing+=("libcap-dev (pkg-config: libcap)")
    fi
    notes+=("Linux source builds require libcap headers because codex-linux-sandbox builds vendored bubblewrap.")
    ;;
  Darwin)
    require_cmd pkg-config
    notes+=("macOS builds usually need Homebrew-managed OpenSSL/pkg-config and may not support the Linux sandbox path.")
    ;;
  *)
    notes+=("Unsupported or unverified platform: $os_name. Source builds are primarily validated on Linux.")
    ;;
esac

if [[ $QUIET -eq 0 ]]; then
  echo "EvCode source build dependency check"
  echo "repo: $REPO_ROOT"
  echo "channel: $CHANNEL"
  echo "platform: $os_name"
  if ((${#notes[@]} > 0)); then
    printf 'notes:\n'
    for note in "${notes[@]}"; do
      printf '  - %s\n' "$note"
    done
  fi
fi

if ((${#missing[@]} > 0)); then
  if [[ $QUIET -eq 0 ]]; then
    printf 'missing:\n'
    for item in "${missing[@]}"; do
      printf '  - %s\n' "$item"
    done
  fi
  exit 1
fi

if [[ $QUIET -eq 0 ]]; then
  echo "status: ok"
fi
