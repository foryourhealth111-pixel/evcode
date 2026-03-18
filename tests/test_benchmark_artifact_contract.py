from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class BenchmarkArtifactContractTests(unittest.TestCase):
    def test_benchmark_run_materializes_handoff_at_requested_workspace_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp_root = Path(tempdir)
            workspace = temp_root / "workspace"
            workspace.mkdir()
            requested_artifacts_root = workspace / "requested-artifacts"
            requested_result_json = workspace / "requested-output" / "result.json"
            fake_codex = temp_root / "fake_codex"
            fake_codex.write_text(
                """#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path

argv = sys.argv[1:]
for index, token in enumerate(argv):
    if token == "--output-last-message":
        Path(argv[index + 1]).write_text("portable handoff completed", encoding="utf-8")
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
                    "Verify benchmark artifact handoff semantics",
                    "--workspace",
                    str(workspace),
                    "--artifacts-root",
                    str(requested_artifacts_root),
                    "--result-json",
                    str(requested_result_json),
                    "--run-id",
                    "portable-handoff-smoke",
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
            artifacts = payload["artifacts"]
            self.assertTrue(artifacts["artifacts_redirected"])
            self.assertNotEqual(str(requested_artifacts_root.resolve()), artifacts["effective_artifacts_root"])
            self.assertEqual(str(requested_result_json.resolve()), artifacts["requested_benchmark_result"])
            self.assertTrue(Path(artifacts["requested_benchmark_result"]).exists())
            self.assertTrue(Path(artifacts["artifacts_handoff_manifest"]).exists())
            self.assertTrue((requested_artifacts_root / "runtime-summary.json").exists())

            result_payload = json.loads(requested_result_json.read_text(encoding="utf-8"))
            self.assertEqual("completed", result_payload["status"])
            self.assertEqual(str(requested_result_json.resolve()), result_payload["requested_result_json_path"])
            self.assertNotEqual(result_payload["requested_result_json_path"], result_payload["effective_result_json_path"])

            manifest = json.loads(Path(artifacts["artifacts_handoff_manifest"]).read_text(encoding="utf-8"))
            self.assertEqual(str(requested_artifacts_root.resolve()), manifest["requested_artifacts_root"])
            self.assertEqual(artifacts["effective_artifacts_root"], manifest["effective_artifacts_root"])
            self.assertTrue(Path(manifest["requested_summary_copy"]).exists())


if __name__ == "__main__":
    unittest.main()
