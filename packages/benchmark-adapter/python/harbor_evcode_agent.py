from __future__ import annotations

import inspect
import tempfile
from pathlib import Path
from typing import Any

from evcode_benchmark_adapter import EvCodeBenchmarkAdapter


def _load_symbol(module_name: str, symbol_name: str) -> Any | None:
    try:
        module = __import__(module_name, fromlist=[symbol_name])
    except ImportError:
        return None
    return getattr(module, symbol_name, None)


BaseAgent = (
    _load_symbol("harbor.agents.base", "BaseAgent")
    or _load_symbol("terminal_bench.agents.base_agent", "BaseAgent")
    or _load_symbol("terminal_bench.agents", "BaseAgent")
    or object
)
AgentResult = (
    _load_symbol("harbor.agents.base", "AgentResult")
    or _load_symbol("terminal_bench.agents.base_agent", "AgentResult")
    or _load_symbol("terminal_bench.agents", "AgentResult")
)


def _workspace_from_session(session: Any | None, fallback: Path) -> Path:
    if session is None:
        return fallback
    for attr in ("cwd", "working_dir", "workspace", "repo_root"):
        value = getattr(session, attr, None)
        if value:
            return Path(value).resolve()
    return fallback


def _artifacts_root_from_inputs(
    *,
    artifacts_root: str | Path | None,
    logging_dir: str | Path | None,
    workspace: Path,
) -> Path:
    if artifacts_root:
        return Path(artifacts_root).resolve()
    if logging_dir:
        return Path(logging_dir).resolve()
    return Path(tempfile.mkdtemp(prefix="evcode-harbor-artifacts-")).resolve()


def _build_agent_result(payload: dict[str, Any]) -> Any:
    if AgentResult is None:
        return payload

    signature = inspect.signature(AgentResult)
    summary = payload.get("summary", {})
    status = summary.get("status", "runtime_error")
    failure_mode = summary.get("failure_type") or (None if status == "completed" else status)
    metadata = {
        "evcode": {
            "summary_path": payload.get("summary_path"),
            "result_json_path": payload.get("result_json_path"),
            "summary": payload.get("summary"),
        }
    }
    kwargs: dict[str, Any] = {}
    for name in signature.parameters:
        if name == "failure_mode":
            kwargs[name] = failure_mode
        elif name in {"prompt_tokens", "completion_tokens", "total_tokens"}:
            kwargs[name] = 0
        elif name in {"metadata", "extra", "info"}:
            kwargs[name] = metadata
        elif name == "trajectory_path":
            kwargs[name] = payload.get("summary_path")
        elif name == "success":
            kwargs[name] = failure_mode is None

    try:
        return AgentResult(**kwargs)
    except TypeError:
        return payload


class HarborEvCodeAgent(BaseAgent):
    """Harbor/Terminal-Bench BaseAgent-compatible EvCode benchmark adapter."""

    def __init__(self, repo_root: str | Path | None = None) -> None:
        super_init = getattr(super(), "__init__", None)
        if callable(super_init):
            try:
                super_init()
            except TypeError:
                pass
        self.repo_root = Path(repo_root or Path(__file__).resolve().parents[3]).resolve()
        self.adapter = EvCodeBenchmarkAdapter(self.repo_root)

    @staticmethod
    def name() -> str:
        return "evcode-harbor"

    def perform_task(
        self,
        task_description: str,
        session: Any | None = None,
        logging_dir: str | Path | None = None,
        artifacts_root: str | Path | None = None,
        workspace: str | None = None,
        **_: Any,
    ) -> Any:
        workspace_path = Path(workspace).resolve() if workspace else _workspace_from_session(session, self.repo_root)
        artifacts_path = _artifacts_root_from_inputs(
            artifacts_root=artifacts_root,
            logging_dir=logging_dir,
            workspace=workspace_path,
        )
        payload = self.adapter.perform_task(
            task_description=task_description,
            artifacts_root=artifacts_path,
            workspace=str(workspace_path),
        )
        return _build_agent_result(payload)


EvCodeHarborAgent = HarborEvCodeAgent
