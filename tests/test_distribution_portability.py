from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class DistributionPortabilityTests(unittest.TestCase):
    def test_distribution_portability_validator_passes(self) -> None:
        completed = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "scripts" / "verify" / "validate_distribution_portability.py"),
                "--repo-root",
                str(REPO_ROOT),
                "--json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"])
        self.assertEqual("portable_user_config", payload["source_mode_external_cwd"]["active_env_source"])
        self.assertEqual("gpt-5.4-portable", payload["source_mode_external_cwd"]["codex_model"])
        self.assertEqual("claude-portable", payload["source_mode_external_cwd"]["claude_model"])
        self.assertEqual("standard", payload["assembled_launchers"]["standard"]["evcode_channel"])
        self.assertEqual("benchmark", payload["assembled_launchers"]["benchmark"]["evcode_channel"])
        self.assertTrue(all(payload["checks"].values()))
