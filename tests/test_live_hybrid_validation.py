from __future__ import annotations

import json
import os
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class LiveHybridValidationTests(unittest.TestCase):
    def test_live_validator_skips_cleanly_without_live_env(self) -> None:
        env = {k: v for k, v in os.environ.items() if k not in {"EVCODE_RIGHTCODES_API_KEY", "EVCODE_ENABLE_LIVE_SPECIALISTS"}}
        completed = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "scripts" / "verify" / "run_live_hybrid_validation.py"),
                "--repo-root",
                str(REPO_ROOT),
                "--json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
            env=env,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("skipped", payload["status"])
        self.assertIn("live", payload["reason"])
