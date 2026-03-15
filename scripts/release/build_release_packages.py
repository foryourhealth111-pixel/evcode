from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tarfile
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def remove_path(path: Path) -> None:
    if not path.exists() and not path.is_symlink():
        return
    if path.is_symlink() or path.is_file():
        path.unlink()
    else:
        shutil.rmtree(path)


def run(cmd: list[str], cwd: Path, capture_output: bool = True) -> subprocess.CompletedProcess[str]:
    if capture_output:
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
    return subprocess.run(cmd, cwd=cwd, text=True, check=True)


def package_dir(source_dir: Path, archive_path: Path) -> None:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(source_dir, arcname=source_dir.name)


def resolve_bundled_host_binary(repo_root: Path, artifacts_root: Path, bundled_host_binary_override: Path | None) -> tuple[Path | None, dict]:
    if bundled_host_binary_override is not None:
        source = bundled_host_binary_override.resolve()
        if not source.exists():
            raise RuntimeError(f"bundled host binary override does not exist: {source}")
        target = artifacts_root / "host" / "codex"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        target.chmod(target.stat().st_mode | 0o111)
        return target, {
            "attempted": False,
            "succeeded": True,
            "binary": str(target),
            "reason": "override",
        }

    cargo_path = shutil.which("cargo")
    bundled_host_binary = None
    host_build_status = {
        "attempted": bool(cargo_path),
        "succeeded": False,
        "binary": None,
        "reason": None,
    }
    if cargo_path:
        bundled_host_binary = artifacts_root / "host" / "codex"
        host_build = run(
            [
                "python3",
                str(repo_root / "scripts" / "build" / "build_patched_host.py"),
                "--output",
                str(bundled_host_binary),
                "--cargo-bin",
                cargo_path,
            ],
            cwd=repo_root,
            capture_output=False,
        )
        built_path = bundled_host_binary
        host_build_status["succeeded"] = built_path.exists()
        host_build_status["binary"] = str(built_path) if built_path.exists() else None
    else:
        host_build_status["reason"] = "cargo-not-found"
    return bundled_host_binary, host_build_status


def build_release(
    repo_root: Path,
    output_root: Path,
    require_patched_host: bool,
    bundled_host_binary_override: Path | None = None,
) -> dict:
    package_json = json.loads((repo_root / "package.json").read_text(encoding="utf-8"))
    version = package_json["version"]
    release_root = output_root / f"evcode-v{version}"
    dist_root = release_root / "assembled"
    artifacts_root = release_root / "artifacts"

    remove_path(release_root)
    artifacts_root.mkdir(parents=True, exist_ok=True)

    bundled_host_binary, host_build_status = resolve_bundled_host_binary(
        repo_root,
        artifacts_root,
        bundled_host_binary_override,
    )

    if require_patched_host and not host_build_status["succeeded"]:
        raise RuntimeError("patched host build was required but cargo/patched host build is unavailable")

    archives: list[dict[str, str | bool | None]] = []
    for channel, binary_name in (("standard", "evcode"), ("benchmark", "evcode-bench")):
        assemble_cmd = [
            "python3",
            str(repo_root / "scripts" / "build" / "assemble_distribution.py"),
            "--channel",
            channel,
            "--output-root",
            str(dist_root),
            "--link-mode",
            "copy",
        ]
        if bundled_host_binary and bundled_host_binary.exists():
            assemble_cmd.extend(["--bundled-host-binary", str(bundled_host_binary)])
        assemble = run(assemble_cmd, cwd=repo_root)
        manifest = json.loads(assemble.stdout)
        channel_dist_root = Path(manifest["dist_root"])
        archive_path = artifacts_root / f"evcode-{channel}-v{version}.tar.gz"
        package_dir(channel_dist_root, archive_path)
        archives.append(
            {
                "channel": channel,
                "binary": binary_name,
                "dist_root": str(channel_dist_root),
                "archive": str(archive_path),
                "bundled_host_binary": manifest.get("bundled_host_binary"),
                "self_contained": bool(manifest.get("bundled_host_binary")),
            }
        )

    release_manifest = {
        "product": "EvCode",
        "version": version,
        "built_at": utc_now(),
        "release_root": str(release_root),
        "self_contained_release": all(bool(item["self_contained"]) for item in archives),
        "host_build": host_build_status,
        "archives": archives,
    }
    manifest_path = artifacts_root / "release-manifest.json"
    manifest_path.write_text(json.dumps(release_manifest, indent=2), encoding="utf-8")
    release_manifest["manifest_path"] = str(manifest_path)
    return release_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build EvCode release packages for standard and benchmark channels.")
    parser.add_argument("--output-root", default="dist/releases", help="Release output root")
    parser.add_argument(
        "--allow-system-host",
        action="store_true",
        help="Allow development-only release packages that fall back to system codex when no bundled host is available",
    )
    parser.add_argument(
        "--bundled-host-binary",
        default="",
        help="Use an existing host binary instead of building one with cargo",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    manifest = build_release(
        repo_root,
        Path(args.output_root).resolve(),
        require_patched_host=not args.allow_system_host,
        bundled_host_binary_override=Path(args.bundled_host_binary) if args.bundled_host_binary else None,
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
