"""
Generate Android launcher icon assets from a single 512x512 source PNG.

This updates the icon files under *all* Android projects in this repo:
- android/app/src/main/res
- mobile/android/app/src/main/res
- mobile-wrapper/android/app/src/main/res

Source image (committed):
  static/BeeSmart_AppIcon_512.png
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image


def _write_icons(res_root: Path, src_img: Image.Image) -> None:
    # Adaptive icon foreground (transparent 432x432) so masks work well on Android 8+
    canvas = Image.new("RGBA", (432, 432), (0, 0, 0, 0))
    pad = 36
    maxsz = 432 - pad * 2
    icon = src_img.copy()
    icon.thumbnail((maxsz, maxsz), Image.LANCZOS)
    x = (432 - icon.size[0]) // 2
    y = (432 - icon.size[1]) // 2
    canvas.alpha_composite(icon, (x, y))

    (res_root / "drawable").mkdir(parents=True, exist_ok=True)
    canvas.save(res_root / "drawable" / "ic_launcher_foreground_png.png", format="PNG", optimize=True)

    # Legacy launcher icons (mipmap)
    sizes = {
        "mipmap-mdpi": 48,
        "mipmap-hdpi": 72,
        "mipmap-xhdpi": 96,
        "mipmap-xxhdpi": 144,
        "mipmap-xxxhdpi": 192,
    }
    for folder, sz in sizes.items():
        d = res_root / folder
        d.mkdir(parents=True, exist_ok=True)
        legacy = src_img.resize((sz, sz), Image.LANCZOS)
        legacy.save(d / "ic_launcher.png", format="PNG", optimize=True)
        legacy.save(d / "ic_launcher_round.png", format="PNG", optimize=True)
        # Some tooling references foreground in mipmap as well.
        legacy.save(d / "ic_launcher_foreground.png", format="PNG", optimize=True)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    src = root / "static" / "BeeSmart_AppIcon_512.png"
    if not src.exists():
        raise SystemExit(f"Missing source icon: {src}")

    src_img = Image.open(src).convert("RGBA")

    res_roots = [
        root / "android" / "app" / "src" / "main" / "res",
        root / "mobile" / "android" / "app" / "src" / "main" / "res",
        root / "mobile-wrapper" / "android" / "app" / "src" / "main" / "res",
    ]
    for r in res_roots:
        _write_icons(r, src_img)
        print(f"Updated icons under {r}")


if __name__ == "__main__":
    main()

