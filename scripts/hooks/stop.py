from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "packages" / "cleanup" / "scripts"))

from phase_cleanup import write_cleanup_receipt


def resolve_workspace(payload: dict) -> Path:
    env_root = (
        os.environ.get("EVCODE_ARTIFACTS_ROOT")
        or os.environ.get("EVCODE_REPO_ROOT")
        or os.environ.get("EVCODE_WORKSPACE_ROOT")
    )
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
    run_id = payload.get("session_id") or os.environ.get("EVCODE_RUN_ID", "hook-stop")
    output_path = workspace / "outputs" / "runtime" / "vibe-sessions" / run_id / "hook-stop-cleanup.json"
    write_cleanup_receipt(output_path)
    response = {
        "continue": True,
        "additionalContext": (
            f"EvCode stop hook wrote cleanup receipt at `{output_path}`. "
            "Phase cleanup is mandatory before the run is considered complete."
        ),
    }
    print(json.dumps(response))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
