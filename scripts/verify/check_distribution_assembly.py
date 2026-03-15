from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path


def verify_channel(repo_root: Path, channel: str) -> None:
    with tempfile.TemporaryDirectory() as tempdir:
        completed = subprocess.run(
            [
                "python3",
                str(repo_root / "scripts" / "build" / "assemble_distribution.py"),
                "--channel",
                channel,
                "--output-root",
                tempdir,
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
        manifest = json.loads(completed.stdout)
        dist_root = Path(manifest["dist_root"])
        skills_root = Path(manifest["skills_root"])
        launcher = Path(manifest["launcher"])
        config_toml = Path(manifest["codex_home"]) / "config.toml"
        patch_file = Path(manifest["patch_file"])

        assert dist_root.exists(), dist_root
        assert launcher.exists(), launcher
        assert config_toml.exists(), config_toml
        assert patch_file.exists(), patch_file
        assert (skills_root / "vibe" / "SKILL.md").exists(), skills_root / "vibe" / "SKILL.md"
        config_text = config_toml.read_text(encoding="utf-8")
        assert "[[hooks.user_prompt_submit]]" in config_text
        assert "user_prompt_submit.py" in config_text
        assert "subagent_start.py" in config_text


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    verify_channel(repo_root, "standard")
    verify_channel(repo_root, "benchmark")
    print("distribution assembly checks: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
