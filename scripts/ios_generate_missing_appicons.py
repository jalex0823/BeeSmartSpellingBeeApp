#!/usr/bin/env python3
"""Generate missing iPad app icons into the Capacitor iOS asset catalog.

Why this exists:
- Xcode warns when iPad icon slots are missing (76x76@2x, 83.5x83.5@2x, etc.)
- The repo already contains the crest-derived icons for iPhone sizes, but older trees can drift.

This script:
- Reads the existing 1024x1024 marketing icon as the source
- Generates required iPad + common iOS sizes if missing
- Writes into: mobile/ios/App/App/Assets.xcassets/AppIcon.appiconset/

It is safe to run repeatedly.

Dependencies:
- Pillow (PIL)

Usage:
  python3 scripts/ios_generate_missing_appicons.py
"""

from __future__ import annotations

from pathlib import Path

try:
    from PIL import Image
except ImportError as e:  # pragma: no cover
    raise SystemExit(
        "Pillow is required. Install with: pip install Pillow"
    ) from e


ROOT = Path(__file__).resolve().parents[1]
APPICON_DIR = ROOT / "mobile" / "ios" / "App" / "App" / "Assets.xcassets" / "AppIcon.appiconset"

SOURCE_CANDIDATES = [
    APPICON_DIR / "Icon-App-1024x1024@1x.png",
    APPICON_DIR / "AppIcon-1024x1024.png",
]

# filename -> pixel_size
REQUIRED = {
    # iPad notification/settings/spotlight sizes
    "Icon-App-20x20@1x.png": 20,
    "Icon-App-20x20@2x.png": 40,
    "Icon-App-29x29@1x.png": 29,
    "Icon-App-29x29@2x.png": 58,
    "Icon-App-40x40@1x.png": 40,
    "Icon-App-40x40@2x.png": 80,
    "Icon-App-76x76@1x.png": 76,
    "Icon-App-76x76@2x.png": 152,
    "Icon-App-83.5x83.5@2x.png": 167,
}


def _find_source() -> Path:
    for p in SOURCE_CANDIDATES:
        if p.exists():
            return p
    raise SystemExit(
        f"No 1024x1024 source icon found. Looked for: {', '.join(str(p) for p in SOURCE_CANDIDATES)}"
    )


def _save_resized(src_img: Image.Image, dest: Path, size: int) -> None:
    # Use high-quality downsampling and ensure we output PNG with alpha if present.
    img = src_img.resize((size, size), Image.Resampling.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, format="PNG", optimize=True)


def main() -> int:
    APPICON_DIR.mkdir(parents=True, exist_ok=True)

    source_path = _find_source()
    src = Image.open(source_path).convert("RGBA")

    written = 0
    for filename, px in REQUIRED.items():
        dest = APPICON_DIR / filename
        if dest.exists():
            continue
        _save_resized(src, dest, px)
        written += 1

    print(f"AppIcon generation complete. Source={source_path.name} written={written} dir={APPICON_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
