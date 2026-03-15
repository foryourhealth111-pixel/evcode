from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


class BenchmarkAdapterTests(unittest.TestCase):
    def test_adapter_creates_summary_in_benchmark_mode(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        module_path = repo_root / "packages" / "benchmark-adapter" / "python" / "evcode_benchmark_adapter.py"
        spec = importlib.util.spec_from_file_location("evcode_benchmark_adapter", module_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        EvCodeBenchmarkAdapter = module.EvCodeBenchmarkAdapter
        adapter = EvCodeBenchmarkAdapter(repo_root)
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
Path(args.result_json).write_text(json.dumps({"status": "completed", "executor": "adapter-fake"}, indent=2), encoding="utf-8")
""",
                encoding="utf-8",
            )
            old_executor = os.environ.get("EVCODE_BENCHMARK_EXECUTOR")
            os.environ["EVCODE_BENCHMARK_EXECUTOR"] = f"python3 {executor_script} --task-file {{task_file}} --result-json {{result_json}} --workspace {{workspace}} --run-dir {{run_dir}}"
            try:
                result = adapter.perform_task(
                    "Implement a benchmark-safe governed run",
                    artifacts_root=temp_root,
                    workspace=str(repo_root),
                )
            finally:
                if old_executor is None:
                    os.environ.pop("EVCODE_BENCHMARK_EXECUTOR", None)
                else:
                    os.environ["EVCODE_BENCHMARK_EXECUTOR"] = old_executor
            summary_path = Path(result["summary_path"])
            self.assertTrue(summary_path.exists())
            payload = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual("benchmark_autonomous", payload["mode"])
            self.assertEqual("benchmark", payload["profile"])
            self.assertEqual("benchmark", payload["channel"])
            self.assertTrue(Path(result["result_json_path"]).exists())
            self.assertEqual(
                [
                    "skeleton_check",
                    "deep_interview",
                    "requirement_doc",
                    "xl_plan",
                    "plan_execute",
                    "phase_cleanup",
                ],
                payload["stage_order"],
            )


if __name__ == "__main__":
    unittest.main()
