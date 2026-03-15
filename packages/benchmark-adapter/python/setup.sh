#!/usr/bin/env bash
set -euo pipefail

if ! command -v node >/dev/null 2>&1; then
  echo "node is required for EvCode benchmark mode." >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required for EvCode benchmark mode." >&2
  exit 1
fi

INSTALL_BIN_DIR="${EVCODE_INSTALL_BIN_DIR:-}"
if [[ -z "$INSTALL_BIN_DIR" ]]; then
  if [[ -d /usr/local/bin && -w /usr/local/bin ]]; then
    INSTALL_BIN_DIR="/usr/local/bin"
  else
    INSTALL_BIN_DIR="$HOME/.local/bin"
  fi
fi

mkdir -p "$INSTALL_BIN_DIR"

cat >"$INSTALL_BIN_DIR/evcode-bench" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

if [[ -n "${EVCODE_BENCH_ENTRYPOINT:-}" && -f "${EVCODE_BENCH_ENTRYPOINT}" ]]; then
  exec node "${EVCODE_BENCH_ENTRYPOINT}" "$@"
fi

if [[ -n "${EVCODE_REPO_ROOT:-}" && -f "${EVCODE_REPO_ROOT}/apps/evcode-bench/bin/evcode-bench.js" ]]; then
  exec node "${EVCODE_REPO_ROOT}/apps/evcode-bench/bin/evcode-bench.js" "$@"
fi

echo "EvCode benchmark entrypoint is unavailable. Set EVCODE_BENCH_ENTRYPOINT or EVCODE_REPO_ROOT." >&2
exit 1
EOF

chmod +x "$INSTALL_BIN_DIR/evcode-bench"
echo "Installed evcode-bench wrapper at $INSTALL_BIN_DIR/evcode-bench"
