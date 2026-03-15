from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_PREFACE = """You are running inside a non-interactive benchmark environment.
No user will answer follow-up questions.
Do not pause for confirmation.
If the task is ambiguous, record your assumptions and continue.
Prefer local files, command outputs, and tests to resolve uncertainty.
If you spawn subagents, every child-task prompt must end with ` $vibe`.
"""


@dataclass(frozen=True)
class BenchmarkExecutionConfig:
    task: str
    workspace: Path
    repo_root: Path
    session_root: Path
    run_id: str
    channel: str
    profile: str
    mode: str
    result_json_path: Path | None = None


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_prompt(task: str) -> str:
    return f"{BENCHMARK_PREFACE}\nTask:\n{task}\n\nComplete the task end-to-end without asking the user for clarification. $vibe"


def resolve_host_binary(repo_root: Path, channel: str) -> str | None:
    env_host = os.environ.get("EVCODE_BENCH_HOST_BIN")
    candidates = [
        env_host,
        repo_root / ".evcode-dist" / channel / "host" / "bin" / "codex",
        repo_root / ".evcode-dist" / "standard" / "host" / "bin" / "codex",
        shutil.which("codex"),
    ]
    for candidate in candidates:
        if not candidate:
            continue
        candidate_path = Path(candidate) if not isinstance(candidate, Path) else candidate
        if isinstance(candidate, str) and "/" not in candidate:
            resolved = shutil.which(candidate)
            if resolved:
                return resolved
            continue
        if candidate_path.exists() and os.access(candidate_path, os.X_OK):
            return str(candidate_path)
    return None


def render_executor_command(template: str, *, prompt_file: Path, workspace: Path, result_json: Path, run_dir: Path, host_bin: str | None) -> list[str]:
    rendered = template.format(
        prompt_file=str(prompt_file),
        task_file=str(prompt_file),
        workspace=str(workspace),
        result_json=str(result_json),
        run_dir=str(run_dir),
        host_bin=host_bin or "",
    )
    return shlex.split(rendered)


def build_command(config: BenchmarkExecutionConfig, prompt_file: Path, result_json_path: Path) -> list[str]:
    template = os.environ.get("EVCODE_BENCHMARK_EXECUTOR")
    host_bin = resolve_host_binary(config.repo_root, config.channel)
    if template:
        return render_executor_command(
            template,
            prompt_file=prompt_file,
            workspace=config.workspace,
            result_json=result_json_path,
            run_dir=config.session_root,
            host_bin=host_bin,
        )
    if not host_bin:
        raise RuntimeError("No benchmark executor configured and no codex-compatible host binary was found.")
    return [host_bin, "exec", "--cd", str(config.workspace), prompt_file.read_text(encoding="utf-8")]


def execute_benchmark_task(config: BenchmarkExecutionConfig) -> dict[str, Any]:
    run_dir = config.session_root
    run_dir.mkdir(parents=True, exist_ok=True)
    prompt_file = run_dir / "benchmark-prompt.txt"
    stdout_path = run_dir / "benchmark.stdout.txt"
    stderr_path = run_dir / "benchmark.stderr.txt"
    result_json_path = config.result_json_path or (run_dir / "result.json")
    prompt_file.write_text(build_prompt(config.task), encoding="utf-8")
    result_json_path.parent.mkdir(parents=True, exist_ok=True)

    timeout_sec = int(os.environ.get("EVCODE_BENCHMARK_EXEC_TIMEOUT_SEC", "1800"))
    command: list[str] | None = None
    failure_type: str | None = None
    exit_code: int | None = None

    try:
        command = build_command(config, prompt_file, result_json_path)
        with stdout_path.open("w", encoding="utf-8") as stdout_handle, stderr_path.open("w", encoding="utf-8") as stderr_handle:
            completed = subprocess.run(
                command,
                cwd=config.workspace,
                stdout=stdout_handle,
                stderr=stderr_handle,
                text=True,
                check=False,
                timeout=timeout_sec,
            )
        exit_code = completed.returncode
        status = "completed" if completed.returncode == 0 else "executor_failed"
    except subprocess.TimeoutExpired:
        failure_type = "timeout"
        status = "timeout"
    except Exception as exc:  # pragma: no cover - defensive path
        failure_type = exc.__class__.__name__
        status = "runtime_error"
        stderr_path.write_text(f"{failure_type}: {exc}\n", encoding="utf-8")

    if result_json_path.exists():
        try:
            existing_payload = json.loads(result_json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing_payload = {"raw_result_path": str(result_json_path)}
    else:
        existing_payload = {}

    result_payload = {
        **existing_payload,
        "run_id": config.run_id,
        "channel": config.channel,
        "profile": config.profile,
        "mode": config.mode,
        "task": config.task,
        "workspace": str(config.workspace),
        "status": existing_payload.get("status", status),
        "exit_code": existing_payload.get("exit_code", exit_code),
        "failure_type": existing_payload.get("failure_type", failure_type),
        "command": existing_payload.get("command", command),
        "prompt_file": str(prompt_file),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "generated_at": utc_now(),
    }
    result_json_path.write_text(json.dumps(result_payload, indent=2), encoding="utf-8")

    receipt_path = run_dir / "phase-execute.json"
    receipt = {
        "run_id": config.run_id,
        "channel": config.channel,
        "profile": config.profile,
        "mode": config.mode,
        "status": result_payload["status"],
        "exit_code": result_payload["exit_code"],
        "failure_type": result_payload["failure_type"],
        "command": result_payload["command"],
        "prompt_file": str(prompt_file),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "result_json_path": str(result_json_path),
        "generated_at": utc_now(),
    }
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return {
        "execute_receipt_path": str(receipt_path),
        "result_json_path": str(result_json_path),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "status": result_payload["status"],
        "exit_code": result_payload["exit_code"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute a benchmark task through the EvCode benchmark bridge.")
    parser.add_argument("--task", required=True)
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--session-root", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--channel", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--mode", required=True)
    parser.add_argument("--result-json", default="")
    args = parser.parse_args()

    payload = execute_benchmark_task(
        BenchmarkExecutionConfig(
            task=args.task,
            workspace=Path(args.workspace).resolve(),
            repo_root=Path(args.repo_root).resolve(),
            session_root=Path(args.session_root).resolve(),
            run_id=args.run_id,
            channel=args.channel,
            profile=args.profile,
            mode=args.mode,
            result_json_path=Path(args.result_json).resolve() if args.result_json else None,
        )
    )
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
