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
