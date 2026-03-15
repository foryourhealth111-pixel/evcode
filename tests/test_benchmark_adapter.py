from __future__ import annotations

import importlib.util
import json
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
            result = adapter.perform_task(
                "Implement a benchmark-safe governed run",
                artifacts_root=Path(tempdir),
                workspace=str(repo_root),
            )
            summary_path = Path(result["summary_path"])
            self.assertTrue(summary_path.exists())
            payload = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual("benchmark_autonomous", payload["mode"])
            self.assertEqual("benchmark", payload["profile"])
            self.assertEqual("benchmark", payload["channel"])
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
