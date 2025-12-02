#!/usr/bin/env python3
"""
Avatar Screenshot Generator for App Store
Creates beautiful avatar cards for App Store registration

Requirements:
    pip install trimesh pyrender pillow numpy pyglet
"""

import os
import sys
import re
from pathlib import Path

# Check dependencies
try:
    import trimesh
    import pyrender
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    DEPS_OK = True
except ImportError as e:
    DEPS_OK = False
    print(f"❌ Missing dependencies: {e}")
    print("\n📦 Install with:")
    print("   pip install trimesh pyrender pillow numpy pyglet")
    sys.exit(1)

# Import avatar catalog for proper names
try:
    from avatar_catalog import AVATAR_CATALOG
    print(f"✅ Loaded avatar catalog ({len(AVATAR_CATALOG)} avatars)")
except ImportError:
    print("⚠️  Could not load avatar_catalog.py - using filename-based names")
    AVATAR_CATALOG = []

# =========================
# CONFIGURATION
# =========================

GLB_DIR = Path("/Users/jalex0823/Dropbox/GitBackUpAppFolder/static/assets/avatars/glb_files")
OUTPUT_DIR = Path("/Users/jalex0823/Dropbox/GitBackUpAppFolder/static/assets/avatars/app_store_cards")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Render resolution - App Store optimized
CARD_SIZE = 2048  # High resolution for App Store

# Colors (RGBA)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
HONEY_GOLD = (250, 210, 90, 255)
CARD_DARK = (25, 25, 35, 255)
TEXT_DARK = (15, 15, 15, 255)
ACCENT_BLUE = (100, 180, 255, 255)

# Layout
NAME_PLATE_HEIGHT_PCT = 0.15
BORDER_MARGIN_PCT = 0.04

# =========================
# NAME HELPERS
# =========================

def get_display_name(glb_filename: str) -> str:
    """Get proper display name from avatar catalog"""
    base = os.path.splitext(os.path.basename(glb_filename))[0]
    
    # Try to match in catalog
    for avatar in AVATAR_CATALOG:
        obj_file = avatar.get('obj_file', '')
        if obj_file and base in obj_file:
            return avatar.get('name', prettify_name(base))
    
    # Fallback to prettified filename
    return prettify_name(base)

def prettify_name(filename: str) -> str:
    """Convert filename to pretty name"""
    base = os.path.splitext(os.path.basename(filename))[0]
    base = base.replace("_", " ")
    base = re.sub(r"(?<!^)(?=[A-Z])", " ", base)
    return " ".join(word.capitalize() for word in base.split())

def slug_from_filename(filename: str) -> str:
    """Create slug from filename"""
    base = os.path.splitext(os.path.basename(filename))[0]
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", slug).strip("_")
    return slug

# =========================
# 3D RENDERING
# =========================

def render_glb_to_image(path: Path, size: int = CARD_SIZE) -> Image.Image:
    """Render GLB file to RGBA image with professional lighting"""
    try:
        # Load mesh
        mesh = trimesh.load(str(path), force="mesh")
        
        # Get scene
        if hasattr(mesh, "scene"):
            scene_tm = mesh.scene()
        else:
            scene_tm = trimesh.Scene(mesh)
        
        # Center and scale
        bounds = scene_tm.bounds
        min_corner, max_corner = bounds
        center = (min_corner + max_corner) / 2.0
        size_vec = max_corner - min_corner
        max_dim = float(size_vec.max())
        
        if max_dim <= 0:
            max_dim = 1.0
        
        scale = 1.8 / max_dim  # Slightly larger for better visibility
        scene_tm.apply_scale(scale)
        scene_tm.apply_translation(-center * scale)
        
        # Convert to pyrender
        if hasattr(scene_tm, "dump"):
            tm_mesh = trimesh.util.concatenate(scene_tm.dump())
        else:
            tm_mesh = mesh
        
        pr_mesh = pyrender.Mesh.from_trimesh(tm_mesh, smooth=True)
        
        # Create scene with transparent background
        scene = pyrender.Scene(bg_color=[0, 0, 0, 0], ambient_light=[0.15, 0.15, 0.15, 1.0])
        scene.add(pr_mesh)
        
        # Camera setup - optimal viewing angle
        camera = pyrender.PerspectiveCamera(yfov=np.pi / 4.5, aspectRatio=1.0)
        camera_dist = 2.2
        camera_pose = np.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.0, np.cos(-0.2), -np.sin(-0.2), camera_dist],
            [0.0, np.sin(-0.2), np.cos(-0.2), 0.6],
            [0.0, 0.0, 0.0, 1.0]
        ])
        scene.add(camera, pose=camera_pose)
        
        # Professional 3-point lighting
        # Key light
        key_light = pyrender.DirectionalLight(color=np.ones(3), intensity=4.0)
        scene.add(key_light, pose=camera_pose)
        
        # Fill light (from side)
        fill_pose = np.array([
            [1.0, 0.0, 0.0, -2.0],
            [0.0, 1.0, 0.0, 1.0],
            [0.0, 0.0, 1.0, 1.5],
            [0.0, 0.0, 0.0, 1.0]
        ])
        fill_light = pyrender.DirectionalLight(color=np.array([1.0, 0.95, 0.9]), intensity=2.0)
        scene.add(fill_light, pose=fill_pose)
        
        # Rim light (back)
        rim_pose = np.array([
            [1.0, 0.0, 0.0, 0.5],
            [0.0, 1.0, 0.0, -2.5],
            [0.0, 0.0, 1.0, 2.0],
            [0.0, 0.0, 0.0, 1.0]
        ])
        rim_light = pyrender.DirectionalLight(color=np.array([1.0, 1.0, 1.0]), intensity=1.5)
        scene.add(rim_light, pose=rim_pose)
        
        # Render
        r = pyrender.OffscreenRenderer(viewport_width=size, viewport_height=size)
        color, _ = r.render(scene)
        r.delete()
        
        return Image.fromarray(color, mode="RGBA")
    
    except Exception as e:
        print(f"      ⚠️  Render error: {e}")
        # Return placeholder image
        img = Image.new("RGBA", (size, size), (50, 50, 50, 255))
        return img

# =========================
# CARD COMPOSITION
# =========================

def compose_app_store_card(bee_img: Image.Image, display_name: str, size: int = CARD_SIZE) -> Image.Image:
    """Create App Store-ready avatar card"""
    card = Image.new("RGBA", (size, size), BLACK)
    draw = ImageDraw.Draw(card)
    
    w, h = size, size
    margin = int(w * BORDER_MARGIN_PCT)
    
    # Gradient background effect (dark with subtle gradient)
    for y in range(h):
        alpha = int(255 * (1.0 - y / h * 0.3))
        color = (CARD_DARK[0], CARD_DARK[1], CARD_DARK[2], alpha)
        draw.line([(0, y), (w, y)], fill=color)
    
    # Main card panel
    panel_rect = [margin, margin, w - margin, h - margin]
    draw.rounded_rectangle(panel_rect, radius=int(w * 0.035), fill=None, outline=HONEY_GOLD, width=int(w * 0.005))
    
    # Name plate
    plate_h = int(h * NAME_PLATE_HEIGHT_PCT)
    plate_top = h - margin - plate_h - int(h * 0.02)
    plate_rect = [
        margin + int(w * 0.05),
        plate_top,
        w - margin - int(w * 0.05),
        h - margin - int(h * 0.02)
    ]
    draw.rounded_rectangle(plate_rect, radius=int(w * 0.025), fill=HONEY_GOLD)
    
    # Bee area
    top = margin + int(h * 0.05)
    bottom = plate_top - int(h * 0.04)
    left = margin + int(w * 0.08)
    right = w - margin - int(w * 0.08)
    
    # Resize bee
    area_w = right - left
    area_h = bottom - top
    bee_w, bee_h = bee_img.size
    
    scale = min(area_w / bee_w, area_h / bee_h) * 0.88
    new_w = int(bee_w * scale)
    new_h = int(bee_h * scale)
    bee_resized = bee_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Paste bee centered
    bee_x = left + (area_w - new_w) // 2
    bee_y = top + (area_h - new_h) // 2
    card.alpha_composite(bee_resized, (bee_x, bee_y))
    
    # Name text
    font_size = int(plate_h * 0.45)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/SF-Pro-Display-Bold.otf", font_size)
        except:
            font = ImageFont.load_default()
    
    # Get text size using textbbox
    bbox = draw.textbbox((0, 0), display_name, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    text_x = plate_rect[0] + (plate_rect[2] - plate_rect[0] - text_w) // 2
    text_y = plate_rect[1] + (plate_rect[3] - plate_rect[1] - text_h) // 2
    
    draw.text((text_x, text_y), display_name, font=font, fill=TEXT_DARK)
    
    return card

# =========================
# MAIN
# =========================

def main():
    """Generate App Store avatar cards"""
    print("=" * 70)
    print("🎨 AVATAR SCREENSHOT GENERATOR FOR APP STORE")
    print("=" * 70)
    print(f"\n📂 Input:  {GLB_DIR}")
    print(f"📂 Output: {OUTPUT_DIR}")
    print(f"📐 Size:   {CARD_SIZE}x{CARD_SIZE}px\n")
    
    glb_files = sorted([p for p in GLB_DIR.iterdir() if p.suffix.lower() == ".glb"])
    
    if not glb_files:
        print(f"❌ No .glb files found in {GLB_DIR}")
        return
    
    print(f"✅ Found {len(glb_files)} GLB files\n")
    
    success_count = 0
    failed_count = 0
    
    for i, glb_path in enumerate(glb_files, 1):
        display_name = get_display_name(glb_path.name)
        slug = slug_from_filename(glb_path.name)
        
        print(f"[{i}/{len(glb_files)}] {glb_path.name}")
        print(f"      → {display_name}")
        
        try:
            bee_img = render_glb_to_image(glb_path, size=CARD_SIZE)
            card_img = compose_app_store_card(bee_img, display_name, size=CARD_SIZE)
            
            out_path = OUTPUT_DIR / f"{slug}.png"
            card_img.save(out_path, format="PNG", optimize=True)
            print(f"      ✅ Saved: {out_path.name}")
            success_count += 1
            
        except Exception as e:
            print(f"      ❌ Failed: {e}")
            failed_count += 1
        
        print()
    
    print("=" * 70)
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed:  {failed_count}")
    print(f"📁 Output:  {OUTPUT_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    if not DEPS_OK:
        sys.exit(1)
    main()
