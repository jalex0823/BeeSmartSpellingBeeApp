#!/usr/bin/env python3
"""Flatten promoted IAP images for App Store Connect.

App Store Connect promotional images require:
- PNG or JPEG
- 1024 x 1024
- RGB, flattened (no transparency)
- no rounded corners

This script takes the generated PNGs under:
  static/assets/avatars/app_store_cards
(which may contain transparency), flattens them onto a solid background, and
writes results to:
  static/assets/avatars/app_store_cards_flattened

Background defaults to white to appear "no background" while staying flattened.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[1]
IN_DIR = REPO_ROOT / "static" / "assets" / "avatars" / "app_store_cards"
OUT_DIR = REPO_ROOT / "static" / "assets" / "avatars" / "app_store_cards_flattened"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED = (1024, 1024)
BG = (255, 255, 255)  # white
DPI = (72, 72)


def main() -> int:
    if not IN_DIR.exists():
        print(f"❌ Input folder not found: {IN_DIR}")
        return 2

    pngs = sorted(IN_DIR.glob("*.png"))
    if not pngs:
        print(f"❌ No .png files found in: {IN_DIR}")
        return 2

    bad_size = 0
    converted = 0

    for p in pngs:
        with Image.open(p) as im:
            im = im.convert("RGBA")
            if im.size != EXPECTED:
                bad_size += 1
                print(f"⚠️  Skipping {p.name}: size {im.size[0]}x{im.size[1]} (expected 1024x1024)")
                continue

            # Flatten RGBA -> RGB on solid background
            bg = Image.new("RGB", im.size, BG)
            bg.paste(im, mask=im.split()[3])

            out = OUT_DIR / p.name
            bg.save(out, format="PNG", optimize=True, dpi=DPI)
            converted += 1

    if bad_size:
        print(f"⚠️  {bad_size} files skipped due to wrong size")

    print(f"✅ Wrote {converted} flattened promo images to: {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
