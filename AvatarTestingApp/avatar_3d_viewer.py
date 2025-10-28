#!/usr/bin/env python3
"""
Avatar 3D Viewer - Renders avatars side-by-side using matplotlib and trimesh
"""

import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import threading
import numpy as np

try:
    import trimesh
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    HAS_3D = True
except ImportError:
    HAS_3D = False


class Avatar3DViewer:
    """3D viewer for avatars side-by-side"""
    
    def __init__(self, working_path, broken_path, working_name, broken_name):
        self.working_path = Path(working_path)
        self.broken_path = Path(broken_path)
        self.working_name = working_name
        self.broken_name = broken_name
        self.working_mesh = None
        self.broken_mesh = None
        
    def load_meshes(self):
        """Load OBJ files"""
        # Find OBJ files
        working_obj = None
        broken_obj = None
        
        for obj_file in self.working_path.glob("*.obj"):
            working_obj = obj_file
            break
        
        for obj_file in self.broken_path.glob("*.obj"):
            broken_obj = obj_file
            break
        
        if working_obj:
            try:
                self.working_mesh = trimesh.load(str(working_obj))
            except Exception as e:
                print(f"Failed to load working mesh: {e}")
        
        if broken_obj:
            try:
                self.broken_mesh = trimesh.load(str(broken_obj))
            except Exception as e:
                print(f"Failed to load broken mesh: {e}")
        
        return self.working_mesh is not None, self.broken_mesh is not None
    
    def create_window(self):
        """Create and display 3D viewer window"""
        if not HAS_3D:
            messagebox.showerror("Error", "Required libraries not installed.\nRun: pip install matplotlib trimesh numpy")
            return
        
        # Load meshes
        working_loaded, broken_loaded = self.load_meshes()
        
        if not working_loaded or not broken_loaded:
            messagebox.showerror("Error", "Failed to load one or both avatar models")
            return
        
        # Create window
        window = tk.Toplevel()
        window.title("Avatar 3D Comparison - Side by Side")
        window.geometry("1600x1000")
        window.configure(bg="#1a1a2e")
        
        # Header
        header = tk.Label(window, text="🎨 Avatar 3D Viewer - Side by Side",
                         font=("Arial", 16, "bold"), bg="#ff6b9d", fg="white", pady=10)
        header.pack(fill=tk.X)
        
        # Status
        status = tk.Label(window, text="Loading 3D models...",
                         font=("Arial", 10), bg="#0f0f1e", fg="#feca57")
        status.pack(fill=tk.X, padx=10, pady=5)
        
        # Create figure with subplots
        fig = Figure(figsize=(16, 10), dpi=80, facecolor='#1a1a2e', edgecolor='#ff6b9d')
        
        # Left subplot (Working)
        ax1 = fig.add_subplot(121, projection='3d', facecolor='#0f0f1e')
        ax1.set_title(f"✓ {self.working_name}", color='#00d084', fontsize=14, fontweight='bold', pad=10)
        
        # Right subplot (Broken)
        ax2 = fig.add_subplot(122, projection='3d', facecolor='#0f0f1e')
        ax2.set_title(f"✗ {self.broken_name}", color='#ff6b6b', fontsize=14, fontweight='bold', pad=10)
        
        # Render working mesh
        if self.working_mesh:
            self._render_mesh(ax1, self.working_mesh, '#00d084')
        
        # Render broken mesh
        if self.broken_mesh:
            self._render_mesh(ax2, self.broken_mesh, '#ff6b6b')
        
        # Embed figure in tkinter
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Info panel at bottom
        info_frame = tk.Frame(window, bg="#0f0f1e", height=150)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        info_frame.pack_propagate(False)
        
        # Add comparison info
        info_text = self._get_comparison_text()
        info_label = tk.Label(info_frame, text=info_text, bg="#0f0f1e", fg="#e0e0e0",
                             font=("Courier", 9), justify=tk.LEFT, anchor=tk.NW)
        info_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        status.config(text="✓ 3D models loaded successfully - Use mouse to rotate, scroll to zoom")
    
    def _render_mesh(self, ax, mesh, color):
        """Render a mesh on the given axes"""
        if mesh is None:
            return
        
        # Handle mesh collections
        if isinstance(mesh, trimesh.base.Trimesh):
            meshes = [mesh]
        else:
            meshes = mesh.split()
        
        # Get bounds for all meshes
        all_bounds = np.array([m.bounds for m in meshes])
        center = all_bounds.mean(axis=0).mean(axis=0)
        extent = (all_bounds[:, 1] - all_bounds[:, 0]).max()
        
        for m in meshes:
            # Get vertices and faces
            vertices = m.vertices
            faces = m.faces
            
            # Plot triangles
            for face in faces:
                tri = vertices[face]
                # Create triangle
                xs = np.append(tri[:, 0], tri[0, 0])
                ys = np.append(tri[:, 1], tri[0, 1])
                zs = np.append(tri[:, 2], tri[0, 2])
                ax.plot(xs, ys, zs, color=color, linewidth=0.1, alpha=0.3)
            
            # Plot vertices as dots
            ax.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2], 
                      c=color, s=0.5, alpha=0.5)
        
        # Set limits and labels
        ax.set_xlim(center[0] - extent/2, center[0] + extent/2)
        ax.set_ylim(center[1] - extent/2, center[1] + extent/2)
        ax.set_zlim(center[2] - extent/2, center[2] + extent/2)
        
        ax.set_xlabel('X', color='#feca57')
        ax.set_ylabel('Y', color='#feca57')
        ax.set_zlabel('Z', color='#feca57')
        
        # Style axes
        ax.tick_params(colors='#feca57', labelsize=8)
        ax.grid(True, color='#333333', alpha=0.3)
    
    def _get_comparison_text(self):
        """Get comparison text"""
        working_verts = len(self.working_mesh.vertices) if self.working_mesh else 0
        working_faces = len(self.working_mesh.faces) if self.working_mesh else 0
        broken_verts = len(self.broken_mesh.vertices) if self.broken_mesh else 0
        broken_faces = len(self.broken_mesh.faces) if self.broken_mesh else 0
        
        return f"""
📊 MESH COMPARISON:
  Working ({self.working_name}):  {working_verts:,} vertices  |  {working_faces:,} faces
  Broken ({self.broken_name}):   {broken_verts:,} vertices  |  {broken_faces:,} faces
  
  Delta: {broken_verts - working_verts:+,} vertices  |  {broken_faces - working_faces:+,} faces

🎯 MOUSE CONTROLS:
  • Left click + drag: Rotate
  • Right click + drag: Zoom
  • Middle click + drag: Pan
        """
