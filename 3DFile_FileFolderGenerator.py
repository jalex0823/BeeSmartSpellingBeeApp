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
        mesh = trimesh.load_mesh(str(obj_path), process=False)
        if isinstance(mesh, trimesh.Scene):
            mesh = trimesh.util.concatenate(mesh.dump())

        scene = pyrender.Scene(
            bg_color=BACKGROUND_COLOR,
            ambient_light=[0.35, 0.35, 0.35]
        )
        mesh_node = pyrender.Mesh.from_trimesh(mesh, smooth=True)
        scene.add(mesh_node)

        # Camera placement
        bounds = mesh.bounds
        center = bounds.mean(axis=0)
        extents = mesh.extents
        radius = np.linalg.norm(extents) * 0.5
        distance = max(0.1, radius * CAMERA_DISTANCE_MULT)

        cam = pyrender.PerspectiveCamera(yfov=np.pi / 4.0)
        cam_pose = np.eye(4)
        cam_pose[:3, 3] = center + np.array([0.0, 0.0, distance])
        forward = (center - cam_pose[:3, 3]); forward /= (np.linalg.norm(forward) + 1e-7)
        up = np.array([0.0, 1.0, 0.0])
        right = np.cross(up, forward); right /= (np.linalg.norm(right) + 1e-7)
        up = np.cross(forward, right); up /= (np.linalg.norm(up) + 1e-7)
        cam_pose[:3, :3] = np.vstack([right, up, forward]).T
        scene.add(cam, pose=cam_pose)

        key = pyrender.DirectionalLight(color=np.ones(3), intensity=LIGHT_INTENSITY)
        fill = pyrender.DirectionalLight(color=np.ones(3), intensity=LIGHT_INTENSITY * 0.6)
        scene.add(key, pose=cam_pose)
        fill_pose = np.array(cam_pose); fill_pose[:3, 3] = center + np.array([distance, distance, distance])
        scene.add(fill, pose=fill_pose)

        r = pyrender.OffscreenRenderer(*RENDER_SIZE)
        color, _ = r.render(scene)
        r.delete()

        img = Image.fromarray(color).convert("RGBA")
        img.save(thumb_path)
        print(f"📸 Thumbnail: {thumb_path}")
    except Exception as e:
        print(f"⚠️ Thumbnail render failed for {obj_path.name}: {e}")

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
