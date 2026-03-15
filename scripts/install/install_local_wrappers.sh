#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)"
INSTALL_DIR="${HOME}/.local/bin"

usage() {
  cat <<'EOF'
Usage: scripts/install/install_local_wrappers.sh [--install-dir PATH]

Install local developer wrappers for:
  - evcode
  - evcode-bench

The wrappers point at this repository's Node entrypoints so local commands stay
aligned with the current checkout.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --install-dir)
      INSTALL_DIR="${2:-}"
      shift 2
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

mkdir -p "$INSTALL_DIR"

cat >"$INSTALL_DIR/evcode" <<EOF
#!/usr/bin/env bash
exec node "$REPO_ROOT/apps/evcode/bin/evcode.js" "\$@"
EOF

cat >"$INSTALL_DIR/evcode-bench" <<EOF
#!/usr/bin/env bash
exec node "$REPO_ROOT/apps/evcode-bench/bin/evcode-bench.js" "\$@"
EOF

chmod +x "$INSTALL_DIR/evcode" "$INSTALL_DIR/evcode-bench"

cat <<EOF
Installed local EvCode wrappers:
  $INSTALL_DIR/evcode
  $INSTALL_DIR/evcode-bench
EOF
