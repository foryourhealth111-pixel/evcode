from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BENCHMARK_PREFACE = """You are running inside a non-interactive benchmark environment.
No user will answer follow-up questions.
Do not pause for confirmation.
If the task is ambiguous, record your assumptions and continue.
Prefer local files, command outputs, and tests to resolve uncertainty.
Do not write governance artifacts, receipts, docs/requirements, docs/plans, or outputs/runtime into the task workspace.
Only modify files required by the task itself.
If you need scratch files, logs, notes, or receipts, keep them outside the task workspace.
If you spawn subagents, every child-task prompt must end with ` $vibe`, but keep execution in benchmark fast-path mode.
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
    artifacts_root: Path
    result_json_path: Path | None = None


@dataclass(frozen=True)
class BenchmarkProviderSettings:
    model_provider: str
    model: str
    reasoning_effort: str
    provider_block: str | None
    source_codex_home: Path
    auth_strategy: str | None = None


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_prompt(task: str, artifacts_root: Path) -> str:
    return (
        f"{BENCHMARK_PREFACE}\n"
        f"External artifacts root: {artifacts_root}\n\n"
        f"Task:\n{task}\n\n"
        "Complete the task end-to-end without asking the user for clarification."
    )


def path_is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def ensure_external_artifact_path(path: Path, workspace: Path, *, suffix: str, run_id: str) -> Path:
    if path_is_within(path, workspace):
        redirected_root = Path(tempfile.mkdtemp(prefix=f"evcode-bench-{run_id}-"))
        return redirected_root / suffix
    return path


def resolve_source_codex_home() -> Path:
    configured = os.environ.get("EVCODE_BENCH_SOURCE_CODEX_HOME") or os.environ.get("CODEX_HOME")
    if configured:
        return Path(configured).expanduser().resolve()
    return (Path.home() / ".codex").resolve()


def load_provider_policy(repo_root: Path) -> dict[str, Any]:
    policy_path = repo_root / "config" / "provider-policy.benchmark.json"
    if not policy_path.exists():
        return {}
    return json.loads(policy_path.read_text(encoding="utf-8"))


def read_text_if_exists(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def extract_toml_string(text: str, key: str) -> str | None:
    match = re.search(rf'(?m)^{re.escape(key)}\s*=\s*"([^"]+)"\s*$', text)
    return match.group(1) if match else None


def extract_provider_block(text: str, provider_name: str) -> str | None:
    lines = text.splitlines()
    target_header = f"[model_providers.{provider_name}]"
    start = None
    for index, line in enumerate(lines):
        if line.strip() == target_header:
            start = index
            break
    if start is None:
        return None

    block_lines: list[str] = []
    for line in lines[start:]:
        if block_lines and line.startswith("[") and line.endswith("]"):
            break
        block_lines.append(line)
    return "\n".join(block_lines).strip() if block_lines else None


def resolve_benchmark_provider_settings(config: BenchmarkExecutionConfig) -> BenchmarkProviderSettings:
    policy = load_provider_policy(config.repo_root)
    source_codex_home = resolve_source_codex_home()
    source_config_text = read_text_if_exists(source_codex_home / "config.toml")

    model_provider = (
        os.environ.get("EVCODE_BENCHMARK_MODEL_PROVIDER")
        or policy.get("preferred_model_provider")
        or extract_toml_string(source_config_text, "model_provider")
        or "openai"
    )
    model = (
        os.environ.get("EVCODE_BENCHMARK_MODEL")
        or policy.get("preferred_model")
        or extract_toml_string(source_config_text, "model")
        or "gpt-5"
    )
    reasoning_effort = (
        os.environ.get("EVCODE_BENCHMARK_REASONING_EFFORT")
        or policy.get("preferred_reasoning_effort")
        or extract_toml_string(source_config_text, "model_reasoning_effort")
        or "high"
    )
    provider_block = extract_provider_block(source_config_text, model_provider)
    auth_strategy = str(policy.get("auth_strategy")) if policy.get("auth_strategy") else None
    return BenchmarkProviderSettings(
        model_provider=model_provider,
        model=model,
        reasoning_effort=reasoning_effort,
        provider_block=provider_block,
        source_codex_home=source_codex_home,
        auth_strategy=auth_strategy,
    )


def build_benchmark_codex_config(workspace: Path, settings: BenchmarkProviderSettings) -> str:
    workspace_posix = workspace.resolve().as_posix()
    lines = [
        f'model_provider = "{settings.model_provider}"',
        f'model = "{settings.model}"',
        f'model_reasoning_effort = "{settings.reasoning_effort}"',
        'profile = "benchmark"',
        "disable_cron = true",
        "",
        "[profiles.benchmark]",
        "disable_cron = true",
        f'model_provider = "{settings.model_provider}"',
        f'model = "{settings.model}"',
        f'model_reasoning_effort = "{settings.reasoning_effort}"',
        "",
    ]
    if settings.provider_block:
        lines.extend([settings.provider_block, ""])
    lines.extend(
        [
            f'[projects."{workspace_posix}"]',
            'trust_level = "trusted"',
            "",
            "[mcp_servers]",
            "",
        ]
    )
    return "\n".join(lines)


def copy_auth_material(settings: BenchmarkProviderSettings, destination_codex_home: Path) -> None:
    auth_path = settings.source_codex_home / "auth.json"
    if auth_path.exists():
        shutil.copy2(auth_path, destination_codex_home / "auth.json")


def materialize_benchmark_codex_home(config: BenchmarkExecutionConfig, settings: BenchmarkProviderSettings) -> Path:
    codex_home = config.session_root / "codex-home"
    codex_home.mkdir(parents=True, exist_ok=True)
    (codex_home / "config.toml").write_text(
        build_benchmark_codex_config(config.workspace, settings),
        encoding="utf-8",
    )
    copy_auth_material(settings, codex_home)
    return codex_home


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


def build_command(
    config: BenchmarkExecutionConfig,
    prompt_file: Path,
    result_json_path: Path,
    assistant_output_path: Path,
    settings: BenchmarkProviderSettings,
) -> list[str]:
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
    return [
        host_bin,
        "exec",
        "--skip-git-repo-check",
        "--cd",
        str(config.workspace),
        "--color",
        "never",
        "--sandbox",
        "workspace-write",
        "--full-auto",
        "--model",
        settings.model,
        "--profile",
        "benchmark",
        "--ephemeral",
        "--output-last-message",
        str(assistant_output_path),
        "-c",
        f'model_provider="{settings.model_provider}"',
        "-c",
        f'model_reasoning_effort="{settings.reasoning_effort}"',
        "-c",
        "mcp_servers={}",
        prompt_file.read_text(encoding="utf-8"),
    ]


def execute_benchmark_task(config: BenchmarkExecutionConfig) -> dict[str, Any]:
    run_dir = config.session_root
    run_dir.mkdir(parents=True, exist_ok=True)
    prompt_file = run_dir / "benchmark-prompt.txt"
    stdout_path = run_dir / "benchmark.stdout.txt"
    stderr_path = run_dir / "benchmark.stderr.txt"
    assistant_output_path = run_dir / "assistant-last-message.txt"
    result_json_path = ensure_external_artifact_path(
        config.result_json_path or (config.artifacts_root / config.run_id / "result.json"),
        config.workspace,
        suffix="result.json",
        run_id=config.run_id,
    )
    prompt_file.write_text(build_prompt(config.task, config.artifacts_root), encoding="utf-8")
    result_json_path.parent.mkdir(parents=True, exist_ok=True)
    provider_settings = resolve_benchmark_provider_settings(config)
    codex_home = materialize_benchmark_codex_home(config, provider_settings)

    timeout_sec = int(os.environ.get("EVCODE_BENCHMARK_EXEC_TIMEOUT_SEC", "1800"))
    command: list[str] | None = None
    failure_type: str | None = None
    exit_code: int | None = None

    try:
        command = build_command(config, prompt_file, result_json_path, assistant_output_path, provider_settings)
        exec_env = {
            **os.environ,
            "CODEX_HOME": str(codex_home),
            "EVCODE_BENCHMARK_FAST_PATH": "1",
            "EVCODE_BENCHMARK_ARTIFACTS_ROOT": str(config.artifacts_root),
            "EVCODE_WORKSPACE_ROOT": str(config.workspace),
        }
        with stdout_path.open("w", encoding="utf-8") as stdout_handle, stderr_path.open("w", encoding="utf-8") as stderr_handle:
            completed = subprocess.run(
                command,
                cwd=config.workspace,
                stdout=stdout_handle,
                stderr=stderr_handle,
                text=True,
                check=False,
                timeout=timeout_sec,
                env=exec_env,
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
        "assistant_output_path": str(assistant_output_path),
        "codex_home": str(codex_home),
        "model_provider": provider_settings.model_provider,
        "model": provider_settings.model,
        "reasoning_effort": provider_settings.reasoning_effort,
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
        "assistant_output_path": str(assistant_output_path),
        "codex_home": str(codex_home),
        "model_provider": provider_settings.model_provider,
        "model": provider_settings.model,
        "reasoning_effort": provider_settings.reasoning_effort,
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
    parser.add_argument("--artifacts-root", required=True)
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
            artifacts_root=Path(args.artifacts_root).resolve(),
            result_json_path=Path(args.result_json).resolve() if args.result_json else None,
        )
    )
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
