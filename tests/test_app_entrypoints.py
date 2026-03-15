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
                },
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(["--version"], payload["argv"])
            self.assertEqual("interactive_governed", payload["evcode_mode"])
            self.assertEqual("standard", payload["evcode_channel"])

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


if __name__ == "__main__":
    unittest.main()
