from __future__ import annotations

import argparse
import shutil
import stat
import subprocess
from pathlib import Path


def remove_path(path: Path) -> None:
    if not path.exists() and not path.is_symlink():
        return
    if path.is_symlink() or path.is_file():
        path.unlink()
    else:
        shutil.rmtree(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a patched EvCode host binary from the vendored Codex upstream.")
    parser.add_argument("--output", required=True, help="Output path for the patched codex binary")
    parser.add_argument(
        "--workdir",
        default=".evcode-build/patched-host",
        help="Temporary workspace used to materialize, patch, and build the host",
    )
    parser.add_argument(
        "--host-source",
        default="vendor/codex-host/upstream",
        help="Vendored host source root",
    )
    parser.add_argument(
        "--patch-file",
        default="vendor/codex-host/patches/subagent-vibe-suffix.patch",
        help="Patch file that enforces hard vibe equivalence",
    )
    parser.add_argument("--cargo-bin", default="cargo", help="Cargo executable")
    parser.add_argument("--package", default="codex-cli", help="Cargo package to build")
    parser.add_argument("--binary-name", default="codex", help="Compiled host binary name")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    host_source = (repo_root / args.host_source).resolve()
    patch_file = (repo_root / args.patch_file).resolve()
    workdir = Path(args.workdir).resolve()
    output = Path(args.output).resolve()

    remove_path(workdir)
    workdir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(host_source, workdir)
    subprocess.run(["git", "apply", str(patch_file)], cwd=workdir, check=True)

    cargo_root = workdir / "codex-rs"
    subprocess.run(
        [args.cargo_bin, "build", "-p", args.package, "--release"],
        cwd=cargo_root,
        check=True,
    )

    built_binary = cargo_root / "target" / "release" / args.binary_name
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(built_binary, output)
    output.chmod(output.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(str(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
