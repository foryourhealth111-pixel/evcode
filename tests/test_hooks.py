from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "hooks"


def read_fixture(name: str) -> str:
    return (FIXTURE_ROOT / name).read_text(encoding="utf-8")


class HookTests(unittest.TestCase):
    def test_user_prompt_submit_emits_governed_context(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            requirements_dir = Path(tempdir) / "docs" / "requirements"
            plans_dir = Path(tempdir) / "docs" / "plans"
            requirements_dir.mkdir(parents=True, exist_ok=True)
            plans_dir.mkdir(parents=True, exist_ok=True)
            (requirements_dir / "2026-03-15-sample.md").write_text("# req", encoding="utf-8")
            (plans_dir / "2026-03-15-sample-execution-plan.md").write_text("# plan", encoding="utf-8")
            fixture = json.loads(read_fixture("user_prompt_submit.json"))
            fixture["cwd"] = tempdir
            completed = subprocess.run(
                ["python3", str(REPO_ROOT / "scripts" / "hooks" / "user_prompt_submit.py")],
                cwd=REPO_ROOT,
                input=json.dumps(fixture),
                capture_output=True,
                text=True,
                check=True,
                env={**os.environ, "EVCODE_MODE": "benchmark_autonomous"},
            )
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["continue"])
        self.assertEqual(
            "EvCode governed runtime is active. Preserve requirement freezing, plan traceability, verification evidence, and phase cleanup.",
            payload["systemMessage"],
        )
        self.assertIn("mode: benchmark_autonomous", payload["additionalContext"])
        self.assertIn("latest requirement doc:", payload["additionalContext"])
        self.assertIn("` $vibe`", payload["additionalContext"])

    def test_subagent_hook_preserves_suffix_policy(self) -> None:
        completed = subprocess.run(
            ["python3", str(REPO_ROOT / "scripts" / "hooks" / "subagent_start.py")],
            cwd=REPO_ROOT,
            input=read_fixture("subagent_start.json"),
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertIn("agent_type: researcher", payload["additionalContext"])
        self.assertIn("` $vibe`", payload["additionalContext"])

    def test_stop_hook_writes_cleanup_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            fixture = json.loads(read_fixture("stop.json"))
            fixture["cwd"] = tempdir
            completed = subprocess.run(
                ["python3", str(REPO_ROOT / "scripts" / "hooks" / "stop.py")],
                cwd=REPO_ROOT,
                input=json.dumps(fixture),
                capture_output=True,
                text=True,
                check=True,
                env={**os.environ, "EVCODE_RUN_ID": "stop-hook-test"},
            )
            payload = json.loads(completed.stdout)
            cleanup_receipt = Path(tempdir) / "outputs" / "runtime" / "vibe-sessions" / "fixture-session" / "hook-stop-cleanup.json"
            self.assertTrue(cleanup_receipt.exists())
            self.assertIn(str(cleanup_receipt), payload["additionalContext"])

    def test_task_completed_hook_emits_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            fixture = json.loads(read_fixture("task_completed.json"))
            fixture["cwd"] = tempdir
            completed = subprocess.run(
                ["python3", str(REPO_ROOT / "scripts" / "hooks" / "task_completed.py")],
                cwd=REPO_ROOT,
                input=json.dumps(fixture),
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(completed.stdout)
            receipt_path = Path(tempdir) / "outputs" / "runtime" / "vibe-sessions" / "fixture-session" / "task-completed-hook.json"
            self.assertTrue(receipt_path.exists())
            self.assertIn(str(receipt_path), payload["additionalContext"])

    def test_user_prompt_submit_handles_empty_payload(self) -> None:
        completed = subprocess.run(
            ["python3", str(REPO_ROOT / "scripts" / "hooks" / "user_prompt_submit.py")],
            cwd=REPO_ROOT,
            input="{}",
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["continue"])
        self.assertIsInstance(payload["additionalContext"], str)


if __name__ == "__main__":
    unittest.main()
