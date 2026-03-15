from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class BenchmarkExecutionBridgeTests(unittest.TestCase):
    def test_benchmark_run_uses_default_host_flags_and_keeps_workspace_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp_root = Path(tempdir)
            workspace = temp_root / "workspace"
            workspace.mkdir()
            artifacts_root = temp_root / "artifacts"
            source_codex_home = temp_root / "source-codex-home"
            source_codex_home.mkdir()
            submission_preset = temp_root / "submission-preset.json"
            submission_preset.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "name": "test-rightcode-preset",
                        "model_provider": "rightcode",
                        "model": "gpt-5.4",
                        "reasoning_effort": "xhigh",
                        "auth_strategy": "copy-openai-auth",
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            (source_codex_home / "config.toml").write_text(
                """
model_provider = "rightcode"
model = "gpt-5.4"
model_reasoning_effort = "high"

[model_providers.rightcode]
name = "rightcode"
base_url = "https://right.codes/codex/v1"
wire_api = "responses"
requires_openai_auth = true
""".strip()
                + "\n",
                encoding="utf-8",
            )
            (source_codex_home / "auth.json").write_text(
                json.dumps({"OPENAI_API_KEY": "sk-test-benchmark"}, indent=2),
                encoding="utf-8",
            )
            args_log = temp_root / "fake_codex_args.json"
            fake_codex = temp_root / "fake_codex"
            fake_codex.write_text(
                """#!/usr/bin/env python3
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

argv = sys.argv[1:]
output_path = None
for index, token in enumerate(argv):
    if token == "--output-last-message":
        output_path = argv[index + 1]
        break

payload = {
    "argv": argv,
    "cwd": os.getcwd(),
    "codex_home": os.environ.get("CODEX_HOME"),
    "workspace_root": os.environ.get("EVCODE_WORKSPACE_ROOT"),
    "artifacts_root": os.environ.get("EVCODE_BENCHMARK_ARTIFACTS_ROOT"),
}
Path(os.environ["FAKE_CODEX_ARGS_LOG"]).write_text(json.dumps(payload, indent=2), encoding="utf-8")
if output_path:
    Path(output_path).write_text("benchmark completed", encoding="utf-8")
sys.exit(0)
""",
                encoding="utf-8",
            )
            fake_codex.chmod(0o755)

            env = {
                **os.environ,
                "EVCODE_BENCH_HOST_BIN": str(fake_codex),
                "EVCODE_BENCH_SOURCE_CODEX_HOME": str(source_codex_home),
                "EVCODE_SUBMISSION_PRESET": str(submission_preset),
                "FAKE_CODEX_ARGS_LOG": str(args_log),
            }
            completed = subprocess.run(
                [
                    "node",
                    str(REPO_ROOT / "apps" / "evcode-bench" / "bin" / "evcode-bench.js"),
                    "run",
                    "--task",
                    "Implement benchmark bridge smoke execution",
                    "--workspace",
                    str(workspace),
                    "--artifacts-root",
                    str(artifacts_root),
                    "--run-id",
                    "benchmark-bridge-smoke",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
                env=env,
            )

            payload = json.loads(completed.stdout)
            summary_artifacts = payload["artifacts"]
            self.assertEqual(str(artifacts_root.resolve()), summary_artifacts["effective_artifacts_root"])
            self.assertFalse(summary_artifacts["artifacts_redirected"])
            self.assertFalse((workspace / "docs").exists())
            self.assertFalse((workspace / "outputs").exists())

            result_json_path = Path(summary_artifacts["benchmark_result"])
            self.assertTrue(result_json_path.exists())
            result_payload = json.loads(result_json_path.read_text(encoding="utf-8"))
            self.assertEqual("completed", result_payload["status"])
            self.assertTrue(Path(result_payload["codex_home"]).exists())
            self.assertEqual("test-rightcode-preset", result_payload["submission_preset_name"])
            self.assertEqual(str(submission_preset.resolve()), result_payload["submission_preset_path"])
            self.assertEqual("submission_preset", result_payload["execution_target_source"])
            config_toml = Path(result_payload["codex_home"]) / "config.toml"
            config_text = config_toml.read_text(encoding="utf-8")
            self.assertIn("[mcp_servers]", config_text)
            self.assertIn('model_provider = "rightcode"', config_text)
            self.assertIn('model = "gpt-5.4"', config_text)
            self.assertIn('model_reasoning_effort = "xhigh"', config_text)
            self.assertIn("[model_providers.rightcode]", config_text)
            auth_json = Path(result_payload["codex_home"]) / "auth.json"
            self.assertTrue(auth_json.exists())
            self.assertEqual(
                {"OPENAI_API_KEY": "sk-test-benchmark"},
                json.loads(auth_json.read_text(encoding="utf-8")),
            )
            args_payload = json.loads(args_log.read_text(encoding="utf-8"))
            self.assertEqual(str(workspace.resolve()), args_payload["cwd"])
            self.assertEqual(str(workspace.resolve()), args_payload["workspace_root"])
            self.assertEqual(str(artifacts_root.resolve()), args_payload["artifacts_root"])

            command = result_payload["command"]
            self.assertIn("--skip-git-repo-check", command)
            self.assertIn("--model", command)
            self.assertIn("gpt-5.4", command)
            self.assertIn("--profile", command)
            self.assertIn("benchmark", command)
            self.assertIn("--ephemeral", command)
            self.assertIn("--output-last-message", command)
            self.assertIn("mcp_servers={}", command)
            self.assertIn('model_provider="rightcode"', command)
            self.assertIn('model_reasoning_effort="xhigh"', command)

    def test_benchmark_run_redirects_artifacts_root_when_it_points_inside_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp_root = Path(tempdir)
            workspace = temp_root / "workspace"
            workspace.mkdir()
            leaky_artifacts_root = workspace / "should-not-be-used"
            fake_codex = temp_root / "fake_codex"
            fake_codex.write_text(
                """#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path

argv = sys.argv[1:]
for index, token in enumerate(argv):
    if token == "--output-last-message":
        Path(argv[index + 1]).write_text("redirected", encoding="utf-8")
        break
sys.exit(0)
""",
                encoding="utf-8",
            )
            fake_codex.chmod(0o755)
            env = {
                **os.environ,
                "EVCODE_BENCH_HOST_BIN": str(fake_codex),
            }
            completed = subprocess.run(
                [
                    "node",
                    str(REPO_ROOT / "apps" / "evcode-bench" / "bin" / "evcode-bench.js"),
                    "run",
                    "--task",
                    "Redirect benchmark artifacts outside the task workspace",
                    "--workspace",
                    str(workspace),
                    "--artifacts-root",
                    str(leaky_artifacts_root),
                    "--run-id",
                    "benchmark-bridge-redirect",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
                env=env,
            )

            payload = json.loads(completed.stdout)
            effective_root = Path(payload["artifacts"]["effective_artifacts_root"])
            self.assertTrue(payload["artifacts"]["artifacts_redirected"])
            self.assertNotEqual(effective_root, leaky_artifacts_root.resolve())
            self.assertFalse((workspace / "docs").exists())
            self.assertFalse((workspace / "outputs").exists())
            self.assertTrue(Path(payload["artifacts"]["benchmark_result"]).exists())


if __name__ == "__main__":
    unittest.main()
