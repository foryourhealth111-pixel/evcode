from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    distributions = json.loads((repo_root / "config" / "distributions.json").read_text(encoding="utf-8"))
    standard = distributions["channels"]["standard"]
    benchmark = distributions["channels"]["benchmark"]

    assert standard["default_mode"] == "interactive_governed"
    assert benchmark["default_mode"] == "benchmark_autonomous"
    assert standard["profile"] != benchmark["profile"]
    assert standard["app_dir"] != benchmark["app_dir"]
    assert standard["benchmark_adapter"] is False
    assert benchmark["benchmark_adapter"] is True
    print("distribution diff checks: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
