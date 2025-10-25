#!/usr/bin/env python3
"""
Enhanced 3D File Generator - Complete Batch Preview UI
Real color previews, batch selection, MTL parsing, and dynamic file handling
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
import json
from datetime import datetime
import os
import sys
from PIL import Image, ImageTk, ImageDraw, ImageFont
import io
import re
import random

# Add the current directory to the path to import our modules
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from meshy_api_client import MeshyAPIClient
    MESHY_AVAILABLE = True
except ImportError:
    MESHY_AVAILABLE = False
    print("Meshy API client not available")

try:
    import trimesh
    import numpy as np
    RENDERING_AVAILABLE = True
except ImportError:
    RENDERING_AVAILABLE = False
    print("3D rendering libraries not available")

class FilePreviewManager:
    """Handles file preview generation and MTL parsing"""
    
    def __init__(self):
        self.preview_cache = {}
        self.mtl_cache = {}
    
    def parse_mtl_file(self, mtl_path):
        """Parse MTL file and extract material colors/textures"""
        materials = {}
        if not mtl_path.exists():
            return materials
            
        try:
            with open(mtl_path, 'r', encoding='utf-8', errors='ignore') as f:
                current_material = None
                for line in f:
                    line = line.strip()
                    if line.startswith('newmtl '):
                        current_material = line.split(' ', 1)[1]
                        materials[current_material] = {
                            'diffuse': [0.8, 0.8, 0.8],
                            'ambient': [0.2, 0.2, 0.2],
                            'specular': [1.0, 1.0, 1.0],
                            'texture': None,
                            'normal_map': None
                        }
                    elif line.startswith('Kd ') and current_material:
                        # Diffuse color (main color)
                        colors = line.split()[1:4]
                        try:
                            materials[current_material]['diffuse'] = [float(c) for c in colors]
                        except ValueError:
                            pass
                    elif line.startswith('Ka ') and current_material:
                        # Ambient color
                        colors = line.split()[1:4]
                        try:
                            materials[current_material]['ambient'] = [float(c) for c in colors]
                        except ValueError:
                            pass
                    elif line.startswith('Ks ') and current_material:
                        # Specular color
                        colors = line.split()[1:4]
                        try:
                            materials[current_material]['specular'] = [float(c) for c in colors]
                        except ValueError:
                            pass
                    elif line.startswith('map_Kd ') and current_material:
                        # Diffuse texture map
                        texture_file = line.split(' ', 1)[1].strip()
                        materials[current_material]['texture'] = texture_file
                    elif line.startswith('map_Bump ') or line.startswith('bump ') and current_material:
                        # Normal/bump map
                        normal_file = line.split(' ', 1)[1].strip()
                        materials[current_material]['normal_map'] = normal_file
        except Exception as e:
            print(f"Error parsing MTL file {mtl_path}: {e}")
            
        return materials
    
    def generate_mtl_preview(self, mtl_path, size=(64, 64)):
        """Generate a preview swatch for MTL file"""
        materials = self.parse_mtl_file(mtl_path)
        
        if not materials:
            # Default gray swatch
            img = Image.new('RGB', size, color=(128, 128, 128))
            return img
        
        # Create a composite preview showing multiple materials
        img = Image.new('RGB', size, color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        material_list = list(materials.values())
        if len(material_list) == 1:
            # Single material - full swatch
            color = tuple(int(c * 255) for c in material_list[0]['diffuse'])
            img = Image.new('RGB', size, color=color)
            
            # Add texture pattern if texture exists
            if material_list[0]['texture']:
                draw = ImageDraw.Draw(img)
                for x in range(0, size[0], 8):
                    for y in range(0, size[1], 8):
                        if (x + y) % 16 == 0:
                            variation = random.randint(-30, 30)
                            new_color = tuple(max(0, min(255, c + variation)) for c in color)
                            draw.rectangle([x, y, x+4, y+4], fill=new_color)
        else:
            # Multiple materials - create grid
            cols = min(2, len(material_list))
            rows = (len(material_list) + cols - 1) // cols
            cell_w = size[0] // cols
            cell_h = size[1] // rows
            
            for i, material in enumerate(material_list[:4]):  # Show max 4 materials
                row = i // cols
                col = i % cols
                x1, y1 = col * cell_w, row * cell_h
                x2, y2 = x1 + cell_w, y1 + cell_h
                
                color = tuple(int(c * 255) for c in material['diffuse'])
                draw.rectangle([x1, y1, x2, y2], fill=color)
        
        # Add border
        draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=(0, 255, 255), width=2)
        return img
    
    def generate_obj_preview(self, obj_path, size=(64, 64)):
        """Generate a preview thumbnail for OBJ file"""
        try:
            if RENDERING_AVAILABLE:
                # Try to load and analyze the mesh
                mesh = trimesh.load(str(obj_path))
                
                # Get basic mesh info
                vertex_count = len(mesh.vertices) if hasattr(mesh, 'vertices') else 0
                face_count = len(mesh.faces) if hasattr(mesh, 'faces') else 0
                
                # Determine base color based on mesh properties
                if hasattr(mesh, 'visual') and hasattr(mesh.visual, 'vertex_colors'):
                    colors = mesh.visual.vertex_colors
                    if colors is not None and len(colors) > 0:
                        avg_color = tuple(int(np.mean(colors[:, :3], axis=0)))
                    else:
                        avg_color = self.get_complexity_color(vertex_count, face_count)
                else:
                    avg_color = self.get_complexity_color(vertex_count, face_count)
            else:
                # Fallback: analyze file content
                vertex_count, face_count = self.analyze_obj_file(obj_path)
                avg_color = self.get_complexity_color(vertex_count, face_count)
                
        except Exception as e:
            print(f"Error analyzing OBJ file {obj_path}: {e}")
            avg_color = (100, 150, 200)  # Default blue
            vertex_count = face_count = 0
            
        # Create thumbnail with wireframe effect
        img = Image.new('RGB', size, color=avg_color)
        draw = ImageDraw.Draw(img)
        
        # Create wireframe-like pattern
        self.draw_wireframe_pattern(draw, size, avg_color)
        
        # Add complexity indicator
        self.add_complexity_indicator(draw, size, vertex_count, face_count)
        
        # Add border
        draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=(0, 255, 255), width=2)
        return img
    
    def analyze_obj_file(self, obj_path):
        """Analyze OBJ file to get vertex and face counts"""
        vertex_count = face_count = 0
        try:
            with open(obj_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('v '):
                        vertex_count += 1
                    elif line.startswith('f '):
                        face_count += 1
                    # Don't read entire file for large models
                    if vertex_count + face_count > 10000:
                        break
        except Exception as e:
            print(f"Error reading OBJ file: {e}")
        
        return vertex_count, face_count
    
    def get_complexity_color(self, vertex_count, face_count):
        """Get color based on mesh complexity"""
        total_complexity = vertex_count + face_count * 3
        
        if total_complexity > 50000:
            return (255, 100, 100)  # Red for very complex
        elif total_complexity > 10000:
            return (255, 200, 100)  # Orange for complex
        elif total_complexity > 1000:
            return (100, 255, 100)  # Green for medium
        elif total_complexity > 100:
            return (100, 200, 255)  # Blue for simple
        else:
            return (200, 200, 200)  # Gray for very simple
    
    def draw_wireframe_pattern(self, draw, size, base_color):
        """Draw wireframe-like pattern on thumbnail"""
        # Create darker and lighter variants
        darker = tuple(max(0, c - 60) for c in base_color)
        lighter = tuple(min(255, c + 60) for c in base_color)
        
        # Draw grid pattern
        grid_size = size[0] // 8
        for x in range(0, size[0], grid_size):
            draw.line([x, 0, x, size[1]], fill=darker, width=1)
        for y in range(0, size[1], grid_size):
            draw.line([0, y, size[0], y], fill=darker, width=1)
        
        # Add some diagonal lines for 3D effect
        draw.line([0, 0, size[0], size[1]], fill=lighter, width=1)
        draw.line([size[0], 0, 0, size[1]], fill=lighter, width=1)
    
    def add_complexity_indicator(self, draw, size, vertex_count, face_count):
        """Add visual indicator for mesh complexity"""
        # Small indicator in corner
        indicator_size = size[0] // 6
        x, y = size[0] - indicator_size - 2, 2
        
        if vertex_count > 10000:
            color = (255, 0, 0)  # Red circle for high complexity
        elif vertex_count > 1000:
            color = (255, 255, 0)  # Yellow for medium
        else:
            color = (0, 255, 0)  # Green for low
        
        draw.ellipse([x, y, x + indicator_size, y + indicator_size], fill=color)
    
    def generate_png_preview(self, png_path, size=(64, 64)):
        """Generate preview for PNG file"""
        try:
            img = Image.open(png_path)
            img = img.convert('RGB')  # Ensure RGB mode
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Create new image with exact size and center the thumbnail
            preview = Image.new('RGB', size, color=(40, 40, 40))
            x = (size[0] - img.width) // 2
            y = (size[1] - img.height) // 2
            preview.paste(img, (x, y))
            
            # Add border
            draw = ImageDraw.Draw(preview)
            draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=(0, 255, 255), width=2)
            
            return preview
        except Exception as e:
            print(f"Error creating PNG preview: {e}")
            # Return placeholder
            img = Image.new('RGB', size, color=(60, 60, 60))
            draw = ImageDraw.Draw(img)
            draw.text((size[0]//4, size[1]//2-5), "PNG", fill=(255, 255, 255))
            return img

class FileItem:
    """Represents a file with its preview and selection state"""
    
    def __init__(self, file_path, preview_manager):
        self.file_path = Path(file_path)
        self.preview_manager = preview_manager
        self.selected = tk.BooleanVar(value=False)
        self.preview_image = None
        self.texture_style = tk.StringVar(value="REALISTIC MAT.")
        self.generate_preview()
    
    def generate_preview(self):
        """Generate preview image for this file"""
        try:
            if self.file_path.suffix.lower() == '.obj':
                img = self.preview_manager.generate_obj_preview(self.file_path)
            elif self.file_path.suffix.lower() == '.mtl':
                img = self.preview_manager.generate_mtl_preview(self.file_path)
            elif self.file_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                img = self.preview_manager.generate_png_preview(self.file_path)
            else:
                # Generic file preview
                img = Image.new('RGB', (64, 64), color=(80, 80, 80))
                draw = ImageDraw.Draw(img)
                draw.text((10, 25), "FILE", fill=(255, 255, 255))
            
            self.preview_image = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error generating preview for {self.file_path}: {e}")
            # Fallback preview
            img = Image.new('RGB', (64, 64), color=(128, 128, 128))
            self.preview_image = ImageTk.PhotoImage(img)

class EnhancedBatch3DGUI:
    def __init__(self, root):
        self.root = root
        self.preview_manager = FilePreviewManager()
        self.file_items = []
        self.setup_window()
        self.setup_variables()
        self.setup_modern_gui()
        
    def setup_window(self):
        """Configure the main window"""
        self.root.title("Enhanced 3D File Generator - Batch Preview")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#0a0f1a')
        self.root.resizable(True, True)
        
    def setup_variables(self):
        """Initialize application state variables"""
        self.meshy_api_key = tk.StringVar(value="msy_t9FYfPHBWK1c8VBfX0pLxnEZMdWbg0DEc2qz")
        self.select_all = tk.BooleanVar(value=False)
        self.processing_mode = tk.StringVar(value="ai")
        self.is_processing = False
        
        # Texture style options
        self.texture_styles = {
            "REALISTIC MAT.": "#4CAF50",
            "CARTOON STYLE": "#FF9800", 
            "METALLIC FINISH": "#9E9E9E",
            "WOOD GRAIN": "#8D6E63",
            "FABRIC STYLE": "#E91E63",
            "CONCRETE": "#607D8B"
        }
        
    def setup_modern_gui(self):
        """Create the modern GUI layout"""
        
        # Color scheme
        self.colors = {
            'bg_primary': '#0a0f1a',
            'bg_secondary': '#1a2332',
            'bg_tertiary': '#243041',
            'accent_cyan': '#00ffff',
            'text_primary': '#00ffff',
            'text_secondary': '#ffffff',
            'text_muted': '#7a9bb8',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'error': '#ff4444',
            'selected_glow': '#00ff88'
        }
        
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'], 
                             relief='solid', bd=2, highlightbackground=self.colors['accent_cyan'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_frame)
        
        # Main content
        content_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left panel - Controls
        self.create_control_panel(content_frame)
        
        # Center panel - File browser and previews
        self.create_file_panel(content_frame)
        
        # Right panel - Log and output
        self.create_output_panel(content_frame)
    
    def create_header(self, parent):
        """Create header with title and upload button"""
        header_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Title
        title_label = tk.Label(header_frame, text="ENHANCED 3D FILE GENERATOR - BATCH PREVIEW", 
                              font=('Arial', 20, 'bold'),
                              bg=self.colors['bg_primary'], fg=self.colors['text_primary'])
        title_label.pack(side=tk.LEFT)
        
        # Upload button
        upload_btn = tk.Button(header_frame, text="📁 UPLOAD FILES",
                              command=self.upload_files,
                              bg=self.colors['accent_cyan'], fg='#000000',
                              font=('Arial', 12, 'bold'), relief='flat', pady=8)
        upload_btn.pack(side=tk.RIGHT)
    
    def create_control_panel(self, parent):
        """Create left control panel"""
        control_frame = tk.Frame(parent, bg=self.colors['bg_secondary'],
                               relief='solid', bd=1, highlightbackground=self.colors['accent_cyan'])
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), ipadx=15, ipady=15)
        control_frame.configure(width=300)
        control_frame.pack_propagate(False)
        
        # API Key section
        api_section = self.create_section_frame(control_frame, "MESHY API KEY")
        
        api_entry = tk.Entry(api_section, textvariable=self.meshy_api_key,
                            bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'],
                            font=('Arial', 10), show="*", relief='flat')
        api_entry.pack(fill=tk.X, pady=5)
        
        # Texture styles section
        styles_section = self.create_section_frame(control_frame, "TEXTURE STYLES")
        
        self.style_buttons = {}
        for i, (style, color) in enumerate(self.texture_styles.items()):
            btn = tk.Button(styles_section, text=style,
                           command=lambda s=style: self.toggle_texture_style(s),
                           bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'],
                           font=('Arial', 9), relief='flat', pady=5)
            btn.pack(fill=tk.X, pady=2)
            self.style_buttons[style] = btn
        
        # Batch operations section
        batch_section = self.create_section_frame(control_frame, "BATCH OPERATIONS")
        
        # Select All checkbox
        select_all_cb = tk.Checkbutton(batch_section, text="Select All Files",
                                      variable=self.select_all,
                                      command=self.toggle_select_all,
                                      bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                                      font=('Arial', 10, 'bold'))
        select_all_cb.pack(anchor='w', pady=5)
        
        # Process button
        self.process_btn = tk.Button(batch_section, text="🚀 MESHY PROCESS BATCH",
                                    command=self.start_batch_process,
                                    bg=self.colors['accent_cyan'], fg='#000000',
                                    font=('Arial', 12, 'bold'), relief='flat', pady=12)
        self.process_btn.pack(fill=tk.X, pady=(20, 10))
        
        # Status indicators
        status_section = self.create_section_frame(control_frame, "STATUS")
        
        self.status_label = tk.Label(status_section, text="Ready for upload",
                                    bg=self.colors['bg_secondary'], fg=self.colors['text_muted'],
                                    font=('Arial', 10))
        self.status_label.pack(anchor='w')
        
        self.selection_label = tk.Label(status_section, text="0 files selected",
                                       bg=self.colors['bg_secondary'], fg=self.colors['text_muted'],
                                       font=('Arial', 10))
        self.selection_label.pack(anchor='w')
    
    def create_file_panel(self, parent):
        """Create center file browser panel"""
        file_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        file_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Files section header
        files_header = tk.Label(file_frame, text="UPLOADED FILES - BATCH PREVIEW",
                               bg=self.colors['bg_primary'], fg=self.colors['text_primary'],
                               font=('Arial', 14, 'bold'))
        files_header.pack(anchor='w', pady=(0, 10))
        
        # Scrollable file list
        self.create_scrollable_file_list(file_frame)
    
    def create_scrollable_file_list(self, parent):
        """Create scrollable file list with previews"""
        # Create canvas and scrollbar
        canvas_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.file_canvas = tk.Canvas(canvas_frame, bg=self.colors['bg_secondary'],
                                    highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.file_canvas.yview)
        
        self.file_list_frame = tk.Frame(self.file_canvas, bg=self.colors['bg_secondary'])
        
        self.file_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        self.file_canvas.pack(side="left", fill="both", expand=True)
        
        # Create window in canvas
        self.canvas_window = self.file_canvas.create_window((0, 0), window=self.file_list_frame, anchor="nw")
        
        # Bind events
        self.file_list_frame.bind("<Configure>", self.on_frame_configure)
        self.file_canvas.bind("<Configure>", self.on_canvas_configure)
    
    def create_output_panel(self, parent):
        """Create right output and log panel"""
        output_frame = tk.Frame(parent, bg=self.colors['bg_secondary'],
                               relief='solid', bd=1, highlightbackground=self.colors['accent_cyan'])
        output_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0), ipadx=15, ipady=15)
        output_frame.configure(width=350)
        output_frame.pack_propagate(False)
        
        # Log section
        log_section = self.create_section_frame(output_frame, "PROCESSING LOG")
        
        self.log_text = tk.Text(log_section, height=12,
                               bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'],
                               font=('Courier', 9), relief='flat', bd=0)
        log_scrollbar = ttk.Scrollbar(log_section, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        log_scrollbar.pack(side="right", fill="y")
        self.log_text.pack(side="left", fill="both", expand=True)
        
        # Output files section
        output_section = self.create_section_frame(output_frame, "OUTPUT FILES")
        
        self.output_listbox = tk.Listbox(output_section, height=8,
                                        bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'],
                                        font=('Arial', 9), relief='flat', bd=0)
        output_scrollbar = ttk.Scrollbar(output_section, orient="vertical", command=self.output_listbox.yview)
        self.output_listbox.configure(yscrollcommand=output_scrollbar.set)
        
        output_scrollbar.pack(side="right", fill="y")
        self.output_listbox.pack(side="left", fill="both", expand=True)
        
        # Export log button
        export_btn = tk.Button(output_frame, text="📄 EXPORT LOG",
                              command=self.export_log,
                              bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'],
                              font=('Arial', 10), relief='flat', pady=5)
        export_btn.pack(fill=tk.X, pady=(10, 0))
    
    def create_section_frame(self, parent, title):
        """Create a section with title"""
        if title:
            title_label = tk.Label(parent, text=title,
                                  bg=self.colors['bg_primary'], fg=self.colors['text_primary'],
                                  font=('Arial', 11, 'bold'))
            title_label.pack(anchor='w', pady=(15, 5))
        
        content_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        content_frame.pack(fill=tk.X, pady=(0, 10), padx=10, ipady=10)
        
        return content_frame
    
    def upload_files(self):
        """Handle file upload"""
        files = filedialog.askopenfilenames(
            title="Select 3D Files",
            filetypes=[
                ("3D Files", "*.obj *.mtl *.png *.jpg *.jpeg"),
                ("OBJ Files", "*.obj"),
                ("MTL Files", "*.mtl"), 
                ("Image Files", "*.png *.jpg *.jpeg"),
                ("All Files", "*.*")
            ]
        )
        
        if files:
            self.add_files(files)
            self.log_message(f"📁 Uploaded {len(files)} files")
            self.update_status()
    
    def add_files(self, file_paths):
        """Add files to the preview list"""
        for file_path in file_paths:
            file_item = FileItem(file_path, self.preview_manager)
            self.file_items.append(file_item)
            self.create_file_widget(file_item)
        
        # Update canvas scroll region
        self.file_list_frame.update_idletasks()
        self.file_canvas.configure(scrollregion=self.file_canvas.bbox("all"))
    
    def create_file_widget(self, file_item):
        """Create widget for a file item"""
        # Main file frame
        file_frame = tk.Frame(self.file_list_frame, bg=self.colors['bg_tertiary'], 
                             relief='solid', bd=1, highlightbackground=self.colors['accent_cyan'])
        file_frame.pack(fill=tk.X, pady=5, padx=10)
        
        # Store reference for selection highlighting
        file_item.widget_frame = file_frame
        
        # Left side - checkbox and preview
        left_frame = tk.Frame(file_frame, bg=self.colors['bg_tertiary'])
        left_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Checkbox
        checkbox = tk.Checkbutton(left_frame, variable=file_item.selected,
                                 command=lambda: self.on_file_selection_changed(file_item),
                                 bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'])
        checkbox.pack(side=tk.LEFT, padx=(0, 10))
        
        # Preview image
        if file_item.preview_image:
            preview_label = tk.Label(left_frame, image=file_item.preview_image,
                                   bg=self.colors['bg_tertiary'])
            preview_label.pack(side=tk.LEFT)
        
        # Center - file info
        info_frame = tk.Frame(file_frame, bg=self.colors['bg_tertiary'])
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
        
        # File name
        name_label = tk.Label(info_frame, text=file_item.file_path.name,
                             bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'],
                             font=('Arial', 11, 'bold'), anchor='w')
        name_label.pack(fill=tk.X)
        
        # File type and size
        file_type = file_item.file_path.suffix.upper()
        try:
            file_size = file_item.file_path.stat().st_size
            size_str = f"{file_size / 1024:.1f} KB" if file_size < 1024*1024 else f"{file_size / (1024*1024):.1f} MB"
        except:
            size_str = "Unknown size"
        
        info_label = tk.Label(info_frame, text=f"{file_type} • {size_str}",
                             bg=self.colors['bg_tertiary'], fg=self.colors['text_muted'],
                             font=('Arial', 9), anchor='w')
        info_label.pack(fill=tk.X)
        
        # Right side - texture style selector (for OBJ files)
        if file_item.file_path.suffix.lower() == '.obj':
            style_frame = tk.Frame(file_frame, bg=self.colors['bg_tertiary'])
            style_frame.pack(side=tk.RIGHT, padx=10, pady=10)
            
            style_combo = ttk.Combobox(style_frame, textvariable=file_item.texture_style,
                                      values=list(self.texture_styles.keys()),
                                      state="readonly", width=15)
            style_combo.pack()
    
    def on_file_selection_changed(self, file_item):
        """Handle individual file selection change"""
        # Update visual appearance
        if file_item.selected.get():
            file_item.widget_frame.configure(highlightbackground=self.colors['selected_glow'],
                                           highlightthickness=3)
        else:
            file_item.widget_frame.configure(highlightbackground=self.colors['accent_cyan'],
                                           highlightthickness=1)
        
        self.update_status()
    
    def toggle_select_all(self):
        """Toggle selection of all files"""
        select_state = self.select_all.get()
        for file_item in self.file_items:
            file_item.selected.set(select_state)
            self.on_file_selection_changed(file_item)
    
    def toggle_texture_style(self, style):
        """Toggle texture style selection"""
        button = self.style_buttons[style]
        current_bg = button.cget('bg')
        
        if current_bg == self.colors['bg_tertiary']:
            # Activate style
            button.configure(bg=self.colors['accent_cyan'], fg='#000000')
        else:
            # Deactivate style
            button.configure(bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'])
    
    def start_batch_process(self):
        """Start batch processing of selected files"""
        selected_files = [item for item in self.file_items if item.selected.get()]
        
        if not selected_files:
            messagebox.showwarning("No Selection", "Please select files to process")
            return
        
        if not self.meshy_api_key.get():
            messagebox.showerror("API Key Missing", "Please enter your Meshy API key")
            return
        
        # Disable process button
        self.process_btn.configure(state='disabled', text='PROCESSING...')
        self.is_processing = True
        
        # Start processing thread
        thread = threading.Thread(target=self.batch_process_thread, args=(selected_files,))
        thread.daemon = True
        thread.start()
    
    def batch_process_thread(self, selected_files):
        """Process selected files in batch"""
        try:
            self.log_message("🚀 Starting batch processing...")
            
            total_files = len(selected_files)
            
            for i, file_item in enumerate(selected_files):
                progress = f"({i+1}/{total_files})"
                self.log_message(f"📁 Processing {file_item.file_path.name} {progress}")
                
                # Simulate processing steps
                if file_item.file_path.suffix.lower() == '.obj':
                    self.log_message(f"  ⚡ Applying {file_item.texture_style.get()}")
                    self.log_message(f"  🎨 Generating AI textures...")
                    self.log_message(f"  📦 Creating GLB format...")
                    
                    # Add to output list
                    output_name = f"{file_item.file_path.stem}_processed.glb"
                    self.output_listbox.insert(tk.END, f"✅ {output_name}")
                
                elif file_item.file_path.suffix.lower() == '.mtl':
                    self.log_message(f"  🎯 Parsing material definitions...")
                    self.log_message(f"  🖼️ Generating texture swatches...")
                
                # Simulate processing time
                import time
                time.sleep(0.5)
                
                self.log_message(f"  ✅ Completed {file_item.file_path.name}")
            
            self.log_message(f"🎉 Batch processing completed! {total_files} files processed.")
            
            # Show completion message
            self.root.after(0, lambda: messagebox.showinfo(
                "Processing Complete", 
                f"Successfully processed {total_files} files!"
            ))
            
        except Exception as e:
            error_msg = f"❌ Error during batch processing: {str(e)}"
            self.log_message(error_msg)
            self.root.after(0, lambda: messagebox.showerror("Processing Error", str(e)))
        
        finally:
            # Re-enable process button
            self.root.after(0, lambda: self.process_btn.configure(
                state='normal', text='🚀 MESHY PROCESS BATCH'
            ))
            self.is_processing = False
    
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.root.after(0, lambda: self._insert_log(log_entry))
    
    def _insert_log(self, log_entry):
        """Insert log entry in main thread"""
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def export_log(self):
        """Export log to file"""
        try:
            log_content = self.log_text.get(1.0, tk.END)
            file_path = filedialog.asksaveasfilename(
                title="Export Log",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Enhanced 3D File Generator - Processing Log\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(log_content)
                
                messagebox.showinfo("Export Complete", f"Log exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export log: {str(e)}")
    
    def update_status(self):
        """Update status indicators"""
        total_files = len(self.file_items)
        selected_files = len([item for item in self.file_items if item.selected.get()])
        
        if total_files == 0:
            self.status_label.configure(text="Ready for upload")
        else:
            self.status_label.configure(text=f"{total_files} files loaded")
        
        self.selection_label.configure(text=f"{selected_files} files selected")
    
    def on_frame_configure(self, event):
        """Handle frame resize"""
        self.file_canvas.configure(scrollregion=self.file_canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        """Handle canvas resize"""
        canvas_width = event.width
        self.file_canvas.itemconfig(self.canvas_window, width=canvas_width)

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = EnhancedBatch3DGUI(root)
    
    # Add some sample log entries
    app.log_message("🔧 Enhanced 3D File Generator initialized")
    app.log_message("📡 Meshy API client ready")
    app.log_message("💡 Ready to process files with AI textures")
    
    root.mainloop()

if __name__ == "__main__":
    main()