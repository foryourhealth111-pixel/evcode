from __future__ import annotations

import argparse
import json
import tarfile
from pathlib import Path


def inspect_archive(archive_path: Path) -> dict:
    with tarfile.open(archive_path, "r:gz") as archive:
        members = archive.getmembers()
        symlinks = [member for member in members if member.issym() or member.islnk()]
        names = {member.name for member in members}
    return {
        "archive": str(archive_path),
        "has_bundled_host": any(name.endswith("/host/bin/codex") for name in names),
        "symlinks": [member.name for member in symlinks],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate EvCode release archives are self-contained.")
    parser.add_argument("--manifest", required=True, help="Release manifest path")
    args = parser.parse_args()

    manifest_path = Path(args.manifest).resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["self_contained_release"], "release manifest indicates a non-self-contained release"

    for entry in manifest["archives"]:
        archive_info = inspect_archive(Path(entry["archive"]).resolve())
        assert archive_info["has_bundled_host"], archive_info
        assert not archive_info["symlinks"], archive_info

    print("release package checks: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
