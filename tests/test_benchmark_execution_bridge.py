from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class BenchmarkExecutionBridgeTests(unittest.TestCase):
    def test_benchmark_run_executes_bridge_and_writes_result_json(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp_root = Path(tempdir)
            executor_script = temp_root / "fake_executor.py"
            executor_script.write_text(
                """from __future__ import annotations
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--task-file", required=True)
parser.add_argument("--result-json", required=True)
parser.add_argument("--workspace", required=True)
parser.add_argument("--run-dir", required=True)
args = parser.parse_args()
task_text = Path(args.task_file).read_text(encoding="utf-8")
payload = {
    "status": "completed",
    "executor": "fake",
    "workspace": args.workspace,
    "task_excerpt": task_text.splitlines()[-1],
}
Path(args.result_json).write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(json.dumps(payload))
""",
                encoding="utf-8",
            )
            result_json_path = temp_root / "bench-out" / "result.json"
            env = {
                **os.environ,
                "EVCODE_BENCHMARK_EXECUTOR": f"python3 {executor_script} --task-file {{task_file}} --result-json {{result_json}} --workspace {{workspace}} --run-dir {{run_dir}}",
            }
            completed = subprocess.run(
                [
                    "node",
                    str(REPO_ROOT / "apps" / "evcode-bench" / "bin" / "evcode-bench.js"),
                    "run",
                    "--task",
                    "Implement benchmark bridge smoke execution",
                    "--workspace",
                    str(REPO_ROOT),
                    "--artifacts-root",
                    tempdir,
                    "--run-id",
                    "benchmark-bridge-smoke",
                    "--result-json",
                    str(result_json_path),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
                env=env,
            )
            payload = json.loads(completed.stdout)
            execute_receipt = Path(payload["artifacts"]["execute_receipt"])
            self.assertTrue(execute_receipt.exists())
            self.assertEqual(str(result_json_path), payload["artifacts"]["benchmark_result"])
            result_payload = json.loads(result_json_path.read_text(encoding="utf-8"))
            self.assertEqual("completed", result_payload["status"])
            self.assertEqual("fake", result_payload["executor"])


if __name__ == "__main__":
    unittest.main()
