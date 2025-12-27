#!/usr/bin/env python3
"""Verify App Store avatar card PNG sizes.

Apple requires 1024 x 1024 px images for App Store / IAP promotional assets.
This script checks the generated card images under:
  static/assets/avatars/app_store_cards

Exits non-zero if any image isn't exactly 1024x1024.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[1]
CARDS_DIR = REPO_ROOT / "static" / "assets" / "avatars" / "app_store_cards"
EXPECTED = (1024, 1024)


def main() -> int:
    if not CARDS_DIR.exists():
        print(f"❌ Cards folder not found: {CARDS_DIR}")
        return 2

    pngs = sorted(CARDS_DIR.glob("*.png"))
    if not pngs:
        print(f"❌ No .png files found in: {CARDS_DIR}")
        return 2

    bad: list[tuple[Path, tuple[int, int]]] = []
    for p in pngs:
        try:
            with Image.open(p) as im:
                size = im.size
        except Exception as e:
            print(f"❌ Failed to read {p.name}: {e}")
            bad.append((p, (-1, -1)))
            continue

        if size != EXPECTED:
            bad.append((p, size))

    if bad:
        print(f"❌ Size check failed: expected {EXPECTED[0]}x{EXPECTED[1]} for all cards")
        for p, size in bad:
            print(f"   - {p.name}: {size[0]}x{size[1]}")
        print(f"Checked {len(pngs)} files in {CARDS_DIR}")
        return 1

    print(f"✅ All {len(pngs)} card images are {EXPECTED[0]}x{EXPECTED[1]} in {CARDS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
