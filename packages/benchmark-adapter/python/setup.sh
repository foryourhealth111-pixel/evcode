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

cat >/usr/local/bin/evcode-bench <<'EOF'
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

chmod +x /usr/local/bin/evcode-bench
echo "Installed evcode-bench wrapper at /usr/local/bin/evcode-bench"
