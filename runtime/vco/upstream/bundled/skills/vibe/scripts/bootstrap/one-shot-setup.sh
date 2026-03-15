#!/usr/bin/env bash
set -euo pipefail

PROFILE="full"
TARGET_ROOT="${HOME}/.codex"
SKIP_EXTERNAL_INSTALL="false"
STRICT_OFFLINE="false"
OPENAI_BASE_URL="${OPENAI_BASE_URL:-}"
OPENAI_API_KEY_INPUT=""
ARK_BASE_URL="${ARK_BASE_URL:-}"
ARK_API_KEY_INPUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile) PROFILE="$2"; shift 2 ;;
    --target-root) TARGET_ROOT="$2"; shift 2 ;;
    --skip-external-install) SKIP_EXTERNAL_INSTALL="true"; shift ;;
    --strict-offline) STRICT_OFFLINE="true"; shift ;;
    --openai-base-url) OPENAI_BASE_URL="$2"; shift 2 ;;
    --openai-api-key) OPENAI_API_KEY_INPUT="$2"; shift 2 ;;
    --ark-base-url) ARK_BASE_URL="$2"; shift 2 ;;
    --ark-api-key) ARK_API_KEY_INPUT="$2"; shift 2 ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
INSTALL_SH="${REPO_ROOT}/install.sh"
CHECK_SH="${REPO_ROOT}/check.sh"
MATERIALIZE_PS1="${REPO_ROOT}/scripts/setup/materialize-codex-mcp-profile.ps1"
PERSIST_OPENAI_PS1="${REPO_ROOT}/scripts/setup/persist-codex-openai-env.ps1"
PERSIST_ARK_PS1="${REPO_ROOT}/scripts/setup/persist-codex-ark-env.ps1"

require_cmd() {
  local cmd="$1"
  local hint="${2:-}"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "[FAIL] Missing required command: ${cmd}${hint:+ (${hint})}" >&2
    exit 1
  fi
}

pick_python() {
  if command -v python3 >/dev/null 2>&1; then
    echo "python3"
    return 0
  fi
  if command -v python >/dev/null 2>&1; then
    echo "python"
    return 0
  fi
  return 1
}

read_existing_settings_env_value() {
  local codex_root="$1"
  local name="$2"
  local python_bin

  if ! python_bin="$(pick_python)"; then
    return 1
  fi

  "${python_bin}" - "${codex_root}" "${name}" <<'PY'
import json
import sys
from pathlib import Path

codex_root, name = sys.argv[1:3]
settings_path = Path(codex_root) / "settings.json"
if not settings_path.exists():
    raise SystemExit(1)

try:
    with settings_path.open("r", encoding="utf-8-sig") as fh:
        settings = json.load(fh)
except Exception:
    raise SystemExit(1)

env = settings.get("env", {})
value = env.get(name)
if isinstance(value, str) and value.strip():
    print(value)
    raise SystemExit(0)
raise SystemExit(1)
PY
}

seed_settings_env_with_python() {
  local codex_root="$1"
  local provider="$2"
  local base_url="$3"
  local api_key="$4"
  local python_bin

  if ! python_bin="$(pick_python)"; then
    echo "[WARN] Python not found; skipping ${provider} settings seed." >&2
    return 0
  fi

  "${python_bin}" - "${codex_root}" "${provider}" "${base_url}" "${api_key}" <<'PY'
import json
import os
import sys
from pathlib import Path

codex_root, provider, base_url, api_key = sys.argv[1:5]
settings_path = Path(codex_root) / "settings.json"
if not settings_path.exists():
    raise SystemExit(f"settings.json not found: {settings_path}")

with settings_path.open("r", encoding="utf-8-sig") as fh:
    settings = json.load(fh)

env = settings.setdefault("env", {})

if provider == "openai":
    if base_url:
        env["OPENAI_BASE_URL"] = base_url
    if api_key:
        env["OPENAI_API_KEY"] = api_key
elif provider == "ark":
    if base_url:
        env["ARK_BASE_URL"] = base_url
    if api_key:
        env["ARK_API_KEY"] = api_key

env.setdefault("VCO_PROFILE", "full")
env.setdefault("VCO_CODEX_MODE", "true")

with settings_path.open("w", encoding="utf-8", newline="\n") as fh:
    json.dump(settings, fh, ensure_ascii=False, indent=2)
    fh.write("\n")
PY
}

materialize_mcp_profile_with_python() {
  local repo_root="$1"
  local target_root="$2"
  local requested_profile="$3"
  local python_bin

  if ! python_bin="$(pick_python)"; then
    echo "[FAIL] Python is required to materialize the MCP active profile when pwsh is unavailable." >&2
    exit 1
  fi

  "${python_bin}" - "${repo_root}" "${target_root}" "${requested_profile}" <<'PY'
import json
import sys
from pathlib import Path

repo_root = Path(sys.argv[1])
target_root = Path(sys.argv[2])
requested_profile = sys.argv[3].strip()

settings_path = target_root / "settings.json"
profile_name = requested_profile
if not profile_name and settings_path.exists():
    with settings_path.open("r", encoding="utf-8-sig") as fh:
        settings = json.load(fh)
    profile_name = (
        settings.get("vco", {}).get("mcp_profile")
        if isinstance(settings.get("vco"), dict)
        else None
    )
profile_name = profile_name or "full"

template_path = repo_root / "mcp" / "servers.template.json"
profile_path = repo_root / "mcp" / "profiles" / f"{profile_name}.json"
if not template_path.exists():
    raise SystemExit(f"MCP servers template not found: {template_path}")
if not profile_path.exists():
    raise SystemExit(f"MCP profile not found: {profile_path}")

with template_path.open("r", encoding="utf-8-sig") as fh:
    template = json.load(fh)
with profile_path.open("r", encoding="utf-8-sig") as fh:
    profile = json.load(fh)

servers = template.get("servers", {})
enabled = [str(item) for item in profile.get("enabled_servers", [])]
missing = [name for name in enabled if name not in servers]
if missing:
    raise SystemExit("MCP profile references unknown servers: " + ", ".join(sorted(set(missing))))

active = {name: servers[name] for name in enabled}
artifact = {
    "generated_at": __import__("datetime").datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "target_root": str(target_root.resolve()),
    "profile": profile_name,
    "source_template": "mcp/servers.template.json",
    "source_profile": f"mcp/profiles/{profile_name}.json",
    "enabled_servers": enabled,
    "servers": active,
}

output_path = target_root / "mcp" / "servers.active.json"
output_path.parent.mkdir(parents=True, exist_ok=True)
with output_path.open("w", encoding="utf-8", newline="\n") as fh:
    json.dump(artifact, fh, ensure_ascii=False, indent=2)
    fh.write("\n")
PY
}

require_cmd bash "Linux/macOS bootstrap requires bash"
require_cmd git "required by the repository install flow"
require_cmd "$(pick_python || echo python3)" "required for shell-native settings and MCP materialization fallback"
if [[ "${SKIP_EXTERNAL_INSTALL}" != "true" ]]; then
  require_cmd node "required for npm-managed runtimes"
  require_cmd npm "required for claude-flow / external CLI provisioning"
fi

echo "=== VCO One-Shot Setup (shell) ==="
echo "Repo root             : ${REPO_ROOT}"
echo "Target root           : ${TARGET_ROOT}"
echo "Profile               : ${PROFILE}"
echo "StrictOffline         : ${STRICT_OFFLINE}"
echo "SkipExternalInstall   : ${SKIP_EXTERNAL_INSTALL}"
if [[ "${SKIP_EXTERNAL_INSTALL}" != "true" ]]; then
  echo "External CLI install  : enabled (npm-based steps such as claude-flow may take several minutes; deprecated warnings are advisory unless the command exits non-zero)"
fi

install_args=(--profile "${PROFILE}" --target-root "${TARGET_ROOT}")
if [[ "${SKIP_EXTERNAL_INSTALL}" != "true" ]]; then
  install_args+=(--install-external)
fi
if [[ "${STRICT_OFFLINE}" == "true" ]]; then
  install_args+=(--strict-offline)
fi

echo
echo "[1/5] Installing governed runtime payload..."
bash "${INSTALL_SH}" "${install_args[@]}"

resolved_openai_api_key="${OPENAI_API_KEY_INPUT:-${OPENAI_API_KEY:-}}"
existing_openai_key=""
if existing_openai_key="$(read_existing_settings_env_value "${TARGET_ROOT}" "OPENAI_API_KEY" 2>/dev/null)"; then
  :
else
  existing_openai_key=""
fi
if [[ -n "${resolved_openai_api_key}" ]]; then
  echo "[2/5] Seeding OPENAI settings into target settings.json..."
  if command -v pwsh >/dev/null 2>&1; then
    pwsh -NoProfile -File "${PERSIST_OPENAI_PS1}" -CodexRoot "${TARGET_ROOT}" -BaseUrl "${OPENAI_BASE_URL}" -ApiKey "${resolved_openai_api_key}"
  else
    seed_settings_env_with_python "${TARGET_ROOT}" "openai" "${OPENAI_BASE_URL}" "${resolved_openai_api_key}"
  fi
elif [[ -n "${existing_openai_key}" ]]; then
  echo "[2/5] OPENAI settings already exist in target settings.json; keeping current value."
else
  echo "[WARN] OPENAI_API_KEY not provided and not present in the current environment. Full online readiness will remain pending."
fi

resolved_ark_api_key="${ARK_API_KEY_INPUT:-${ARK_API_KEY:-}}"
existing_ark_key=""
if existing_ark_key="$(read_existing_settings_env_value "${TARGET_ROOT}" "ARK_API_KEY" 2>/dev/null)"; then
  :
else
  existing_ark_key=""
fi
if [[ -n "${resolved_ark_api_key}" ]]; then
  echo "[3/5] Seeding ARK settings into target settings.json..."
  if command -v pwsh >/dev/null 2>&1; then
    pwsh -NoProfile -File "${PERSIST_ARK_PS1}" -CodexRoot "${TARGET_ROOT}" -BaseUrl "${ARK_BASE_URL}" -ApiKey "${resolved_ark_api_key}"
  else
    seed_settings_env_with_python "${TARGET_ROOT}" "ark" "${ARK_BASE_URL}" "${resolved_ark_api_key}"
  fi
elif [[ -n "${existing_ark_key}" ]]; then
  echo "[3/5] ARK settings already exist in target settings.json; keeping current value."
else
  echo "[3/5] ARK settings not provided; skipping optional ARK seeding."
fi

echo "[4/5] Materializing MCP profile..."
if command -v pwsh >/dev/null 2>&1; then
  pwsh -NoProfile -File "${MATERIALIZE_PS1}" -TargetRoot "${TARGET_ROOT}" -Force >/dev/null
else
  materialize_mcp_profile_with_python "${REPO_ROOT}" "${TARGET_ROOT}" "${PROFILE}"
fi

echo "[5/5] Running deep health check..."
bash "${CHECK_SH}" --profile "${PROFILE}" --target-root "${TARGET_ROOT}" --deep

echo
echo "One-shot setup completed."
echo "- Re-run deep doctor anytime with: bash ./check.sh --profile ${PROFILE} --target-root \"${TARGET_ROOT}\" --deep"
echo "- MCP active file: ${TARGET_ROOT}/mcp/servers.active.json"
echo "- Doctor artifacts: ${REPO_ROOT}/outputs/verify"
if ! command -v pwsh >/dev/null 2>&1; then
  if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
    echo "[WARN] Neither pwsh nor Python is available. Deep authoritative doctor coverage remains unavailable in this shell environment."
  else
    echo "[INFO] pwsh is not installed, but the shell runtime-neutral verification path was used where supported."
  fi
fi
