from __future__ import annotations

import importlib.util
import sys
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


def install_terminal_bench_installed_agent_stub() -> tuple[type, type]:
    for name in [
        "terminal_bench",
        "terminal_bench.agents",
        "terminal_bench.agents.installed_agents",
        "terminal_bench.agents.installed_agents.abstract_installed_agent",
        "terminal_bench.harness_models",
    ]:
        sys.modules.pop(name, None)

    terminal_bench = types.ModuleType("terminal_bench")
    agents = types.ModuleType("terminal_bench.agents")
    installed_agents = types.ModuleType("terminal_bench.agents.installed_agents")
    abstract_module = types.ModuleType("terminal_bench.agents.installed_agents.abstract_installed_agent")
    harness_models = types.ModuleType("terminal_bench.harness_models")

    class AbstractInstalledAgent:
        pass

    @dataclass
    class TerminalCommand:
        command: str
        max_timeout_sec: float
        block: bool

    abstract_module.AbstractInstalledAgent = AbstractInstalledAgent
    harness_models.TerminalCommand = TerminalCommand
    installed_agents.abstract_installed_agent = abstract_module
    agents.installed_agents = installed_agents
    terminal_bench.agents = agents

    sys.modules["terminal_bench"] = terminal_bench
    sys.modules["terminal_bench.agents"] = agents
    sys.modules["terminal_bench.agents.installed_agents"] = installed_agents
    sys.modules["terminal_bench.agents.installed_agents.abstract_installed_agent"] = abstract_module
    sys.modules["terminal_bench.harness_models"] = harness_models
    return AbstractInstalledAgent, TerminalCommand


class TerminalBenchAdapterSmokeTests(unittest.TestCase):
    def test_terminal_bench_agent_exposes_installed_agent_surface(self) -> None:
        AbstractInstalledAgent, TerminalCommand = install_terminal_bench_installed_agent_stub()
        module = load_module(
            "terminal_bench_evcode_agent",
            REPO_ROOT / "packages" / "benchmark-adapter" / "python" / "terminal_bench_evcode_agent.py",
        )
        TerminalBenchEvCodeAgent = module.TerminalBenchEvCodeAgent
        self.assertTrue(issubclass(TerminalBenchEvCodeAgent, AbstractInstalledAgent))

        agent = TerminalBenchEvCodeAgent(REPO_ROOT)
        self.assertTrue(agent._install_agent_script_path.exists())
        self.assertEqual("evcode-installed", agent.name())

        commands = agent._run_agent_commands("Solve task without follow-up questions")
        self.assertEqual(1, len(commands))
        self.assertIsInstance(commands[0], TerminalCommand)
        self.assertIn("evcode-bench run --task", commands[0].command)
        self.assertIn("--workspace \"$PWD\"", commands[0].command)
        self.assertIn("EVCODE_INSTALLED_AGENT_ARTIFACTS_ROOT", commands[0].command)
        self.assertEqual(float("inf"), commands[0].max_timeout_sec)
        self.assertTrue(commands[0].block)


if __name__ == "__main__":
    unittest.main()
