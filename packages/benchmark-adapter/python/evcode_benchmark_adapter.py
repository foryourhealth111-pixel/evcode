from __future__ import annotations

import json
import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path


FIXED_STAGE_ORDER = [
    "skeleton_check",
    "deep_interview",
    "requirement_doc",
    "xl_plan",
    "plan_execute",
    "phase_cleanup",
]


@dataclass(frozen=True)
class BenchmarkAdapterConfig:
    channel: str = "benchmark"
    profile: str = "benchmark"
    mode: str = "benchmark_autonomous"
    binary: str = "evcode-bench"


class EvCodeBenchmarkAdapter:
    def __init__(self, repo_root: Path, config: BenchmarkAdapterConfig | None = None) -> None:
        self.repo_root = Path(repo_root)
        self.config = config or BenchmarkAdapterConfig()

    def build_command(self, task_description: str) -> list[str]:
        return [
            "node",
            str(self.repo_root / "apps" / "evcode-bench" / "bin" / "evcode-bench.js"),
            "run",
            "--task",
            task_description,
        ]

    def perform_task(self, task_description: str, artifacts_root: Path, workspace: str | None = None) -> dict:
        run_id = f"bench-{uuid.uuid4().hex[:12]}"
        command = self.build_command(task_description) + [
            "--workspace",
            workspace or str(self.repo_root),
            "--artifacts-root",
            str(artifacts_root),
            "--run-id",
            run_id,
        ]
        completed = subprocess.run(
            command,
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        runtime_summary = json.loads(completed.stdout)
        session_root = Path(runtime_summary["artifacts"]["session_root"])
        summary = {
            "run_id": run_id,
            "channel": self.config.channel,
            "profile": self.config.profile,
            "mode": self.config.mode,
            "workspace": workspace or str(self.repo_root),
            "task_description": task_description,
            "stage_order": FIXED_STAGE_ORDER,
            "command": command,
            "runtime_summary_path": runtime_summary["summary_path"],
        }
        summary_path = session_root / "benchmark-adapter-summary.json"
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        return {
            "summary_path": str(summary_path),
            "summary": summary,
        }
