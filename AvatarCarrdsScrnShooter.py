import os
import re
import math
import numpy as np
from pathlib import Path

import trimesh
import pyrender
from PIL import Image, ImageDraw, ImageFont

# =========================
# CONFIGURATION
# =========================

# Folder with your GLB bee avatars
GLB_DIR = Path("/Users/jalex0823/Dropbox/GitBackUpAppFolder/static/assets/avatars/glb_files")

# Output folder for the “baseball card” PNGs
OUTPUT_DIR = GLB_DIR.parent / "cards"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Render resolution (square card)
CARD_SIZE = 1024  # 1024x1024

# Colors (RGBA)
BLACK = (0, 0, 0, 255)
HONEY_GOLD = (250, 210, 90, 255)
CARD_DARK = (18, 18, 18, 255)
TEXT_DARK = (15, 15, 15, 255)

# Layout
NAME_PLATE_HEIGHT_PCT = 0.18   # portion of card height
BORDER_MARGIN_PCT = 0.06       # empty space around avatar area


# =========================
# NAME HELPERS
# =========================

def prettify_name_from_filename(filename: str) -> str:
    """
    'AlBee.glb' -> 'Al Bee'
    'queen_bee.glb' -> 'Queen Bee'
    """
    base = os.path.splitext(os.path.basename(filename))[0]

    # special cases if you want exact marketing names
    overrides = {
        "al_bee": "Al Bee Avatar",
        "albee": "Al Bee Avatar",
    }
    key = base.lower()
    if key in overrides:
        return overrides[key]

    base = base.replace("_", " ")
    # split CamelCase into separate words
    base = re.sub(r"(?<!^)(?=[A-Z])", " ", base)
    # Capitalize each word
    return " ".join(word.capitalize() for word in base.split())


def slug_from_filename(filename: str) -> str:
    """
    'AlBee.glb' -> 'albee'
    'queen_bee.glb' -> 'queen_bee'
    """
    base = os.path.splitext(os.path.basename(filename))[0]
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", slug).strip("_")
    return slug


# =========================
# 3D RENDERING
# =========================

def render_glb_to_image(path: Path, size: int = CARD_SIZE) -> Image.Image:
    """
    Load a GLB file, render it to an RGBA image using pyrender,
    with a black background and nice lighting.
    """
    # Load mesh via trimesh
    mesh = trimesh.load(path, force="mesh")

    # Center and scale mesh
    scene_tm = mesh.scene() if hasattr(mesh, "scene") else trimesh.Scene(mesh)
    # get bounding box
    bounds = scene_tm.bounds  # (min, max)
    min_corner, max_corner = bounds
    center = (min_corner + max_corner) / 2.0
    size_vec = max_corner - min_corner
    max_dim = float(size_vec.max())

    # translate to origin and scale into unit box
    if max_dim <= 0:
        max_dim = 1.0

    scale = 1.0 / max_dim
    scene_tm.apply_scale(scale)
    scene_tm.apply_translation(-center * scale)

    # convert to pyrender
    tm_mesh = trimesh.util.concatenate(scene_tm.dump()) if hasattr(scene_tm, "dump") else mesh
    pr_mesh = pyrender.Mesh.from_trimesh(tm_mesh, smooth=True)

    scene = pyrender.Scene(bg_color=[0, 0, 0, 0], ambient_light=[0.1, 0.1, 0.1, 1.0])
    scene.add(pr_mesh)

    # camera – slightly above and in front, looking at origin
    camera = pyrender.PerspectiveCamera(yfov=np.pi / 4.0, aspectRatio=1.0)
    camera_dist = 2.0
    camera_y = -camera_dist
    camera_z = 0.7
    cam_pose = np.eye(4)
    cam_pose[:3, 3] = np.array([0.0, camera_y, camera_z])

    # point camera at origin
    target = np.array([0.0, 0.0, 0.4])
    forward = (target - cam_pose[:3, 3])
    forward /= np.linalg.norm(forward)
    up = np.array([0.0, 0.0, 1.0])
    right = np.cross(forward, up)
    right /= np.linalg.norm(right)
    up = np.cross(right, forward)

    cam_pose[:3, 0] = right
    cam_pose[:3, 1] = up
    cam_pose[:3, 2] = -forward

    scene.add(camera, pose=cam_pose)

    # lights
    light = pyrender.DirectionalLight(color=np.ones(3), intensity=3.0)
    scene.add(light, pose=cam_pose)  # roughly aligned with camera
    scene.add(
        pyrender.DirectionalLight(color=np.array([1.0, 0.95, 0.9]), intensity=1.5),
        pose=np.array([
            [1, 0, 0, 1.5],
            [0, 1, 0, -1.5],
            [0, 0, 1, 2.5],
            [0, 0, 0, 1],
        ]),
    )

    r = pyrender.OffscreenRenderer(viewport_width=size, viewport_height=size)
    color, _ = r.render(scene)
    r.delete()

    img = Image.fromarray(color, mode="RGBA")
    return img


# =========================
# CARD COMPOSITION
# =========================

def compose_baseball_card(bee_img: Image.Image, display_name: str, size: int = CARD_SIZE) -> Image.Image:
    """
    Place rendered bee on a black baseball-card layout with
    name plate at the bottom.
    """
    card = Image.new("RGBA", (size, size), BLACK)
    draw = ImageDraw.Draw(card)

    w, h = size, size

    # Card panel (dark rectangle slightly inset)
    margin = int(w * BORDER_MARGIN_PCT)
    panel_rect = [margin, margin, w - margin, h - margin]
    draw.rounded_rectangle(panel_rect, radius=int(w * 0.04), fill=CARD_DARK)

    # Name plate
    plate_h = int(h * NAME_PLATE_HEIGHT_PCT)
    plate_top = h - margin - plate_h
    plate_rect = [margin + int(w * 0.03), plate_top, w - margin - int(w * 0.03), h - margin - int(w * 0.02)]
    draw.rounded_rectangle(plate_rect, radius=int(w * 0.03), fill=HONEY_GOLD)

    # Bee area (above name plate)
    top = margin + int(h * 0.04)
    bottom = plate_top - int(h * 0.03)
    left = margin + int(w * 0.06)
    right = w - margin - int(w * 0.06)

    # Resize bee to fit nicely in this area
    area_w = right - left
    area_h = bottom - top
    bee_w, bee_h = bee_img.size

    scale = min(area_w / bee_w, area_h / bee_h) * 0.9
    new_w = int(bee_w * scale)
    new_h = int(bee_h * scale)
    bee_resized = bee_img.resize((new_w, new_h), Image.LANCZOS)

    # Paste bee centered in the area
    bee_x = left + (area_w - new_w) // 2
    bee_y = top + (area_h - new_h) // 2
    card.alpha_composite(bee_resized, (bee_x, bee_y))

    # Name text
    text = display_name
    font_size = int(plate_h * 0.45)
    try:
        # You can change this font path to any .ttf on your Mac if you prefer
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    text_w, text_h = draw.textsize(text, font=font)
    text_x = plate_rect[0] + (plate_rect[2] - plate_rect[0] - text_w) // 2
    text_y = plate_rect[1] + (plate_rect[3] - plate_rect[1] - text_h) // 2

    draw.text((text_x, text_y), text, font=font, fill=TEXT_DARK)

    return card


# =========================
# MAIN LOOP
# =========================

def main():
    glb_files = sorted([p for p in GLB_DIR.iterdir() if p.suffix.lower() == ".glb"])
    if not glb_files:
        print(f"No .glb files found in {GLB_DIR}")
        return

    print(f"Found {len(glb_files)} GLB files")

    for glb_path in glb_files:
        display_name = prettify_name_from_filename(glb_path.name)
        slug = slug_from_filename(glb_path.name)

        print(f"Processing: {glb_path.name} -> {slug}.png ({display_name})")

        try:
            bee_img = render_glb_to_image(glb_path, size=CARD_SIZE)
            card_img = compose_baseball_card(bee_img, display_name, size=CARD_SIZE)

            out_path = OUTPUT_DIR / f"{slug}.png"
            card_img.save(out_path, format="PNG")
            print(f"  ✓ Saved {out_path}")
        except Exception as e:
            print(f"  ✗ Failed on {glb_path.name}: {e}")

    print("Done.")


if __name__ == "__main__":
    main()
