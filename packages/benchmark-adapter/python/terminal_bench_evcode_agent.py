from __future__ import annotations

import os
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _load_symbol(module_name: str, symbol_name: str) -> Any | None:
    try:
        module = __import__(module_name, fromlist=[symbol_name])
    except ImportError:
        return None
    return getattr(module, symbol_name, None)


AbstractInstalledAgent = _load_symbol(
    "terminal_bench.agents.installed_agents.abstract_installed_agent",
    "AbstractInstalledAgent",
) or object

TerminalCommand = _load_symbol("terminal_bench.harness_models", "TerminalCommand")
if TerminalCommand is None:
    @dataclass
    class TerminalCommand:  # type: ignore[no-redef]
        command: str
        max_timeout_sec: float = 0.0
        block: bool = True


class TerminalBenchEvCodeAgent(AbstractInstalledAgent):
    """Terminal-Bench installed-agent compatible EvCode entrypoint."""

    def __init__(self, repo_root: str | Path | None = None) -> None:
        super_init = getattr(super(), "__init__", None)
        if callable(super_init):
            try:
                super_init()
            except TypeError:
                pass
        self.repo_root = Path(repo_root or Path(__file__).resolve().parents[3]).resolve()

    @staticmethod
    def name() -> str:
        return "evcode-installed"

    @property
    def _install_agent_script_path(self) -> Path:
        return Path(__file__).with_name("setup.sh")

    @property
    def _env(self) -> dict[str, str]:
        passthrough = {
            key: value
            for key, value in os.environ.items()
            if key.startswith("OPENAI_")
            or key.startswith("EVCODE_")
            or key.endswith("_API_KEY")
            or key.endswith("_BASE_URL")
        }
        passthrough.setdefault("EVCODE_BENCHMARK_FAST_PATH", "1")
        passthrough.setdefault("EVCODE_REPO_ROOT", str(self.repo_root))
        return passthrough

    def _run_agent_commands(self, task_description: str) -> list[TerminalCommand]:
        escaped_task = shlex.quote(task_description)
        command = (
            "mkdir -p \"${EVCODE_INSTALLED_AGENT_ARTIFACTS_ROOT:-/tmp/evcode-bench-artifacts}\" && "
            f"evcode-bench run --task {escaped_task} "
            "--workspace \"$PWD\" "
            "--artifacts-root \"${EVCODE_INSTALLED_AGENT_ARTIFACTS_ROOT:-/tmp/evcode-bench-artifacts}\""
        )
        return [
            TerminalCommand(
                command=command,
                max_timeout_sec=float("inf"),
                block=True,
            )
        ]


EvCodeInstalledAgent = TerminalBenchEvCodeAgent
