from __future__ import annotations

from pathlib import Path


REQUIRED_DOCS = {
    "docs/benchmark/acceptance-matrix.md": ["Hard Gates", "fixed 6-stage order preserved"],
    "docs/benchmark/compliance-proof.md": ["Compliance Boundaries", "no hidden second orchestrator"],
    "docs/status/stability-proof.md": ["Goal", "stage-order contract tests"],
    "docs/status/usability-proof.md": ["Goal", "host-native behavior"],
    "docs/status/intelligence-proof.md": ["Goal", "inferred assumptions"],
}


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    for relative_path, needles in REQUIRED_DOCS.items():
        text = (repo_root / relative_path).read_text(encoding="utf-8")
        for needle in needles:
            assert needle in text, f"{needle!r} missing from {relative_path}"
    print("proof doc checks: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
