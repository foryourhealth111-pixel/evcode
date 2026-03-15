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
printf '%s\\n' \"$0\"
""",
        encoding="utf-8",
    )
    stub_path.chmod(stub_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return stub_path


class ReleasePackageTests(unittest.TestCase):
    def test_release_packages_are_self_contained_with_stub_host(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            stub = make_stub_host(tempdir)
            built = subprocess.run(
                [
                    "python3",
                    str(REPO_ROOT / "scripts" / "release" / "build_release_packages.py"),
                    "--output-root",
                    tempdir,
                    "--bundled-host-binary",
                    str(stub),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            manifest = json.loads(built.stdout)
            self.assertTrue(manifest["self_contained_release"])
            verify = subprocess.run(
                [
                    "python3",
                    str(REPO_ROOT / "scripts" / "verify" / "check_release_packages.py"),
                    "--manifest",
                    manifest["manifest_path"],
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertIn("release package checks: ok", verify.stdout)


if __name__ == "__main__":
    unittest.main()
