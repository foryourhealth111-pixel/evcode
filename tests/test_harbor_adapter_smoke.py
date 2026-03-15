from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_module(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class HarborAdapterSmokeTests(unittest.TestCase):
    def test_harbor_style_agent_delegates_to_benchmark_adapter(self) -> None:
        adapter_module = load_module(
            "evcode_benchmark_adapter",
            REPO_ROOT / "packages" / "benchmark-adapter" / "python" / "evcode_benchmark_adapter.py",
        )
        harbor_module = load_module(
            "harbor_evcode_agent",
            REPO_ROOT / "packages" / "benchmark-adapter" / "python" / "harbor_evcode_agent.py",
        )
        HarborEvCodeAgent = harbor_module.HarborEvCodeAgent
        self.assertIsNotNone(adapter_module.EvCodeBenchmarkAdapter)

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
Path(args.result_json).write_text(json.dumps({"status": "completed", "executor": "harbor-fake"}, indent=2), encoding="utf-8")
""",
                encoding="utf-8",
            )
            old_executor = os.environ.get("EVCODE_BENCHMARK_EXECUTOR")
            os.environ["EVCODE_BENCHMARK_EXECUTOR"] = f"python3 {executor_script} --task-file {{task_file}} --result-json {{result_json}} --workspace {{workspace}} --run-dir {{run_dir}}"
            try:
                agent = HarborEvCodeAgent(REPO_ROOT)
                result = agent.perform_task(
                    task_description="Harbor smoke benchmark task",
                    artifacts_root=temp_root,
                    workspace=str(REPO_ROOT),
                )
            finally:
                if old_executor is None:
                    os.environ.pop("EVCODE_BENCHMARK_EXECUTOR", None)
                else:
                    os.environ["EVCODE_BENCHMARK_EXECUTOR"] = old_executor

            self.assertTrue(Path(result["summary_path"]).exists())
            result_payload = json.loads(Path(result["result_json_path"]).read_text(encoding="utf-8"))
            self.assertEqual("completed", result_payload["status"])
            self.assertEqual("harbor-fake", result_payload["executor"])


if __name__ == "__main__":
    unittest.main()
