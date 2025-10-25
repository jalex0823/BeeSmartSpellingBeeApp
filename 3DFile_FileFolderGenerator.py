import os
import re
import sys
import csv
import json
import shutil
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

# Rendering deps
import trimesh
import pyrender
from PIL import Image
import os

# Try to use pyglet platform on Windows which is more reliable
os.environ['PYOPENGL_PLATFORM'] = 'pyglet'

class ZipProcessorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("3D Model ZIP Processor")
        self.root.geometry("800x600")
        self.selected_zip_files = []
        self.output_folder = None
        self.setup_gui()
    
    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="3D Model ZIP Processor", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # ZIP file selection
        zip_frame = ttk.LabelFrame(main_frame, text="1. Select ZIP Files", padding="10")
        zip_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(zip_frame, text="📁 Select ZIP Files", 
                  command=self.select_zip_files).grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(zip_frame, text="🗑️ Clear List", 
                  command=self.clear_zip_list).grid(row=0, column=1)
        
        # List of selected files
        self.zip_listbox = tk.Listbox(zip_frame, height=6)
        self.zip_listbox.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Output folder selection
        output_frame = ttk.LabelFrame(main_frame, text="2. Output Folder", padding="10")
        output_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(output_frame, text="📂 Select Output Folder", 
                  command=self.select_output_folder).grid(row=0, column=0, padx=(0, 10))
        
        self.output_label = ttk.Label(output_frame, text="No folder selected")
        self.output_label.grid(row=0, column=1)
        
        # Process button
        self.process_btn = ttk.Button(main_frame, text="🚀 Process ZIP Files", 
                                     command=self.process_files, state='disabled')
        self.process_btn.grid(row=3, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Log output
        log_frame = ttk.LabelFrame(main_frame, text="Progress Log", padding="10")
        log_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.log_text = ScrolledText(log_frame, height=10, state='disabled')
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        zip_frame.columnconfigure(0, weight=1)
        output_frame.columnconfigure(1, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
    
    def log(self, message):
        """Add message to log output."""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.root.update()
    
    def select_zip_files(self):
        """Open dialog to select multiple ZIP files."""
        zip_files = filedialog.askopenfilenames(
            title="Select ZIP files containing 3D models",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")],
            initialdir=str(Path.home() / "Downloads")
        )
        
        if zip_files:
            self.selected_zip_files.extend(zip_files)
            self.update_zip_list()
            self.update_process_button()
    
    def clear_zip_list(self):
        """Clear the list of selected ZIP files."""
        self.selected_zip_files.clear()
        self.update_zip_list()
        self.update_process_button()
    
    def update_zip_list(self):
        """Update the listbox showing selected ZIP files."""
        self.zip_listbox.delete(0, tk.END)
        for zip_file in self.selected_zip_files:
            self.zip_listbox.insert(tk.END, Path(zip_file).name)
    
    def select_output_folder(self):
        """Select output folder."""
        folder = filedialog.askdirectory(
            title="Select output folder for processed models",
            initialdir=str(Path.home() / "Downloads")
        )
        
        if folder:
            self.output_folder = Path(folder)
            self.output_label.config(text=f"Output: {self.output_folder.name}")
            self.update_process_button()
    
    def update_process_button(self):
        """Enable/disable process button based on selections."""
        if self.selected_zip_files and self.output_folder:
            self.process_btn.config(state='normal')
        else:
            self.process_btn.config(state='disabled')
    
    def extract_zip_file(self, zip_path: Path, extract_to: Path) -> Optional[Path]:
        """Extract a ZIP file and return the extraction folder."""
        try:
            self.log(f"📦 Extracting: {zip_path.name}")
            
            # Create extraction folder
            extract_folder = extract_to / zip_path.stem
            extract_folder.mkdir(parents=True, exist_ok=True)
            
            # Extract ZIP
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_folder)
            
            self.log(f"✅ Extracted to: {extract_folder.name}")
            return extract_folder
            
        except Exception as e:
            self.log(f"❌ Failed to extract {zip_path.name}: {e}")
            return None
    
    def process_files(self):
        """Process all selected ZIP files."""
        if not self.selected_zip_files or not self.output_folder:
            messagebox.showerror("Error", "Please select ZIP files and output folder")
            return
        
        try:
            self.process_btn.config(state='disabled')
            self.progress.start()
            
            self.log("🚀 Starting processing...")
            
            # Create temporary extraction folder
            temp_extract = self.output_folder / "temp_extract"
            temp_extract.mkdir(parents=True, exist_ok=True)
            
            processed_count = 0
            
            for zip_file in self.selected_zip_files:
                zip_path = Path(zip_file)
                
                # Extract ZIP file
                extract_folder = self.extract_zip_file(zip_path, temp_extract)
                if not extract_folder:
                    continue
                
                # Process the extracted content
                self.process_extracted_folder(extract_folder)
                processed_count += 1
            
            # Clean up temporary folder
            if temp_extract.exists():
                shutil.rmtree(temp_extract)
                self.log("🧹 Cleaned up temporary files")
            
            self.progress.stop()
            self.process_btn.config(state='normal')
            
            self.log(f"✅ COMPLETED! Processed {processed_count} ZIP files")
            self.log(f"📂 Output folder: {self.output_folder}")
            
            # Ask to open output folder
            if messagebox.askyesno("Complete", f"Processing complete!\n\nProcessed {processed_count} ZIP files.\n\nOpen output folder?"):
                try:
                    import subprocess
                    subprocess.run(['explorer', str(self.output_folder)], check=True)
                except:
                    pass
            
        except Exception as e:
            self.progress.stop()
            self.process_btn.config(state='normal')
            self.log(f"❌ Error during processing: {e}")
            messagebox.showerror("Error", f"Processing failed: {e}")
    
    def process_extracted_folder(self, extract_folder: Path):
        """Process an extracted folder containing 3D models."""
        self.log(f"🔍 Processing: {extract_folder.name}")
        
        # Find all subfolders that might contain 3D models
        for folder in extract_folder.rglob("*"):
            if folder.is_dir():
                # Check if this folder contains 3D model files
                has_obj = any(folder.glob("*.obj"))
                has_mtl = any(folder.glob("*.mtl"))
                has_images = any(p.suffix.lower() in IMG_EXTS for p in folder.iterdir() if p.is_file())
                
                if has_obj or has_mtl or has_images:
                    self.log(f"   📁 Found model folder: {folder.name}")
                    
                    # Load override settings
                    file_overrides = load_overrides_file(extract_folder)
                    merged_overrides = {**file_overrides, **OVERRIDES}
                    
                    # Process this model folder
                    process_model_folder(folder, self.output_folder, merged_overrides)
    
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()

def select_source_folder() -> Optional[Path]:
    """Open a dialog to select the source folder containing 3D models."""
    try:
        print("🔄 Opening folder selection dialog...")
        print("   (Dialog may appear behind other windows - check your taskbar)")
        
        # Hide the main tkinter window
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)  # Bring to front
        root.lift()
        root.focus_force()
        
        # Open folder selection dialog
        folder_path = filedialog.askdirectory(
            title="Select Source Folder (containing OBJ/3D model folders)",
            initialdir=str(Path.home() / "Downloads"),
            parent=root
        )
        
        root.destroy()
        
        if folder_path:
            print(f"✅ Selected: {folder_path}")
            return Path(folder_path).resolve()
        else:
            print("❌ No folder selected")
            return None
    except Exception as e:
        print(f"⚠️ Error opening folder dialog: {e}")
        print("   Falling back to manual input...")
        return None

def select_output_folder(default_name: str = "Meshy_Cleaned") -> Optional[Path]:
    """Open a dialog to select the output folder."""
    try:
        root = tk.Tk()
        root.withdraw()
        
        # Suggest a default output folder
        default_path = Path.home() / "Downloads" / default_name
        
        folder_path = filedialog.askdirectory(
            title="Select Output Folder (where cleaned models will be saved)",
            initialdir=str(default_path.parent)
        )
        
        root.destroy()
        
        if folder_path:
            return Path(folder_path).resolve()
        return None
    except Exception as e:
        print(f"⚠️ Error opening folder dialog: {e}")
        return None

def get_folder_interactively(prompt: str, default_path: str) -> Path:
    """Get folder path either through GUI or command line input."""
    print(f"\n{prompt}")
    print(f"Default: {default_path}")
    
    choice = input("Choose method: (G)UI dialog, (D)efault, or (T)ype path [G]: ").strip().upper()
    
    if choice == "D":
        return Path(default_path).resolve()
    elif choice == "T":
        while True:
            user_path = input("Enter folder path: ").strip().strip('"')
            if user_path:
                path = Path(user_path).resolve()
                if path.exists() or choice == "T":  # Allow non-existing for output
                    return path
                else:
                    print(f"❌ Path doesn't exist: {path}")
            else:
                print("❌ Please enter a valid path")
    else:  # Default to GUI
        if "Source" in prompt:
            folder = select_source_folder()
        else:
            folder = select_output_folder()
        
        if folder:
            return folder
        else:
            print("No folder selected, using default...")
            return Path(default_path).resolve()

# ========================= USER SETTINGS =========================
# Source parent with one or many Meshy export folders (unzipped)
# NOTE: When running the script, you'll be prompted to select folders interactively
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
        print("🔄 Trying matplotlib fallback...")
        render_thumbnail_matplotlib_fallback(obj_path, thumb_path)

def render_thumbnail_matplotlib_fallback(obj_path: Path, thumb_path: Path):
    """Fallback rendering using matplotlib for systems without proper OpenGL."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        
        print(f"🔄 Using matplotlib fallback for: {obj_path}")
        
        # Load mesh
        mesh = trimesh.load_mesh(str(obj_path), process=False)
        if isinstance(mesh, trimesh.Scene):
            mesh = trimesh.util.concatenate(mesh.dump())
        
        if len(mesh.vertices) == 0:
            print("⚠️ Mesh has no vertices!")
            create_placeholder_thumbnail(obj_path, thumb_path)
            return
            
        # Create a simple 2D projection view
        fig, ax = plt.subplots(figsize=(8, 8), facecolor='none')
        ax.set_facecolor('none')
        
        # Project 3D vertices to 2D (simple orthographic projection)
        vertices = mesh.vertices
        
        # Use X,Y coordinates (top view) or rotate for isometric
        x_coords = vertices[:, 0]
        y_coords = vertices[:, 1]
        
        # Draw edges by connecting face vertices
        faces = mesh.faces
        for face in faces[:min(200, len(faces))]:  # Limit for performance
            face_verts = vertices[face]
            # Draw triangle edges
            for i in range(3):
                start = face_verts[i]
                end = face_verts[(i + 1) % 3]
                ax.plot([start[0], end[0]], [start[1], end[1]], 
                       'b-', alpha=0.6, linewidth=0.5)
        
        # Set equal aspect and remove axes
        ax.set_aspect('equal')
        ax.set_axis_off()
        
        # Set limits based on mesh bounds
        bounds = mesh.bounds
        margin = mesh.extents.max() * 0.1
        ax.set_xlim(bounds[0, 0] - margin, bounds[1, 0] + margin)
        ax.set_ylim(bounds[0, 1] - margin, bounds[1, 1] + margin)
        
        # Save with transparent background
        plt.savefig(thumb_path, transparent=True, bbox_inches='tight', 
                   dpi=100, format='png', facecolor='none', 
                   edgecolor='none', pad_inches=0)
        plt.close(fig)
        
        print(f"📸 Matplotlib wireframe thumbnail: {thumb_path}")
        
    except Exception as e:
        print(f"⚠️ Matplotlib fallback failed: {e}")
        # Create a simple placeholder image
        create_placeholder_thumbnail(obj_path, thumb_path)

def create_placeholder_thumbnail(obj_path: Path, thumb_path: Path):
    """Create a simple placeholder thumbnail when rendering fails."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple placeholder
        background_color = (240, 240, 240, 128)
        img = Image.new('RGBA', RENDER_SIZE, background_color)
        draw = ImageDraw.Draw(img)
        
        # Draw a simple 3D box icon
        w, h = RENDER_SIZE
        cx, cy = w//2, h//2
        size = min(w, h) // 4
        
        # Draw isometric cube
        points = [
            (cx - size, cy), (cx, cy - size//2), (cx + size, cy), (cx, cy + size//2)
        ]
        draw.polygon(points, fill=(100, 150, 200, 180), outline=(50, 100, 150, 255))
        
        # Add text
        text = obj_path.stem[:20]  # Truncate if too long
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
            
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        draw.text((cx - text_w//2, cy + size + 20), text, 
                 fill=(50, 50, 50, 255), font=font)
        
        img.save(thumb_path)
        print(f"📸 Placeholder thumbnail: {thumb_path}")
        
    except Exception as e:
        print(f"⚠️ Even placeholder creation failed: {e}")

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

class Dark3DProcessorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("3D Model Processor")
        self.root.geometry("600x500")
        self.root.configure(bg='#2b2b2b')  # Dark background
        
        self.selected_zip_files = []
        self.converted_folders = []
        self.setup_dark_gui()
    
    def setup_dark_gui(self):
        # Configure dark theme colors
        bg_color = '#2b2b2b'
        fg_color = '#ffffff'
        button_color = '#404040'
        selected_color = '#0078d4'
        
        # Title
        title_label = tk.Label(self.root, text="3D Model Processor", 
                              font=('Arial', 18, 'bold'),
                              bg=bg_color, fg=fg_color)
        title_label.pack(pady=20)
        
        # Selected files frame
        files_frame = tk.LabelFrame(self.root, text="Selected ZIP Files", 
                                   bg=bg_color, fg=fg_color,
                                   font=('Arial', 12, 'bold'))
        files_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Listbox for showing selected files
        self.files_listbox = tk.Listbox(files_frame, height=8,
                                       bg='#1e1e1e', fg=fg_color,
                                       selectbackground=selected_color,
                                       font=('Consolas', 10))
        self.files_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Progress log frame
        progress_frame = tk.LabelFrame(self.root, text="Processing Progress", 
                                      bg=bg_color, fg=fg_color,
                                      font=('Arial', 12, 'bold'))
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollable text widget for progress log
        progress_scroll = tk.Scrollbar(progress_frame)
        progress_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.progress_text = tk.Text(progress_frame, height=10,
                                     bg='#1e1e1e', fg='#00ff00',  # Green text for terminal look
                                     font=('Consolas', 9),
                                     wrap=tk.WORD,
                                     yscrollcommand=progress_scroll.set)
        self.progress_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        progress_scroll.config(command=self.progress_text.yview)
        
        # Configure text tags for colored output
        self.progress_text.tag_configure('success', foreground='#00ff00')
        self.progress_text.tag_configure('processing', foreground='#00bfff')
        self.progress_text.tag_configure('error', foreground='#ff4444')
        self.progress_text.tag_configure('info', foreground='#ffff00')
        self.progress_text.tag_configure('complete', foreground='#00ff00', font=('Consolas', 9, 'bold'))
        
        # Buttons frame
        button_frame = tk.Frame(self.root, bg=bg_color)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Select ZIP Files button
        self.select_btn = tk.Button(button_frame, text="📁 Select ZIP Files",
                                   command=self.select_zip_files,
                                   bg=button_color, fg=fg_color,
                                   font=('Arial', 12, 'bold'),
                                   relief='raised', bd=2)
        self.select_btn.pack(side=tk.LEFT, padx=(0, 10), pady=5, fill=tk.X, expand=True)
        
        # Convert button
        self.convert_btn = tk.Button(button_frame, text="🔄 Convert Files",
                                    command=self.convert_files,
                                    bg=button_color, fg=fg_color,
                                    font=('Arial', 12, 'bold'),
                                    relief='raised', bd=2)
        self.convert_btn.pack(side=tk.LEFT, padx=(0, 10), pady=5, fill=tk.X, expand=True)
        
        # Create PNG button
        self.png_btn = tk.Button(button_frame, text="🖼️ Create PNG!",
                                command=self.create_png,
                                bg=button_color, fg=fg_color,
                                font=('Arial', 12, 'bold'),
                                relief='raised', bd=2)
        self.png_btn.pack(side=tk.LEFT, pady=5, fill=tk.X, expand=True)
        
        # Status bar
        self.status_label = tk.Label(self.root, text="Ready - Select ZIP files to begin",
                                    bg='#1e1e1e', fg=fg_color,
                                    font=('Arial', 10),
                                    relief='sunken', bd=1)
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=10)
    
    def log_progress(self, message, tag='info'):
        """Add a message to the progress log with color coding."""
        self.progress_text.insert(tk.END, f"{message}\n", tag)
        self.progress_text.see(tk.END)  # Auto-scroll to bottom
        self.root.update()
    
    def clear_progress_log(self):
        """Clear the progress log."""
        self.progress_text.delete(1.0, tk.END)
    
    def select_zip_files(self):
        """Select multiple ZIP files containing 3D models."""
        zip_files = filedialog.askopenfilenames(
            title="Select ZIP files containing 3D models",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")],
            initialdir=str(Path.home() / "Downloads")
        )
        
        if zip_files:
            self.selected_zip_files.extend(zip_files)
            self.update_file_list()
            self.status_label.config(text=f"Selected {len(self.selected_zip_files)} ZIP files")
            
            # Log selected files
            self.log_progress(f"📁 Selected {len(zip_files)} new ZIP file(s):", 'info')
            for zip_file in zip_files:
                self.log_progress(f"  ✓ {Path(zip_file).name}", 'success')
    
    def update_file_list(self):
        """Update the listbox with selected ZIP files."""
        self.files_listbox.delete(0, tk.END)
        for zip_file in self.selected_zip_files:
            self.files_listbox.insert(tk.END, Path(zip_file).name)
    
    def convert_files(self):
        """Extract and convert ZIP files to organized 3D model folders."""
        if not self.selected_zip_files:
            messagebox.showwarning("No Files", "Please select ZIP files first")
            return
        
        try:
            self.clear_progress_log()
            self.log_progress("=" * 60, 'info')
            self.log_progress("🔄 STARTING FILE CONVERSION", 'complete')
            self.log_progress("=" * 60, 'info')
            
            self.status_label.config(text="Converting ZIP files...")
            self.root.update()
            
            # Create output directory
            output_root = Path.home() / "Downloads" / "Converted_3D_Models"
            output_root.mkdir(parents=True, exist_ok=True)
            self.log_progress(f"📂 Output directory: {output_root}", 'info')
            
            self.converted_folders = []
            total_files = len(self.selected_zip_files)
            
            for idx, zip_file in enumerate(self.selected_zip_files, 1):
                zip_path = Path(zip_file)
                
                self.log_progress(f"\n[{idx}/{total_files}] Processing: {zip_path.name}", 'processing')
                self.status_label.config(text=f"Extracting [{idx}/{total_files}]: {zip_path.name}")
                self.root.update()
                
                # Extract ZIP to temporary folder
                extract_folder = output_root / zip_path.stem
                extract_folder.mkdir(parents=True, exist_ok=True)
                
                self.log_progress(f"  📦 Extracting ZIP archive...", 'processing')
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    file_list = zip_ref.namelist()
                    self.log_progress(f"  📋 Found {len(file_list)} files in archive", 'info')
                    
                    for file_idx, file_name in enumerate(file_list, 1):
                        zip_ref.extract(file_name, extract_folder)
                        if file_idx % 10 == 0 or file_idx == len(file_list):
                            self.status_label.config(text=f"Extracting [{idx}/{total_files}]: {file_idx}/{len(file_list)} files")
                            self.root.update()
                    
                    self.log_progress(f"  ✓ Extracted all files to: {extract_folder.name}", 'success')
                
                # Process extracted content using existing functions
                self.log_progress(f"  🔄 Processing 3D model content...", 'processing')
                processed_count = self.process_extracted_content(extract_folder, output_root)
                self.log_progress(f"  ✓ Processed {processed_count} model folder(s)", 'success')
                
                self.converted_folders.append(extract_folder)
            
            self.log_progress(f"\n{'=' * 60}", 'info')
            self.log_progress(f"✅ CONVERSION COMPLETE!", 'complete')
            self.log_progress(f"{'=' * 60}", 'info')
            self.log_progress(f"📊 Total ZIP files processed: {total_files}", 'success')
            self.log_progress(f"📁 Output location: {output_root}", 'success')
            
            self.status_label.config(text=f"✅ Converted {len(self.selected_zip_files)} ZIP files")
            messagebox.showinfo("Success", f"Converted {len(self.selected_zip_files)} ZIP files to:\n{output_root}")
            
        except Exception as e:
            self.log_progress(f"\n❌ ERROR: {str(e)}", 'error')
            self.status_label.config(text=f"❌ Conversion failed: {str(e)}")
            messagebox.showerror("Error", f"Conversion failed: {e}")
    
    def process_extracted_content(self, extract_folder: Path, output_root: Path):
        """Process extracted folder content using existing functions."""
        # Load overrides
        file_overrides = load_overrides_file(extract_folder)
        merged_overrides = {**file_overrides, **OVERRIDES}
        
        processed_count = 0
        
        # Find folders with 3D content
        for folder in extract_folder.rglob("*"):
            if folder.is_dir():
                has_obj = any(folder.glob("*.obj"))
                has_mtl = any(folder.glob("*.mtl"))
                has_images = any(p.suffix.lower() in IMG_EXTS for p in folder.iterdir() if p.is_file())
                
                if has_obj or has_mtl or has_images:
                    self.log_progress(f"    → Processing model: {folder.name}", 'processing')
                    process_model_folder(folder, output_root, merged_overrides)
                    processed_count += 1
        
        return processed_count
    
    def create_png(self):
        """Create PNG thumbnails for all OBJ files in converted folders."""
        if not self.converted_folders:
            messagebox.showwarning("No Converted Files", "Please convert files first")
            return
        
        try:
            self.log_progress(f"\n{'=' * 60}", 'info')
            self.log_progress("🖼️  STARTING PNG THUMBNAIL GENERATION", 'complete')
            self.log_progress(f"{'=' * 60}", 'info')
            
            self.status_label.config(text="Creating PNG thumbnails...")
            self.root.update()
            
            png_count = 0
            total_obj_files = []
            
            # First, collect all OBJ files
            for folder in self.converted_folders:
                for obj_file in folder.rglob("*.obj"):
                    total_obj_files.append(obj_file)
            
            total_files = len(total_obj_files)
            self.log_progress(f"📊 Found {total_files} OBJ file(s) to render", 'info')
            
            for idx, obj_file in enumerate(total_obj_files, 1):
                self.log_progress(f"\n[{idx}/{total_files}] Rendering: {obj_file.name}", 'processing')
                self.status_label.config(text=f"Rendering [{idx}/{total_files}]: {obj_file.name}")
                self.root.update()
                
                try:
                    # Create PNG thumbnail with "!" suffix
                    png_file = obj_file.with_name(f"{obj_file.stem}!.png")
                    self.log_progress(f"  🎨 Generating transparent thumbnail...", 'processing')
                    
                    render_thumbnail_transparent(obj_file, png_file)
                    
                    self.log_progress(f"  ✓ Saved: {png_file.name}", 'success')
                    png_count += 1
                    
                except Exception as e:
                    self.log_progress(f"  ❌ Failed to render {obj_file.name}: {str(e)}", 'error')
            
            self.log_progress(f"\n{'=' * 60}", 'info')
            self.log_progress(f"✅ PNG GENERATION COMPLETE!", 'complete')
            self.log_progress(f"{'=' * 60}", 'info')
            self.log_progress(f"📊 Successfully created: {png_count}/{total_files} thumbnails", 'success')
            
            self.status_label.config(text=f"✅ Created {png_count} PNG thumbnails")
            messagebox.showinfo("Success", f"Created {png_count} PNG thumbnails!")
            
        except Exception as e:
            self.log_progress(f"\n❌ ERROR: {str(e)}", 'error')
            self.status_label.config(text=f"❌ PNG creation failed: {str(e)}")
            messagebox.showerror("Error", f"PNG creation failed: {e}")
    
    def run(self):
        """Start the GUI."""
        self.root.mainloop()

def main():
    """Main entry point."""
    # Create and run the dark-themed GUI
    app = Dark3DProcessorGUI()
    app.run()
            
if __name__ == "__main__":
    main()
    main()
