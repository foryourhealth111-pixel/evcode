from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from runtime_lib import GovernedRuntimeConfig, new_run_id, write_runtime_session


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the EvCode governed runtime bridge.")
    parser.add_argument("--task", required=True, help="Task description")
    parser.add_argument("--mode", choices=["interactive_governed", "benchmark_autonomous"], required=True)
    parser.add_argument("--channel", choices=["standard", "benchmark"], required=True)
    parser.add_argument("--profile", choices=["standard", "benchmark"], required=True)
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--workspace", default="", help="Workspace path override")
    parser.add_argument("--artifacts-root", default="", help="Artifact root override")
    parser.add_argument("--run-id", default="", help="Optional run id")
    parser.add_argument("--result-json", default="", help="Optional benchmark result.json path")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    workspace = Path(args.workspace).resolve() if args.workspace else repo_root
    run_id = args.run_id or new_run_id("governed")
    if args.artifacts_root:
        artifacts_root = Path(args.artifacts_root).resolve()
    elif args.channel == "benchmark":
        artifacts_root = Path(tempfile.mkdtemp(prefix=f"evcode-bench-artifacts-{run_id}-")).resolve()
    else:
        artifacts_root = repo_root
    result_json_path = Path(args.result_json).resolve() if args.result_json else None

    summary = write_runtime_session(
        GovernedRuntimeConfig(
            mode=args.mode,
            task=args.task,
            repo_root=repo_root,
            workspace=workspace,
            artifacts_root=artifacts_root,
            run_id=run_id,
            channel=args.channel,
            profile=args.profile,
            result_json_path=result_json_path,
        )
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
