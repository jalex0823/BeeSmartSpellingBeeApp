import os
import re
import sys
import csv
import json
import shutil
import zipfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from threading import Thread
import queue
import numpy as np

# Rendering deps
try:
    import trimesh
    import pyrender
    from PIL import Image
    RENDERING_AVAILABLE = True
except ImportError:
    trimesh = None
    pyrender = None
    Image = None
    RENDERING_AVAILABLE = False
    print("⚠️ Rendering dependencies not available. Thumbnails will be skipped.")

class MeshyProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("3D File Folder Converter")
        self.root.geometry("700x600")
        
        # Processing settings
        self.input_folder = tk.StringVar()
        self.recursive = tk.BooleanVar(value=True)
        self.ask_names = tk.BooleanVar(value=False)  # Default to False for GUI
        self.render_thumbnails = tk.BooleanVar(value=True)
        
        # Constants from original script
        self.NUM_SUFFIX = re.compile(r"(?:[_-]\d{6,})+$", re.IGNORECASE)
        self.SEP_SPLIT = re.compile(r"[_\-]+")
        self.DROP_TRAILING_TOKENS = {
            "texture", "tex", "mat", "material", "albedo", "basecolor", "base_color", "obj", "mtl"
        }
        self.PRIMARY_TAGS = [
            "basecolor", "base_color", "albedo", "color", "diffuse"
        ]
        self.SECONDARY_TAGS = [
            "normal", "nrm", "roughness", "metallic", "metalness", "specular",
            "gloss", "glossiness", "ao", "ambientocclusion", "ambient_occlusion",
            "emissive", "emission", "height", "displacement", "opacity", "alpha"
        ]
        self.IMG_EXTS = {".png", ".jpg", ".jpeg"}
        self.RENDER_SIZE = (640, 640)
        self.BACKGROUND_COLOR = (0, 0, 0, 0)
        self.CAMERA_DISTANCE_MULT = 2.2
        self.LIGHT_INTENSITY = 6.0
        
        # Queue for thread communication
        self.message_queue = queue.Queue()
        
        # Track selected ZIP files
        self.selected_zip_files = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="news")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Input folder selection
        ttk.Label(main_frame, text="Select Input Folder:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.input_folder, width=50).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_input_folder).grid(row=0, column=2, padx=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Processing Options", padding="10")
        options_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=10)
        
        ttk.Checkbutton(options_frame, text="Process subfolders recursively", 
                       variable=self.recursive).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Ask for custom names (interactive mode)", 
                       variable=self.ask_names).grid(row=1, column=0, sticky=tk.W)
        
        if RENDERING_AVAILABLE:
            ttk.Checkbutton(options_frame, text="Generate thumbnails", 
                           variable=self.render_thumbnails).grid(row=2, column=0, sticky=tk.W)
        else:
            ttk.Label(options_frame, text="⚠️ Thumbnail generation unavailable (missing dependencies)", 
                     foreground="orange").grid(row=2, column=0, sticky=tk.W)
        
        # Process button
        self.process_btn = ttk.Button(main_frame, text="Start Processing", 
                                    command=self.start_processing, style="Accent.TButton")
        self.process_btn.grid(row=2, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=3, sticky="ew", pady=5)
        
        # Log output
        ttk.Label(main_frame, text="Processing Log:").grid(row=4, column=0, sticky=tk.W, pady=(10, 0))
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, width=80)
        self.log_text.grid(row=5, column=0, columnspan=3, sticky="news", pady=5)
        
        # Configure row weights for text expansion
        main_frame.rowconfigure(5, weight=1)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(5, 0))
        
        # Start checking message queue
        self.check_queue()
        
    def browse_input_folder(self):
        # Ask user to choose between folder or ZIP file
        choice = messagebox.askyesnocancel("Input Selection", 
                                          "Select input type:\n\n"
                                          "YES = Browse for ZIP file(s)\n"
                                          "NO = Browse for folder\n"
                                          "CANCEL = Cancel selection")
        
        if choice is None:  # Cancel
            return
        elif choice:  # YES - ZIP files
            files = filedialog.askopenfilenames(
                title="Select ZIP file(s) containing 3D model exports",
                filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")]
            )
            if files:
                # If multiple files selected, use the directory of the first file
                self.input_folder.set(str(Path(files[0]).parent))
                self.selected_zip_files = files
        else:  # NO - Folder
            folder = filedialog.askdirectory(title="Select folder containing 3D model exports")
            if folder:
                self.input_folder.set(folder)
                self.selected_zip_files = None
            
    def log_message(self, message):
        """Add message to log and scroll to bottom"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def check_queue(self):
        """Check for messages from processing thread"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                if message == "DONE":
                    self.progress.stop()
                    self.process_btn.config(state='normal')
                    self.status_var.set("Processing complete")
                elif message == "ERROR":
                    self.progress.stop()
                    self.process_btn.config(state='normal')
                    self.status_var.set("Processing failed")
                else:
                    self.log_message(message)
        except queue.Empty:
            pass
        self.root.after(100, self.check_queue)
        
    def start_processing(self):
        """Start processing in a separate thread"""
        if not self.input_folder.get():
            messagebox.showerror("Error", "Please select an input folder")
            return
            
        if not os.path.exists(self.input_folder.get()):
            messagebox.showerror("Error", "Selected folder does not exist")
            return
            
        self.process_btn.config(state='disabled')
        self.progress.start(10)
        self.status_var.set("Processing...")
        self.log_text.delete(1.0, tk.END)
        
        # Start processing thread
        thread = Thread(target=self.process_files)
        thread.daemon = True
        thread.start()
        
    def extract_zip_files(self, zip_files: List[str], extract_root: Path) -> List[Path]:
        """Extract ZIP files and return list of extracted folders"""
        extracted_folders = []
        
        for zip_path in zip_files:
            zip_file = Path(zip_path)
            self.message_queue.put(f"📦 Extracting ZIP file: {zip_file.name}")
            
            try:
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    # Create extraction folder based on ZIP filename
                    extract_folder = extract_root / zip_file.stem
                    extract_folder.mkdir(parents=True, exist_ok=True)
                    
                    # Extract all contents
                    zip_ref.extractall(extract_folder)
                    extracted_folders.append(extract_folder)
                    self.message_queue.put(f"✅ Extracted to: {extract_folder}")
                    
            except Exception as e:
                self.message_queue.put(f"❌ Failed to extract {zip_file.name}: {e}")
                
        return extracted_folders
        
    def find_zip_files_in_folder(self, folder: Path) -> List[Path]:
        """Find all ZIP files in a folder recursively"""
        zip_files = []
        for zip_file in folder.rglob("*.zip"):
            zip_files.append(zip_file)
        return zip_files
        
    def process_files(self):
        """Main processing function - runs in separate thread"""
        try:
            in_root = Path(self.input_folder.get()).resolve()
            out_root = in_root / "Converted"  # Create Converted subfolder
            
            self.message_queue.put(f"📁 Input folder: {in_root}")
            self.message_queue.put(f"📁 Output folder: {out_root}")
            
            if not in_root.exists():
                self.message_queue.put(f"❌ Input folder not found: {in_root}")
                self.message_queue.put("ERROR")
                return
                
            out_root.mkdir(parents=True, exist_ok=True)
            
            # Load overrides
            merged_overrides = self.load_overrides_file(in_root)
            
            # Find folders to process
            folders = self.iter_source_folders(in_root, self.recursive.get())
            count = 0
            total_candidates = 0
            
            # Count candidate folders first
            for folder in folders:
                if folder == out_root or out_root in folder.parents:
                    continue  # Skip the output folder itself
                has_candidate = any(folder.glob("*.obj")) or any(folder.glob("*.mtl")) or any(
                    p.suffix.lower() in self.IMG_EXTS for p in folder.iterdir() if p.is_file()
                )
                if has_candidate:
                    total_candidates += 1
                    
            self.message_queue.put(f"🔍 Found {total_candidates} folders with 3D assets to process")
            
            # Process each folder
            for folder in folders:
                if folder == out_root or out_root in folder.parents:
                    continue  # Skip the output folder itself
                    
                has_candidate = any(folder.glob("*.obj")) or any(folder.glob("*.mtl")) or any(
                    p.suffix.lower() in self.IMG_EXTS for p in folder.iterdir() if p.is_file()
                )
                if not has_candidate:
                    continue
                    
                count += 1
                self.message_queue.put(f"\n📦 Processing {count}/{total_candidates}: {folder.name}")
                self.process_model_folder(folder, out_root, merged_overrides)
                
            self.message_queue.put(f"\n✅ Processing complete! Processed {count} folder(s).")
            self.message_queue.put(f"📂 Output saved to: {out_root}")
            self.message_queue.put("DONE")
            
        except Exception as e:
            self.message_queue.put(f"❌ Error during processing: {str(e)}")
            self.message_queue.put("ERROR")
            
    # All the helper methods from the original script
    def camel_no_underscores(self, s: str) -> str:
        """Remove underscores/dashes and convert to compact CamelCase-ish."""
        parts = [p for p in self.SEP_SPLIT.split(s) if p]
        if not parts:
            return s.replace("_", "").replace("-", "")
        return "".join(p[:1].upper() + p[1:] for p in parts)

    def clean_base_from_stem(self, stem: str) -> str:
        """Derive a clean base from a filename stem."""
        stem = self.NUM_SUFFIX.sub("", stem)
        parts = [p for p in self.SEP_SPLIT.split(stem) if p]
        while parts and parts[-1].lower() in self.DROP_TRAILING_TOKENS:
            parts.pop()
        if not parts:
            parts = [stem]
        cleaned = self.camel_no_underscores("_".join(parts))
        return cleaned or "MeshyModel"

    def detect_files(self, src_folder: Path) -> Tuple[Optional[Path], Optional[Path], List[Path]]:
        """Find the primary OBJ, optional MTL, and all images in a folder."""
        obj = next((p for p in src_folder.glob("*.obj")), None)
        mtl = next((p for p in src_folder.glob("*.mtl")), None)
        imgs = [p for p in src_folder.iterdir() if p.is_file() and p.suffix.lower() in self.IMG_EXTS]
        return obj, mtl, imgs

    def pick_primary_texture(self, imgs: List[Path], base_hint: str) -> Optional[Path]:
        """Pick the best candidate as the main color/albedo texture."""
        if not imgs:
            return None
        by_score = []
        for img in imgs:
            low = img.stem.lower()
            score = 0
            for t in self.PRIMARY_TAGS:
                if t in low:
                    score += 10
            if base_hint.lower() in low:
                score += 1
            by_score.append((score, img))
        by_score.sort(key=lambda x: x[0], reverse=True)
        return by_score[0][1] if by_score else imgs[0]

    def suffix_from_name(self, stem: str) -> str:
        """Return CamelCase suffix based on known tags, otherwise empty."""
        low = stem.lower()
        for tag in self.PRIMARY_TAGS + self.SECONDARY_TAGS:
            if tag in low:
                return self.camel_no_underscores(tag)
        return ""

    def copy_and_rename(self, obj: Optional[Path], mtl: Optional[Path], imgs: List[Path], 
                       out_folder: Path, base: str) -> Tuple[Optional[Path], Optional[Path], List[Path], Optional[Path]]:
        """Copy and rename files into out_folder with clean names."""
        out_obj = out_mtl = None
        out_imgs: List[Path] = []
        primary_out = None

        if obj:
            out_obj = out_folder / f"{base}.obj"
            shutil.copy2(obj, out_obj)
            self.message_queue.put(f"  📄 Copied: {obj.name} → {out_obj.name}")

        if mtl:
            out_mtl = out_folder / f"{base}.mtl"
            shutil.copy2(mtl, out_mtl)
            self.message_queue.put(f"  📄 Copied: {mtl.name} → {out_mtl.name}")

        if imgs:
            primary = self.pick_primary_texture(imgs, base)
            for img in imgs:
                ext = img.suffix.lower()
                if img == primary:
                    primary_out = out_folder / f"{base}{ext}"
                    shutil.copy2(img, primary_out)
                    out_imgs.append(primary_out)
                    self.message_queue.put(f"  🖼️ Primary texture: {img.name} → {primary_out.name}")
                else:
                    suf = self.suffix_from_name(img.stem)
                    out_path = out_folder / (f"{base}{suf}{ext}" if suf else f"{base}{ext}")
                    if primary_out and out_path.name == primary_out.name:
                        out_path = out_folder / f"{base}Tex{ext}"
                    shutil.copy2(img, out_path)
                    out_imgs.append(out_path)
                    self.message_queue.put(f"  🖼️ Texture: {img.name} → {out_path.name}")

        return out_obj, out_mtl, out_imgs, primary_out

    def patch_obj(self, obj_path: Path, new_mtl_name: Optional[str]):
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

    def patch_mtl(self, mtl_path: Path, images: List[Path], primary_img: Optional[Path]):
        """Update map_* references in MTL to renamed/clean images."""
        if not mtl_path or not mtl_path.exists():
            return
        try:
            lines = mtl_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            return

        by_tag: Dict[str, str] = {}
        for img in images:
            tag = self.suffix_from_name(img.stem)
            if tag:
                by_tag[tag.lower()] = img.name

        def choose_texture(orig_name: str) -> str:
            tag = self.suffix_from_name(Path(orig_name).stem).lower()
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

    def render_thumbnail_transparent(self, obj_path: Path, thumb_path: Path):
        """Render OBJ to a transparent PNG using pyrender OffscreenRenderer."""
        if not RENDERING_AVAILABLE or trimesh is None or pyrender is None or Image is None:
            self.message_queue.put(f"  ⚠️ Thumbnail generation skipped - dependencies not available")
            return
            
        try:
            mesh = trimesh.load_mesh(str(obj_path), process=False)
            if isinstance(mesh, trimesh.Scene):
                mesh = trimesh.util.concatenate(mesh.dump())

            scene = pyrender.Scene(
                bg_color=self.BACKGROUND_COLOR,
                ambient_light=[0.35, 0.35, 0.35]
            )
            mesh_node = pyrender.Mesh.from_trimesh(mesh, smooth=True)
            scene.add(mesh_node)

            # Camera placement
            bounds = mesh.bounds
            center = bounds.mean(axis=0)
            extents = mesh.extents
            radius = np.linalg.norm(extents) * 0.5
            distance = max(0.1, radius * self.CAMERA_DISTANCE_MULT)

            cam = pyrender.PerspectiveCamera(yfov=np.pi / 4.0)
            cam_pose = np.eye(4)
            cam_pose[:3, 3] = center + np.array([0.0, 0.0, distance])
            forward = (center - cam_pose[:3, 3])
            forward /= (np.linalg.norm(forward) + 1e-7)
            up = np.array([0.0, 1.0, 0.0])
            right = np.cross(up, forward)
            right /= (np.linalg.norm(right) + 1e-7)
            up = np.cross(forward, right)
            up /= (np.linalg.norm(up) + 1e-7)
            cam_pose[:3, :3] = np.vstack([right, up, forward]).T
            scene.add(cam, pose=cam_pose)

            key = pyrender.DirectionalLight(color=np.ones(3), intensity=self.LIGHT_INTENSITY)
            fill = pyrender.DirectionalLight(color=np.ones(3), intensity=self.LIGHT_INTENSITY * 0.6)
            scene.add(key, pose=cam_pose)
            fill_pose = np.array(cam_pose)
            fill_pose[:3, 3] = center + np.array([distance, distance, distance])
            scene.add(fill, pose=fill_pose)

            r = pyrender.OffscreenRenderer(*self.RENDER_SIZE)
            color, _ = r.render(scene)
            r.delete()

            img = Image.fromarray(color).convert("RGBA")
            img.save(thumb_path)
            self.message_queue.put(f"  📸 Thumbnail: {thumb_path.name}")
        except Exception as e:
            self.message_queue.put(f"  ⚠️ Thumbnail render failed for {obj_path.name}: {e}")

    def load_overrides_file(self, in_root: Path) -> Dict[str, str]:
        """Load override mappings from JSON or CSV files."""
        out: Dict[str, str] = {}
        j = in_root / "overrides.json"
        c = in_root / "overrides.csv"
        
        if j.exists():
            try:
                data = json.loads(j.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    out.update(data)
                    self.message_queue.put(f"📋 Loaded overrides from {j.name}")
            except Exception as e:
                self.message_queue.put(f"⚠️ Failed to load {j.name}: {e}")
                
        if c.exists():
            try:
                with c.open("r", encoding="utf-8", newline="") as fh:
                    rdr = csv.reader(fh)
                    for row in rdr:
                        if len(row) >= 2:
                            out[row[0].strip()] = row[1].strip()
                    self.message_queue.put(f"📋 Loaded overrides from {c.name}")
            except Exception as e:
                self.message_queue.put(f"⚠️ Failed to load {c.name}: {e}")
                
        return out

    def choose_output_name_for_folder(self, folder: Path, auto_base: str, overrides: Dict[str, str]) -> str:
        """Choose output name for a folder."""
        key = folder.name
        if key in overrides:
            return self.camel_no_underscores(overrides[key])
        if self.ask_names.get():
            # For GUI, we could implement a dialog here, but for now just use auto name
            pass
        return auto_base

    def process_model_folder(self, src_folder: Path, out_parent: Path, overrides: Dict[str, str]):
        """Process a single model folder."""
        obj, mtl, imgs = self.detect_files(src_folder)
        if not obj and not mtl and not imgs:
            return

        # Decide default base
        base_source = obj or mtl or (imgs[0] if imgs else None)
        auto_base = self.clean_base_from_stem(base_source.stem if base_source else src_folder.name)

        base = self.choose_output_name_for_folder(src_folder, auto_base, overrides)

        out_folder = out_parent / base
        out_folder.mkdir(parents=True, exist_ok=True)

        out_obj, out_mtl, out_imgs, primary_img = self.copy_and_rename(obj, mtl, imgs, out_folder, base)

        if out_obj:
            self.patch_obj(out_obj, out_mtl.name if out_mtl else None)
        if out_mtl:
            self.patch_mtl(out_mtl, out_imgs, primary_img)

        if out_obj and out_obj.exists() and self.render_thumbnails.get():
            thumb_path = out_folder / f"{base}!.png"
            self.render_thumbnail_transparent(out_obj, thumb_path)

    def iter_source_folders(self, root: Path, recursive: bool) -> List[Path]:
        """Iterate over source folders to process."""
        if not recursive:
            return [p for p in root.iterdir() if p.is_dir()]
        return [p for p in root.rglob("*") if p.is_dir()]


def main():
    root = tk.Tk()
    app = MeshyProcessorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()