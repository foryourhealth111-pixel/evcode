from __future__ import annotations

import json
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


class DistributionAssemblyTests(unittest.TestCase):
    def test_standard_distribution_can_adopt_source_codex_home(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            stub = make_stub_host(tempdir)
            source_codex_home = Path(tempdir) / "source-codex-home"
            source_codex_home.mkdir(parents=True, exist_ok=True)
            (source_codex_home / "config.toml").write_text(
                """
model_provider = "rightcode"
model = "gpt-5.4"
model_reasoning_effort = "high"

[model_providers.rightcode]
base_url = "https://right.codes/codex/v1"
wire_api = "responses"
requires_openai_auth = true

[mcp_servers.github]
url = "https://api.githubcopilot.com/mcp/"
bearer_token_env_var = "CODEX_GITHUB_PERSONAL_ACCESS_TOKEN"
""".strip()
                + "\n",
                encoding="utf-8",
            )
            (source_codex_home / "auth.json").write_text('{"OPENAI_API_KEY":"test-key"}\n', encoding="utf-8")
            (source_codex_home / "env.local").write_text(
                "export CODEX_GITHUB_PERSONAL_ACCESS_TOKEN='test-token'\n",
                encoding="utf-8",
            )

            assembled = subprocess.run(
                [
                    "python3",
                    str(REPO_ROOT / "scripts" / "build" / "assemble_distribution.py"),
                    "--channel",
                    "standard",
                    "--output-root",
                    tempdir,
                    "--host-binary",
                    str(stub),
                    "--source-codex-home",
                    str(source_codex_home),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            manifest = json.loads(assembled.stdout)
            dist_root = Path(manifest["dist_root"])
            config_toml = (dist_root / "codex-home" / "config.toml").read_text(encoding="utf-8")
            self.assertIn('model_provider = "rightcode"', config_toml)
            self.assertIn('model = "gpt-5.4"', config_toml)
            self.assertIn("[model_providers.rightcode]", config_toml)
            self.assertIn('base_url = "https://right.codes/codex/v1"', config_toml)
            self.assertIn("[mcp_servers.github]", config_toml)
            self.assertTrue((dist_root / "codex-home" / "auth.json").exists())
            self.assertTrue((dist_root / "codex-home" / "env.local").exists())
            self.assertEqual(str(source_codex_home.resolve()), manifest["source_codex_home"])
            self.assertTrue(manifest["copied_auth_json"])
            self.assertTrue(manifest["copied_env_local"])

    def test_standard_distribution_assembles_and_launches(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            stub = make_stub_host(tempdir)
            assembled = subprocess.run(
                [
                    "python3",
                    str(REPO_ROOT / "scripts" / "build" / "assemble_distribution.py"),
                    "--channel",
                    "standard",
                    "--output-root",
                    tempdir,
                    "--host-binary",
                    str(stub),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            manifest = json.loads(assembled.stdout)
            dist_root = Path(manifest["dist_root"])
            self.assertTrue((dist_root / "codex-home" / "skills" / "vibe" / "SKILL.md").exists())
            launched = subprocess.run(
                [str(dist_root / "bin" / "evcode"), "resume", "--yolo"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(launched.stdout)
            self.assertEqual(["resume", "--yolo"], payload["argv"])
            self.assertEqual("interactive_governed", payload["evcode_mode"])
            self.assertEqual("standard", payload["evcode_channel"])
            self.assertTrue(payload["codex_home"].endswith("/codex-home"))
            config_toml = (dist_root / "codex-home" / "config.toml").read_text(encoding="utf-8")
            self.assertIn('profile = "standard"', config_toml)
            self.assertIn("[profiles.standard]", config_toml)

    def test_standard_distribution_prefers_bundled_host_binary(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            stub = make_stub_host(tempdir)
            assembled = subprocess.run(
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
            manifest = json.loads(assembled.stdout)
            dist_root = Path(manifest["dist_root"])
            self.assertTrue((dist_root / "host" / "bin" / "codex").exists())
            launched = subprocess.run(
                [str(dist_root / "bin" / "evcode"), "resume"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(launched.stdout)
            self.assertEqual(["resume"], payload["argv"])
            self.assertEqual("standard", payload["evcode_channel"])

    def test_benchmark_distribution_assembles_and_launches(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            stub = make_stub_host(tempdir)
            assembled = subprocess.run(
                [
                    "python3",
                    str(REPO_ROOT / "scripts" / "build" / "assemble_distribution.py"),
                    "--channel",
                    "benchmark",
                    "--output-root",
                    tempdir,
                    "--host-binary",
                    str(stub),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            manifest = json.loads(assembled.stdout)
            dist_root = Path(manifest["dist_root"])
            launched = subprocess.run(
                [str(dist_root / "bin" / "evcode-bench"), "--version"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(launched.stdout)
            self.assertEqual(["--version"], payload["argv"])
            self.assertEqual("benchmark_autonomous", payload["evcode_mode"])
            self.assertEqual("benchmark", payload["evcode_channel"])


if __name__ == "__main__":
    unittest.main()
