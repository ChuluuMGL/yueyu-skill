#!/usr/bin/env python3
"""
Validate public visual assets for yueyu-skill.

This intentionally pins the current approved image hashes. If the logo or
social preview is intentionally redesigned, update the expected hashes in this
file after visually reviewing the output.
"""
from __future__ import annotations

import hashlib
import re
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_IMAGES = {
    "social-preview.png": {
        "size": (1280, 640),
        "sha256": "1897160ddc05a0376380b9735429f7de3d40aa0a2a0bb538f661f7145d923492",
    },
    "assets/brand/yueyu-logo-wordmark.png": {
        "size": (590, 120),
        "sha256": "fad2e532ccdcf834058229b24212cb6e1d3f8a53039bd3a14db14494792338b0",
    },
}

README_FILES = ("README.md", "README.en.md")
SOCIAL_PREVIEW_REF = re.compile(r"!\[[^\]]+\]\(social-preview\.png(?:\?[^)]*)?\)")


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as f:
        head = f.read(24)
    if len(head) < 24 or head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file")
    return struct.unpack(">II", head[16:24])


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    errors: list[str] = []

    for rel, expected in EXPECTED_IMAGES.items():
        path = ROOT / rel
        if not path.exists():
            errors.append(f"{rel}: missing")
            continue
        try:
            actual_size = png_size(path)
        except Exception as exc:
            errors.append(f"{rel}: cannot read PNG dimensions: {exc}")
            continue
        if actual_size != expected["size"]:
            errors.append(f"{rel}: size {actual_size} != {expected['size']}")
        actual_hash = sha256(path)
        if actual_hash != expected["sha256"]:
            errors.append(f"{rel}: sha256 {actual_hash} != {expected['sha256']}")

    for rel in README_FILES:
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        if not SOCIAL_PREVIEW_REF.search(text):
            errors.append(f"{rel}: missing social-preview.png image reference")

    brand_readme = (ROOT / "assets/brand/README.md").read_text(encoding="utf-8")
    for marker in ("YUEYU wordmark", "Do not use the older"):
        if marker not in brand_readme:
            errors.append(f"assets/brand/README.md: missing marker {marker!r}")

    if errors:
        print("Asset check failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("✓ Asset check passed: social preview and canonical YUEYU logo are pinned")
    return 0


if __name__ == "__main__":
    sys.exit(main())
