#!/usr/bin/env python3
"""
Standalone Avatar Delta Analyzer - No servers needed!
Direct file analysis with comprehensive rigging, materials, and mesh comparison
With 3D rendering support using matplotlib/trimesh
"""

import os
import re
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
import tkinter as tk
from tkinter import ttk, messagebox
import threading
try:
    import trimesh
    TRIMESH_AVAILABLE = True
except ImportError:
    TRIMESH_AVAILABLE = False

from avatar_viewer_ui import show_viewer

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class TextureInfo:
    name: str
    path: str
    exists: bool = False
    size_bytes: int = 0

@dataclass
class MaterialInfo:
    name: str
    color: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    textures: List[TextureInfo] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)

@dataclass
class BoneInfo:
    name: str
    weight_count: int = 0
    issues: List[str] = field(default_factory=list)

@dataclass
class RiggingInfo:
    bone_count: int = 0
    bones: List[BoneInfo] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)

@dataclass
class MeshInfo:
    vertices: int = 0
    faces: int = 0
    materials_used: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)

@dataclass
class AvatarFileAnalysis:
    name: str
    path: str
    mesh: MeshInfo
    materials: List[MaterialInfo]
    rigging: RiggingInfo
    critical_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)

# ============================================================================
# PARSER ENGINE
# ============================================================================

class AvatarFileParser:
    def __init__(self, avatar_dir: Path):
        self.avatar_dir = Path(avatar_dir)
        self.obj_file: Optional[Path] = None
        self.mtl_file: Optional[Path] = None

    def parse(self) -> Optional[AvatarFileAnalysis]:
        """Parse avatar files and return analysis"""
        if not self.avatar_dir.exists():
            return None

        self._find_obj_file()
        if not self.obj_file:
            return AvatarFileAnalysis(
                name=self.avatar_dir.name,
                path=str(self.avatar_dir),
                mesh=MeshInfo(issues=["No .obj file found"]),
                materials=[],
                rigging=RiggingInfo(),
                critical_issues=["Missing OBJ file"],
                warnings=[],
                info=[]
            )

        self._find_mtl_file()
        mesh_info = self._parse_obj_file()
        materials = self._parse_mtl_file() if self.mtl_file else []
        rigging_info = self._parse_rigging_data()

        analysis = AvatarFileAnalysis(
            name=self.avatar_dir.name,
            path=str(self.avatar_dir),
            mesh=mesh_info,
            materials=materials,
            rigging=rigging_info,
            critical_issues=[],
            warnings=[],
            info=[]
        )

        self._run_diagnostics(analysis)
        return analysis

    def _find_obj_file(self):
        """Find .obj file in directory"""
        if self.obj_file:
            return
        obj_files = list(self.avatar_dir.glob('*.obj'))
        if obj_files:
            self.obj_file = obj_files[0]

    def _find_mtl_file(self):
        """Find .mtl file in directory"""
        if self.mtl_file:
            return
        mtl_files = list(self.avatar_dir.glob('*.mtl'))
        if mtl_files:
            self.mtl_file = mtl_files[0]

    def _parse_obj_file(self) -> MeshInfo:
        """Extract mesh data from OBJ file"""
        mesh = MeshInfo()

        try:
            if not self.obj_file or not self.obj_file.exists():
                mesh.issues.append("OBJ file not found")
                return mesh

            with open(self.obj_file, 'r', encoding='utf-8', errors='ignore') as f:
                vertices = 0
                faces = 0
                materials_used = set()
                vertex_normals = 0
                vertex_texture_coords = 0

                for line in f:
                    if line.startswith('v '):
                        vertices += 1
                    elif line.startswith('vn '):
                        vertex_normals += 1
                    elif line.startswith('vt '):
                        vertex_texture_coords += 1
                    elif line.startswith('f '):
                        faces += 1
                    elif line.startswith('usemtl '):
                        mat_name = line.split(maxsplit=1)[1].strip()
                        materials_used.add(mat_name)

                mesh.vertices = vertices
                mesh.faces = faces
                mesh.materials_used = list(materials_used)

                if vertices == 0:
                    mesh.issues.append("No vertices found in OBJ")
                if faces == 0:
                    mesh.issues.append("No faces found in OBJ")
                if vertex_normals == 0:
                    mesh.issues.append("No vertex normals - may affect lighting")
                if vertex_texture_coords == 0 and materials_used:
                    mesh.issues.append("No texture coordinates - materials won't display correctly")

        except Exception as e:
            mesh.issues.append(f"Error parsing OBJ: {str(e)}")

        return mesh

    def _parse_mtl_file(self) -> List[MaterialInfo]:
        """Extract material data from MTL file"""
        materials: List[MaterialInfo] = []

        try:
            if not self.mtl_file or not self.mtl_file.exists():
                return materials

            current_mat: Optional[MaterialInfo] = None
            with open(self.mtl_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('newmtl '):
                        if current_mat:
                            materials.append(current_mat)
                        mat_name = line.split(maxsplit=1)[1]
                        current_mat = MaterialInfo(name=mat_name)
                    elif line.startswith('Kd ') and current_mat:
                        # Diffuse color
                        parts = line.split()
                        try:
                            current_mat.color = (float(parts[1]), float(parts[2]), float(parts[3]))
                        except (ValueError, IndexError):
                            pass
                    elif line.startswith('map_Kd ') and current_mat:
                        # Texture map
                        tex_path = line.split(maxsplit=1)[1]
                        tex_info = TextureInfo(name=Path(tex_path).name, path=tex_path)
                        
                        # Check if texture exists
                        full_path = self.avatar_dir / tex_path
                        if full_path.exists():
                            tex_info.exists = True
                            try:
                                tex_info.size_bytes = full_path.stat().st_size
                            except OSError:
                                pass
                        else:
                            current_mat.issues.append(f"Missing texture: {tex_path}")
                        
                        current_mat.textures.append(tex_info)

                if current_mat:
                    materials.append(current_mat)

        except Exception as e:
            pass  # Silently skip if MTL parsing fails

        return materials

    def _parse_rigging_data(self) -> RiggingInfo:
        """Extract rigging/skeleton data from OBJ file"""
        rigging = RiggingInfo()

        # OBJ files don't typically store rigging data, but we can detect
        # potential rigging issues by checking for bone naming conventions
        # or look for weight data if available
        
        try:
            if not self.obj_file or not self.obj_file.exists():
                return rigging

            with open(self.obj_file, 'r', encoding='utf-8', errors='ignore') as f:
                bone_names = set()
                for line in f:
                    # Look for comments that might mention bones
                    if line.startswith('#') and ('bone' in line.lower() or 'armature' in line.lower()):
                        # Extract potential bone references
                        words = line.lower().split()
                        for word in words:
                            if 'bone' in word or 'joint' in word:
                                bone_names.add(word)

                rigging.bone_count = len(bone_names)
                rigging.bones = [BoneInfo(name=bn) for bn in sorted(bone_names)]

        except Exception:
            pass

        return rigging

    def _run_diagnostics(self, analysis: AvatarFileAnalysis):
        """Run diagnostic checks"""
        if analysis.mesh.vertices == 0:
            analysis.critical_issues.append("Empty mesh - no geometry")
        
        if analysis.mesh.faces == 0:
            analysis.critical_issues.append("No faces - mesh is incomplete")

        # Check for missing textures
        missing_textures = []
        for mat in analysis.materials:
            missing_textures.extend(mat.issues)
        
        if missing_textures:
            analysis.warnings.append(f"Missing textures: {len(missing_textures)}")

        # Check rigging issues
        if analysis.rigging.bone_count == 0 and analysis.mesh.vertices > 0:
            analysis.warnings.append("No rigging/bones detected")

        # Info
        analysis.info.append(f"Vertices: {analysis.mesh.vertices:,}")
        analysis.info.append(f"Faces: {analysis.mesh.faces:,}")
        analysis.info.append(f"Materials: {len(analysis.materials)}")
        analysis.info.append(f"Bones: {analysis.rigging.bone_count}")

# ============================================================================
# DELTA COMPARATOR
# ============================================================================

class AvatarDeltaComparator:
    @staticmethod
    def compare(working: AvatarFileAnalysis, broken: AvatarFileAnalysis) -> Dict:
        """Compare two avatar analyses - returns structured delta report"""
        
        # Material differences
        material_diffs = []
        working_mats = {m.name: m for m in working.materials}
        broken_mats = {m.name: m for m in broken.materials}
        
        for mat_name in set(list(working_mats.keys()) + list(broken_mats.keys())):
            w_mat = working_mats.get(mat_name)
            b_mat = broken_mats.get(mat_name)
            
            if w_mat and not b_mat:
                material_diffs.append({
                    "material": mat_name,
                    "issue": "Missing in broken avatar",
                    "working": "present",
                    "broken": None
                })
            elif b_mat and not w_mat:
                material_diffs.append({
                    "material": mat_name,
                    "issue": "Extra in broken avatar",
                    "working": None,
                    "broken": "present"
                })
            elif w_mat and b_mat:
                # Check texture differences
                w_textures = {t.name: t for t in w_mat.textures}
                b_textures = {t.name: t for t in b_mat.textures}
                
                for tex_name in set(list(w_textures.keys()) + list(b_textures.keys())):
                    w_tex = w_textures.get(tex_name)
                    b_tex = b_textures.get(tex_name)
                    
                    if w_tex and not b_tex:
                        material_diffs.append({
                            "material": mat_name,
                            "issue": "Missing texture map",
                            "working": w_tex.name,
                            "broken": None
                        })
                    elif b_tex and not w_tex:
                        material_diffs.append({
                            "material": mat_name,
                            "issue": "Extra texture map",
                            "working": None,
                            "broken": b_tex.name
                        })
                    elif w_tex and b_tex and w_tex.exists != b_tex.exists:
                        material_diffs.append({
                            "material": mat_name,
                            "issue": f"Texture exists: {w_tex.exists} vs {b_tex.exists}",
                            "working": w_tex.name if w_tex.exists else f"{w_tex.name} (missing)",
                            "broken": b_tex.name if b_tex.exists else f"{b_tex.name} (missing)"
                        })
        
        # Rigging differences
        rigging_diffs = []
        working_bones = {b.name: b for b in working.rigging.bones}
        broken_bones = {b.name: b for b in broken.rigging.bones}
        
        for bone_name in set(list(working_bones.keys()) + list(broken_bones.keys())):
            w_bone = working_bones.get(bone_name)
            b_bone = broken_bones.get(bone_name)
            
            if w_bone and not b_bone:
                rigging_diffs.append({
                    "bone": bone_name,
                    "issue": "Missing in broken avatar"
                })
            elif b_bone and not w_bone:
                rigging_diffs.append({
                    "bone": bone_name,
                    "issue": "Extra in broken avatar"
                })
            elif w_bone and b_bone and w_bone.weight_count != b_bone.weight_count:
                rigging_diffs.append({
                    "bone": bone_name,
                    "issue": f"Weight count mismatch: {w_bone.weight_count} vs {b_bone.weight_count}"
                })
        
        return {
            "mesh": {
                "vertex_count": {
                    "working": working.mesh.vertices,
                    "broken": broken.mesh.vertices
                },
                "face_count": {
                    "working": working.mesh.faces,
                    "broken": broken.mesh.faces
                },
                "vertex_delta": broken.mesh.vertices - working.mesh.vertices,
                "face_delta": broken.mesh.faces - working.mesh.faces,
                "issues": working.mesh.issues + broken.mesh.issues
            },
            "materials": {
                "count": {
                    "working": len(working.materials),
                    "broken": len(broken.materials)
                },
                "differences": material_diffs
            },
            "rigging": {
                "bone_count": {
                    "working": working.rigging.bone_count,
                    "broken": broken.rigging.bone_count
                },
                "issues": rigging_diffs
            },
            "summary": {
                "working_critical": len(working.critical_issues),
                "working_warnings": len(working.warnings),
                "broken_critical": len(broken.critical_issues),
                "broken_warnings": len(broken.warnings),
            }
        }

# ============================================================================
# GUI
# ============================================================================

class AvatarAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Avatar Delta Analyzer - Comprehensive")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1a1a2e")
        
        # Find avatar directory
        base_path = Path(__file__).parent.parent / "static" / "Avatars" / "3D Avatar Files"
        if not base_path.exists():
            base_path = Path("../static/Avatars/3D Avatar Files").resolve()
        
        self.avatar_base = base_path
        self.avatars = self._discover_avatars()
        
        self._build_ui()

    def _discover_avatars(self) -> List[str]:
        """Discover all avatar directories"""
        if not self.avatar_base.exists():
            messagebox.showerror("Error", f"Avatar directory not found: {self.avatar_base}")
            return []
        
        # Define working vs broken based on actual rendering status
        # Working avatars (render correctly)
        self.working_avatars = {
            'AlBee', 'AnxiousBee', 'MascotBee', 'MonsterBee', 
            'ProfessorBee', 'RockerBee', 'VampBee', 'WareBee', 'ZomBee'
        }
        
        # Broken avatars (white blob/not rendering)
        self.broken_avatars = {
            'BikerBee', 'BitterBee', 'BlissfulBee', 'BrotherBee', 
            'BuilderBee', 'CoolBee', 'DivaBee', 'DoctorBee', 
            'ExplorerBee', 'KnightBee', 'QueenBee', 'RoboBee'
        }
        
        avatars = sorted([d.name for d in self.avatar_base.iterdir() if d.is_dir()])
        return avatars

    def _build_ui(self):
        """Build the GUI"""
        # Header
        header = tk.Frame(self.root, bg="#ff6b9d", height=60)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)
        
        title = tk.Label(header, text="🔍 Avatar Delta Analyzer - Deep Forensic Comparison", 
                        font=("Arial", 18, "bold"), bg="#ff6b9d", fg="white")
        title.pack(pady=10)
        
        # Controls frame
        control_frame = tk.Frame(self.root, bg="#1a1a2e")
        control_frame.pack(fill=tk.X, padx=20, pady=15)
        
        # Separate working and broken avatars for dropdowns
        working_avatars = sorted([a for a in self.avatars if a in self.working_avatars])
        broken_avatars = sorted([a for a in self.avatars if a in self.broken_avatars])
        
        # Working avatar selector (✓)
        tk.Label(control_frame, text="✓ Working Avatar:", bg="#1a1a2e", fg="#00d084", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self.working_var = tk.StringVar(value=working_avatars[0] if working_avatars else "")
        working_combo = ttk.Combobox(control_frame, textvariable=self.working_var, 
                                     values=working_avatars, width=20, state="readonly")
        working_combo.pack(side=tk.LEFT, padx=5)
        
        # Broken avatar selector (✗)
        tk.Label(control_frame, text="✗ Broken Avatar:", bg="#1a1a2e", fg="#ff6b6b", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self.broken_var = tk.StringVar(value=broken_avatars[0] if broken_avatars else "")
        broken_combo = ttk.Combobox(control_frame, textvariable=self.broken_var, 
                                    values=broken_avatars, width=20, state="readonly")
        broken_combo.pack(side=tk.LEFT, padx=5)
        
        # Compare button
        compare_btn = tk.Button(control_frame, text="🔍 Deep Analyze", command=self._on_compare,
                               bg="#feca57", fg="black", font=("Arial", 10, "bold"), 
                               padx=15, pady=5, cursor="hand2")
        compare_btn.pack(side=tk.LEFT, padx=20)
        
        # Export button
        export_btn = tk.Button(control_frame, text="💾 Export JSON", command=self._on_export,
                              bg="#00d084", fg="black", font=("Arial", 10, "bold"), 
                              padx=15, pady=5, cursor="hand2")
        export_btn.pack(side=tk.LEFT, padx=5)
        
        # Add button to show 3D view
        view_btn = tk.Button(control_frame, text="👁️ View 3D", command=self._show_3d_view,
                            bg="#9c27b0", fg="white", font=("Arial", 10, "bold"), 
                            padx=15, pady=5, cursor="hand2")
        view_btn.pack(side=tk.LEFT, padx=5)
        
        # Results frame (with scrollbar)
        results_frame = tk.Frame(self.root, bg="#1a1a2e")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Text widget for results
        scrollbar = ttk.Scrollbar(results_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_text = tk.Text(results_frame, bg="#0f0f1e", fg="#00ff00", 
                                   font=("Courier", 9), yscrollcommand=scrollbar.set,
                                   wrap=tk.WORD)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.results_text.yview)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bg="#0f0f1e", 
                             fg="#ff6b9d", anchor=tk.W, padx=10)
        status_bar.pack(fill=tk.X, pady=5)
        
        self.last_delta = None
        self.working_analysis = None
        self.broken_analysis = None

    def _on_compare(self):
        """Handle compare button click"""
        working_name = self.working_var.get()
        broken_name = self.broken_var.get()
        
        if not working_name or not broken_name:
            messagebox.showwarning("Warning", "Please select both avatars")
            return
        
        if working_name == broken_name:
            messagebox.showwarning("Warning", "Please select different avatars")
            return
        
        # Run analysis in background thread
        thread = threading.Thread(target=self._analyze, args=(working_name, broken_name))
        thread.daemon = True
        thread.start()

    def _on_export(self):
        """Export last analysis to JSON"""
        if not self.last_delta:
            messagebox.showwarning("Warning", "No analysis to export. Run compare first.")
            return
        
        try:
            filename = "avatar_delta_analysis.json"
            with open(filename, 'w') as f:
                json.dump(self.last_delta, f, indent=2)
            messagebox.showinfo("Success", f"Exported to {filename}")
            self.status_var.set(f"✓ Exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")

    def _analyze(self, working_name: str, broken_name: str):
        """Analyze avatars"""
        self.status_var.set("Analyzing...")
        self.root.update()
        
        try:
            # Parse avatars
            working_path = self.avatar_base / working_name
            broken_path = self.avatar_base / broken_name
            
            working_parser = AvatarFileParser(working_path)
            broken_parser = AvatarFileParser(broken_path)
            
            working_analysis = working_parser.parse()
            broken_analysis = broken_parser.parse()
            
            # Store for 3D view
            self.working_analysis = working_analysis
            self.broken_analysis = broken_analysis
            
            if not working_analysis or not broken_analysis:
                messagebox.showerror("Error", "Failed to parse avatars")
                return
            
            # Compare
            delta = AvatarDeltaComparator.compare(working_analysis, broken_analysis)
            self.last_delta = delta  # Store for export
            
            # Display results
            self._display_results(working_analysis, broken_analysis, delta)
            self.status_var.set(f"✓ Analysis complete - {working_name} vs {broken_name}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
            self.status_var.set("✗ Error during analysis")

    def _show_3d_view(self):
        """Show side-by-side 3D rendering of avatars"""
        if not self.working_analysis or not self.broken_analysis:
            messagebox.showwarning("Warning", "Run analysis first")
            return
        
        # Show viewer with full avatar lists
        self.status_var.set("✓ Opening avatar viewer...")
        
        # Create analysis dictionaries
        working_name = self.working_var.get()
        broken_name = self.broken_var.get()
        working_analyses = {working_name: self.working_analysis} if working_name else {}
        broken_analyses = {broken_name: self.broken_analysis} if broken_name else {}
        
        show_viewer(self.avatar_base, list(self.working_avatars), list(self.broken_avatars),
                   working_analyses, broken_analyses)

    def _create_info_panel(self, parent_frame, analysis):
        """Create information panel with avatar details"""
        info_frame = tk.Frame(parent_frame, bg="#0f0f1e")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create scrollable text
        scrollbar = ttk.Scrollbar(info_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(info_frame, bg="#1a1a2e", fg="#e0e0e0", 
                             font=("Courier", 9), yscrollcommand=scrollbar.set,
                             height=25, width=50)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        
        # Build info text
        info_text = []
        info_text.append("=" * 50)
        info_text.append(f"AVATAR: {analysis.avatar_name}")
        info_text.append("=" * 50)
        info_text.append("")
        
        # File info
        info_text.append("📁 FILE INFORMATION")
        info_text.append("-" * 50)
        info_text.append(f"OBJ File: {Path(analysis.obj_file).name if analysis.obj_file else 'N/A'}")
        info_text.append(f"MTL File: {Path(analysis.mtl_file).name if analysis.mtl_file else 'None'}")
        info_text.append(f"File Size: {analysis.file_size / (1024*1024):.2f} MB")
        info_text.append("")
        
        # Mesh info
        info_text.append("🗂️ MESH INFORMATION")
        info_text.append("-" * 50)
        total_verts = sum(m.vertex_count for m in analysis.meshes)
        total_faces = sum(m.face_count for m in analysis.meshes)
        total_normals = sum(m.normal_count for m in analysis.meshes)
        total_texcoords = sum(m.texture_coord_count for m in analysis.meshes)
        
        info_text.append(f"Total Vertices: {total_verts:,}")
        info_text.append(f"Total Faces: {total_faces:,}")
        info_text.append(f"Normals: {total_normals:,}")
        info_text.append(f"Tex Coords: {total_texcoords:,}")
        info_text.append("")
        
        # Material info
        info_text.append("🎨 MATERIALS")
        info_text.append("-" * 50)
        info_text.append(f"Count: {len(analysis.materials)}")
        for mat in analysis.materials:
            info_text.append(f"  • {mat.name}")
            info_text.append(f"    Textures: {len(mat.textures)}")
            for tex in mat.textures:
                status = "✓" if tex.exists else "✗"
                info_text.append(f"    {status} {tex.name}")
        info_text.append("")
        
        # Issues
        if analysis.critical_issues:
            info_text.append("🔴 CRITICAL ISSUES")
            info_text.append("-" * 50)
            for issue in analysis.critical_issues:
                info_text.append(f"  ✗ {issue}")
            info_text.append("")
        
        if analysis.warnings:
            info_text.append("⚠️ WARNINGS")
            info_text.append("-" * 50)
            for warning in analysis.warnings:
                info_text.append(f"  ⚠ {warning}")
            info_text.append("")
        
        # Insert text
        full_text = "\n".join(info_text)
        text_widget.insert(1.0, full_text)
        text_widget.config(state=tk.DISABLED)
        
        return info_frame

    def _display_results(self, working, broken, delta):
        """Display analysis results in structured format"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        output = []
        output.append("=" * 100)
        output.append("AVATAR DELTA ANALYSIS REPORT")
        output.append("=" * 100)
        output.append("")
        
        # Mesh section
        output.append("📊 MESH COMPARISON")
        output.append("-" * 100)
        output.append(f"Working: {delta['mesh']['vertex_count']['working']:,} vertices, {delta['mesh']['face_count']['working']:,} faces")
        output.append(f"Broken:  {delta['mesh']['vertex_count']['broken']:,} vertices, {delta['mesh']['face_count']['broken']:,} faces")
        output.append(f"Delta:   Vertices {delta['mesh']['vertex_delta']:+,}, Faces {delta['mesh']['face_delta']:+,}")
        if delta['mesh']['issues']:
            output.append("Issues:")
            for issue in delta['mesh']['issues']:
                output.append(f"  - {issue}")
        output.append("")
        
        # Materials section
        output.append("🎨 MATERIALS")
        output.append("-" * 100)
        output.append(f"Working: {delta['materials']['count']['working']} materials")
        output.append(f"Broken:  {delta['materials']['count']['broken']} materials")
        output.append(f"Delta:   {delta['materials']['count']['broken'] - delta['materials']['count']['working']:+d}")
        if delta['materials']['differences']:
            output.append("Differences:")
            for diff in delta['materials']['differences']:
                output.append(f"  • {diff['material']}: {diff['issue']}")
                output.append(f"    Working: {diff['working']}, Broken: {diff['broken']}")
        output.append("")
        
        # Rigging section
        output.append("🦴 RIGGING")
        output.append("-" * 100)
        output.append(f"Working: {delta['rigging']['bone_count']['working']} bones")
        output.append(f"Broken:  {delta['rigging']['bone_count']['broken']} bones")
        output.append(f"Delta:   {delta['rigging']['bone_count']['broken'] - delta['rigging']['bone_count']['working']:+d}")
        if delta['rigging']['issues']:
            output.append("Issues:")
            for issue in delta['rigging']['issues']:
                output.append(f"  • {issue['bone']}: {issue['issue']}")
        output.append("")
        
        # Summary
        output.append("📋 ISSUE SUMMARY")
        output.append("-" * 100)
        output.append(f"Working: {delta['summary']['working_critical']} critical, {delta['summary']['working_warnings']} warnings")
        output.append(f"Broken:  {delta['summary']['broken_critical']} critical, {delta['summary']['broken_warnings']} warnings")
        output.append("")
        output.append("=" * 100)
        
        text = "\n".join(output)
        self.results_text.insert(1.0, text)
        self.results_text.config(state=tk.DISABLED)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = AvatarAnalyzerGUI(root)
    root.mainloop()
