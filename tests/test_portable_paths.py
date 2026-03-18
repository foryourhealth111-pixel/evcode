from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class PortablePathTests(unittest.TestCase):
    def test_status_prefers_portable_user_config_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            xdg_root = Path(tempdir) / "xdg-config"
            portable_root = xdg_root / "evcode"
            portable_root.mkdir(parents=True, exist_ok=True)
            portable_env = portable_root / "assistant-providers.env"
            portable_env.write_text(
                "\n".join(
                    [
                        "EVCODE_RIGHTCODES_API_KEY=sk-portable-test",
                        "EVCODE_CODEX_MODEL=gpt-5.4-portable",
                        "EVCODE_CLAUDE_MODEL=claude-portable",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                ["node", str(REPO_ROOT / "apps" / "evcode" / "bin" / "evcode.js"), "status", "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
                env={
                    **os.environ,
                    "XDG_CONFIG_HOME": str(xdg_root),
                },
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(str(portable_root), payload["provider_setup"]["portable_config_root"])
            self.assertEqual(str(portable_env), payload["provider_setup"]["portable_env_path"])
            self.assertEqual("portable_user_config", payload["provider_setup"]["active_env_source"])
            self.assertEqual(str(portable_env), payload["provider_setup"]["resolved_local_env_path"])
            self.assertTrue(payload["provider_setup"]["local_env_present"])
            self.assertEqual("gpt-5.4-portable", payload["assistant_provider_resolution"]["codex"]["model"])
            self.assertEqual("claude-portable", payload["assistant_provider_resolution"]["claude"]["model"])

    def test_run_help_displays_usage_instead_of_missing_task_error(self) -> None:
        standard = subprocess.run(
            ["node", str(REPO_ROOT / "apps" / "evcode" / "bin" / "evcode.js"), "run", "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        benchmark = subprocess.run(
            ["node", str(REPO_ROOT / "apps" / "evcode-bench" / "bin" / "evcode-bench.js"), "run", "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, standard.returncode, standard.stderr or standard.stdout)
        self.assertIn("Usage: evcode run", standard.stdout)
        self.assertNotIn("Missing --task", standard.stdout + standard.stderr)
        self.assertEqual(0, benchmark.returncode, benchmark.stderr or benchmark.stdout)
        self.assertIn("Usage: evcode-bench run", benchmark.stdout)
        self.assertNotIn("Missing --task", benchmark.stdout + benchmark.stderr)


if __name__ == "__main__":
    unittest.main()
