from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import re

try:
    import tomllib as toml_reader
except ModuleNotFoundError:
    try:
        import toml as toml_reader
    except ModuleNotFoundError:
        from pip._vendor import tomli as toml_reader


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def remove_path(path: Path) -> None:
    if not path.exists() and not path.is_symlink():
        return
    if path.is_symlink() or path.is_file():
        path.unlink()
    else:
        shutil.rmtree(path)


def stage_directory(source: Path, target: Path, link_mode: str) -> None:
    remove_path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    if link_mode == "symlink":
        os.symlink(source, target, target_is_directory=True)
        return
    shutil.copytree(source, target)


def write_text(path: Path, content: str, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if executable:
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def read_text_if_exists(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def load_source_codex_config(source_codex_home: Path | None) -> dict:
    if source_codex_home is None:
        return {}
    config_path = source_codex_home / "config.toml"
    if not config_path.exists():
        return {}
    return toml_reader.loads(config_path.read_text(encoding="utf-8"))


def format_toml_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(value)


def quote_toml_key(part: str) -> str:
    return part if re.match(r"^[A-Za-z0-9_-]+$", part) else json.dumps(part)


def render_toml_table(parts: list[str], table: dict) -> list[str]:
    lines = [f"[{'.'.join(quote_toml_key(part) for part in parts)}]"]
    nested_tables: list[tuple[list[str], dict]] = []
    for key, value in table.items():
        if isinstance(value, dict):
            nested_tables.append((parts + [key], value))
            continue
        lines.append(f"{quote_toml_key(key)} = {format_toml_value(value)}")
    lines.append("")
    for nested_parts, nested_table in nested_tables:
        lines.extend(render_toml_table(nested_parts, nested_table))
    return lines


def build_adopted_config_sections(source_config: dict) -> tuple[list[str], list[str]]:
    top_level_keys = [
        "model_provider",
        "model",
        "model_reasoning_effort",
        "model_verbosity",
        "network_access",
        "disable_response_storage",
        "windows_wsl_setup_acknowledged",
        "ask_for_approval",
        "dangerously_bypass_approvals_and_sandbox",
        "full-auto",
        "bypass-approvals",
        "bypass-sandbox",
        "sandbox_mode",
        "trusted-workspace",
    ]
    table_keys = ["model_providers", "mcp_servers", "projects", "notice"]
    top_level_lines: list[str] = []
    for key in top_level_keys:
        if key in source_config:
            top_level_lines.append(f"{key} = {format_toml_value(source_config[key])}")
    if top_level_lines:
        top_level_lines.append("")
    table_lines: list[str] = []
    for table_key in table_keys:
        table = source_config.get(table_key)
        if isinstance(table, dict) and table:
            table_lines.extend(render_toml_table([table_key], table))
    return top_level_lines, table_lines


def build_config_toml(runtime_root: Path, profile: str, source_config: dict | None = None) -> str:
    hooks_root = runtime_root / "hooks"
    lines: list[str] = []
    adopted_table_lines: list[str] = []
    if source_config:
        adopted_top_level_lines, adopted_table_lines = build_adopted_config_sections(source_config)
        lines.extend(adopted_top_level_lines)
    lines.extend(
        [
            f'profile = "{profile}"',
            "disable_cron = false",
            "",
            f"[profiles.{profile}]",
            "disable_cron = false",
            "",
        ]
    )
    lines.extend(adopted_table_lines)
    lines.extend(
        [
            "[hooks]",
            "",
            "[[hooks.user_prompt_submit]]",
            f'command = ["python3", "{(hooks_root / "user_prompt_submit.py").as_posix()}"]',
            "",
            "[[hooks.subagent_start]]",
            f'command = ["python3", "{(hooks_root / "subagent_start.py").as_posix()}"]',
            "",
            "[[hooks.task_completed]]",
            f'command = ["python3", "{(hooks_root / "task_completed.py").as_posix()}"]',
            "",
            "[[hooks.stop]]",
            f'command = ["python3", "{(hooks_root / "stop.py").as_posix()}"]',
            "",
        ]
    )
    return "\n".join(lines)


def build_launcher(binary_name: str, mode: str, channel: str, profile: str, host_binary: str) -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail

SELF_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
DIST_ROOT="$(CDPATH= cd -- "$SELF_DIR/.." && pwd)"
DEFAULT_HOST_BIN="{host_binary}"
BUNDLED_HOST_BIN="$DIST_ROOT/host/bin/codex"
HOST_BIN="${{EVCODE_HOST_BIN:-}}"
if [[ -z "$HOST_BIN" && -x "$BUNDLED_HOST_BIN" ]]; then
  HOST_BIN="$BUNDLED_HOST_BIN"
fi
HOST_BIN="${{HOST_BIN:-$DEFAULT_HOST_BIN}}"
if [[ "$HOST_BIN" != */* ]]; then
  if ! command -v "$HOST_BIN" >/dev/null 2>&1; then
    echo "EvCode could not find host binary: $HOST_BIN" >&2
    exit 1
  fi
  HOST_BIN="$(command -v "$HOST_BIN")"
elif [[ ! -x "$HOST_BIN" ]]; then
  echo "EvCode host binary is not executable: $HOST_BIN" >&2
  exit 1
fi

export CODEX_HOME="$DIST_ROOT/codex-home"
export EVCODE_MODE="{mode}"
export EVCODE_CHANNEL="{channel}"
export EVCODE_PROFILE="{profile}"
export EVCODE_DIST_ROOT="$DIST_ROOT"
export EVCODE_RUNTIME_ROOT="$DIST_ROOT/evcode-runtime"
export EVCODE_ARTIFACTS_ROOT="${{EVCODE_ARTIFACTS_ROOT:-$PWD}}"
export EVCODE_WORKSPACE_ROOT="${{EVCODE_WORKSPACE_ROOT:-$PWD}}"

exec "$HOST_BIN" "$@"
"""


def stage_metadata(repo_root: Path, metadata_root: Path) -> None:
    metadata_root.mkdir(parents=True, exist_ok=True)
    for relative_path in (
        "config/sources.lock.json",
        "config/runtime-contract.json",
        "config/distributions.json",
        "config/host-integration.json",
        "vendor/codex-host/materialization.json",
        "runtime/vco/materialization.json",
        "runtime/vco/freshness.json",
        "runtime/vco/required-runtime-markers.json",
        "vendor/codex-host/UPSTREAM.md",
        "vendor/codex-host/PATCHES.md",
    ):
        source = repo_root / relative_path
        target = metadata_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def stage_runtime(repo_root: Path, runtime_root: Path, link_mode: str) -> None:
    stage_directory(repo_root / "scripts" / "hooks", runtime_root / "hooks", link_mode)
    stage_directory(repo_root / "scripts" / "runtime", runtime_root / "runtime", link_mode)
    stage_directory(repo_root / "config", runtime_root / "config", link_mode)
    stage_directory(repo_root / "protocols", runtime_root / "protocols", link_mode)
    stage_directory(repo_root / "core", runtime_root / "core", link_mode)


def stage_skills(repo_root: Path, codex_home: Path, link_mode: str) -> None:
    bundled_skills = repo_root / "runtime" / "vco" / "upstream" / "bundled" / "skills"
    stage_directory(bundled_skills, codex_home / "skills", link_mode)


def stage_source_codex_material(source_codex_home: Path | None, codex_home: Path) -> dict[str, bool]:
    copied = {"auth_json": False, "env_local": False}
    if source_codex_home is None:
        return copied
    for filename, manifest_key in (("auth.json", "auth_json"), ("env.local", "env_local")):
        source = source_codex_home / filename
        if not source.exists():
            continue
        shutil.copy2(source, codex_home / filename)
        copied[manifest_key] = True
    return copied


def stage_patch_file(repo_root: Path, dist_root: Path) -> Path:
    patch_source = repo_root / "vendor" / "codex-host" / "patches" / "subagent-vibe-suffix.patch"
    patch_target = dist_root / "vendor" / "codex-host" / "patches" / "subagent-vibe-suffix.patch"
    patch_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(patch_source, patch_target)
    return patch_target


def stage_patched_host_source(repo_root: Path, dist_root: Path, patch_path: Path) -> Path:
    source_root = repo_root / "vendor" / "codex-host" / "upstream"
    target_root = dist_root / "vendor" / "codex-host" / "patched-upstream"
    remove_path(target_root)
    shutil.copytree(source_root, target_root)
    subprocess.run(["git", "apply", str(patch_path)], cwd=target_root, check=True)
    return target_root


def stage_bundled_host_binary(source: Path, dist_root: Path) -> Path:
    target = dist_root / "host" / "bin" / "codex"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Assemble an EvCode distribution directory.")
    parser.add_argument("--channel", choices=["standard", "benchmark"], required=True)
    parser.add_argument("--output-root", default=".evcode-dist", help="Distribution output root")
    parser.add_argument("--link-mode", choices=["symlink", "copy"], default="symlink")
    parser.add_argument("--host-binary", default="", help="Host binary path or command name")
    parser.add_argument("--bundled-host-binary", default="", help="Optional patched host binary to embed in the distribution")
    parser.add_argument("--stage-patched-host-source", action="store_true")
    parser.add_argument("--source-codex-home", default="", help="Optional source CODEX_HOME to adopt model/provider/auth settings from")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    distributions = json.loads((repo_root / "config" / "distributions.json").read_text(encoding="utf-8"))
    channel_info = distributions["channels"][args.channel]

    dist_root = Path(args.output_root).resolve() / args.channel
    remove_path(dist_root)
    dist_root.mkdir(parents=True, exist_ok=True)

    profile = channel_info["profile"]
    mode = channel_info["default_mode"]
    binary_name = channel_info["binary"]
    host_binary = args.host_binary or shutil.which("codex") or "codex"

    runtime_root = dist_root / "evcode-runtime"
    codex_home = dist_root / "codex-home"
    stage_runtime(repo_root, runtime_root, args.link_mode)
    stage_skills(repo_root, codex_home, args.link_mode)
    source_codex_home = Path(args.source_codex_home).expanduser().resolve() if args.source_codex_home else None
    source_config = load_source_codex_config(source_codex_home)
    write_text(codex_home / "config.toml", build_config_toml(runtime_root, profile, source_config))
    copied_source_material = stage_source_codex_material(source_codex_home, codex_home)

    metadata_root = dist_root / "metadata"
    stage_metadata(repo_root, metadata_root)
    patch_target = stage_patch_file(repo_root, dist_root)

    patched_host_root = None
    if args.stage_patched_host_source:
        patched_host_root = stage_patched_host_source(repo_root, dist_root, patch_target)

    bundled_host_binary = None
    if args.bundled_host_binary:
        bundled_host_binary = stage_bundled_host_binary(Path(args.bundled_host_binary).resolve(), dist_root)

    launcher_path = dist_root / "bin" / binary_name
    write_text(launcher_path, build_launcher(binary_name, mode, args.channel, profile, host_binary), executable=True)

    manifest = {
        "assembled_at": utc_now(),
        "channel": args.channel,
        "profile": profile,
        "mode": mode,
        "binary": binary_name,
        "dist_root": str(dist_root),
        "launcher": str(launcher_path),
        "codex_home": str(codex_home),
        "runtime_root": str(runtime_root),
        "skills_root": str(codex_home / "skills"),
        "link_mode": args.link_mode,
        "host_binary": host_binary,
        "bundled_host_binary": str(bundled_host_binary) if bundled_host_binary else None,
        "patch_file": str(patch_target),
        "patched_host_source": str(patched_host_root) if patched_host_root else None,
        "source_codex_home": str(source_codex_home) if source_codex_home else None,
        "copied_auth_json": copied_source_material["auth_json"],
        "copied_env_local": copied_source_material["env_local"],
    }
    write_text(metadata_root / "assembly-manifest.json", json.dumps(manifest, indent=2))
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
