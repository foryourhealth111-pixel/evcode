from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))

from runtime_lib import write_json


def resolve_workspace(payload: dict) -> Path:
    env_root = os.environ.get("EVCODE_ARTIFACTS_ROOT") or os.environ.get("EVCODE_WORKSPACE_ROOT")
    if env_root:
        return Path(env_root).resolve()
    payload_cwd = payload.get("cwd")
    if isinstance(payload_cwd, str):
        candidate = Path(payload_cwd)
        if candidate.exists():
            return candidate.resolve()
    return Path(__file__).resolve().parents[2]


def main() -> int:
    payload = json.load(sys.stdin) if not sys.stdin.isatty() else {}
    workspace = resolve_workspace(payload)
    run_id = payload.get("session_id") or os.environ.get("EVCODE_RUN_ID", "task-completed")
    receipt_path = workspace / "outputs" / "runtime" / "vibe-sessions" / run_id / "task-completed-hook.json"
    write_json(
        receipt_path,
        {
            "event": "task_completed",
            "mode": os.environ.get("EVCODE_MODE", "interactive_governed"),
            "task_id": payload.get("task_id"),
            "task_subject": payload.get("task_subject"),
            "teammate_name": payload.get("teammate_name"),
            "team_name": payload.get("team_name"),
            "payload_keys": sorted(payload.keys()),
        },
    )
    response = {
        "continue": True,
        "additionalContext": (
            f"EvCode task_completed hook wrote receipt at `{receipt_path}`. "
            "Keep execution lineage and verification receipts aligned with the frozen requirement and plan."
        ),
    }
    print(json.dumps(response))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
