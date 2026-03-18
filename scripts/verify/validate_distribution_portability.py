from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_stub_host(root: Path) -> Path:
    stub_path = root / "codex-stub.sh"
    stub_path.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
python3 - "$@" <<'PY'
import json
import os
import sys
print(json.dumps({
  "argv": sys.argv[1:],
  "pwd": os.getcwd(),
  "codex_home": os.environ.get("CODEX_HOME"),
  "evcode_mode": os.environ.get("EVCODE_MODE"),
  "evcode_channel": os.environ.get("EVCODE_CHANNEL"),
  "evcode_profile": os.environ.get("EVCODE_PROFILE"),
  "evcode_dist_root": os.environ.get("EVCODE_DIST_ROOT"),
  "evcode_runtime_root": os.environ.get("EVCODE_RUNTIME_ROOT"),
}))
PY
""",
        encoding="utf-8",
    )
    stub_path.chmod(stub_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return stub_path


def run_json(command: list[str], *, cwd: Path, env: dict[str, str]) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    return json.loads(completed.stdout)


def validate(repo_root: Path, keep_temp: bool) -> dict[str, Any]:
    temp_root_path = Path(tempfile.mkdtemp(prefix="evcode-distribution-portability-"))
    try:
        xdg_config_home = temp_root_path / "xdg-config"
        portable_root = xdg_config_home / "evcode"
        portable_root.mkdir(parents=True, exist_ok=True)
        portable_env_path = portable_root / "assistant-providers.env"
        portable_env_path.write_text(
            "\n".join(
                [
                    "EVCODE_RIGHTCODES_API_KEY=sk-portable-test",
                    "EVCODE_CODEX_MODEL=gpt-5.4-portable",
                    "EVCODE_CLAUDE_MODEL=claude-portable",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        external_workspace = temp_root_path / "external-workspace"
        external_workspace.mkdir(parents=True, exist_ok=True)
        source_mode_status = run_json(
            ["node", str(repo_root / "apps" / "evcode" / "bin" / "evcode.js"), "status", "--json"],
            cwd=external_workspace,
            env={**os.environ, "XDG_CONFIG_HOME": str(xdg_config_home)},
        )

        stub_host = write_stub_host(temp_root_path)
        install_root = temp_root_path / "install"
        for channel in ("standard", "benchmark"):
            subprocess.run(
                [
                    "python3",
                    str(repo_root / "scripts" / "build" / "assemble_distribution.py"),
                    "--channel",
                    channel,
                    "--output-root",
                    str(install_root),
                    "--link-mode",
                    "copy",
                    "--host-binary",
                    "missing-codex-host",
                    "--bundled-host-binary",
                    str(stub_host),
                ],
                cwd=repo_root,
                capture_output=True,
                text=True,
                check=True,
            )

        standard_launcher_payload = run_json(
            [str(install_root / "standard" / "bin" / "evcode"), "--version"],
            cwd=external_workspace,
            env=os.environ.copy(),
        )
        benchmark_launcher_payload = run_json(
            [str(install_root / "benchmark" / "bin" / "evcode-bench"), "--version"],
            cwd=external_workspace,
            env=os.environ.copy(),
        )

        return {
            "task": "evcode distributed install portability validation",
            "generated_at": utc_now(),
            "repo_root": str(repo_root),
            "temp_root": str(temp_root_path),
            "external_workspace": str(external_workspace),
            "portable_config_root": str(portable_root),
            "portable_env_path": str(portable_env_path),
            "source_mode_external_cwd": {
                "cwd": str(external_workspace),
                "active_env_source": source_mode_status["provider_setup"]["active_env_source"],
                "resolved_local_env_path": source_mode_status["provider_setup"]["resolved_local_env_path"],
                "portable_config_root": source_mode_status["provider_setup"]["portable_config_root"],
                "codex_model": source_mode_status["assistant_provider_resolution"]["codex"]["model"],
                "claude_model": source_mode_status["assistant_provider_resolution"]["claude"]["model"],
            },
            "assembled_launchers": {
                "standard": standard_launcher_payload,
                "benchmark": benchmark_launcher_payload,
            },
            "checks": {
                "portable_source_mode_external_cwd": (
                    source_mode_status["provider_setup"]["active_env_source"] == "portable_user_config"
                    and source_mode_status["assistant_provider_resolution"]["codex"]["model"] == "gpt-5.4-portable"
                ),
                "standard_launcher_external_workspace": (
                    standard_launcher_payload["evcode_channel"] == "standard"
                    and str(install_root / "standard" / "codex-home") == standard_launcher_payload["codex_home"]
                    and standard_launcher_payload["pwd"] == str(external_workspace)
                ),
                "benchmark_launcher_external_workspace": (
                    benchmark_launcher_payload["evcode_channel"] == "benchmark"
                    and str(install_root / "benchmark" / "codex-home") == benchmark_launcher_payload["codex_home"]
                    and benchmark_launcher_payload["pwd"] == str(external_workspace)
                ),
            },
        }
    finally:
        if not keep_temp:
            shutil.rmtree(temp_root_path, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate EvCode portability from a distributed-install perspective.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--keep-temp", action="store_true")
    args = parser.parse_args()

    payload = validate(Path(args.repo_root).resolve(), keep_temp=args.keep_temp)
    payload["status"] = "pass" if all(payload["checks"].values()) else "fail"
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"status={payload['status']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
