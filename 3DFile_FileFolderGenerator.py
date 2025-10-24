import os
import re
import sys
import csv
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np

# Rendering deps
import trimesh
import pyrender
from PIL import Image
import os

# Try to use pyglet platform on Windows which is more reliable
os.environ['PYOPENGL_PLATFORM'] = 'pyglet'

# ========================= USER SETTINGS =========================
# Source parent with one or many Meshy export folders (unzipped)
INPUT_ROOT  = r"C:\Users\Jeff\Downloads\Meshy_Imports"
# Destination parent where cleaned folders are created
OUTPUT_ROOT = r"C:\Users\Jeff\Downloads\Meshy_Cleaned"

# If True, process all nested subfolders under INPUT_ROOT; else only immediate children
RECURSIVE = True

# Ask interactively for a name for each folder (press Enter to accept default)
ASK = True

# Optional hard-coded overrides here: {"exact-folder-name": "DesiredOutputName", ...}
# These override auto-detect and skip prompting for matches.
OVERRIDES: Dict[str, str] = {
    # "Explorer_Bee_1023150321_texture_obj": "AstroBee"
}

# Optional overrides file (placed in INPUT_ROOT). If present, it overrides auto-detect.
# Supported: overrides.json  OR  overrides.csv  (two columns: source_folder,output_name)
OVERRIDES_JSON = "overrides.json"
OVERRIDES_CSV  = "overrides.csv"

# Thumbnail render settings
RENDER_SIZE = (640, 640)                  # width, height
BACKGROUND_COLOR = (0, 0, 0, 0)           # RGBA — transparent
CAMERA_DISTANCE_MULT = 2.2                # farther = smaller object
LIGHT_INTENSITY = 6.0
# =================================================================

# Regex to strip Meshy-style numeric suffixes (e.g., _1023150321)
NUM_SUFFIX = re.compile(r"(?:[_-]\d{6,})+$", re.IGNORECASE)
# Split on underscores/dashes, collapse multi-separators
SEP_SPLIT = re.compile(r"[_\-]+")

# Any trailing tokens you do NOT want to define the base name
DROP_TRAILING_TOKENS = {
    "texture", "tex", "mat", "material", "albedo", "basecolor", "base_color", "obj", "mtl"
}

# Preferred tags for picking the "primary" texture
PRIMARY_TAGS = [
    "basecolor", "base_color", "albedo", "color", "diffuse"
]

# Optional secondary texture tags (will be preserved as CamelCase suffix)
SECONDARY_TAGS = [
    "normal", "nrm", "roughness", "metallic", "metalness", "specular",
    "gloss", "glossiness", "ao", "ambientocclusion", "ambient_occlusion",
    "emissive", "emission", "height", "displacement", "opacity", "alpha"
]

IMG_EXTS = {".png", ".jpg", ".jpeg"}

# --------------------------- Helpers -----------------------------

def camel_no_underscores(s: str) -> str:
    """
    Remove underscores/dashes and convert to compact CamelCase-ish.
    'Explorer_Bee' -> 'ExplorerBee' ; 'robo-bee' -> 'RoboBee'
    """
    parts = [p for p in SEP_SPLIT.split(s) if p]
    if not parts:
        return s.replace("_", "").replace("-", "")
    return "".join(p[:1].upper() + p[1:] for p in parts)

def clean_base_from_stem(stem: str) -> str:
    """Derive a clean base from a filename stem:
       - strip trailing numeric suffixes
       - drop trailing tokens like 'texture'
       - remove underscores/dashes and camelize
    """
    stem = NUM_SUFFIX.sub("", stem)
    parts = [p for p in SEP_SPLIT.split(stem) if p]
    # Drop trailing junk tokens
    while parts and parts[-1].lower() in DROP_TRAILING_TOKENS:
        parts.pop()
    if not parts:
        parts = [stem]
    cleaned = camel_no_underscores("_".join(parts))
    return cleaned or "MeshyModel"

def detect_files(src_folder: Path) -> Tuple[Optional[Path], Optional[Path], List[Path]]:
    """Find the primary OBJ, optional MTL, and all images in a folder."""
    obj = next((p for p in src_folder.glob("*.obj")), None)
    mtl = next((p for p in src_folder.glob("*.mtl")), None)
    imgs = [p for p in src_folder.iterdir() if p.is_file() and p.suffix.lower() in IMG_EXTS]
    return obj, mtl, imgs

def pick_primary_texture(imgs: List[Path], base_hint: str) -> Optional[Path]:
    """Pick the best candidate as the main color/albedo texture."""
    if not imgs:
        return None
    # Prefer files that contain PRIMARY_TAGS
    by_score = []
    for img in imgs:
        low = img.stem.lower()
        score = 0
        for t in PRIMARY_TAGS:
            if t in low:
                score += 10
        if base_hint.lower() in low:
            score += 1
        by_score.append((score, img))
    by_score.sort(key=lambda x: x[0], reverse=True)
    return by_score[0][1] if by_score else imgs[0]

def suffix_from_name(stem: str) -> str:
    """Return CamelCase suffix based on known tags, otherwise empty."""
    low = stem.lower()
    for tag in PRIMARY_TAGS + SECONDARY_TAGS:
        if tag in low:
            return camel_no_underscores(tag)
    return ""

def copy_and_rename(
    obj: Optional[Path],
    mtl: Optional[Path],
    imgs: List[Path],
    out_folder: Path,
    base: str
) -> Tuple[Optional[Path], Optional[Path], List[Path], Optional[Path]]:
    """
    Copy and rename files into out_folder with clean names:
      - base.obj, base.mtl, base.png (primary), base<CapSuffix>.png for others
    Returns (obj_out, mtl_out, all_img_outs, primary_img_out)
    """
    out_obj = out_mtl = None
    out_imgs: List[Path] = []
    primary_out = None

    if obj:
        out_obj = out_folder / f"{base}.obj"
        shutil.copy2(obj, out_obj)

    if mtl:
        out_mtl = out_folder / f"{base}.mtl"
        shutil.copy2(mtl, out_mtl)

    if imgs:
        primary = pick_primary_texture(imgs, base)
        for img in imgs:
            ext = img.suffix.lower()
            if img == primary:
                primary_out = out_folder / f"{base}{ext}"
                shutil.copy2(img, primary_out)
                out_imgs.append(primary_out)
            else:
                suf = suffix_from_name(img.stem)
                out_path = out_folder / (f"{base}{suf}{ext}" if suf else f"{base}{ext}")
                # Avoid collision with the primary
                if primary_out and out_path.name == primary_out.name:
                    out_path = out_folder / f"{base}Tex{ext}"
                shutil.copy2(img, out_path)
                out_imgs.append(out_path)

    return out_obj, out_mtl, out_imgs, primary_out

def patch_obj(obj_path: Path, new_mtl_name: Optional[str]):
    """Ensure OBJ references the correct MTL filename."""
    if not obj_path or not obj_path.exists():
        return
    try:
        lines = obj_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return
    out, found = [], False
    for line in lines:
        if line.lower().startswith("mtllib ") and new_mtl_name:
            out.append(f"mtllib {new_mtl_name}")
            found = True
        else:
            out.append(line)
    if new_mtl_name and not found:
        out.insert(0, f"mtllib {new_mtl_name}")
    obj_path.write_text("\n".join(out), encoding="utf-8")

def patch_mtl(mtl_path: Path, images: List[Path], primary_img: Optional[Path]):
    """Update map_* references in MTL to renamed/clean images."""
    if not mtl_path or not mtl_path.exists():
        return
    try:
        lines = mtl_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return

    by_tag: Dict[str, str] = {}
    for img in images:
        tag = suffix_from_name(img.stem)
        if tag:
            by_tag[tag.lower()] = img.name

    def choose_texture(orig_name: str) -> str:
        tag = suffix_from_name(Path(orig_name).stem).lower()
        if tag and tag in by_tag:
            return by_tag[tag]
        if primary_img:
            return primary_img.name
        return images[0].name if images else orig_name

    out = []
    for line in lines:
        if re.match(r"(?i)^\s*map_[a-z]+\s+.+", line):
            parts = line.split()
            parts[-1] = choose_texture(parts[-1])
            out.append(" ".join(parts))
        else:
            out.append(line)

    mtl_path.write_text("\n".join(out), encoding="utf-8")

def render_thumbnail_transparent(obj_path: Path, thumb_path: Path):
    """Render OBJ to a transparent PNG using pyrender OffscreenRenderer."""
    try:
        print(f"🔍 Loading mesh: {obj_path}")
        mesh = trimesh.load_mesh(str(obj_path), process=False)
        
        # Debug mesh loading
        if isinstance(mesh, trimesh.Scene):
            print(f"   Scene loaded with {len(mesh.geometry)} geometries")
            mesh = trimesh.util.concatenate(mesh.dump())
        
        print(f"   Mesh bounds: {mesh.bounds}")
        print(f"   Mesh extents: {mesh.extents}")
        print(f"   Vertex count: {len(mesh.vertices)}")
        print(f"   Face count: {len(mesh.faces)}")
        
        # Check if mesh is empty or degenerate
        if len(mesh.vertices) == 0:
            print("⚠️ Mesh has no vertices!")
            return
        if len(mesh.faces) == 0:
            print("⚠️ Mesh has no faces!")
            return

        scene = pyrender.Scene(
            bg_color=BACKGROUND_COLOR,
            ambient_light=[0.35, 0.35, 0.35]
        )
        
        # Try to create mesh node with error handling
        try:
            mesh_node = pyrender.Mesh.from_trimesh(mesh, smooth=True)
            scene.add(mesh_node)
            print("   ✅ Mesh added to scene")
        except Exception as mesh_err:
            print(f"   ⚠️ Failed to create mesh node: {mesh_err}")
            # Try without smoothing
            mesh_node = pyrender.Mesh.from_trimesh(mesh, smooth=False)
            scene.add(mesh_node)
            print("   ✅ Mesh added to scene (without smoothing)")

        # Camera placement with more debugging
        bounds = mesh.bounds
        center = bounds.mean(axis=0)
        extents = mesh.extents
        radius = np.linalg.norm(extents) * 0.5
        distance = max(0.1, radius * CAMERA_DISTANCE_MULT)
        
        print(f"   Camera center: {center}")
        print(f"   Camera distance: {distance}")
        print(f"   Mesh radius: {radius}")

        cam = pyrender.PerspectiveCamera(yfov=np.pi / 4.0)
        cam_pose = np.eye(4)
        cam_pose[:3, 3] = center + np.array([0.0, 0.0, distance])
        
        # Simplified camera orientation - just look at center from positive Z
        forward = (center - cam_pose[:3, 3])
        forward_norm = np.linalg.norm(forward)
        if forward_norm > 1e-7:
            forward /= forward_norm
        else:
            forward = np.array([0.0, 0.0, -1.0])
            
        up = np.array([0.0, 1.0, 0.0])
        right = np.cross(up, forward)
        right_norm = np.linalg.norm(right)
        if right_norm > 1e-7:
            right /= right_norm
        else:
            right = np.array([1.0, 0.0, 0.0])
            
        up = np.cross(forward, right)
        up_norm = np.linalg.norm(up)
        if up_norm > 1e-7:
            up /= up_norm
            
        cam_pose[:3, :3] = np.vstack([right, up, forward]).T
        scene.add(cam, pose=cam_pose)
        print("   ✅ Camera added to scene")

        # Add stronger lighting
        key = pyrender.DirectionalLight(color=np.ones(3), intensity=LIGHT_INTENSITY)
        fill = pyrender.DirectionalLight(color=np.ones(3), intensity=LIGHT_INTENSITY * 0.6)
        scene.add(key, pose=cam_pose)
        
        # Position fill light differently
        fill_pose = np.eye(4)
        fill_pose[:3, 3] = center + np.array([distance * 0.5, distance * 0.5, distance * 0.5])
        scene.add(fill, pose=fill_pose)
        print("   ✅ Lights added to scene")

        # Try different renderer flags
        try:
            r = pyrender.OffscreenRenderer(*RENDER_SIZE)
            print(f"   ✅ Renderer created: {RENDER_SIZE}")
            
            color, depth = r.render(scene)
            print(f"   Rendered color shape: {color.shape}, dtype: {color.dtype}")
            print(f"   Color range: min={color.min()}, max={color.max()}")
            
            # Check if we actually rendered anything
            if color.max() == 0:
                print("   ⚠️ Rendered image is completely black!")
                # Try with a white background for debugging
                scene.bg_color = [1.0, 1.0, 1.0, 1.0]
                color, depth = r.render(scene)
                print(f"   White background render - Color range: min={color.min()}, max={color.max()}")
                scene.bg_color = BACKGROUND_COLOR  # Restore transparent background
                
            r.delete()

            # Convert and save with more debugging
            img = Image.fromarray(color)
            print(f"   PIL Image mode: {img.mode}, size: {img.size}")
            
            if img.mode != "RGBA":
                img = img.convert("RGBA")
                print(f"   Converted to RGBA")
            
            # Save with debugging
            img.save(thumb_path)
            file_size = thumb_path.stat().st_size if thumb_path.exists() else 0
            print(f"📸 Thumbnail saved: {thumb_path} ({file_size} bytes)")
            
        except Exception as render_err:
            print(f"   ⚠️ Rendering failed: {render_err}")
            raise
            
    except Exception as e:
        print(f"⚠️ Thumbnail render failed for {obj_path.name}: {e}")
        import traceback
        traceback.print_exc()

def test_rendering_simple():
    """Test rendering with a simple generated mesh to verify the pipeline works."""
    platforms_to_try = [
        ('pyglet', 'Standard Pyglet'),
        ('win32', 'Windows Native'),
        (None, 'Default Platform')
    ]
    
    for platform, platform_name in platforms_to_try:
        try:
            print(f"🧪 Testing rendering with {platform_name}...")
            
            if platform:
                os.environ['PYOPENGL_PLATFORM'] = platform
            elif 'PYOPENGL_PLATFORM' in os.environ:
                del os.environ['PYOPENGL_PLATFORM']
            
            # Create a simple test mesh (cube)
            box = trimesh.creation.box(extents=[1, 1, 1])
            
            scene = pyrender.Scene(
                bg_color=[0, 0, 0, 0],  # Transparent
                ambient_light=[0.4, 0.4, 0.4]
            )
            
            mesh_node = pyrender.Mesh.from_trimesh(box, smooth=False)
            scene.add(mesh_node)
            
            # Simple camera setup
            cam = pyrender.PerspectiveCamera(yfov=np.pi / 4.0)
            cam_pose = np.eye(4)
            cam_pose[:3, 3] = [0, 0, 3]  # Move camera back 3 units
            scene.add(cam, pose=cam_pose)
            
            # Add light
            light = pyrender.DirectionalLight(color=np.ones(3), intensity=3.0)
            scene.add(light, pose=cam_pose)
            
            # Render
            r = pyrender.OffscreenRenderer(640, 640)
            color, depth = r.render(scene)
            r.delete()
            
            # Save test image
            test_path = Path("test_render.png")
            img = Image.fromarray(color).convert("RGBA")
            img.save(test_path)
            
            print(f"✅ Test render saved to: {test_path}")
            print(f"   Image stats: {color.shape}, min={color.min()}, max={color.max()}")
            
            # Verify the image isn't blank
            if color.max() > 0:
                print(f"✅ {platform_name} works! Continuing with this platform.")
                return True
            else:
                print(f"⚠️ {platform_name} produced blank image, trying next...")
                
        except Exception as e:
            print(f"❌ {platform_name} failed: {e}")
            continue
    
    print("❌ All platforms failed. Install Mesa or check graphics drivers.")
    return False

# ---------------------- Overrides / Naming -----------------------

def load_overrides_file(in_root: Path) -> Dict[str, str]:
    out: Dict[str, str] = {}
    j = in_root / OVERRIDES_JSON
    c = in_root / OVERRIDES_CSV
    if j.exists():
        try:
            data = json.loads(j.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                out.update(data)
        except Exception:
            pass
    if c.exists():
        try:
            with c.open("r", encoding="utf-8", newline="") as fh:
                rdr = csv.reader(fh)
                for row in rdr:
                    if len(row) >= 2:
                        out[row[0].strip()] = row[1].strip()
        except Exception:
            pass
    return out

def choose_output_name_for_folder(folder: Path, auto_base: str, overrides: Dict[str, str]) -> str:
    key = folder.name
    if key in overrides:
        return camel_no_underscores(overrides[key])
    if ASK:
        print(f"\nSource folder: {folder}")
        user = input(f"Output name? (Enter for '{auto_base}'): ").strip()
        if user:
            return camel_no_underscores(user)
    return auto_base

# --------------------- Main processing flow ----------------------

def process_model_folder(src_folder: Path, out_parent: Path, overrides: Dict[str, str]):
    obj, mtl, imgs = detect_files(src_folder)
    if not obj and not mtl and not imgs:
        return  # nothing to do

    # Decide default base (prefer OBJ stem, else MTL, else any image)
    base_source = obj or mtl or (imgs[0] if imgs else None)
    auto_base = clean_base_from_stem(base_source.stem if base_source else src_folder.name)

    base = choose_output_name_for_folder(src_folder, auto_base, overrides)

    out_folder = out_parent / base
    out_folder.mkdir(parents=True, exist_ok=True)

    out_obj, out_mtl, out_imgs, primary_img = copy_and_rename(obj, mtl, imgs, out_folder, base)

    if out_obj:
        patch_obj(out_obj, out_mtl.name if out_mtl else None)
    if out_mtl:
        patch_mtl(out_mtl, out_imgs, primary_img)

    if out_obj and out_obj.exists():
        thumb_path = out_folder / f"{base}!.png"
        render_thumbnail_transparent(out_obj, thumb_path)

def iter_source_folders(root: Path, recursive: bool) -> List[Path]:
    if not recursive:
        return [p for p in root.iterdir() if p.is_dir()]
    return [p for p in root.rglob("*") if p.is_dir()]

def main():
    # Test rendering first
    print("🔧 Testing rendering setup...")
    if not test_rendering_simple():
        print("❌ Cannot establish working OpenGL context for rendering.")
        print("💡 Try installing: pip install PyOpenGL-accelerate")
        print("💡 Or try updating your graphics drivers.")
        return
    
    in_root = Path(INPUT_ROOT).resolve()
    out_root = Path(OUTPUT_ROOT).resolve()
    if not in_root.exists():
        print(f"❌ INPUT_ROOT not found: {in_root}")
        sys.exit(1)
    out_root.mkdir(parents=True, exist_ok=True)

    # Merge override sources: file(s) + in-script dict
    file_overrides = load_overrides_file(in_root)
    merged_overrides = {**file_overrides, **OVERRIDES}

    folders = iter_source_folders(in_root, RECURSIVE)
    count = 0
    for folder in folders:
        has_candidate = any(folder.glob("*.obj")) or any(folder.glob("*.mtl")) or any(
            p.suffix.lower() in IMG_EXTS for p in folder.iterdir() if p.is_file()
        )
        if not has_candidate:
            continue
        process_model_folder(folder, out_root, merged_overrides)
        count += 1

    print(f"\n✅ Done. Processed {count} folder(s).\nOutput → {out_root}")

if __name__ == "__main__":
    main()
