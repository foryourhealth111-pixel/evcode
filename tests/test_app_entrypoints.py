from __future__ import annotations

import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def make_stub_host(tempdir: str) -> Path:
    stub_path = Path(tempdir) / "codex-stub.sh"
    stub_path.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
python3 - "$@" <<'PY'
import json
import os
import sys
print(json.dumps({
  "argv": sys.argv[1:],
  "codex_home": os.environ.get("CODEX_HOME"),
  "evcode_mode": os.environ.get("EVCODE_MODE"),
  "evcode_channel": os.environ.get("EVCODE_CHANNEL"),
}))
PY
""",
        encoding="utf-8",
    )
    stub_path.chmod(stub_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return stub_path


class AppEntrypointTests(unittest.TestCase):
    def test_benchmark_status_reports_default_submission_preset(self) -> None:
        completed = subprocess.run(
            ["node", str(REPO_ROOT / "apps" / "evcode-bench" / "bin" / "evcode-bench.js"), "status", "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("benchmark", payload["channel"])
        self.assertEqual(
            "config/submission-presets/rightcode-gpt-5.4-xhigh.json",
            payload["default_submission_preset"],
        )

    def test_standard_entrypoint_passthrough_launches_native_host(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            stub = make_stub_host(tempdir)
            source_codex_home = Path(tempdir) / "source-codex-home"
            source_codex_home.mkdir(parents=True, exist_ok=True)
            (source_codex_home / "config.toml").write_text(
                """
model_provider = "rightcode"
model = "gpt-5.4"

[model_providers.rightcode]
base_url = "https://right.codes/codex/v1"
wire_api = "responses"
requires_openai_auth = true
""".strip()
                + "\n",
                encoding="utf-8",
            )
            (source_codex_home / "auth.json").write_text('{"OPENAI_API_KEY":"test-key"}\n', encoding="utf-8")
            completed = subprocess.run(
                ["node", str(REPO_ROOT / "apps" / "evcode" / "bin" / "evcode.js"), "--version"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
                env={
                    **os.environ,
                    "EVCODE_HOST_BIN": str(stub),
                    "EVCODE_DIST_OUTPUT_ROOT": tempdir,
                    "EVCODE_SOURCE_CODEX_HOME": str(source_codex_home),
                },
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(["--version"], payload["argv"])
            self.assertEqual("interactive_governed", payload["evcode_mode"])
            self.assertEqual("standard", payload["evcode_channel"])
            assembled_config = (Path(tempdir) / "standard" / "codex-home" / "config.toml").read_text(encoding="utf-8")
            self.assertIn('model_provider = "rightcode"', assembled_config)
            self.assertIn('model = "gpt-5.4"', assembled_config)
            self.assertTrue((Path(tempdir) / "standard" / "codex-home" / "auth.json").exists())

    def test_standard_status_reports_assembled_config_snapshot(self) -> None:
        completed = subprocess.run(
            ["node", str(REPO_ROOT / "apps" / "evcode" / "bin" / "evcode.js"), "status", "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("standard", payload["channel"])
        self.assertIn("bundled_host_available", payload)
        self.assertIn("source_codex_home", payload)
        if payload["assembled_distribution_exists"]:
            self.assertIn("assembled", payload)

    def test_standard_entrypoint_uses_bundled_host_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            stub = make_stub_host(tempdir)
            subprocess.run(
                [
                    "python3",
                    str(REPO_ROOT / "scripts" / "build" / "assemble_distribution.py"),
                    "--channel",
                    "standard",
                    "--output-root",
                    tempdir,
                    "--host-binary",
                    "missing-codex-host",
                    "--bundled-host-binary",
                    str(stub),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            completed = subprocess.run(
                ["node", str(REPO_ROOT / "apps" / "evcode" / "bin" / "evcode.js"), "native", "--version"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
                env={
                    **os.environ,
                    "EVCODE_DIST_OUTPUT_ROOT": tempdir,
                },
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(["--version"], payload["argv"])
            self.assertEqual("standard", payload["evcode_channel"])

    def test_benchmark_entrypoint_auto_adopts_source_codex_home_and_bundled_host(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            stub = make_stub_host(tempdir)
            source_codex_home = Path(tempdir) / "source-codex-home"
            source_codex_home.mkdir(parents=True, exist_ok=True)
            (source_codex_home / "config.toml").write_text(
                """
model_provider = "rightcode"
model = "gpt-5.4"

[model_providers.rightcode]
base_url = "https://right.codes/codex/v1"
wire_api = "responses"
requires_openai_auth = true
""".strip()
                + "\n",
                encoding="utf-8",
            )
            (source_codex_home / "auth.json").write_text('{"OPENAI_API_KEY":"test-key"}\n', encoding="utf-8")
            subprocess.run(
                [
                    "python3",
                    str(REPO_ROOT / "scripts" / "build" / "assemble_distribution.py"),
                    "--channel",
                    "benchmark",
                    "--output-root",
                    tempdir,
                    "--host-binary",
                    "missing-codex-host",
                    "--bundled-host-binary",
                    str(stub),
                    "--source-codex-home",
                    str(source_codex_home),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            completed = subprocess.run(
                ["node", str(REPO_ROOT / "apps" / "evcode-bench" / "bin" / "evcode-bench.js"), "native", "--version"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
                env={
                    **os.environ,
                    "EVCODE_DIST_OUTPUT_ROOT": tempdir,
                    "EVCODE_SOURCE_CODEX_HOME": str(source_codex_home),
                },
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(["--version"], payload["argv"])
            self.assertEqual("benchmark_autonomous", payload["evcode_mode"])
            self.assertEqual("benchmark", payload["evcode_channel"])
            assembled_config = (Path(tempdir) / "benchmark" / "codex-home" / "config.toml").read_text(encoding="utf-8")
            self.assertIn('model_provider = "rightcode"', assembled_config)
            self.assertIn('model = "gpt-5.4"', assembled_config)
            self.assertTrue((Path(tempdir) / "benchmark" / "codex-home" / "auth.json").exists())


if __name__ == "__main__":
    unittest.main()
