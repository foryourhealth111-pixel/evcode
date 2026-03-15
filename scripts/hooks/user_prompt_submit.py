from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))

from runtime_lib import build_context_advice, render_context_block


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
    task = payload.get("input") or payload.get("prompt") or os.environ.get("EVCODE_TASK", "")
    mode = os.environ.get("EVCODE_MODE", "interactive_governed")
    workspace = resolve_workspace(payload)
    advice = build_context_advice(task, mode, workspace)
    response = {
        "continue": True,
        "systemMessage": (
            "EvCode governed runtime is active. Preserve requirement freezing, plan traceability, "
            "verification evidence, and phase cleanup."
        ),
        "additionalContext": render_context_block(advice),
    }
    print(json.dumps(response))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
