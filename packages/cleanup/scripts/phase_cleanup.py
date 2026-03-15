from __future__ import annotations

import json
from pathlib import Path


def write_cleanup_receipt(output_path: Path, temp_files_removed: int = 0, node_processes_cleaned: int = 0) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "temp_files_removed": temp_files_removed,
        "node_processes_cleaned": node_processes_cleaned,
        "status": "ok",
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path
