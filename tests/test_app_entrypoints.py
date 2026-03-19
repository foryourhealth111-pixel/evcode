from __future__ import annotations

import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def make_stub_host(tempdir: str) -> Path:
    stub_path = Path(tempdir) / "codex-stub.sh"
    stub_path.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
python3 - "$@" <<'PY'
import json
import os
import sys
print(json.dumps({
  "argv": sys.argv[1:],
  "codex_home": os.environ.get("CODEX_HOME"),
  "evcode_mode": os.environ.get("EVCODE_MODE"),
  "evcode_channel": os.environ.get("EVCODE_CHANNEL"),
}))
PY
""",
        encoding="utf-8",
    )
    stub_path.chmod(stub_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return stub_path


class AppEntrypointTests(unittest.TestCase):
    def test_benchmark_status_reports_default_submission_preset(self) -> None:
        completed = subprocess.run(
            ["node", str(REPO_ROOT / "apps" / "evcode-bench" / "bin" / "evcode-bench.js"), "status", "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("benchmark", payload["channel"])
        self.assertEqual(
            "config/submission-presets/rightcode-gpt-5.4-xhigh.json",
            payload["default_submission_preset"],
        )
        self.assertEqual("core_benchmark", payload["baseline_family"])
        self.assertEqual("config/baseline-families.json", payload["baseline_families_config"])
        self.assertEqual("config/assistant-policy.benchmark.json", payload["assistant_policy"])
        self.assertEqual("config/specialist-routing.json", payload["specialist_routing"])
        self.assertEqual("codex_primary_benchmark", payload["specialist_rollout_phase"])
        self.assertEqual("core_benchmark", payload["baseline_surface"]["family"])
        self.assertIn("codex", payload["assistants"])
        self.assertEqual("config/assistant-providers.env.local", payload["provider_setup"]["local_env_path"])
        self.assertEqual("docs/configuration/openai-compatible-provider-setup.md", payload["provider_setup"]["setup_doc_path"])
        self.assertEqual("chat_completions", payload["assistant_api_compatibility"]["primary_wire_api"])
        self.assertEqual("vco_artifacts", payload["governance_surface"]["persistent_memory_owner"])
        self.assertIn("codex_only", payload["governance_surface"]["capability_classes"])

    def test_standard_entrypoint_passthrough_launches_native_host(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            stub = make_stub_host(tempdir)
            source_codex_home = Path(tempdir) / "source-codex-home"
            source_codex_home.mkdir(parents=True, exist_ok=True)
            (source_codex_home / "config.toml").write_text(
                """
model_provider = "rightcode"
model = "gpt-5.4"

[model_providers.rightcode]
base_url = "https://right.codes/codex/v1"
wire_api = "responses"
requires_openai_auth = true
""".strip()
                + "\n",
                encoding="utf-8",
            )
            (source_codex_home / "auth.json").write_text('{"OPENAI_API_KEY":"test-key"}\n', encoding="utf-8")
            completed = subprocess.run(
                ["node", str(REPO_ROOT / "apps" / "evcode" / "bin" / "evcode.js"), "--version"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
                env={
                    **os.environ,
                    "EVCODE_HOST_BIN": str(stub),
                    "EVCODE_DIST_OUTPUT_ROOT": tempdir,
                    "EVCODE_SOURCE_CODEX_HOME": str(source_codex_home),
                },
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(["--version"], payload["argv"])
            self.assertEqual("interactive_governed", payload["evcode_mode"])
            self.assertEqual("standard", payload["evcode_channel"])
            assembled_config = (Path(tempdir) / "standard" / "codex-home" / "config.toml").read_text(encoding="utf-8")
            self.assertIn('model_provider = "rightcode"', assembled_config)
            self.assertIn('model = "gpt-5.4"', assembled_config)
            self.assertTrue((Path(tempdir) / "standard" / "codex-home" / "auth.json").exists())

    def test_standard_entrypoint_ignores_self_managed_codex_home_when_adopting_source_config(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp_root = Path(tempdir)
            stub = make_stub_host(tempdir)
            home = temp_root / "home"
            source_codex_home = home / ".codex"
            source_codex_home.mkdir(parents=True, exist_ok=True)
            (source_codex_home / "config.toml").write_text(
                """
model_provider = "rightcode"
model = "gpt-5.4"

[model_providers.rightcode]
base_url = "https://right.codes/codex/v1"
wire_api = "responses"
requires_openai_auth = true
""".strip()
                + "\n",
                encoding="utf-8",
            )
            (source_codex_home / "auth.json").write_text('{"OPENAI_API_KEY":"test-key"}\n', encoding="utf-8")
            self_managed_codex_home = temp_root / "standard" / "codex-home"
            self_managed_codex_home.mkdir(parents=True, exist_ok=True)
            (self_managed_codex_home / "config.toml").write_text('profile = "standard"\n', encoding="utf-8")
            completed = subprocess.run(
                ["node", str(REPO_ROOT / "apps" / "evcode" / "bin" / "evcode.js"), "--version"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
                env={
                    **os.environ,
                    "HOME": str(home),
                    "CODEX_HOME": str(self_managed_codex_home),
                    "EVCODE_HOST_BIN": str(stub),
                    "EVCODE_DIST_OUTPUT_ROOT": tempdir,
                },
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(["--version"], payload["argv"])
            assembled_config = (temp_root / "standard" / "codex-home" / "config.toml").read_text(encoding="utf-8")
            self.assertIn('model_provider = "rightcode"', assembled_config)
            self.assertIn('model = "gpt-5.4"', assembled_config)
            self.assertTrue((temp_root / "standard" / "codex-home" / "auth.json").exists())

    def test_standard_status_reports_assembled_config_snapshot(self) -> None:
        completed = subprocess.run(
            ["node", str(REPO_ROOT / "apps" / "evcode" / "bin" / "evcode.js"), "status", "--json"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual("standard", payload["channel"])
        self.assertIn("bundled_host_available", payload)
        self.assertIn("source_codex_home", payload)
        self.assertEqual("config/assistant-policy.standard.json", payload["assistant_policy"])
        self.assertEqual("config/specialist-routing.json", payload["specialist_routing"])
        self.assertEqual("hybrid_governed", payload["baseline_family"])
        self.assertEqual("config/baseline-families.json", payload["baseline_families_config"])
        self.assertEqual("tier_a_advisory_only", payload["specialist_rollout_phase"])
        self.assertEqual("hybrid_governed", payload["baseline_surface"]["family"])
        self.assertIn("claude", payload["assistants"])
        self.assertIn("gemini", payload["assistants"])
        self.assertEqual("config/assistant-providers.env.local", payload["provider_setup"]["local_env_path"])
        self.assertEqual("docs/configuration/openai-compatible-provider-setup.md", payload["provider_setup"]["setup_doc_path"])
        self.assertEqual("chat_completions", payload["assistant_api_compatibility"]["primary_wire_api"])
        self.assertEqual("gpt-5.4", payload["assistant_provider_resolution"]["codex"]["model"])
        self.assertEqual("vco_artifacts", payload["governance_surface"]["persistent_memory_owner"])
        self.assertEqual("codex_only", payload["governance_surface"]["assistants"]["codex"]["capability_mode"])
        self.assertEqual("proxy_mediated", payload["governance_surface"]["assistants"]["claude"]["capability_mode"])
        if payload["assembled_distribution_exists"]:
            self.assertIn("assembled", payload)

    def test_status_can_load_provider_overrides_from_local_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            env_file = Path(tempdir) / "assistant-providers.env.local"
            env_file.write_text(
                """
EVCODE_ENABLE_LIVE_SPECIALISTS=1
EVCODE_RIGHTCODES_API_KEY=sk-local-test
EVCODE_CODEX_MODEL=gpt-5.4-custom
EVCODE_CLAUDE_MODEL=claude-custom
EVCODE_GEMINI_BASE_URL=https://example.test/gemini/v1
""".strip() + "\n",
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
                    "EVCODE_PROVIDER_ENV_FILE": str(env_file),
                },
            )
            payload = json.loads(completed.stdout)
            self.assertTrue(payload["provider_setup"]["local_env_present"])
            self.assertTrue(payload["provider_setup"]["loaded_from_file"])
            self.assertIn("EVCODE_CODEX_MODEL", payload["provider_setup"]["loaded_keys"])
            self.assertEqual(str(env_file), payload["provider_setup"]["resolved_local_env_path"])
            self.assertEqual("gpt-5.4-custom", payload["assistant_provider_resolution"]["codex"]["model"])
            self.assertEqual("claude-custom", payload["assistant_provider_resolution"]["claude"]["model"])
            self.assertEqual("https://example.test/gemini/v1", payload["assistant_provider_resolution"]["gemini"]["base_url"])
            self.assertTrue(payload["assistant_provider_resolution"]["claude"]["api_key_present"])

    def test_standard_run_emits_non_silent_warning_when_specialist_provider_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            completed = subprocess.run(
                [
                    "node",
                    str(REPO_ROOT / "apps" / "evcode" / "bin" / "evcode.js"),
                    "run",
                    "--task",
                    "Plan the product architecture and UX workflow for an ambiguous redesign",
                    "--artifacts-root",
                    tempdir,
                    "--run-id",
                    "non-silent-fallback",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
                env={
                    **os.environ,
                    "EVCODE_ENABLE_LIVE_SPECIALISTS": "1",
                    "EVCODE_RIGHTCODES_API_KEY": "sk-local-test",
                    "EVCODE_CLAUDE_BASE_URL": "http://127.0.0.1:9/claude/v1",
                    "EVCODE_CLAUDE_MODEL": "claude-opus-4-6",
                },
            )
            payload = json.loads(completed.stdout)
            self.assertEqual("degraded_fallback_to_codex", payload["execution_outcome"])
            self.assertTrue(payload["warnings"])
            warning = payload["warnings"][0]
            self.assertEqual("claude", warning["assistant_name"])
            self.assertIn("degraded mode", warning["message"])
            self.assertIn("Warning:", completed.stderr)
            degraded = {item["assistant_name"] for item in payload["specialist_routing"]["degraded_delegates"]}
            self.assertIn("claude", degraded)
            codex_integration = json.loads(Path(payload["artifacts"]["codex_integration_receipt"]).read_text(encoding="utf-8"))
            self.assertIn("claude", codex_integration["degraded_specialists"])

    def test_standard_probe_providers_reports_non_live_statuses(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            env_file = Path(tempdir) / "assistant-providers.env.local"
            env_file.write_text("", encoding="utf-8")
            completed = subprocess.run(
                [
                    "node",
                    str(REPO_ROOT / "apps" / "evcode" / "bin" / "evcode.js"),
                    "probe-providers",
                    "--json",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
                env={
                    **os.environ,
                    "EVCODE_PROVIDER_ENV_FILE": str(env_file),
                    "EVCODE_RIGHTCODES_API_KEY": "",
                    "EVCODE_ENABLE_LIVE_SPECIALISTS": "0",
                },
            )
        payload = json.loads(completed.stdout)
        self.assertEqual("standard", payload["channel"])
        self.assertEqual("hybrid_governed", payload["baseline_family"])
        self.assertEqual("config/baseline-families.json", payload["baseline_families_config"])
        self.assertFalse(payload["live_probe_requested"])
        self.assertEqual("chat_completions", payload["compatibility_surface"]["primary_wire_api"])
        by_name = {item["assistant_name"]: item for item in payload["results"]}
        self.assertEqual("missing_api_key", by_name["codex"]["status"])
        self.assertEqual("missing_api_key", by_name["claude"]["status"])
        self.assertEqual("missing_api_key", by_name["gemini"]["status"])
        self.assertEqual("advisory_only", by_name["claude"]["authority_tier"])
        self.assertEqual("proxy_mediated", by_name["gemini"]["capability_mode"])

    def test_benchmark_probe_providers_reports_policy_state(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            env_file = Path(tempdir) / "assistant-providers.env.local"
            env_file.write_text("", encoding="utf-8")
            completed = subprocess.run(
                [
                    "node",
                    str(REPO_ROOT / "apps" / "evcode-bench" / "bin" / "evcode-bench.js"),
                    "probe-providers",
                    "--json",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
                env={
                    **os.environ,
                    "EVCODE_PROVIDER_ENV_FILE": str(env_file),
                    "EVCODE_RIGHTCODES_API_KEY": "",
                    "EVCODE_ENABLE_LIVE_SPECIALISTS": "0",
                },
            )
        payload = json.loads(completed.stdout)
        self.assertEqual("benchmark", payload["channel"])
        self.assertEqual("core_benchmark", payload["baseline_family"])
        self.assertEqual("config/baseline-families.json", payload["baseline_families_config"])
        by_name = {item["assistant_name"]: item for item in payload["results"]}
        self.assertEqual("missing_api_key", by_name["codex"]["status"])
        self.assertEqual("policy_disabled", by_name["claude"]["status"])
        self.assertEqual("policy_disabled", by_name["gemini"]["status"])
        self.assertEqual("codex_only", by_name["codex"]["capability_mode"])

    def test_standard_entrypoint_uses_bundled_host_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            stub = make_stub_host(tempdir)
            subprocess.run(
                [
                    "python3",
                    str(REPO_ROOT / "scripts" / "build" / "assemble_distribution.py"),
                    "--channel",
                    "standard",
                    "--output-root",
                    tempdir,
                    "--host-binary",
                    "missing-codex-host",
                    "--bundled-host-binary",
                    str(stub),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            completed = subprocess.run(
                ["node", str(REPO_ROOT / "apps" / "evcode" / "bin" / "evcode.js"), "native", "--version"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
                env={
                    **os.environ,
                    "EVCODE_DIST_OUTPUT_ROOT": tempdir,
                },
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(["--version"], payload["argv"])
            self.assertEqual("standard", payload["evcode_channel"])

    def test_benchmark_entrypoint_auto_adopts_source_codex_home_and_bundled_host(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            stub = make_stub_host(tempdir)
            source_codex_home = Path(tempdir) / "source-codex-home"
            source_codex_home.mkdir(parents=True, exist_ok=True)
            (source_codex_home / "config.toml").write_text(
                """
model_provider = "rightcode"
model = "gpt-5.4"

[model_providers.rightcode]
base_url = "https://right.codes/codex/v1"
wire_api = "responses"
requires_openai_auth = true
""".strip()
                + "\n",
                encoding="utf-8",
            )
            (source_codex_home / "auth.json").write_text('{"OPENAI_API_KEY":"test-key"}\n', encoding="utf-8")
            subprocess.run(
                [
                    "python3",
                    str(REPO_ROOT / "scripts" / "build" / "assemble_distribution.py"),
                    "--channel",
                    "benchmark",
                    "--output-root",
                    tempdir,
                    "--host-binary",
                    "missing-codex-host",
                    "--bundled-host-binary",
                    str(stub),
                    "--source-codex-home",
                    str(source_codex_home),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            completed = subprocess.run(
                ["node", str(REPO_ROOT / "apps" / "evcode-bench" / "bin" / "evcode-bench.js"), "native", "--version"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
                env={
                    **os.environ,
                    "EVCODE_DIST_OUTPUT_ROOT": tempdir,
                    "EVCODE_SOURCE_CODEX_HOME": str(source_codex_home),
                },
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(["--version"], payload["argv"])
            self.assertEqual("benchmark_autonomous", payload["evcode_mode"])
            self.assertEqual("benchmark", payload["evcode_channel"])
            assembled_config = (Path(tempdir) / "benchmark" / "codex-home" / "config.toml").read_text(encoding="utf-8")
            self.assertIn('model_provider = "rightcode"', assembled_config)
            self.assertIn('model = "gpt-5.4"', assembled_config)
            self.assertTrue((Path(tempdir) / "benchmark" / "codex-home" / "auth.json").exists())


    def test_benchmark_trace_replays_saved_runtime_events(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp_root = Path(tempdir)
            workspace = temp_root / "workspace"
            workspace.mkdir()
            fake_codex = temp_root / "fake_codex"
            fake_codex.write_text(
                """#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path

argv = sys.argv[1:]
for index, token in enumerate(argv):
    if token == "--output-last-message":
        Path(argv[index + 1]).write_text("benchmark trace ready", encoding="utf-8")
        break
sys.exit(0)
""",
                encoding="utf-8",
            )
            fake_codex.chmod(0o755)
            subprocess.run(
                [
                    "node",
                    str(REPO_ROOT / "apps" / "evcode-bench" / "bin" / "evcode-bench.js"),
                    "run",
                    "--task",
                    "Build a benchmark-safe autonomous runtime smoke test with proof artifacts",
                    "--workspace",
                    str(workspace),
                    "--artifacts-root",
                    tempdir,
                    "--run-id",
                    "benchmark-trace-demo",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
                env={
                    **os.environ,
                    "EVCODE_BENCH_HOST_BIN": str(fake_codex),
                },
            )
            traced = subprocess.run(
                [
                    "node",
                    str(REPO_ROOT / "apps" / "evcode-bench" / "bin" / "evcode-bench.js"),
                    "trace",
                    "benchmark-trace-demo",
                    "--artifacts-root",
                    tempdir,
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertIn("EvCode Governed Run", traced.stdout)
            self.assertIn("run_id: benchmark-trace-demo", traced.stdout)
            self.assertIn("route: codex_only_benchmark", traced.stdout)
            self.assertIn("Timeline", traced.stdout)

    def test_standard_run_trace_surfaces_actor_timeline(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            completed = subprocess.run(
                [
                    "node",
                    str(REPO_ROOT / "apps" / "evcode" / "bin" / "evcode.js"),
                    "run",
                    "--task",
                    "Design a responsive frontend landing page with typography, spacing, motion, and visual polish",
                    "--trace",
                    "--artifacts-root",
                    tempdir,
                    "--run-id",
                    "trace-actor-demo",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
                env={
                    **os.environ,
                    "EVCODE_ENABLE_LIVE_SPECIALISTS": "0",
                },
            )
            self.assertIn("EvCode Governed Run", completed.stdout)
            self.assertIn("route: codex_with_specialists", completed.stdout)
            self.assertIn("Actors", completed.stdout)
            self.assertIn("GEMI", completed.stdout)
            self.assertIn("Timeline", completed.stdout)
            self.assertIn("runtime_events:", completed.stdout)

    def test_standard_trace_replays_saved_runtime_events(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            subprocess.run(
                [
                    "node",
                    str(REPO_ROOT / "apps" / "evcode" / "bin" / "evcode.js"),
                    "run",
                    "--task",
                    "Plan the product architecture and UX workflow for an ambiguous redesign",
                    "--artifacts-root",
                    tempdir,
                    "--run-id",
                    "trace-replay-demo",
                    "--json",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
                env={
                    **os.environ,
                    "EVCODE_ENABLE_LIVE_SPECIALISTS": "0",
                },
            )
            traced = subprocess.run(
                [
                    "node",
                    str(REPO_ROOT / "apps" / "evcode" / "bin" / "evcode.js"),
                    "trace",
                    "trace-replay-demo",
                    "--artifacts-root",
                    tempdir,
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertIn("EvCode Governed Run", traced.stdout)
            self.assertIn("run_id: trace-replay-demo", traced.stdout)
            self.assertIn("CLAU", traced.stdout)
            self.assertIn("Timeline", traced.stdout)
            self.assertIn("route: codex_with_specialists", traced.stdout)



    def test_standard_resume_restores_latest_governed_session(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            subprocess.run(
                [
                    "node",
                    str(REPO_ROOT / "apps" / "evcode" / "bin" / "evcode.js"),
                    "run",
                    "--task",
                    "Plan the product architecture and UX workflow for an ambiguous redesign",
                    "--artifacts-root",
                    tempdir,
                    "--run-id",
                    "resume-history-demo",
                    "--json",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
                env={**os.environ, "EVCODE_ENABLE_LIVE_SPECIALISTS": "0"},
            )
            resumed = subprocess.run(
                [
                    "node",
                    str(REPO_ROOT / "apps" / "evcode" / "bin" / "evcode.js"),
                    "resume",
                    "--artifacts-root",
                    tempdir,
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertIn("EvCode Governed Run", resumed.stdout)
            self.assertIn("run_id: resume-history-demo", resumed.stdout)
            self.assertIn("route: codex_with_specialists", resumed.stdout)

    def test_standard_resume_errors_clearly_when_no_governed_session_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            resumed = subprocess.run(
                [
                    "node",
                    str(REPO_ROOT / "apps" / "evcode" / "bin" / "evcode.js"),
                    "resume",
                    "--artifacts-root",
                    tempdir,
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(0, resumed.returncode)
            self.assertIn("No governed runtime sessions found", resumed.stderr)


if __name__ == "__main__":
    unittest.main()
