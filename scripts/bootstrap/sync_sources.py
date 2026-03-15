from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run(command: list[str], cwd: Path | None = None) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def clean_directory_contents(target: Path, preserved_names: set[str]) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for item in target.iterdir():
        if item.name in preserved_names:
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def sparse_clone(remote: str, commit: str, target: Path, paths: list[str]) -> None:
    clean_directory_contents(target, preserved_names={".git"})
    if not (target / ".git").exists():
        run(["git", "init"], cwd=target)
        run(["git", "remote", "add", "origin", remote], cwd=target)
    else:
        remotes = subprocess.run(["git", "remote"], cwd=target, capture_output=True, text=True, check=True).stdout.split()
        if "origin" not in remotes:
            run(["git", "remote", "add", "origin", remote], cwd=target)
        else:
            run(["git", "remote", "set-url", "origin", remote], cwd=target)

    run(["git", "config", "core.sparseCheckout", "true"], cwd=target)
    sparse_file = target / ".git" / "info" / "sparse-checkout"
    sparse_file.parent.mkdir(parents=True, exist_ok=True)
    sparse_file.write_text("\n".join(paths) + "\n", encoding="utf-8")
    run(["git", "fetch", "--depth=1", "origin", commit], cwd=target)
    run(["git", "checkout", "FETCH_HEAD"], cwd=target)
    run(["git", "checkout", "--", "."], cwd=target)
    run(["git", "sparse-checkout", "reapply"], cwd=target)


def write_materialization_receipt(target: Path, payload: dict, paths: list[str]) -> None:
    receipt = {
        "materialized_at": utc_now(),
        "source": payload["id"],
        "remote": payload["remote"],
        "branch": payload.get("branch", "main"),
        "commit": payload["commit"],
        "target_dir": str(target),
        "materialized_subdir": payload.get("materialized_subdir", ""),
        "sparse_paths": paths,
    }
    (target / "materialization.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize local source markers for the selected host and runtime.")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--write-markers", action="store_true", help="Write source markers into target directories")
    parser.add_argument("--clone-missing", action="store_true", help="Clone the host/runtime repositories when target directories are empty")
    parser.add_argument("--materialize", choices=["host", "runtime", "all"], help="Materialize pinned upstream sources using sparse checkout")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    lock_path = repo_root / "config" / "sources.lock.json"
    payload = json.loads(lock_path.read_text(encoding="utf-8"))

    if args.clone_missing:
        host_dir = repo_root / payload["host"]["vendored_dir"]
        runtime_dir = repo_root / payload["runtime"]["mirrored_dir"]
        if not any(host_dir.iterdir()) if host_dir.exists() else True:
            run(["git", "clone", "--depth=1", payload["host"]["remote"], str(host_dir)])
        if not any(runtime_dir.iterdir()) if runtime_dir.exists() else True:
            run(["git", "clone", "--depth=1", payload["runtime"]["remote"], str(runtime_dir)])

    if args.materialize:
        if args.materialize in {"host", "all"}:
            host_root = repo_root / payload["host"]["vendored_dir"]
            host_target = host_root / payload["host"].get("materialized_subdir", "upstream")
            host_paths = [
                "README.md",
                "docs",
                "scripts",
                "LICENSE",
                "Cargo.toml",
                "codex-rs",
            ]
            sparse_clone(payload["host"]["remote"], payload["host"]["commit"], host_target, host_paths)
            write_materialization_receipt(host_root, payload["host"], host_paths)

        if args.materialize in {"runtime", "all"}:
            runtime_root = repo_root / payload["runtime"]["mirrored_dir"]
            runtime_target = runtime_root / payload["runtime"].get("materialized_subdir", "upstream")
            runtime_paths = [
                "README.md",
                "README.en.md",
                "SKILL.md",
                "install.ps1",
                "install.sh",
                "check.ps1",
                "check.sh",
                "adapters",
                "agents",
                "bundled",
                "protocols",
                "config",
                "core",
                "dist",
                "hooks",
                "mcp",
                "references",
                "rules",
                "schemas",
                "scripts/common",
                "scripts/router",
                "scripts/runtime",
                "scripts/verify",
                "docs",
                "templates",
                "third_party",
                "vendor",
            ]
            sparse_clone(payload["runtime"]["remote"], payload["runtime"]["commit"], runtime_target, runtime_paths)
            write_materialization_receipt(runtime_root, payload["runtime"], runtime_paths)

    if args.write_markers:
        host_marker = repo_root / payload["host"]["vendored_dir"] / ".source.json"
        runtime_marker = repo_root / payload["runtime"]["mirrored_dir"] / ".source.json"
        host_marker.parent.mkdir(parents=True, exist_ok=True)
        runtime_marker.parent.mkdir(parents=True, exist_ok=True)
        host_marker.write_text(json.dumps(payload["host"], indent=2), encoding="utf-8")
        runtime_marker.write_text(json.dumps(payload["runtime"], indent=2), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
