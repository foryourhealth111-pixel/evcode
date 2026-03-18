from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class HybridBaselineTests(unittest.TestCase):
    def test_baseline_family_runner_reports_hybrid_and_core_lanes(self) -> None:
        completed = subprocess.run(
            [
                "python3",
                str(REPO_ROOT / "scripts" / "verify" / "run_hybrid_baseline.py"),
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
        self.assertEqual("hybrid_governed", payload["profile_mapping"]["standard"])
        self.assertEqual("core_benchmark", payload["profile_mapping"]["benchmark"])
        self.assertEqual("pass", payload["families"]["hybrid_governed"]["status"])
        self.assertEqual("pass", payload["families"]["core_benchmark"]["status"])
        hybrid_scenarios = {item["id"]: item for item in payload["families"]["hybrid_governed"]["scenarios"]}
        self.assertEqual("codex_only", hybrid_scenarios["codex_backend_only"]["observed"]["route_kind"])
        self.assertEqual(["claude"], hybrid_scenarios["claude_planning"]["observed"]["requested_delegates"])
        self.assertEqual(["gemini"], hybrid_scenarios["gemini_frontend_visual"]["observed"]["requested_delegates"])
        core_scenarios = {item["id"]: item for item in payload["families"]["core_benchmark"]["scenarios"]}
        self.assertEqual("codex_only_benchmark", core_scenarios["benchmark_specialist_suppression"]["observed"]["route_kind"])
