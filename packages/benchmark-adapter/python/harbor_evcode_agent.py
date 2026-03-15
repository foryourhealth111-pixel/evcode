from __future__ import annotations

from pathlib import Path
from typing import Any

from evcode_benchmark_adapter import EvCodeBenchmarkAdapter


class HarborEvCodeAgent:
    """Thin Harbor-facing adapter over the shared EvCode benchmark runtime."""

    def __init__(self, repo_root: str | Path | None = None) -> None:
        self.repo_root = Path(repo_root or Path(__file__).resolve().parents[3]).resolve()
        self.adapter = EvCodeBenchmarkAdapter(self.repo_root)

    def perform_task(self, task_description: str, artifacts_root: str | Path, workspace: str | None = None, **_: Any) -> dict[str, Any]:
        return self.adapter.perform_task(
            task_description=task_description,
            artifacts_root=Path(artifacts_root).resolve(),
            workspace=workspace,
        )
