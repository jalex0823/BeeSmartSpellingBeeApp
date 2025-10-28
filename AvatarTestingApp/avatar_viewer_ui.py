#!/usr/bin/env python3
"""
Avatar Viewer UI - Professional side-by-side comparison with full avatar lists
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path
import threading

try:
    import trimesh
    HAS_RENDERING = True
except ImportError:
    HAS_RENDERING = False


class AvatarViewerUI:
    """Professional UI for avatar comparison with visual difference highlighting"""
    
    def __init__(self, root, avatar_base, working_avatars, broken_avatars, 
                 working_analyses=None, broken_analyses=None):
        """
        Initialize the viewer with all avatars
        
        Args:
            root: Tkinter root window
            avatar_base: Path to avatar directory
            working_avatars: List of working avatar names
            broken_avatars: List of broken avatar names
            working_analyses: Dict mapping avatar names to analyses
            broken_analyses: Dict mapping avatar names to analyses
        """
        self.root = root
        self.avatar_base = Path(avatar_base)
        self.working_avatars = sorted(working_avatars)
        self.broken_avatars = sorted(broken_avatars)
        self.working_analyses = working_analyses or {}
        self.broken_analyses = broken_analyses or {}
        
        self.root.title("🎨 Avatar Comparison Viewer")
        self.root.geometry("1800x1200")
        self.root.configure(bg="#1a1a2e")
        
        # Variables for selected avatars
        self.selected_working = tk.StringVar(value=self.working_avatars[0] if self.working_avatars else "")
        self.selected_broken = tk.StringVar(value=self.broken_avatars[0] if self.broken_avatars else "")
        
        # Compare mode toggle
        self.compare_mode = tk.BooleanVar(value=False)
        self.show_suggestions = tk.BooleanVar(value=True)
        
        # Store delta for suggestions
        self.current_delta = None
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the main UI"""
        # Header
        header_frame = tk.Frame(self.root, bg="#ff6b9d", height=60)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame, text="🎨 AVATAR COMPARISON VIEWER",
                               font=("Arial", 18, "bold"), bg="#ff6b9d", fg="white")
        header_label.pack(pady=10)
        
        # Control bar with compare mode options
        control_frame = tk.Frame(self.root, bg="#0f0f1e", height=50)
        control_frame.pack(fill=tk.X, padx=0, pady=0)
        control_frame.pack_propagate(False)
        
        compare_check = tk.Checkbutton(control_frame, text="🔍 Compare Mode (Highlight Diffs)",
                                       variable=self.compare_mode, bg="#0f0f1e", fg="#feca57",
                                       font=("Arial", 10, "bold"), cursor="hand2",
                                       command=self._toggle_compare_mode)
        compare_check.pack(side=tk.LEFT, padx=15, pady=10)
        
        suggestions_check = tk.Checkbutton(control_frame, text="💡 Show Fix Suggestions",
                                          variable=self.show_suggestions, bg="#0f0f1e", fg="#00d084",
                                          font=("Arial", 10, "bold"), cursor="hand2")
        suggestions_check.pack(side=tk.LEFT, padx=5, pady=10)
        
        export_btn = tk.Button(control_frame, text="📊 Export Report", command=self._export_report,
                              bg="#9c27b0", fg="white", font=("Arial", 9, "bold"), 
                              padx=10, pady=5, cursor="hand2")
        export_btn.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Main container
        main_frame = tk.Frame(self.root, bg="#1a1a2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Left side (Working)
        left_frame = tk.Frame(main_frame, bg="#0f0f1e", relief=tk.RAISED, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.left_panel = left_frame
        self._create_avatar_panel(left_frame, self.selected_working, self.working_avatars, 
                                 is_working=True)
        
        # Right side (Broken)
        right_frame = tk.Frame(main_frame, bg="#0f0f1e", relief=tk.RAISED, bd=2)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.right_panel = right_frame
        self._create_avatar_panel(right_frame, self.selected_broken, self.broken_avatars, 
                                 is_working=False)
        
        # Suggestions/Differences panel (right side, collapsible)
        suggestions_frame = tk.Frame(main_frame, bg="#1a1a1a", relief=tk.SUNKEN, bd=1)
        suggestions_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5)
        suggestions_frame.config(width=300)
        
        # Title
        sug_title = tk.Label(suggestions_frame, text="🔧 DIAGNOSTICS & FIXES",
                            bg="#9c27b0", fg="white", font=("Arial", 11, "bold"), pady=8)
        sug_title.pack(fill=tk.X)
        
        # Scrollable suggestions text
        scrollbar = ttk.Scrollbar(suggestions_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.suggestions_text = tk.Text(suggestions_frame, bg="#1a1a1a", fg="#ffd54f",
                                       font=("Courier", 8), yscrollcommand=scrollbar.set,
                                       width=35, height=40)
        self.suggestions_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.suggestions_text.yview)
        
        # Initial message
        self.suggestions_text.insert(1.0, "Select both avatars and enable\nCompare Mode to see diagnostics\nand fix suggestions here.")
        self.suggestions_text.config(state=tk.DISABLED)
    
    def _create_avatar_panel(self, parent, selected_var, avatar_list, is_working):
        """Create a single avatar panel with dropdown"""
        # Header with status
        header_color = "#00d084" if is_working else "#ff6b6b"
        status_icon = "✓ WORKING AVATAR" if is_working else "✗ NON-WORKING AVATAR"
        
        header = tk.Label(parent, text=status_icon, bg=header_color, fg="black",
                         font=("Arial", 12, "bold"), pady=10)
        header.pack(fill=tk.X)
        
        # Avatar selector dropdown
        selector_frame = tk.Frame(parent, bg="#0f0f1e")
        selector_frame.pack(fill=tk.X, padx=10, pady=10)
        
        label = tk.Label(selector_frame, text="Select Avatar:", bg="#0f0f1e", fg="#feca57",
                        font=("Arial", 10, "bold"))
        label.pack(anchor=tk.W, pady=(0, 5))
        
        selector = ttk.Combobox(selector_frame, textvariable=selected_var, state="readonly",
                               values=avatar_list, width=40)
        selector.pack(fill=tk.X)
        selector.bind("<<ComboboxSelected>>", 
                     lambda e: self._on_avatar_changed(selected_var, is_working))
        
        # 3D Preview area
        preview_frame = tk.Frame(parent, bg="#1a1a2e", height=350, relief=tk.SUNKEN, bd=1)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        preview_frame.pack_propagate(False)
        
        # Store preview frame for updates
        if is_working:
            self.working_preview_frame = preview_frame
        else:
            self.broken_preview_frame = preview_frame
        
        # Load initial preview
        self._load_model_preview(preview_frame, selected_var.get(), is_working)
        
        # Separator
        sep = tk.Frame(parent, bg="#333333", height=2)
        sep.pack(fill=tk.X, padx=10, pady=5)
        
        # File description section
        desc_label = tk.Label(parent, text="AVATAR FILE DESCRIPTION",
                             bg="#0f0f1e", fg="#feca57", font=("Arial", 11, "bold"), pady=5)
        desc_label.pack(fill=tk.X, padx=10)
        
        # Info grid
        info_frame = tk.Frame(parent, bg="#0f0f1e")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create scrollable text for details
        scrollbar = ttk.Scrollbar(info_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        info_text = tk.Text(info_frame, bg="#1a1a2e", fg="#e0e0e0",
                           font=("Courier", 9), yscrollcommand=scrollbar.set,
                           height=20, width=35)
        info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=info_text.yview)
        
        # Store text widget for updates
        if is_working:
            self.working_info_text = info_text
        else:
            self.broken_info_text = info_text
        
        # Populate initial info
        avatar_name = selected_var.get()
        avatar_path = self.avatar_base / avatar_name
        analysis = self.working_analyses.get(avatar_name) if is_working else self.broken_analyses.get(avatar_name)
        info_content = self._get_avatar_info(avatar_path, analysis)
        info_text.insert(1.0, info_content)
        info_text.config(state=tk.DISABLED)
    
    def _on_avatar_changed(self, selected_var, is_working):
        """Handle avatar selection change"""
        avatar_name = selected_var.get()
        avatar_path = self.avatar_base / avatar_name
        
        # Update preview
        preview_frame = self.working_preview_frame if is_working else self.broken_preview_frame
        for widget in preview_frame.winfo_children():
            widget.destroy()
        self._load_model_preview(preview_frame, avatar_name, is_working)
        
        # Update info text
        info_text = self.working_info_text if is_working else self.broken_info_text
        analysis = self.working_analyses.get(avatar_name) if is_working else self.broken_analyses.get(avatar_name)
        info_content = self._get_avatar_info(avatar_path, analysis)
        
        info_text.config(state=tk.NORMAL)
        info_text.delete(1.0, tk.END)
        info_text.insert(1.0, info_content)
        info_text.config(state=tk.DISABLED)
        
        # Update suggestions if compare mode is on
        if self.compare_mode.get():
            self._update_suggestions()
    
    def _toggle_compare_mode(self):
        """Toggle compare mode and update suggestions"""
        if self.compare_mode.get():
            self._update_suggestions()
        else:
            self.suggestions_text.config(state=tk.NORMAL)
            self.suggestions_text.delete(1.0, tk.END)
            self.suggestions_text.insert(1.0, "Compare Mode disabled.\nEnable to see diagnostics.")
            self.suggestions_text.config(state=tk.DISABLED)
    
    def _update_suggestions(self):
        """Generate and display suggestions based on avatar comparison"""
        from avatar_file_parser import AvatarDeltaComparator
        
        working_name = self.selected_working.get()
        broken_name = self.selected_broken.get()
        
        if not working_name or not broken_name:
            return
        
        working_analysis = self.working_analyses.get(working_name)
        broken_analysis = self.broken_analyses.get(broken_name)
        
        if not working_analysis or not broken_analysis:
            return
        
        # Run delta comparison
        delta = AvatarDeltaComparator.compare(working_analysis, broken_analysis)
        self.current_delta = delta
        
        # Generate suggestions
        suggestions = self._generate_fix_suggestions(delta)
        
        # Display in suggestions panel
        self.suggestions_text.config(state=tk.NORMAL)
        self.suggestions_text.delete(1.0, tk.END)
        self.suggestions_text.insert(1.0, suggestions)
        self.suggestions_text.config(state=tk.DISABLED)
    
    def _generate_fix_suggestions(self, delta):
        """Generate intelligent fix suggestions from delta analysis"""
        output = []
        output.append("=" * 33)
        output.append("🔍 DETAILED DIAGNOSTICS")
        output.append("=" * 33)
        output.append("")
        
        # Mesh issues
        output.append("📊 MESH ANALYSIS")
        output.append("-" * 33)
        vertex_delta = delta['mesh']['vertex_delta']
        face_delta = delta['mesh']['face_delta']
        
        if vertex_delta != 0:
            output.append(f"⚠ Vertex count delta: {vertex_delta:+,}")
            if vertex_delta < 0:
                output.append("  FIX: Reimport mesh or check")
                output.append("       for geometry loss")
        
        if face_delta != 0:
            output.append(f"⚠ Face count delta: {face_delta:+,}")
            if face_delta < 0:
                output.append("  FIX: Check for degenerate")
                output.append("       or missing faces")
        
        if delta['mesh']['issues']:
            for issue in delta['mesh']['issues'][:3]:
                output.append(f"⚠ {issue}")
        
        output.append("")
        
        # Material issues
        output.append("🎨 MATERIAL ANALYSIS")
        output.append("-" * 33)
        mat_count_delta = (delta['materials']['count']['broken'] - 
                          delta['materials']['count']['working'])
        
        if mat_count_delta != 0:
            output.append(f"⚠ Material count delta: {mat_count_delta:+d}")
            if mat_count_delta < 0:
                output.append("  FIX: Missing materials in")
                output.append("       broken avatar")
        
        if delta['materials']['differences']:
            output.append(f"⚠ {len(delta['materials']['differences'])} material diffs:")
            for diff in delta['materials']['differences'][:3]:
                output.append(f"  • {diff['material']}")
                output.append(f"    Issue: {diff['issue']}")
                if diff['working'] and not diff['broken']:
                    output.append("    FIX: Add missing texture")
        
        output.append("")
        
        # Rigging issues
        output.append("🦴 RIGGING ANALYSIS")
        output.append("-" * 33)
        bone_delta = (delta['rigging']['bone_count']['broken'] - 
                     delta['rigging']['bone_count']['working'])
        
        if bone_delta != 0:
            output.append(f"⚠ Bone count delta: {bone_delta:+d}")
            if bone_delta < 0:
                output.append("  FIX: Re-rig avatar or")
                output.append("       import skeleton")
        
        if delta['rigging']['issues']:
            for issue in delta['rigging']['issues'][:3]:
                output.append(f"  • {issue['bone']}")
                output.append(f"    {issue['issue']}")
        
        output.append("")
        output.append("=" * 33)
        output.append("💡 COMMON FIXES")
        output.append("=" * 33)
        
        # General recommendations
        critical_count = delta['summary']['broken_critical']
        if critical_count > 0:
            output.append(f"🔴 {critical_count} critical issues")
            output.append("   • Check file integrity")
            output.append("   • Verify all asset links")
        
        if delta['materials']['differences']:
            output.append("🎨 Texture/Material")
            output.append("   • Reimport textures")
            output.append("   • Update MTL references")
        
        if bone_delta != 0:
            output.append("🦴 Rigging")
            output.append("   • Re-export with rig")
            output.append("   • Verify bone weights")
        
        output.append("")
        output.append("📋 Use 'Export Report'")
        output.append("for full diagnostic JSON")
        
        return "\n".join(output)
    
    def _export_report(self):
        """Export diagnostic report to JSON file"""
        import json
        from datetime import datetime
        
        if not self.current_delta:
            self.suggestions_text.config(state=tk.NORMAL)
            self.suggestions_text.insert(1.0, "\n\n⚠ No comparison data.\nRun Compare Mode first.")
            self.suggestions_text.config(state=tk.DISABLED)
            return
        
        working_name = self.selected_working.get()
        broken_name = self.selected_broken.get()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "comparison": {
                "working": working_name,
                "broken": broken_name
            },
            "delta": self.current_delta,
            "suggestions": {
                "mesh": self._generate_mesh_suggestions(self.current_delta),
                "materials": self._generate_material_suggestions(self.current_delta),
                "rigging": self._generate_rigging_suggestions(self.current_delta)
            }
        }
        
        filename = f"avatar_diagnostic_{working_name}_vs_{broken_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.suggestions_text.config(state=tk.NORMAL)
            self.suggestions_text.insert(1.0, f"\n\n✓ Report exported:\n{filename}")
            self.suggestions_text.config(state=tk.DISABLED)
        except Exception as e:
            self.suggestions_text.config(state=tk.NORMAL)
            self.suggestions_text.insert(1.0, f"\n\n✗ Export failed:\n{str(e)}")
            self.suggestions_text.config(state=tk.DISABLED)
    
    def _generate_mesh_suggestions(self, delta):
        """Generate mesh-specific suggestions"""
        suggestions = []
        vertex_delta = delta['mesh']['vertex_delta']
        face_delta = delta['mesh']['face_delta']
        
        if vertex_delta < -1000:
            suggestions.append("Critical: Major vertex loss detected. Reimport model.")
        elif vertex_delta < 0:
            suggestions.append("Minor vertex count difference. May be optimization.")
        
        if face_delta < -1000:
            suggestions.append("Critical: Major face loss. Check for degenerate faces.")
        
        return suggestions or ["Mesh structure appears normal"]
    
    def _generate_material_suggestions(self, delta):
        """Generate material-specific suggestions"""
        suggestions = []
        diffs = delta['materials']['differences']
        
        missing_textures = [d for d in diffs if d['working'] and not d['broken']]
        if missing_textures:
            suggestions.append(f"Add {len(missing_textures)} missing textures")
        
        missing_materials = [d for d in diffs if not d['working'] and d['broken']]
        if missing_materials:
            suggestions.append(f"Remove {len(missing_materials)} extra materials")
        
        return suggestions or ["Materials appear correct"]
    
    def _generate_rigging_suggestions(self, delta):
        """Generate rigging-specific suggestions"""
        suggestions = []
        issues = delta['rigging']['issues']
        
        if not issues:
            return ["Rigging structure appears normal"]
        
        if len(issues) > 5:
            suggestions.append(f"Major rigging mismatch: {len(issues)} issues detected")
            suggestions.append("Consider re-importing rigged model")
        else:
            for issue in issues:
                suggestions.append(f"{issue['bone']}: {issue['issue']}")
        
        return suggestions

    
    def _load_model_preview(self, parent, avatar_name, is_working):
        """Load and display 3D model preview with visual indicators"""
        avatar_path = self.avatar_base / avatar_name
        
        # Find OBJ file
        obj_file = None
        for file in avatar_path.glob("*.obj"):
            obj_file = file
            break
        
        if not obj_file:
            label = tk.Label(parent, text="📦 No 3D Model Found\n(OBJ file missing)",
                           bg="#1a1a2e", fg="#ff6b6b", font=("Arial", 11))
            label.pack(fill=tk.BOTH, expand=True)
            return
        
        # Load mesh info and get analysis for comparison highlighting
        try:
            if not HAS_RENDERING:
                raise ImportError("trimesh not available")
            
            mesh = trimesh.load(str(obj_file))
            vertex_count = len(mesh.vertices)
            face_count = len(mesh.faces)
            
            # Get analysis to check for issues
            analysis = None
            if is_working:
                analysis = self.working_analyses.get(avatar_name)
            else:
                analysis = self.broken_analyses.get(avatar_name)
            
            # Determine status color based on geometry and analysis
            if vertex_count == 0 or face_count == 0:
                color = "#ff6b6b"  # Red - critical
                status = "✗ Empty Mesh"
            elif analysis and analysis.critical_issues:
                color = "#ff9100"  # Orange - warnings
                status = f"⚠ {len(analysis.critical_issues)} Issues"
            elif vertex_count < 1000:
                color = "#ffeb3b"  # Yellow - possibly broken
                status = "⚡ Low Poly"
            else:
                color = "#00d084"  # Green - healthy
                status = "✓ Loaded"
            
            # Highlight if in compare mode with differences
            if self.compare_mode.get() and self.current_delta:
                mesh_issues = self.current_delta['mesh']['issues']
                if mesh_issues:
                    color = "#ff5722"  # Deep orange for comparison issues
                    status = f"⚠ {len(mesh_issues)} Diffs"
            
            info = f"""
📦 3D MODEL LOADED
{'─' * 25}
Vertices: {vertex_count:,}
Faces: {face_count:,}

File: {obj_file.name}
Size: {obj_file.stat().st_size / (1024*1024):.2f} MB

Status: {status}
            """
            
            label = tk.Label(parent, text=info, bg="#1a1a2e", fg=color,
                           font=("Courier", 10), justify=tk.LEFT)
            label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
        except Exception as e:
            label = tk.Label(parent, text=f"❌ Error Loading Model\n{str(e)[:50]}",
                           bg="#1a1a2e", fg="#ff6b6b", font=("Arial", 10))
            label.pack(fill=tk.BOTH, expand=True)
    
    def _get_avatar_info(self, avatar_path, analysis):
        """Get formatted avatar information"""
        info = []
        
        # File info
        info.append("File: " + str(avatar_path.name))
        
        # Find OBJ file
        obj_files = list(avatar_path.glob("*.obj"))
        if obj_files:
            obj_file = obj_files[0]
            info.append("Mesh: " + obj_file.name)
            try:
                if HAS_RENDERING:
                    mesh = trimesh.load(str(obj_file))
                    info.append(f"Vertices: {len(mesh.vertices):,}")
                    info.append(f"Faces: {len(mesh.faces):,}")
            except:
                info.append("Vertices: Unable to load")
                info.append("Faces: Unable to load")
        else:
            info.append("Mesh: None")
        
        # Find MTL file
        mtl_files = list(avatar_path.glob("*.mtl"))
        if mtl_files:
            mtl_file = mtl_files[0]
            info.append("Material: " + mtl_file.name)
        else:
            info.append("Material: None")
        
        # Materials and textures
        info.append("")
        info.append("Type: " + ("PBR Standard" if obj_files else "None"))
        
        # Find textures
        texture_files = list(avatar_path.glob("*.png")) + list(avatar_path.glob("*.jpg")) + list(avatar_path.glob("*.jpeg"))
        if texture_files:
            info.append("")
            info.append("Textures:")
            for tex_file in sorted(texture_files)[:5]:
                info.append("  • " + tex_file.name)
            if len(texture_files) > 5:
                info.append(f"  ... and {len(texture_files) - 5} more")
        
        # Analysis info if provided
        if analysis:
            info.append("")
            info.append("ANALYSIS INFO:")
            if hasattr(analysis, 'mesh') and hasattr(analysis.mesh, 'vertices'):
                info.append(f"Vertices: {analysis.mesh.vertices:,}")
                info.append(f"Faces: {analysis.mesh.faces:,}")
            if hasattr(analysis, 'materials'):
                info.append(f"Materials: {len(analysis.materials)}")
        
        return "\n".join(info)


def show_viewer(avatar_base, working_avatars, broken_avatars, 
                working_analyses=None, broken_analyses=None):
    """Create and show the viewer with all avatars"""
    window = tk.Tk()
    viewer = AvatarViewerUI(window, avatar_base, working_avatars, broken_avatars,
                           working_analyses, broken_analyses)
    window.mainloop()
