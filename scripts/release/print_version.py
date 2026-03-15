from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    package_json = json.loads((repo_root / "package.json").read_text(encoding="utf-8"))
    print(package_json["version"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
