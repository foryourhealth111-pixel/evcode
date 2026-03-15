from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_STAGE_ORDER = [
    "skeleton_check",
    "deep_interview",
    "requirement_doc",
    "xl_plan",
    "plan_execute",
    "phase_cleanup",
]


class RuntimeBridgeTests(unittest.TestCase):
    def test_standard_run_writes_governed_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            completed = subprocess.run(
                [
                    "node",
                    str(REPO_ROOT / "apps" / "evcode" / "bin" / "evcode.js"),
                    "run",
                    "--task",
                    "Design and implement a governed standard channel smoke test",
                    "--artifacts-root",
                    tempdir,
                    "--run-id",
                    "standard-smoke",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(completed.stdout)
            self.assertEqual("interactive_governed", payload["mode"])
            self.assertEqual("standard", payload["channel"])
            self.assertEqual(EXPECTED_STAGE_ORDER, payload["stage_order"])
            requirement_doc = Path(payload["artifacts"]["requirement_doc"])
            execution_plan = Path(payload["artifacts"]["execution_plan"])
            cleanup_receipt = Path(payload["artifacts"]["cleanup_receipt"])
            self.assertTrue(requirement_doc.exists())
            self.assertTrue(execution_plan.exists())
            self.assertTrue(cleanup_receipt.exists())

    def test_benchmark_run_writes_governed_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp_root = Path(tempdir)
            workspace = temp_root / "workspace"
            workspace.mkdir()
            fake_codex = temp_root / "fake_codex"
            fake_codex.write_text(
                """#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path

argv = sys.argv[1:]
for index, token in enumerate(argv):
    if token == "--output-last-message":
        Path(argv[index + 1]).write_text("runtime bridge benchmark completed", encoding="utf-8")
        break
sys.exit(0)
""",
                encoding="utf-8",
            )
            fake_codex.chmod(0o755)
            completed = subprocess.run(
                [
                    "node",
                    str(REPO_ROOT / "apps" / "evcode-bench" / "bin" / "evcode-bench.js"),
                    "run",
                    "--task",
                    "Build a benchmark-safe autonomous runtime smoke test with proof artifacts",
                    "--workspace",
                    str(workspace),
                    "--artifacts-root",
                    tempdir,
                    "--run-id",
                    "benchmark-smoke",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
                env={
                    **os.environ,
                    "EVCODE_BENCH_HOST_BIN": str(fake_codex),
                },
            )
            payload = json.loads(completed.stdout)
            self.assertEqual("benchmark_autonomous", payload["mode"])
            self.assertEqual("benchmark", payload["channel"])
            requirement_doc = Path(payload["artifacts"]["requirement_doc"])
            self.assertIn("Assumptions", requirement_doc.read_text(encoding="utf-8"))
            self.assertTrue(Path(payload["artifacts"]["benchmark_result"]).exists())
            self.assertFalse((workspace / "docs").exists())
            self.assertFalse((workspace / "outputs").exists())


if __name__ == "__main__":
    unittest.main()
