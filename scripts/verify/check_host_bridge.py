from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "packages" / "host-integration" / "python"))

from upstream_bridge import analyze_materialized_host


def main() -> int:
    analysis = analyze_materialized_host(REPO_ROOT)
    patch_path = REPO_ROOT / analysis["subagent_start"]["recommended_patch"]
    patch_text = patch_path.read_text(encoding="utf-8")
    host_contract = json.loads((REPO_ROOT / "config" / "host-integration.json").read_text(encoding="utf-8"))

    assert analysis["user_prompt_submit"]["hook_receives_prompt_snapshot"]
    assert analysis["user_prompt_submit"]["hook_updated_input_is_pre_tool_use_only"]
    assert analysis["user_prompt_submit"]["dispatcher_records_context_only"]
    assert analysis["user_prompt_submit"]["turn_uses_original_items_after_hook"]
    assert analysis["user_prompt_submit"]["requires_host_patch_for_physical_suffix"]
    assert analysis["subagent_start"]["hook_supports_additional_context"]
    assert analysis["subagent_start"]["hook_updated_input_is_pre_tool_use_only"]
    assert analysis["subagent_start"]["dispatcher_collects_context_only"]
    assert analysis["subagent_start"]["spawn_agent_injects_context_before_send"]
    assert analysis["subagent_start"]["spawn_team_injects_context_before_send"]
    assert analysis["subagent_start"]["requires_host_patch_for_physical_suffix"]
    assert host_contract["user_turn_policy"]["must_append_vibe_suffix"]
    assert host_contract["subagent_policy"]["must_append_vibe_suffix"]
    assert host_contract["physical_suffix_enforcement"]["strategy"] == "host_patch_required"
    assert host_contract["physical_suffix_enforcement"]["patch_file"] == analysis["user_prompt_submit"]["recommended_patch"]
    assert host_contract["physical_suffix_enforcement"]["patch_file"] == analysis["subagent_start"]["recommended_patch"]

    for needle in (
        "append_vibe_suffix_to_input_items",
        "core/src/codex.rs",
        "spawn.rs",
        "spawn_team.rs",
        " $vibe",
    ):
        assert needle in patch_text, needle

    print(json.dumps(analysis, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
