from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import types
import unittest
from dataclasses import dataclass
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


def install_terminal_bench_base_agent_stub() -> type:
    for name in [
        "terminal_bench",
        "terminal_bench.agents",
        "terminal_bench.agents.base_agent",
    ]:
        sys.modules.pop(name, None)

    terminal_bench = types.ModuleType("terminal_bench")
    agents = types.ModuleType("terminal_bench.agents")
    base_agent = types.ModuleType("terminal_bench.agents.base_agent")

    class BaseAgent:
        pass

    @dataclass
    class AgentResult:
        failure_mode: str | None = None
        metadata: dict | None = None

    base_agent.BaseAgent = BaseAgent
    base_agent.AgentResult = AgentResult
    agents.BaseAgent = BaseAgent
    agents.AgentResult = AgentResult
    terminal_bench.agents = agents

    sys.modules["terminal_bench"] = terminal_bench
    sys.modules["terminal_bench.agents"] = agents
    sys.modules["terminal_bench.agents.base_agent"] = base_agent
    return BaseAgent


class HarborAdapterSmokeTests(unittest.TestCase):
    def test_harbor_agent_exposes_base_agent_surface_and_runs_benchmark_adapter(self) -> None:
        BaseAgent = install_terminal_bench_base_agent_stub()
        load_module(
            "evcode_benchmark_adapter",
            REPO_ROOT / "packages" / "benchmark-adapter" / "python" / "evcode_benchmark_adapter.py",
        )
        harbor_module = load_module(
            "harbor_evcode_agent",
            REPO_ROOT / "packages" / "benchmark-adapter" / "python" / "harbor_evcode_agent.py",
        )
        HarborEvCodeAgent = harbor_module.HarborEvCodeAgent
        self.assertTrue(issubclass(HarborEvCodeAgent, BaseAgent))

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
        Path(argv[index + 1]).write_text("harbor smoke completed", encoding="utf-8")
        break
sys.exit(0)
""",
                encoding="utf-8",
            )
            fake_codex.chmod(0o755)

            old_host_bin = os.environ.get("EVCODE_BENCH_HOST_BIN")
            os.environ["EVCODE_BENCH_HOST_BIN"] = str(fake_codex)
            try:
                agent = HarborEvCodeAgent(REPO_ROOT)
                result = agent.perform_task(
                    task_description="Harbor smoke benchmark task",
                    logging_dir=temp_root,
                    workspace=str(workspace),
                )
            finally:
                if old_host_bin is None:
                    os.environ.pop("EVCODE_BENCH_HOST_BIN", None)
                else:
                    os.environ["EVCODE_BENCH_HOST_BIN"] = old_host_bin

            self.assertIsNone(result.failure_mode)
            metadata = result.metadata["evcode"]
            self.assertTrue(Path(metadata["summary_path"]).exists())
            result_payload = json.loads(Path(metadata["result_json_path"]).read_text(encoding="utf-8"))
            self.assertEqual("completed", result_payload["status"])
            self.assertFalse((workspace / "docs").exists())
            self.assertFalse((workspace / "outputs").exists())


if __name__ == "__main__":
    unittest.main()
