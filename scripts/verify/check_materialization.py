from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    source_lock = json.loads((repo_root / "config" / "sources.lock.json").read_text(encoding="utf-8"))

    host_root = repo_root / source_lock["host"]["vendored_dir"]
    runtime_root = repo_root / source_lock["runtime"]["mirrored_dir"]

    host_receipt = json.loads((host_root / "materialization.json").read_text(encoding="utf-8"))
    runtime_receipt = json.loads((runtime_root / "materialization.json").read_text(encoding="utf-8"))
    freshness = json.loads((runtime_root / "freshness.json").read_text(encoding="utf-8"))
    required_markers = json.loads((runtime_root / "required-runtime-markers.json").read_text(encoding="utf-8"))

    assert host_receipt["commit"] == source_lock["host"]["commit"]
    assert runtime_receipt["commit"] == source_lock["runtime"]["commit"]
    assert freshness["commit"] == source_lock["runtime"]["commit"]

    host_target = host_root / source_lock["host"]["materialized_subdir"]
    runtime_target = runtime_root / source_lock["runtime"]["materialized_subdir"]
    assert host_target.exists(), host_target
    assert runtime_target.exists(), runtime_target

    for marker in required_markers["markers"]:
        assert (runtime_target / marker).exists(), marker

    print("materialization checks: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
