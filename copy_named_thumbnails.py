"""
Create avatar thumbnails from original render PNGs ending with "!".

This script scans the original 3D avatar folders under:
    Avatars/3D Avatar Files/
Each avatar folder contains a single render PNG whose filename ends with '!'
(e.g., "CoolBee!.png"). We use that image to represent the OBJ avatar and
generate a 200x200 thumbnail at:
    static/assets/avatars/<avatar-id>/thumbnail.png

If a matching '!' PNG isn't found for an avatar, we gracefully fall back to
any existing preview.png or texture.png that may already live in the target
avatar folder.
"""

import os
import shutil
from PIL import Image

# Source: original 3D avatar asset folders containing OBJ/MTL/PNG
SOURCE_3D_DIR = os.path.join("Avatars", "3D Avatar Files")

# Target: web app avatar asset folders
TARGET_DIR = "static/assets/avatars"

# Map folder name prefixes to target avatar IDs
# Example folder: "Cool_Bee_1018181944_texture_obj" -> key "Cool_Bee"
FOLDER_PREFIX_TO_AVATAR_ID = {
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
    # Note: we no longer surface a separate 'majesty-bee' in catalog
    "Bee_Majesty": "queen-bee",
    "SeaBee": "sea-bee",
    "Motorcycle_Buzz_Bee": "biker-bee",
    "Builder_Bee": "builder-bee",
    "BrotherBee": "brother-bee",
    "Buzzing_Menace": "killer-bee",
    "Anxious_Bee": "anxious-bee",
}

def _convert_to_rgb_thumbnail(source_path: str, size=(200, 200)) -> Image.Image:
    """Open an image, convert to RGB with white background if needed, and thumbnail it."""
    img = Image.open(source_path)
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        if img.mode == "RGBA":
            background.paste(img, mask=img.split()[3])
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")
    img.thumbnail(size, Image.Resampling.LANCZOS)
    return img


def _find_bang_png_in_folder(folder_path: str) -> str | None:
    """Return the path to the image file (.png/.jpg/.jpeg) whose basename ends with '!'."""
    try:
        exts = (".png", ".jpg", ".jpeg")
        for name in os.listdir(folder_path):
            if not name.lower().endswith(exts):
                continue
            base = os.path.splitext(name)[0]
            if base.endswith("!"):
                return os.path.join(folder_path, name)
    except FileNotFoundError:
        return None
    return None


def _build_folder_to_avatar_mapping() -> dict[str, str]:
    """Map each 3D avatar folder to its target avatar ID using known prefixes."""
    mapping: dict[str, str] = {}
    if not os.path.isdir(SOURCE_3D_DIR):
        return mapping
    for entry in os.listdir(SOURCE_3D_DIR):
        full = os.path.join(SOURCE_3D_DIR, entry)
        if not os.path.isdir(full):
            continue
        for prefix, avatar_id in FOLDER_PREFIX_TO_AVATAR_ID.items():
            if entry.startswith(prefix):
                mapping[full] = avatar_id
                break
    return mapping


def copy_thumbnails():
    """Copy the original '!' PNG renders as thumbnails to each avatar folder."""

    print("🐝 Using '!' PNG renders for OBJ avatars → thumbnails")
    print("=" * 60)

    # Enumerate available 3D folders and match to avatar IDs
    folder_map = _build_folder_to_avatar_mapping()
    if not folder_map:
        print("  ❌ Source 3D avatar directory not found or empty:")
        print(f"     {SOURCE_3D_DIR}")
        return

    # Show a quick inventory
    print("\n📁 Source folders with matching avatar IDs:")
    for folder, avatar_id in sorted(folder_map.items(), key=lambda x: x[1]):
        print(f"  - {os.path.basename(folder)} → {avatar_id}")

    copied = 0
    created_from_preview = 0
    skipped = 0

    # Keep track of which avatars we successfully wrote
    written_avatar_ids: set[str] = set()

    # First pass: copy from original '!' PNGs
    print("\n🔄 Copying from original '!' PNG renders:")
    for folder_path, avatar_id in folder_map.items():
        target_folder = os.path.join(TARGET_DIR, avatar_id)
        target_thumbnail = os.path.join(target_folder, "thumbnail.png")

        # Ensure target folder exists for new avatars
        os.makedirs(target_folder, exist_ok=True)

        source_png = _find_bang_png_in_folder(folder_path)
        if not source_png:
            print(f"  ⚠️  {avatar_id}: No '!' PNG found in {os.path.basename(folder_path)}")
            skipped += 1
            continue

        try:
            img = _convert_to_rgb_thumbnail(source_png)
            img.save(target_thumbnail, "PNG", quality=95, optimize=True)
            size_kb = os.path.getsize(target_thumbnail) / 1024
            print(f"  ✅ {avatar_id}: Copied {os.path.basename(source_png)} ({size_kb:.1f} KB)")
            copied += 1
            written_avatar_ids.add(avatar_id)
        except Exception as e:
            print(f"  ❌ {avatar_id}: Error processing {os.path.basename(source_png)} - {e}")
            skipped += 1

    # Second pass: fill any remaining avatars from preview/texture fallbacks
    print("\n📸 Filling missing thumbnails from preview/texture if available:")
    all_avatars = [
        "cool-bee", "explorer-bee", "rockstar-bee", "doctor-bee",
        "scientist-bee", "professor-bee", "superhero-bee", "knight-bee",
        "robot-bee", "bee-diva", "queen-bee", "builder-bee",
        "sea-bee", "biker-bee", "killer-bee", "anxious-bee", "brother-bee",
    ]

    for avatar_id in all_avatars:
        if avatar_id in written_avatar_ids:
            continue
        target_folder = os.path.join(TARGET_DIR, avatar_id)
        target_thumbnail = os.path.join(target_folder, "thumbnail.png")
        if not os.path.exists(target_folder):
            print(f"  ⚠️  {avatar_id}: Target folder not found → {target_folder}")
            skipped += 1
            continue

        preview_path = os.path.join(target_folder, "preview.png")
        texture_path = os.path.join(target_folder, "texture.png")
        source = preview_path if os.path.exists(preview_path) else (texture_path if os.path.exists(texture_path) else None)
        source_type = "preview" if source == preview_path else ("texture" if source == texture_path else None)

        if not source:
            print(f"  ❌ {avatar_id}: No source available for fallback")
            skipped += 1
            continue

        try:
            img = _convert_to_rgb_thumbnail(source)
            img.save(target_thumbnail, "PNG", quality=95, optimize=True)
            size_kb = os.path.getsize(target_thumbnail) / 1024
            print(f"  📸 {avatar_id}: Created from {source_type} ({size_kb:.1f} KB)")
            created_from_preview += 1
        except Exception as e:
            print(f"  ❌ {avatar_id}: Error generating fallback - {e}")
            skipped += 1

    print("\n" + "=" * 60)
    print("✨ Complete!")
    print(f"   📋 Copied from '!' PNG renders: {copied}")
    print(f"   📸 Created from preview/texture: {created_from_preview}")
    print(f"   ⚠️  Skipped: {skipped}")
    print("=" * 60)

if __name__ == '__main__':
    copy_thumbnails()
