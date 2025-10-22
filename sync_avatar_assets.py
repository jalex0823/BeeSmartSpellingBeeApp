"""
Sync 3D avatar assets (OBJ/MTL/Texture/Thumbnail) into static assets.

Discovers folders under Avatars/3D Avatar Files, maps them to avatar IDs using
known folder prefixes, chooses the latest version when multiple folders map to
the same avatar (based on the trailing numeric id in the folder name), and
copies:
  - model.obj (mtl reference rewritten to model.mtl)
  - model.mtl (texture reference rewritten to texture.png)
  - texture.png (copied from original texture file)
  - thumbnail.png (generated from the render PNG whose basename ends with '!')

Usage:
    python sync_avatar_assets.py
"""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path
from typing import Dict
from PIL import Image

SOURCE_3D_DIR = os.path.join("Avatars", "3D Avatar Files")
TARGET_DIR = os.path.join("static", "assets", "avatars")

# Folder prefix to avatar id mapping (keep in sync with avatar_catalog/copy script)
FOLDER_PREFIX_TO_AVATAR_ID: Dict[str, str] = {
    "Cool_Bee": "cool-bee",
    "Explorer_Bee": "explorer-bee",
    "Rockin_Bee": "rockstar-bee",
    "Bee_Doctor": "doctor-bee",
    "Bee_Scientist": "scientist-bee",
    "Professor_Bee": "professor-bee",
    "Super_Bee_Hero": "superhero-bee",
    "Bee_Knight": "knight-bee",
    "Buzzbot_Bee": "robot-bee",
    "Bee_Diva": "bee-diva",
    "Queen_Bee_Majesty": "queen-bee",
    "Bee_Majesty": "queen-bee",  # consolidate to single catalog entry
    "SeaBee": "sea-bee",
    "Motorcycle_Buzz_Bee": "biker-bee",
    "Builder_Bee": "builder-bee",
    "BrotherBee": "brother-bee",
    "Buzzing_Menace": "killer-bee",
    "Anxious_Bee": "anxious-bee",
}


def _extract_version(folder_name: str) -> int:
    """Extract trailing numeric version from folder name, e.g., *_1019092438_* → 1019092438."""
    m = re.search(r"_(\d+)_", folder_name)
    return int(m.group(1)) if m else -1


def _find_bang_png(folder: Path) -> Path | None:
    """Find the render image whose basename ends with '!'.
    Accept .png/.jpg/.jpeg (any case). Top-level only.
    """
    exts = (".png", ".jpg", ".jpeg")
    for p in folder.iterdir():
        if p.is_file() and p.suffix.lower() in exts:
            if p.stem.endswith("!"):
                return p
    return None


def _find_texture_png(folder: Path) -> Path | None:
    """Locate a likely texture image for fallback thumbnail generation."""
    # Prefer explicit 'texture' naming (any case) and common image types
    for pattern in ["*texture*.png", "*Texture*.png", "*texture*.jpg", "*texture*.jpeg"]:
        for p in folder.glob(pattern):
            if not p.stem.endswith("!"):
                return p
    # Fallback: any image that's not the '!' render
    for pattern in ["*.png", "*.jpg", "*.jpeg", "*.PNG", "*.JPG", "*.JPEG"]:
        for p in folder.glob(pattern):
            if not p.stem.endswith("!"):
                return p
    return None


def _choose_latest_folder_for_avatar() -> Dict[str, Path]:
    """Return mapping avatar_id -> best source Path (latest version)."""
    result: Dict[str, Path] = {}
    versions: Dict[str, int] = {}
    root = Path(SOURCE_3D_DIR)
    if not root.is_dir():
        return result
    for entry in root.iterdir():
        if not entry.is_dir():
            continue
        folder_name = entry.name
        avatar_id = None
        for prefix, aid in FOLDER_PREFIX_TO_AVATAR_ID.items():
            if folder_name.startswith(prefix):
                avatar_id = aid
                break
        if not avatar_id:
            continue
        ver = _extract_version(folder_name)
        if avatar_id not in result or ver > versions.get(avatar_id, -1):
            result[avatar_id] = entry
            versions[avatar_id] = ver
    return result


def _write_thumbnail(src_png: Path, dest_png: Path, size=(200, 200)) -> None:
    img = Image.open(src_png)
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        if img.mode == "RGBA":
            bg.paste(img, mask=img.split()[3])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")
    img.thumbnail(size, Image.Resampling.LANCZOS)
    dest_png.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest_png, "PNG", quality=95, optimize=True)


def _rewrite_obj_mtl_refs(obj_text: str) -> str:
    # Replace mtllib line to standard model.mtl
    obj_text = re.sub(r"^mtllib\s+.*$", "mtllib model.mtl", obj_text, flags=re.MULTILINE)
    return obj_text


def _rewrite_mtl_texture_refs(mtl_text: str) -> str:
    mtl_text = re.sub(r"^map_Kd\s+.*$", "map_Kd texture.png", mtl_text, flags=re.MULTILINE)
    return mtl_text


def sync_assets() -> None:
    print("🐝 Syncing avatar assets to static folder…")
    src_map = _choose_latest_folder_for_avatar()
    if not src_map:
        print(f"❌ No source folders found in {SOURCE_3D_DIR}")
        return

    for avatar_id, folder in src_map.items():
        dest = Path(TARGET_DIR) / avatar_id
        dest.mkdir(parents=True, exist_ok=True)
        print(f"📦 {avatar_id}: from {folder.name}")

        # OBJ → model.obj (rewrite mtllib)
        obj_files = list(folder.glob("*.obj"))
        if obj_files:
            try:
                obj_text = obj_files[0].read_text(encoding="utf-8", errors="ignore")
                obj_text = _rewrite_obj_mtl_refs(obj_text)
                (dest / "model.obj").write_text(obj_text, encoding="utf-8")
            except Exception as e:
                print(f"   ⚠️ OBJ copy failed: {e}")

        # MTL → model.mtl (rewrite texture ref)
        mtl_files = list(folder.glob("*.mtl"))
        if mtl_files:
            try:
                mtl_text = mtl_files[0].read_text(encoding="utf-8", errors="ignore")
                mtl_text = _rewrite_mtl_texture_refs(mtl_text)
                (dest / "model.mtl").write_text(mtl_text, encoding="utf-8")
            except Exception as e:
                print(f"   ⚠️ MTL copy failed: {e}")

        # Texture → texture.png
        tex = _find_texture_png(folder)
        if tex and tex.exists():
            try:
                shutil.copy2(str(tex), dest / "texture.png")
            except Exception as e:
                print(f"   ⚠️ Texture copy failed: {e}")

        # Thumbnail from render '!' PNG, else fallback to texture
        bang = _find_bang_png(folder)
        if bang and bang.exists():
            try:
                _write_thumbnail(bang, dest / "thumbnail.png")
                print(f"   🖼️ Thumbnail from render: {bang.name}")
            except Exception as e:
                print(f"   ⚠️ Thumbnail generation from render failed: {e}")
        else:
            tex_for_thumb = _find_texture_png(folder)
            if tex_for_thumb and tex_for_thumb.exists():
                try:
                    _write_thumbnail(tex_for_thumb, dest / "thumbnail.png")
                    print(f"   🖼️ Thumbnail from texture fallback: {tex_for_thumb.name}")
                except Exception as e:
                    print(f"   ⚠️ Thumbnail generation from texture failed: {e}")
            else:
                print("   ⚠️ No render '!' image or suitable texture found for thumbnail.")

    print("✨ Sync complete.")


if __name__ == "__main__":
    sync_assets()
