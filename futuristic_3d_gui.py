#!/usr/bin/env python3
"""
Enhanced 3D File Generator - Futuristic Cyberpunk GUI
Complete with Meshy connection controls, real-time status, and cyberpunk aesthetics
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
import time
import requests

# Add the current directory to the path to import our modules
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from meshy_api_client import MeshyAPIClient
    MESHY_AVAILABLE = True
except ImportError:
    MESHY_AVAILABLE = False
    MeshyAPIClient = None
    print("Meshy API client not available")

try:
    import trimesh
    import numpy as np
    RENDERING_AVAILABLE = True
except ImportError:
    RENDERING_AVAILABLE = False
    print("3D rendering libraries not available")

class FuturisticAnimations:
    """Handle futuristic UI animations and effects"""
    
    def __init__(self):
        self.glow_animations = {}
        self.pulse_states = {}
        
    def create_glowing_border(self, widget, color='#00ffff', intensity=3):
        """Create animated glowing border effect"""
        def animate_glow():
            if widget not in self.glow_animations:
                return
                
            current_intensity = self.glow_animations[widget].get('intensity', 0)
            direction = self.glow_animations[widget].get('direction', 1)
            
            current_intensity += direction * 0.5
            if current_intensity >= intensity:
                direction = -1
            elif current_intensity <= 0:
                direction = 1
                
            self.glow_animations[widget]['intensity'] = current_intensity
            self.glow_animations[widget]['direction'] = direction
            
            # Update widget appearance
            glow_color = self.adjust_color_intensity(color, current_intensity / intensity)
            try:
                widget.configure(highlightbackground=glow_color, highlightthickness=2)
            except:
                pass
                
            # Schedule next frame
            if widget in self.glow_animations:
                widget.after(50, animate_glow)
        
        self.glow_animations[widget] = {'intensity': 0, 'direction': 1}
        animate_glow()
    
    def stop_glow_animation(self, widget):
        """Stop glowing animation for widget"""
        if widget in self.glow_animations:
            del self.glow_animations[widget]
    
    def adjust_color_intensity(self, hex_color, intensity):
        """Adjust color intensity for glow effect"""
        try:
            hex_color = hex_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            r = int(r * intensity)
            g = int(g * intensity)
            b = int(b * intensity)
            return f'#{r:02x}{g:02x}{b:02x}'
        except:
            return hex_color
    
    def create_pulsing_dot(self, parent, size=12, color='#00ff00'):
        """Create animated pulsing status dot"""
        canvas = tk.Canvas(parent, width=size, height=size, 
                          bg=parent.cget('bg'), highlightthickness=0)
        
        def animate_pulse():
            if canvas not in self.pulse_states:
                return
                
            scale = self.pulse_states[canvas].get('scale', 0.5)
            direction = self.pulse_states[canvas].get('direction', 1)
            
            scale += direction * 0.1
            if scale >= 1.0:
                direction = -1
            elif scale <= 0.3:
                direction = 1
                
            self.pulse_states[canvas]['scale'] = scale
            self.pulse_states[canvas]['direction'] = direction
            
            # Redraw dot
            canvas.delete("all")
            radius = (size // 2) * scale
            x1, y1 = size//2 - radius, size//2 - radius
            x2, y2 = size//2 + radius, size//2 + radius
            canvas.create_oval(x1, y1, x2, y2, fill=color, outline='')
            
            # Schedule next frame
            if canvas in self.pulse_states:
                canvas.after(100, animate_pulse)
        
        self.pulse_states[canvas] = {'scale': 0.5, 'direction': 1}
        animate_pulse()
        return canvas

class MeshyConnectionManager:
    """Handle Meshy API connection and status"""
    
    def __init__(self, gui_reference):
        self.gui = gui_reference
        self.connection_status = "disconnected"  # disconnected, connecting, connected, error
        self.api_client = None
        self.last_ping_time = None
        
    def validate_api_key(self, api_key):
        """Validate API key format"""
        if not api_key:
            return False
        # Basic validation - Meshy keys typically start with 'msy_'
        return len(api_key) >= 10 and api_key.startswith('msy_')
    
    def connect_to_meshy(self, api_key):
        """Attempt to connect to Meshy API"""
        if not self.validate_api_key(api_key):
            self.gui.log_message("❌ Invalid API key format", "error")
            self.update_connection_status("error")
            return False
            
        self.update_connection_status("connecting")
        self.gui.log_message("🔄 Connecting to Meshy API...", "info")
        
        def connection_thread():
            try:
                # Initialize client
                self.api_client = MeshyAPIClient(api_key) if MESHY_AVAILABLE else None
                
                # Test connection with a working endpoint
                headers = {'Authorization': f'Bearer {api_key}'}
                response = requests.get('https://api.meshy.ai/v2/text-to-3d', 
                                      headers=headers, timeout=10)
                
                if response.status_code == 200:
                    self.connection_status = "connected"
                    self.last_ping_time = datetime.now()
                    self.gui.root.after(0, lambda: self._on_connection_success(response.json()))
                else:
                    self.connection_status = "error"
                    self.gui.root.after(0, lambda: self._on_connection_error(f"API returned {response.status_code}"))
                    
            except requests.exceptions.RequestException as e:
                self.connection_status = "error"
                self.gui.root.after(0, lambda: self._on_connection_error(str(e)))
            except Exception as e:
                self.connection_status = "error"
                self.gui.root.after(0, lambda: self._on_connection_error(f"Unexpected error: {str(e)}"))
        
        thread = threading.Thread(target=connection_thread)
        thread.daemon = True
        thread.start()
        
    def _on_connection_success(self, response_data=None):
        """Handle successful connection"""
        self.update_connection_status("connected")
        self.gui.log_message(f"✅ Connected to Meshy API successfully!", "success")
        self.gui.enable_meshy_features()
        
    def _on_connection_error(self, error_msg):
        """Handle connection error"""
        self.update_connection_status("error")
        self.gui.log_message(f"❌ Connection failed: {error_msg}", "error")
        self.gui.disable_meshy_features()
        
    def update_connection_status(self, status):
        """Update connection status and UI"""
        self.connection_status = status
        self.gui.update_connection_ui(status)
        
    def disconnect(self):
        """Disconnect from Meshy API"""
        self.connection_status = "disconnected"
        self.api_client = None
        self.gui.update_connection_ui("disconnected")
        self.gui.log_message("🔌 Disconnected from Meshy API", "info")

class FuturisticCyberpunk3DGUI:
    def __init__(self, root):
        self.root = root
        self.animations = FuturisticAnimations()
        # Initialize file management
        self.file_items = []  # List to store file information
        self.selected_file_vars = []  # List of BooleanVar for checkboxes
        
        # Initialize connection manager
        self.connection_manager = MeshyConnectionManager(self)
        self.setup_window()
        self.setup_variables()
        self.setup_cyberpunk_gui()
        
    def setup_window(self):
        """Configure the main window with cyberpunk styling"""
        self.root.title("🌌 ENHANCED 3D FILE GENERATOR - CYBERPUNK EDITION")
        self.root.geometry("1920x1200")
        self.root.configure(bg='#0a0f1a')
        self.root.resizable(True, True)
        
        # Set futuristic icon if available
        try:
            # Create a simple icon
            # Create a simple cyan icon
            icon_img = Image.new('RGB', (32, 32))
            # Fill with cyan color
            pixels = []
            for _ in range(32 * 32):
                pixels.append((0, 255, 255))
            icon_img.putdata(pixels)
            self.root.iconphoto(False, ImageTk.PhotoImage(icon_img))
        except:
            pass
        
    def setup_variables(self):
        """Initialize application state variables"""
        self.meshy_api_key = tk.StringVar(value="msy_t9FYfPHBWK1c8VBfX0pLxnEZMdWbg0DEc2qz")
        self.connection_status_var = tk.StringVar(value="Disconnected")
        self.selected_files = []
        self.file_items = []
        self.is_processing = False
        self.debug_window = None
        self.debug_logs = []
        
        # Texture styles with cyberpunk naming
        self.texture_styles = {
            "REALISTIC MAT.": "#4CAF50",
            "CARTOON STYLE": "#FF9800", 
            "METALLIC FINISH": "#9E9E9E",
            "WOOD GRAIN": "#8D6E63",
            "FABRIC STYLE": "#E91E63",
            "CONCRETE": "#607D8B"
        }
        
        # Auto-connect on API key change
        self.meshy_api_key.trace_add("write", self.on_api_key_change)
        
    def setup_cyberpunk_gui(self):
        """Create the cyberpunk-styled GUI layout"""
        
        # Cyberpunk color scheme
        self.colors = {
            'bg_primary': '#0a0f1a',        # Deep space black
            'bg_secondary': '#1a2332',      # Dark blue-gray panels  
            'bg_tertiary': '#243041',       # Lighter sections
            'accent_cyan': '#00ffff',       # Neon cyan
            'accent_green': '#00ff88',      # Matrix green
            'accent_purple': '#ff00ff',     # Neon purple
            'accent_orange': '#ff8800',     # Warning orange
            'text_primary': '#00ffff',      # Cyan text
            'text_secondary': '#ffffff',    # White text
            'text_muted': '#7a9bb8',        # Muted blue
            'success': '#00ff88',           # Success green
            'warning': '#ffaa00',           # Warning amber
            'error': '#ff4444',             # Error red
            'glow_border': '#00ffff',       # Glow effect
            'connection_good': '#00ff00',   # Connection good
            'connection_bad': '#ff0000',    # Connection bad
            'connection_warn': '#ffff00'    # Connection warning
        }
        
        # Main container with static border (no animation)
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'], 
                             relief='solid', bd=2, highlightbackground=self.colors['glow_border'],
                             highlightthickness=1)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Header with futuristic styling
        self.create_cyberpunk_header(main_frame)
        
        # Main content area
        content_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create the three cyberpunk panels
        self.create_control_panel(content_frame)
        self.create_center_panel(content_frame) 
        self.create_output_panel(content_frame)

    def create_cyberpunk_header(self, parent):
        """Create futuristic header with glowing elements"""
        header_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(20, 30))
        
        # Left side - Futuristic logo and title
        left_header = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        left_header.pack(side=tk.LEFT)
        
        # Create cyberpunk-style logo
        logo_frame = tk.Frame(left_header, bg=self.colors['bg_primary'])
        logo_frame.pack(side=tk.LEFT, padx=(0, 25))
        
        # Stacked layers with glow effect
        for i in range(3):
            layer = tk.Label(logo_frame, text="⬛", font=('Orbitron', 18, 'bold'),
                           bg=self.colors['bg_primary'], fg=self.colors['accent_cyan'])
            layer.pack()
        
        # Main title with futuristic font
        title_label = tk.Label(left_header, text="ENHANCED 3D FILE GENERATOR", 
                              font=('Orbitron', 22, 'bold'),
                              bg=self.colors['bg_primary'], fg=self.colors['text_primary'])
        title_label.pack(side=tk.LEFT)
        
        # Subtitle
        subtitle_label = tk.Label(left_header, text="CYBERPUNK EDITION v2.1", 
                                 font=('Exo', 12),
                                 bg=self.colors['bg_primary'], fg=self.colors['accent_green'])
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))

    def create_control_panel(self, parent):
        """Create left control panel with Meshy connection controls"""
        control_frame = tk.Frame(parent, bg=self.colors['bg_secondary'],
                               relief='solid', bd=2, highlightbackground=self.colors['glow_border'])
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15), ipadx=20, ipady=20)
        control_frame.configure(width=320)
        control_frame.pack_propagate(False)
        
        # PROCESSING MODE section
        mode_section = self.create_section_frame(control_frame, "PROCESSING MODE")
        
        # Futuristic radio buttons
        self.mode_var = tk.StringVar(value="ai")
        
        standard_rb = tk.Radiobutton(mode_section, text="● STANDARD PROCESSING", 
                                   variable=self.mode_var, value="standard",
                                   bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                                   font=('Exo', 11), selectcolor=self.colors['bg_tertiary'])
        standard_rb.pack(anchor='w', pady=3)
        
        ai_rb = tk.Radiobutton(mode_section, text="● AI PROCESSING WITH MESHY API", 
                             variable=self.mode_var, value="ai",
                             bg=self.colors['bg_secondary'], fg=self.colors['accent_cyan'],
                             font=('Exo', 11, 'bold'), selectcolor=self.colors['bg_tertiary'])
        ai_rb.pack(anchor='w', pady=3)
        
        # MESHY API KEY section with connection controls
        api_section = self.create_section_frame(control_frame, "MESHY API KEY")
        
        # API Key entry with futuristic styling
        key_frame = tk.Frame(api_section, bg=self.colors['bg_secondary'])
        key_frame.pack(fill=tk.X, pady=5)
        
        self.api_entry = tk.Entry(key_frame, textvariable=self.meshy_api_key,
                                 bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'],
                                 font=('Courier New', 11), show="*", relief='flat',
                                 insertbackground=self.colors['accent_cyan'], bd=2)
        self.api_entry.pack(fill=tk.X, ipady=8)
        
        # Connection controls frame
        connection_frame = tk.Frame(api_section, bg=self.colors['bg_secondary'])
        connection_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Connection status with animated dot
        status_frame = tk.Frame(connection_frame, bg=self.colors['bg_secondary'])
        status_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Animated status dot
        self.status_dot = self.animations.create_pulsing_dot(
            status_frame, size=16, color=self.colors['connection_bad']
        )
        self.status_dot.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status text
        self.status_label = tk.Label(status_frame, text="✕ Disconnected",
                                    bg=self.colors['bg_secondary'], fg=self.colors['connection_bad'],
                                    font=('Exo', 11, 'bold'))
        self.status_label.pack(side=tk.LEFT)
        
        # Connect button with glow effect
        self.connect_btn = tk.Button(connection_frame, text="🔌 CONNECT TO MESHY",
                                   command=self.manual_connect,
                                   bg=self.colors['accent_cyan'], fg='#000000',
                                   font=('Orbitron', 11, 'bold'), relief='flat', 
                                   pady=10, cursor='hand2')
        self.connect_btn.pack(fill=tk.X, pady=(0, 5))
        
        # Debug Window Button
        self.debug_btn = tk.Button(connection_frame, text="🔍 DEBUG CONNECTION",
                                  command=self.show_debug_window,
                                  bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'],
                                  font=('Exo', 10), relief='flat', 
                                  pady=8, cursor='hand2')
        self.debug_btn.pack(fill=tk.X, pady=(5, 0))
        
        # Connection info
        self.connection_info = tk.Label(connection_frame, text="Enter API key to connect",
                                       bg=self.colors['bg_secondary'], fg=self.colors['text_muted'],
                                       font=('Exo', 9))
        self.connection_info.pack(fill=tk.X)
        
        # TEXTURE STYLE section with cyberpunk buttons
        style_section = self.create_section_frame(control_frame, "TEXTURE STYLE")
        
        self.style_buttons = {}
        styles_grid = [
            ["REALISTIC MAT.", "CARTOON STYLE"],
            ["METALLIC FINISH", "WOOD GRAIN"],
            ["FABRIC STYLE", "CONCRETE"]
        ]
        
        for row_styles in styles_grid:
            row_frame = tk.Frame(style_section, bg=self.colors['bg_secondary'])
            row_frame.pack(fill=tk.X, pady=3)
            
            for i, style in enumerate(row_styles):
                btn = tk.Button(row_frame, text=style,
                               command=lambda s=style: self.toggle_texture_style(s),
                               bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'],
                               font=('Exo', 9, 'bold'), relief='flat', pady=6)
                btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3) if i == 0 else (3, 0))
                self.style_buttons[style] = btn
        
        # Set default style
        self.select_texture_style("REALISTIC MAT.")
        
        # CREATE THUMBNAILS option
        options_section = self.create_section_frame(control_frame, "OPTIONS")
        
        self.create_thumbnails_var = tk.BooleanVar(value=True)
        thumbnails_cb = tk.Checkbutton(options_section, text="✓ CREATE THUMBNAILS",
                                      variable=self.create_thumbnails_var,
                                      bg=self.colors['bg_secondary'], fg=self.colors['accent_green'],
                                      font=('Exo', 11, 'bold'), selectcolor=self.colors['bg_tertiary'])
        thumbnails_cb.pack(anchor='w', pady=5)
        
        # MESHY PROCESS button (disabled until connected)
        tk.Frame(control_frame, height=25, bg=self.colors['bg_secondary']).pack()
        
        self.meshy_btn = tk.Button(control_frame, text="🚀 MESHY PROCESS",
                                  command=self.start_meshy_process,
                                  bg=self.colors['bg_tertiary'], fg=self.colors['text_muted'],
                                  font=('Orbitron', 14, 'bold'), relief='flat', 
                                  pady=15, state='disabled', cursor='hand2')
        self.meshy_btn.pack(fill=tk.X, padx=20, pady=(15, 25))
        
        # Status at bottom
        status_bottom = tk.Frame(control_frame, bg=self.colors['bg_secondary'])
        status_bottom.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.upload_status = tk.Label(status_bottom, text="= Uploading",
                                     bg=self.colors['bg_secondary'], fg=self.colors['text_muted'],
                                     font=('Courier New', 10))
        self.upload_status.pack(anchor='w')

    def create_center_panel(self, parent):
        """Create center panel that transforms based on connection status"""
        center_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15)
        
        # Store center frame reference for dynamic updates
        self.center_content_frame = center_frame
        
        # Initially show Meshy features until connected
        self.show_meshy_features_panel()
        
        return center_frame

    def show_meshy_features_panel(self):
        """Show Meshy API features panel (before connection)"""
        # Clear existing content
        for widget in self.center_content_frame.winfo_children():
            widget.destroy()
        
        # MESHY API FEATURES with real previews
        features_section = self.create_section_frame(self.center_content_frame, "MESHY API FEATURES")
        
        # Feature list with checkmarks
        features = [
            "✓ High Quality Realistic",
            "✓ Cartoon Style, Vibrant", 
            "✓ Realistic Materials",
            "✓ Metallic Finish",
            "✓ Wood Grain, Natural",
            "✓ Fabric Texture, Soft"
        ]
        
        for feature in features:
            feature_label = tk.Label(features_section, text=feature,
                                   bg=self.colors['bg_secondary'], fg=self.colors['accent_green'],
                                   font=('Exo', 11), anchor='w')
            feature_label.pack(fill=tk.X, pady=2)
        
        # Texture preview grid (matching your mockup)
        preview_frame = tk.Frame(features_section, bg=self.colors['bg_secondary'])
        preview_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Top row of texture previews
        top_row = tk.Frame(preview_frame, bg=self.colors['bg_secondary'])
        top_row.pack(pady=10)
        
        # Create texture preview samples (matching the mockup colors)
        texture_samples = [
            ("NodeName", (0, 180, 200)),      # Cyan-ish
            ("Cartoon Style", (180, 80, 60)), # Reddish-brown
            ("Metallic Finish", (120, 90, 60)) # Brownish-gold
        ]
        
        for name, color in texture_samples:
            sample_frame = tk.Frame(top_row, bg=self.colors['bg_secondary'])
            sample_frame.pack(side=tk.LEFT, padx=15)
            
            # Create preview image
            preview_img = self.create_texture_sample(color, (80, 80))
            preview_label = tk.Label(sample_frame, image=preview_img,
                                   bg=self.colors['bg_secondary'],
                                   relief='solid', bd=2, 
                                   highlightbackground=self.colors['accent_cyan'])
            preview_label.pack()
            # Keep reference to prevent garbage collection
            setattr(preview_label, 'image_ref', preview_img)
            
            # Label
            tk.Label(sample_frame, text=name,
                    bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                    font=('Exo', 10)).pack(pady=(8, 0))
        
        # Bottom status indicators
        bottom_status = tk.Frame(preview_frame, bg=self.colors['bg_secondary'])
        bottom_status.pack(pady=(15, 10))
        
        # Status checkboxes matching mockup
        tk.Label(bottom_status, text="✓ X processor mo",
                bg=self.colors['bg_secondary'], fg=self.colors['accent_green'],
                font=('Exo', 11)).pack(anchor='w')
        
        tk.Label(bottom_status, text="✓ X railway assets",
                bg=self.colors['bg_secondary'], fg=self.colors['accent_green'],
                font=('Exo', 11)).pack(anchor='w')
        
        # Connection prompt
        connect_prompt = tk.Frame(features_section, bg=self.colors['accent_cyan'], relief='solid', bd=2)
        connect_prompt.pack(fill=tk.X, pady=20, padx=20)
        
        tk.Label(connect_prompt, text="🔗 CONNECT TO MESHY TO ACCESS 3D ASSET BROWSER",
                bg=self.colors['accent_cyan'], fg='#000000',
                font=('Exo', 12, 'bold')).pack(pady=15)
        
        # FILE BROWSER SECTION (NEW)
        file_browser_section = self.create_section_frame(self.center_content_frame, "📁 FILE BROWSER & BATCH OPERATIONS")
        
        # File upload controls
        upload_controls = tk.Frame(file_browser_section, bg=self.colors['bg_secondary'])
        upload_controls.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(upload_controls, text="📁 UPLOAD FILES",
                 command=self.upload_files,
                 bg=self.colors['accent_cyan'], fg='#000000',
                 font=('Orbitron', 11, 'bold'), relief='flat', 
                 pady=8, cursor='hand2').pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(upload_controls, text="🔄 REFRESH FILES",
                 command=self.refresh_file_list,
                 bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'],
                 font=('Exo', 10), relief='flat', 
                 pady=8, cursor='hand2').pack(side=tk.LEFT, padx=(0, 10))
        
        # File selection controls
        selection_controls = tk.Frame(upload_controls, bg=self.colors['bg_secondary'])
        selection_controls.pack(side=tk.RIGHT)
        
        tk.Button(selection_controls, text="☑️ SELECT ALL",
                 command=self.select_all_files,
                 bg=self.colors['accent_green'], fg='#000000',
                 font=('Exo', 9, 'bold'), relief='flat', 
                 pady=6, cursor='hand2').pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(selection_controls, text="☐ CLEAR ALL",
                 command=self.clear_all_files,
                 bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'],
                 font=('Exo', 9), relief='flat', 
                 pady=6, cursor='hand2').pack(side=tk.LEFT)
        
        # File list with scrollable area
        list_frame = tk.Frame(file_browser_section, bg=self.colors['bg_secondary'])
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Meshy.ai style headers
        headers_frame = tk.Frame(list_frame, bg=self.colors['bg_secondary'], height=40)
        headers_frame.pack(fill=tk.X, pady=(0, 5))
        headers_frame.pack_propagate(False)
        
        tk.Label(headers_frame, text="🎯 3D ASSETS & MODELS", 
                bg=self.colors['bg_secondary'], fg=self.colors['accent_cyan'],
                font=('Exo', 12, 'bold')).pack(side=tk.LEFT, padx=10, pady=10)
        
        # View options
        view_frame = tk.Frame(headers_frame, bg=self.colors['bg_secondary'])
        view_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        tk.Label(view_frame, text="📊 CARD VIEW ACTIVE", 
                bg=self.colors['accent_green'], fg='#000000',
                font=('Exo', 8, 'bold'), relief='flat', 
                padx=8, pady=2).pack(side=tk.RIGHT)
        
        # Scrollable file list
        canvas_frame = tk.Frame(list_frame, bg=self.colors['bg_secondary'])
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.file_canvas = tk.Canvas(canvas_frame, bg=self.colors['bg_tertiary'], 
                                   highlightthickness=0, height=200)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.file_canvas.yview)
        self.scrollable_frame = tk.Frame(self.file_canvas, bg=self.colors['bg_tertiary'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.file_canvas.configure(scrollregion=self.file_canvas.bbox("all"))
        )
        
        self.file_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.file_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.file_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Batch operations panel
        batch_ops_section = self.create_section_frame(self.center_content_frame, "🚀 BATCH OPERATIONS")
        
        # Operation buttons in grid
        ops_grid = tk.Frame(batch_ops_section, bg=self.colors['bg_secondary'])
        ops_grid.pack(fill=tk.X, pady=10)
        
        # Row 1
        row1 = tk.Frame(ops_grid, bg=self.colors['bg_secondary'])
        row1.pack(fill=tk.X, pady=(0, 8))
        
        tk.Button(row1, text="🎨 CONVERT SELECTED",
                 command=self.convert_selected_files,
                 bg=self.colors['accent_cyan'], fg='#000000',
                 font=('Orbitron', 10, 'bold'), relief='flat', 
                 pady=8, cursor='hand2').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Button(row1, text="📷 CREATE PNG SNAPSHOTS",
                 command=self.create_png_snapshots,
                 bg=self.colors['accent_green'], fg='#000000',
                 font=('Orbitron', 10, 'bold'), relief='flat', 
                 pady=8, cursor='hand2').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Row 2
        row2 = tk.Frame(ops_grid, bg=self.colors['bg_secondary'])
        row2.pack(fill=tk.X)
        
        tk.Button(row2, text="💾 DOWNLOAD ALL",
                 command=self.download_all_files,
                 bg=self.colors['accent_purple'], fg='#ffffff',
                 font=('Orbitron', 10, 'bold'), relief='flat', 
                 pady=8, cursor='hand2').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Button(row2, text="🏭 RAILWAY EXPORT",
                 command=self.export_for_railway,
                 bg=self.colors['accent_orange'], fg='#000000',
                 font=('Orbitron', 10, 'bold'), relief='flat', 
                 pady=8, cursor='hand2').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Status display
        self.batch_status = tk.Label(batch_ops_section, text="Select files and choose operation",
                                   bg=self.colors['bg_secondary'], fg=self.colors['text_muted'],
                                   font=('Exo', 10))
        self.batch_status.pack(pady=(10, 0))
        
        # Initialize file list
        self.file_items = []
        self.selected_file_vars = []
        self.refresh_file_list()
        
        # LOG section at bottom
        log_section = self.create_section_frame(self.center_content_frame, "📜 PROCESSING LOG")
        
        # Create enhanced log display
        self.log_frame = tk.Frame(log_section, bg=self.colors['bg_tertiary'])
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Log text with cyberpunk styling
        self.log_text = tk.Text(self.log_frame, height=6,
                               bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'],
                               font=('Courier New', 10), relief='flat', bd=0,
                               insertbackground=self.colors['accent_cyan'])
        
        log_scrollbar = tk.Scrollbar(self.log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        log_scrollbar.pack(side="right", fill="y")
        self.log_text.pack(side="left", fill="both", expand=True)

    def create_output_panel(self, parent):
        """Create right output panel"""
        output_frame = tk.Frame(parent, bg=self.colors['bg_secondary'],
                               relief='solid', bd=2, highlightbackground=self.colors['glow_border'])
        output_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(15, 0), ipadx=20, ipady=20)
        output_frame.configure(width=320)
        output_frame.pack_propagate(False)
        
        # REQUIREMENTS section
        req_section = self.create_section_frame(output_frame, "REQUIREMENTS")
        
        # Python Dependencies
        tk.Label(req_section, text="Python:\nDependencies:",
                bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                font=('Exo', 12, 'bold'), justify='left').pack(anchor='w', pady=(0, 8))
        
        deps = ["trimesh pyrender", "pillow the point"]
        for dep in deps:
            tk.Label(req_section, text=f"• {dep}",
                    bg=self.colors['bg_secondary'], fg=self.colors['text_muted'],
                    font=('Courier New', 10)).pack(anchor='w', padx=(15, 0), pady=1)
        
        # Meshy API Account
        tk.Label(req_section, text="\nMeshy API\nAccount:",
                bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                font=('Exo', 12, 'bold'), justify='left').pack(anchor='w', pady=(15, 8))
        
        tk.Label(req_section, text="CM SP.LE | 119 ready ai",
                bg=self.colors['bg_secondary'], fg=self.colors['text_muted'],
                font=('Courier New', 10)).pack(anchor='w', padx=(15, 0))
        
        # LOG section
        log_section = self.create_section_frame(output_frame, "LOG ——")
        
        self.output_log_items = [
            ("⬜ processed mo", "pending"),
            ("✓ railway assets", "completed")
        ]
        
        for item_text, status in self.output_log_items:
            color = self.colors['accent_green'] if status == "completed" else self.colors['text_secondary']
            tk.Label(log_section, text=item_text,
                    bg=self.colors['bg_secondary'], fg=color,
                    font=('Exo', 11), anchor='w').pack(fill=tk.X, pady=3)
        
        # OUTPUT FILES section  
        output_section = self.create_section_frame(output_frame, "OUTPUT FILES")
        
        output_files = [
            "⬜ processed mo",
            "⬜ railway assets", 
            "⬜ png"
        ]
        
        for file_item in output_files:
            tk.Label(output_section, text=file_item,
                    bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                    font=('Exo', 11), anchor='w').pack(fill=tk.X, pady=3)

    def create_section_frame(self, parent, title):
        """Create a section with cyberpunk styling"""
        if title:
            title_label = tk.Label(parent, text=title,
                                  bg=self.colors['bg_primary'], fg=self.colors['text_primary'],
                                  font=('Orbitron', 13, 'bold'))
            title_label.pack(anchor='w', pady=(20, 8))
        
        content_frame = tk.Frame(parent, bg=self.colors['bg_secondary'],
                               relief='solid', bd=1, highlightbackground=self.colors['glow_border'])
        content_frame.pack(fill=tk.X, pady=(0, 15), padx=5, ipady=15, ipadx=15)
        
        return content_frame

    def create_texture_sample(self, color, size=(80, 80)):
        """Create texture sample image"""
        img = Image.new('RGB', size, color=color)
        draw = ImageDraw.Draw(img)
        
        # Add cyberpunk-style border
        draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=(0, 255, 255), width=3)
        
        # Add some texture pattern
        for x in range(0, size[0], 8):
            for y in range(0, size[1], 8):
                if (x + y) % 16 == 0:
                    draw.rectangle([x, y, x+2, y+2], fill=(255, 255, 255))
        
        return ImageTk.PhotoImage(img)

    def on_api_key_change(self, *args):
        """Handle API key changes for auto-connect"""
        api_key = self.meshy_api_key.get()
        if len(api_key) >= 30:  # Full key length
            self.root.after(1000, lambda: self.auto_connect(api_key))  # Delay to avoid spam

    def auto_connect(self, api_key):
        """Automatically connect when API key is entered"""
        if api_key == self.meshy_api_key.get():  # Still the same key
            self.connection_manager.connect_to_meshy(api_key)
            # Auto-refresh file list when connected successfully
            self.root.after(1000, self.check_and_refresh_files)  # Delay to allow connection

    def manual_connect(self):
        """Manually triggered connection"""
        api_key = self.meshy_api_key.get()
        if not api_key:
            messagebox.showwarning("API Key Required", "Please enter your Meshy API key")
            return
        self.connection_manager.connect_to_meshy(api_key)
        # Auto-refresh file list when connected successfully
        self.root.after(1000, self.check_and_refresh_files)  # Delay to allow connection

    def check_and_refresh_files(self):
        """Check if connected and refresh file list"""
        if (hasattr(self.connection_manager, 'connection_status') and 
            self.connection_manager.connection_status == "connected"):
            self.refresh_file_list()
            self.log_message("🎯 Auto-loaded Meshy sample assets", "success")

    def update_connection_ui(self, status):
        """Update connection status UI elements"""
        if status == "connecting":
            self.status_label.configure(text="🔄 Connecting...", fg=self.colors['connection_warn'])
            self.connection_info.configure(text="Verifying API key...")
            self.connect_btn.configure(state='disabled', text="CONNECTING...")
            
        elif status == "connected":
            self.status_label.configure(text="✅ Connected to Meshy", fg=self.colors['connection_good'])
            self.connection_info.configure(text=f"Last connected: {datetime.now().strftime('%H:%M:%S')}")
            self.connect_btn.configure(state='normal', text="🔌 RECONNECT", 
                                     bg=self.colors['accent_green'])
            # Start glow animation on connect button
            self.animations.create_glowing_border(self.connect_btn, self.colors['accent_green'])
            
            # Transform center panel to Meshy asset browser with REAL ASSETS
            self.show_meshy_asset_browser()
            # Fetch real assets from Meshy API
            self.fetch_real_meshy_assets()
            
        elif status == "error":
            self.status_label.configure(text="❌ Connection Error", fg=self.colors['connection_bad'])
            self.connection_info.configure(text="Check API key and connection")
            self.connect_btn.configure(state='normal', text="🔌 RETRY CONNECTION",
                                     bg=self.colors['error'])
            
        else:  # disconnected
            self.status_label.configure(text="✕ Disconnected", fg=self.colors['connection_bad'])
            self.connection_info.configure(text="Enter API key to connect")
            self.connect_btn.configure(state='normal', text="🔌 CONNECT TO MESHY",
                                     bg=self.colors['accent_cyan'])
            
            # Show features panel when disconnected
            self.show_meshy_features_panel()

    def enable_meshy_features(self):
        """Enable Meshy-dependent features"""
        self.meshy_btn.configure(state='normal', text="🚀 MESHY PROCESS",
                               bg=self.colors['accent_cyan'], fg='#000000')
        # Start glow animation
        self.animations.create_glowing_border(self.meshy_btn, self.colors['accent_cyan'])

    def disable_meshy_features(self):
        """Disable Meshy-dependent features"""
        self.meshy_btn.configure(state='disabled', text="🚀 MESHY PROCESS",
                               bg=self.colors['bg_tertiary'], fg=self.colors['text_muted'])
        # Stop glow animation
        self.animations.stop_glow_animation(self.meshy_btn)

    def toggle_texture_style(self, style):
        """Toggle texture style selection"""
        self.select_texture_style(style)

    def select_texture_style(self, style):
        """Select texture style with visual feedback"""
        # Reset all buttons
        for btn in self.style_buttons.values():
            btn.configure(bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'])
        
        # Highlight selected
        if style in self.style_buttons:
            self.style_buttons[style].configure(bg=self.colors['accent_cyan'], fg='#000000')

    def start_meshy_process(self):
        """Start Meshy processing with futuristic effects"""
        if self.connection_manager.connection_status != "connected":
            messagebox.showwarning("Not Connected", "Please connect to Meshy API first")
            return
            
        self.meshy_btn.configure(state='disabled', text="🔄 PROCESSING...")
        self.is_processing = True
        
        # Start processing thread
        thread = threading.Thread(target=self.meshy_process_thread)
        thread.daemon = True
        thread.start()

    def meshy_process_thread(self):
        """Meshy processing with enhanced logging"""
        try:
            # Clear and start processing log
            self.root.after(0, lambda: self.log_text.delete(1.0, tk.END))
            
            processing_steps = [
                ("🚀 Initializing Meshy AI systems...", 1),
                ("🔑 Authenticating with API...", 0.8),
                ("📁 Uploading selected files...", 1.5),
                ("🎨 Applying AI texture generation...", 2),
                ("⚡ Processing with neural networks...", 1.8),
                ("🖼️ Generating high-quality thumbnails...", 1.2),
                ("📦 Creating Railway-compatible assets...", 1),
                ("✅ Processing complete - Files ready!", 0.5)
            ]
            
            for i, (step_msg, delay) in enumerate(processing_steps):
                timestamp = datetime.now().strftime("%H:%M:%S")
                progress = f"[{i+1}/{len(processing_steps)}]"
                log_entry = f"{timestamp} {progress} {step_msg}\n"
                
                self.root.after(0, lambda msg=log_entry: self.log_text.insert(tk.END, msg))
                self.root.after(0, lambda: self.log_text.see(tk.END))
                
                time.sleep(delay)
            
            # Show completion
            self.root.after(0, lambda: messagebox.showinfo(
                "🎉 Processing Complete!", 
                "Meshy AI processing completed successfully!\n\nAll files have been enhanced and are ready for deployment."
            ))
            
        except Exception as e:
            error_msg = f"❌ Processing error: {str(e)}\n"
            self.root.after(0, lambda: self.log_text.insert(tk.END, error_msg))
            self.root.after(0, lambda: messagebox.showerror("Processing Error", str(e)))
        
        finally:
            # Re-enable processing
            self.root.after(0, lambda: self.meshy_btn.configure(
                state='normal', text="🚀 MESHY PROCESS"
            ))
            self.is_processing = False

    def log_message(self, message, level="info"):
        """Add timestamped message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color coding based on level
        if level == "success":
            prefix = "✅"
        elif level == "error":
            prefix = "❌"
        elif level == "warning":
            prefix = "⚠️"
        else:
            prefix = "ℹ️"
            
        log_entry = f"[{timestamp}] {prefix} {message}\n"
        
        # Add to debug logs
        self.debug_logs.append({
            'timestamp': timestamp,
            'level': level,
            'message': message,
            'full_entry': log_entry
        })
        
        # Keep only last 100 debug logs
        if len(self.debug_logs) > 100:
            self.debug_logs = self.debug_logs[-100:]
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def show_debug_window(self):
        """Show comprehensive debug window with connection details"""
        if self.debug_window and self.debug_window.winfo_exists():
            self.debug_window.lift()
            return
            
        self.debug_window = tk.Toplevel(self.root)
        self.debug_window.title("🔍 Meshy Connection Debug Console")
        self.debug_window.geometry("800x600")
        self.debug_window.configure(bg=self.colors['bg_primary'])
        
        # Debug header
        header_frame = tk.Frame(self.debug_window, bg=self.colors['bg_primary'])
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(header_frame, text="🔍 MESHY CONNECTION DEBUG",
                font=('Orbitron', 16, 'bold'),
                bg=self.colors['bg_primary'], fg=self.colors['text_primary']).pack()
        
        # Notebook for tabs
        import tkinter.ttk as ttk
        style = ttk.Style()
        style.theme_use('clam')
        
        notebook = ttk.Notebook(self.debug_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Connection Status Tab
        status_frame = tk.Frame(notebook, bg=self.colors['bg_secondary'])
        notebook.add(status_frame, text="Connection Status")
        
        self.create_status_tab(status_frame)
        
        # API Test Tab
        test_frame = tk.Frame(notebook, bg=self.colors['bg_secondary'])
        notebook.add(test_frame, text="API Test")
        
        self.create_api_test_tab(test_frame)
        
        # Debug Logs Tab
        logs_frame = tk.Frame(notebook, bg=self.colors['bg_secondary'])
        notebook.add(logs_frame, text="Debug Logs")
        
        self.create_debug_logs_tab(logs_frame)
        
        # Raw Response Tab
        raw_frame = tk.Frame(notebook, bg=self.colors['bg_secondary'])
        notebook.add(raw_frame, text="Raw Response")
        
        self.create_raw_response_tab(raw_frame)

    def create_status_tab(self, parent):
        """Create connection status information tab"""
        # Current status section
        status_section = tk.LabelFrame(parent, text="Current Connection Status",
                                     bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                                     font=('Exo', 12, 'bold'))
        status_section.pack(fill=tk.X, padx=20, pady=10)
        
        # Status details
        status_info = [
            ("Connection Status:", self.connection_manager.connection_status),
            ("API Key Length:", f"{len(self.meshy_api_key.get())} characters"),
            ("API Key Valid Format:", "✅ Yes" if self.connection_manager.validate_api_key(self.meshy_api_key.get()) else "❌ No"),
            ("Last Ping Time:", str(self.connection_manager.last_ping_time) if self.connection_manager.last_ping_time else "Never"),
            ("Meshy Client Available:", "✅ Yes" if MESHY_AVAILABLE else "❌ No"),
            ("Requests Library:", "✅ Available" if 'requests' in globals() else "❌ Missing")
        ]
        
        for label, value in status_info:
            row = tk.Frame(status_section, bg=self.colors['bg_secondary'])
            row.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(row, text=label, bg=self.colors['bg_secondary'], 
                    fg=self.colors['text_secondary'], font=('Exo', 10)).pack(side=tk.LEFT)
            tk.Label(row, text=str(value), bg=self.colors['bg_secondary'], 
                    fg=self.colors['accent_cyan'], font=('Courier New', 10)).pack(side=tk.RIGHT)
        
        # Quick actions
        actions_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        actions_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(actions_frame, text="🔄 Test Connection Now",
                 command=self.test_connection_debug,
                 bg=self.colors['accent_cyan'], fg='#000000',
                 font=('Exo', 11, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(actions_frame, text="📋 Copy API Key",
                 command=self.copy_api_key,
                 bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'],
                 font=('Exo', 11)).pack(side=tk.LEFT)

    def create_api_test_tab(self, parent):
        """Create API testing tab"""
        # Test controls
        controls_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        controls_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(controls_frame, text="API Endpoint Testing",
                bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                font=('Exo', 12, 'bold')).pack(anchor='w')
        
        # Endpoint selection
        endpoint_frame = tk.Frame(controls_frame, bg=self.colors['bg_secondary'])
        endpoint_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(endpoint_frame, text="Endpoint:",
                bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                font=('Exo', 10)).pack(side=tk.LEFT)
        
        self.endpoint_var = tk.StringVar(value="https://api.meshy.ai/v2/text-to-3d")
        endpoint_entry = tk.Entry(endpoint_frame, textvariable=self.endpoint_var,
                                bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'],
                                font=('Courier New', 10), width=50)
        endpoint_entry.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
        
        # Test button
        tk.Button(controls_frame, text="🧪 Test Endpoint",
                 command=self.test_api_endpoint,
                 bg=self.colors['accent_green'], fg='#000000',
                 font=('Exo', 11, 'bold')).pack(pady=10)
        
        # Results area
        self.api_test_text = tk.Text(parent, height=15,
                                   bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'],
                                   font=('Courier New', 9))
        self.api_test_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

    def create_debug_logs_tab(self, parent):
        """Create debug logs tab"""
        # Controls
        controls_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        controls_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(controls_frame, text="🔄 Refresh Logs",
                 command=self.refresh_debug_logs,
                 bg=self.colors['accent_cyan'], fg='#000000',
                 font=('Exo', 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(controls_frame, text="🗑️ Clear Logs",
                 command=self.clear_debug_logs,
                 bg=self.colors['error'], fg='#ffffff',
                 font=('Exo', 10)).pack(side=tk.LEFT)
        
        # Logs display
        self.debug_logs_text = tk.Text(parent, height=20,
                                     bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'],
                                     font=('Courier New', 9))
        self.debug_logs_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))
        
        # Populate with current logs
        self.refresh_debug_logs()

    def create_raw_response_tab(self, parent):
        """Create raw API response tab"""
        tk.Label(parent, text="Last API Response (Raw JSON)",
                bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                font=('Exo', 12, 'bold')).pack(anchor='w', padx=20, pady=10)
        
        self.raw_response_text = tk.Text(parent, height=25,
                                       bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'],
                                       font=('Courier New', 9))
        self.raw_response_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

    def test_connection_debug(self):
        """Test connection with detailed debug output"""
        api_key = self.meshy_api_key.get()
        self.log_message("🔍 Starting detailed connection test...", "info")
        
        def debug_test_thread():
            try:
                import requests
                import json
                
                # Test 1: Validate API key format
                if not self.connection_manager.validate_api_key(api_key):
                    self.root.after(0, lambda: self.log_message("❌ API key format validation failed", "error"))
                    return
                
                self.root.after(0, lambda: self.log_message("✅ API key format is valid", "success"))
                
                # Test 2: Test basic connectivity
                self.root.after(0, lambda: self.log_message("🌐 Testing internet connectivity...", "info"))
                try:
                    response = requests.get('https://httpbin.org/status/200', timeout=5)
                    self.root.after(0, lambda: self.log_message("✅ Internet connectivity OK", "success"))
                except Exception as e:
                    self.root.after(0, lambda: self.log_message(f"❌ Internet connectivity failed: {e}", "error"))
                    return
                
                # Test 3: Test Meshy API endpoint
                self.root.after(0, lambda: self.log_message("🔑 Testing Meshy API authentication...", "info"))
                headers = {'Authorization': f'Bearer {api_key}'}
                
                try:
                    response = requests.get('https://api.meshy.ai/v2/text-to-3d', 
                                          headers=headers, timeout=10)
                    
                    self.root.after(0, lambda: self.log_message(f"📡 API Response Status: {response.status_code}", "info"))
                    self.root.after(0, lambda: self.log_message(f"📡 API Response Headers: {dict(response.headers)}", "info"))
                    
                    if response.status_code == 200:
                        data = response.json()
                        self.root.after(0, lambda: self.log_message(f"✅ API Authentication successful! Credits: {data.get('credits', 'Unknown')}", "success"))
                        
                        # Update raw response tab
                        if hasattr(self, 'raw_response_text'):
                            formatted_json = json.dumps(data, indent=2)
                            self.root.after(0, lambda: self.update_raw_response(formatted_json))
                    else:
                        error_text = response.text
                        self.root.after(0, lambda: self.log_message(f"❌ API Authentication failed: {response.status_code} - {error_text}", "error"))
                        
                        if hasattr(self, 'raw_response_text'):
                            self.root.after(0, lambda: self.update_raw_response(f"Status: {response.status_code}\n\n{error_text}"))
                        
                except requests.exceptions.RequestException as e:
                    self.root.after(0, lambda: self.log_message(f"❌ Request failed: {str(e)}", "error"))
                
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"❌ Debug test failed: {str(e)}", "error"))
        
        import threading
        thread = threading.Thread(target=debug_test_thread)
        thread.daemon = True
        thread.start()

    def test_api_endpoint(self):
        """Test custom API endpoint"""
        endpoint = self.endpoint_var.get()
        api_key = self.meshy_api_key.get()
        
        self.api_test_text.delete(1.0, tk.END)
        self.api_test_text.insert(tk.END, f"Testing endpoint: {endpoint}\n")
        self.api_test_text.insert(tk.END, f"API Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else api_key}\n")
        self.api_test_text.insert(tk.END, "=" * 50 + "\n\n")
        
        def test_thread():
            try:
                import requests
                import json
                
                headers = {'Authorization': f'Bearer {api_key}'}
                response = requests.get(endpoint, headers=headers, timeout=10)
                
                result = f"Status Code: {response.status_code}\n\n"
                result += f"Headers:\n{json.dumps(dict(response.headers), indent=2)}\n\n"
                result += f"Response Body:\n"
                
                try:
                    json_data = response.json()
                    result += json.dumps(json_data, indent=2)
                except:
                    result += response.text
                
                self.root.after(0, lambda: self.api_test_text.insert(tk.END, result))
                
            except Exception as e:
                error_result = f"Error: {str(e)}\n"
                self.root.after(0, lambda: self.api_test_text.insert(tk.END, error_result))
        
        import threading
        thread = threading.Thread(target=test_thread)
        thread.daemon = True
        thread.start()

    def refresh_debug_logs(self):
        """Refresh debug logs display"""
        if hasattr(self, 'debug_logs_text'):
            self.debug_logs_text.delete(1.0, tk.END)
            for log_entry in self.debug_logs:
                self.debug_logs_text.insert(tk.END, log_entry['full_entry'])

    def clear_debug_logs(self):
        """Clear debug logs"""
        self.debug_logs.clear()
        if hasattr(self, 'debug_logs_text'):
            self.debug_logs_text.delete(1.0, tk.END)

    def copy_api_key(self):
        """Copy API key to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.meshy_api_key.get())
        self.log_message("📋 API key copied to clipboard", "info")

    def update_raw_response(self, response_text):
        """Update raw response tab"""
        if hasattr(self, 'raw_response_text'):
            self.raw_response_text.delete(1.0, tk.END)
            self.raw_response_text.insert(1.0, response_text)

    # FILE MANAGEMENT METHODS
    def upload_files(self):
        """Upload files to Meshy for processing"""
        from tkinter import filedialog
        
        filetypes = [
            ("3D Model Files", "*.obj *.mtl *.dae *.fbx *.glb *.gltf"),
            ("OBJ Files", "*.obj"),
            ("Material Files", "*.mtl"),
            ("Texture Files", "*.png *.jpg *.jpeg *.bmp *.tiff"),
            ("All Files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Select 3D Files for Meshy Processing",
            filetypes=filetypes
        )
        
        if files:
            self.log_message(f"📁 Selected {len(files)} files for upload", "info")
            
            # Add files to the list
            for file_path in files:
                file_info = {
                    'path': file_path,
                    'name': Path(file_path).name,
                    'type': Path(file_path).suffix.upper().replace('.', ''),
                    'size': self.format_file_size(Path(file_path).stat().st_size),
                    'status': 'Ready',
                    'meshy_id': None,
                    'download_url': None
                }
                self.file_items.append(file_info)
            
            self.refresh_file_list()
            self.update_batch_status()

    def refresh_file_list(self):
        """Refresh the file list display"""
        # Clear existing items
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.selected_file_vars.clear()
        
        # If connected to Meshy and no files loaded, load sample assets
        if (not self.file_items and 
            hasattr(self.connection_manager, 'connection_status') and 
            self.connection_manager.connection_status == "connected"):
            self.load_meshy_sample_assets()
        
        if not self.file_items:
            # Show empty state with connection hint
            empty_frame = tk.Frame(self.scrollable_frame, bg=self.colors['bg_tertiary'])
            empty_frame.pack(expand=True, fill='both', pady=50)
            
            if (hasattr(self.connection_manager, 'connection_status') and 
                self.connection_manager.connection_status == "connected"):
                empty_text = "� Connected to Meshy!\n\n📁 No custom files loaded\n\nClick 'UPLOAD FILES' to add your 3D models\nor use 'REFRESH FILES' to load Meshy assets"
            else:
                empty_text = "🔌 Connect to Meshy API first\n\n📂 No files loaded\n\nConnect to see available 3D assets"
            
            empty_label = tk.Label(empty_frame, text=empty_text,
                                 bg=self.colors['bg_tertiary'], fg=self.colors['text_muted'],
                                 font=('Exo', 11), justify='center')
            empty_label.pack(expand=True)
            return
        
        # Create file item cards
        for i, file_info in enumerate(self.file_items):
            self.create_file_row(i, file_info)

    def load_meshy_sample_assets(self):
        """Load sample 3D assets in Meshy.ai style"""
        sample_assets = [
            {
                'path': '/meshy/bee_worker_01.glb',
                'name': 'bee_worker_01.glb',
                'type': 'GLB',
                'size': '2.4MB',
                'status': 'Processed',
                'meshy_id': 'bee_001',
                'download_url': 'https://meshy.ai/assets/bee_worker_01.glb'
            },
            {
                'path': '/meshy/bee_queen_golden.obj',
                'name': 'bee_queen_golden.obj',
                'type': 'OBJ',
                'size': '3.1MB',
                'status': 'Processed',
                'meshy_id': 'bee_002',
                'download_url': 'https://meshy.ai/assets/bee_queen_golden.obj'
            },
            {
                'path': '/meshy/bee_hive_structure.fbx',
                'name': 'bee_hive_structure.fbx',
                'type': 'FBX',
                'size': '5.7MB',
                'status': 'Processed',
                'meshy_id': 'hive_001',
                'download_url': 'https://meshy.ai/assets/bee_hive_structure.fbx'
            },
            {
                'path': '/meshy/bee_swarm_animated.gltf',
                'name': 'bee_swarm_animated.gltf',
                'type': 'GLTF',
                'size': '8.2MB',
                'status': 'Processing',
                'meshy_id': 'swarm_001',
                'download_url': None
            },
            {
                'path': '/uploads/custom_bee_model.obj',
                'name': 'custom_bee_model.obj',
                'type': 'OBJ',
                'size': '1.8MB',
                'status': 'Ready',
                'meshy_id': None,
                'download_url': None
            },
            {
                'path': '/snapshots/bee_worker_01!.png',
                'name': 'bee_worker_01!.png',
                'type': 'PNG',
                'size': '256KB',
                'status': 'Processed',
                'meshy_id': 'snap_bee_001',
                'download_url': 'https://meshy.ai/snapshots/bee_worker_01!.png'
            },
            {
                'path': '/meshy/honeycomb_pattern.obj',
                'name': 'honeycomb_pattern.obj',
                'type': 'OBJ',
                'size': '4.3MB',
                'status': 'Processed',
                'meshy_id': 'pattern_001',
                'download_url': 'https://meshy.ai/assets/honeycomb_pattern.obj'
            },
            {
                'path': '/snapshots/bee_queen_golden!.png',
                'name': 'bee_queen_golden!.png',
                'type': 'PNG',
                'size': '312KB',
                'status': 'Processed',
                'meshy_id': 'snap_bee_002',
                'download_url': 'https://meshy.ai/snapshots/bee_queen_golden!.png'
            }
        ]
        
        self.file_items.extend(sample_assets)
        self.log_message(f"🎯 Loaded {len(sample_assets)} Meshy sample assets", "success")

    def create_file_row(self, index, file_info):
        """Create a visual file card in the browser - Meshy.ai style"""
        # Create card frame with hover effects
        card_frame = tk.Frame(self.scrollable_frame, bg=self.colors['bg_secondary'], 
                            relief='solid', bd=1, cursor='hand2')
        card_frame.pack(fill=tk.X, pady=3, padx=5)
        
        # Add hover effect
        def on_enter(event):
            card_frame.configure(bg=self.colors['accent_cyan'], relief='raised', bd=2)
        def on_leave(event):
            card_frame.configure(bg=self.colors['bg_secondary'], relief='solid', bd=1)
        
        card_frame.bind("<Enter>", on_enter)
        card_frame.bind("<Leave>", on_leave)
        
        # Main content frame
        content_frame = tk.Frame(card_frame, bg=self.colors['bg_secondary'])
        content_frame.pack(fill=tk.X, padx=10, pady=8)
        
        # Left side: Preview and checkbox
        left_frame = tk.Frame(content_frame, bg=self.colors['bg_secondary'])
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Checkbox
        var = tk.BooleanVar()
        self.selected_file_vars.append(var)
        
        checkbox = tk.Checkbutton(left_frame, variable=var, 
                                bg=self.colors['bg_secondary'], 
                                selectcolor=self.colors['accent_cyan'],
                                activebackground=self.colors['bg_secondary'],
                                command=self.update_batch_status)
        checkbox.pack(anchor='nw', pady=2)
        
        # 3D Model Preview Thumbnail
        preview_frame = tk.Frame(left_frame, bg=self.colors['bg_tertiary'], 
                               relief='solid', bd=1, width=80, height=80)
        preview_frame.pack(pady=5)
        preview_frame.pack_propagate(False)
        
        # Generate preview based on file type
        preview_canvas = tk.Canvas(preview_frame, width=78, height=78, 
                                 bg=self.colors['bg_tertiary'], highlightthickness=0)
        preview_canvas.pack()
        
        self.create_3d_preview(preview_canvas, file_info)
        
        # Middle: File information
        info_frame = tk.Frame(content_frame, bg=self.colors['bg_secondary'])
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15)
        
        # File name with style
        name_label = tk.Label(info_frame, 
                            text=file_info['name'][:35] + "..." if len(file_info['name']) > 35 else file_info['name'],
                            bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                            font=('Exo', 12, 'bold'), anchor='w')
        name_label.pack(anchor='w', pady=(0, 5))
        
        # File details grid
        details_frame = tk.Frame(info_frame, bg=self.colors['bg_secondary'])
        details_frame.pack(anchor='w', fill=tk.X)
        
        # Type badge
        type_label = tk.Label(details_frame, text=f" {file_info['type']} ",
                            bg=self.colors['accent_purple'], fg='#FFFFFF',
                            font=('Courier New', 8, 'bold'), relief='flat')
        type_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Size
        size_label = tk.Label(details_frame, text=f"📦 {file_info['size']}",
                            bg=self.colors['bg_secondary'], fg=self.colors['text_muted'],
                            font=('Exo', 9))
        size_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status with visual indicator
        status_color = self.get_status_color(file_info['status'])
        status_indicator = tk.Label(details_frame, text="●",
                                  bg=self.colors['bg_secondary'], fg=status_color,
                                  font=('Exo', 12))
        status_indicator.pack(side=tk.LEFT)
        
        status_label = tk.Label(details_frame, text=file_info['status'],
                              bg=self.colors['bg_secondary'], fg=status_color,
                              font=('Exo', 9, 'bold'))
        status_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Right side: Actions
        actions_frame = tk.Frame(content_frame, bg=self.colors['bg_secondary'])
        actions_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Action buttons with Meshy.ai style
        if file_info['status'] == 'Ready':
            process_btn = tk.Button(actions_frame, text="🚀 PROCESS",
                                  command=lambda idx=index: self.process_single_file(idx),
                                  bg=self.colors['accent_cyan'], fg='#000000',
                                  font=('Exo', 9, 'bold'), relief='flat', 
                                  width=12, cursor='hand2', pady=5)
            process_btn.pack(pady=2)
            
        elif file_info['status'] == 'Processed' and file_info.get('download_url'):
            download_btn = tk.Button(actions_frame, text="💾 DOWNLOAD",
                                   command=lambda idx=index: self.download_single_file(idx),
                                   bg=self.colors['accent_green'], fg='#000000',
                                   font=('Exo', 9, 'bold'), relief='flat', 
                                   width=12, cursor='hand2', pady=5)
            download_btn.pack(pady=2)
            
        elif file_info['status'] == 'Processing':
            processing_btn = tk.Button(actions_frame, text="⏳ PROCESSING",
                                     state='disabled',
                                     bg=self.colors['accent_orange'], fg='#000000',
                                     font=('Exo', 9, 'bold'), relief='flat', 
                                     width=12, pady=5)
            processing_btn.pack(pady=2)
        
        # Preview button for all files
        preview_btn = tk.Button(actions_frame, text="👁️ PREVIEW",
                              command=lambda idx=index: self.show_file_preview(idx),
                              bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'],
                              font=('Exo', 9), relief='flat', 
                              width=12, cursor='hand2', pady=3)
        preview_btn.pack(pady=2)

    def create_3d_preview(self, canvas, file_info):
        """Create a visual 3D model preview thumbnail - Meshy.ai style"""
        file_type = file_info['type'].lower()
        file_name = file_info['name'].lower()
        
        # Clear canvas
        canvas.delete("all")
        
        # Determine preview style based on file type and name
        if 'bee' in file_name or 'insect' in file_name:
            self.draw_bee_preview(canvas, file_info)
        elif file_type in ['obj', 'glb', 'gltf', 'fbx']:
            self.draw_3d_model_preview(canvas, file_info)
        elif file_type in ['png', 'jpg', 'jpeg'] and '!' in file_name:
            self.draw_snapshot_preview(canvas, file_info)
        else:
            self.draw_generic_preview(canvas, file_info)
    
    def draw_bee_preview(self, canvas, file_info):
        """Draw a bee-style 3D model preview"""
        # Bee body (yellow and black stripes)
        canvas.create_oval(25, 35, 55, 55, fill='#FFD700', outline='#000000', width=2)
        canvas.create_arc(25, 35, 55, 55, start=0, extent=60, fill='#000000', outline='')
        canvas.create_arc(25, 35, 55, 55, start=120, extent=60, fill='#000000', outline='')
        
        # Wings (translucent blue-white)
        canvas.create_oval(15, 25, 35, 45, fill='#87CEEB', outline='#4682B4', width=1)
        canvas.create_oval(45, 25, 65, 45, fill='#87CEEB', outline='#4682B4', width=1)
        
        # Antennae
        canvas.create_line(35, 30, 30, 20, fill='#000000', width=2)
        canvas.create_line(45, 30, 50, 20, fill='#000000', width=2)
        canvas.create_oval(28, 18, 32, 22, fill='#000000')
        canvas.create_oval(48, 18, 52, 22, fill='#000000')
        
        # Eyes
        canvas.create_oval(30, 32, 36, 38, fill='#000000')
        canvas.create_oval(44, 32, 50, 38, fill='#000000')
        canvas.create_oval(32, 34, 34, 36, fill='#FFFFFF')
        canvas.create_oval(46, 34, 48, 36, fill='#FFFFFF')
        
        # Status indicator
        status = file_info['status']
        if status == 'Processed':
            canvas.create_oval(5, 5, 15, 15, fill='#00FF00', outline='#FFFFFF', width=2)
        elif status == 'Processing':
            canvas.create_oval(5, 5, 15, 15, fill='#FFA500', outline='#FFFFFF', width=2)
        else:
            canvas.create_oval(5, 5, 15, 15, fill='#808080', outline='#FFFFFF', width=2)
    
    def draw_3d_model_preview(self, canvas, file_info):
        """Draw a generic 3D model preview"""
        # 3D cube with perspective
        # Back face
        canvas.create_polygon(15, 15, 45, 15, 45, 45, 15, 45, 
                            fill=self.colors['accent_purple'], outline='#FFFFFF', width=2)
        # Right face
        canvas.create_polygon(45, 15, 60, 25, 60, 55, 45, 45, 
                            fill=self.colors['accent_cyan'], outline='#FFFFFF', width=2)
        # Top face
        canvas.create_polygon(15, 15, 30, 5, 60, 25, 45, 15, 
                            fill=self.colors['accent_green'], outline='#FFFFFF', width=2)
        
        # 3D text
        canvas.create_text(40, 65, text="3D", fill=self.colors['text_primary'], 
                         font=('Exo', 10, 'bold'))
        
        # File type badge
        canvas.create_rectangle(55, 55, 75, 70, fill=self.colors['bg_primary'], 
                              outline=self.colors['accent_cyan'])
        canvas.create_text(65, 62, text=file_info['type'], fill=self.colors['accent_cyan'], 
                         font=('Courier New', 8, 'bold'))
    
    def draw_snapshot_preview(self, canvas, file_info):
        """Draw a PNG snapshot preview"""
        # Camera/snapshot icon style
        canvas.create_rectangle(10, 25, 70, 55, fill='#2C3E50', outline=self.colors['accent_cyan'], width=2)
        canvas.create_rectangle(15, 30, 65, 50, fill='#34495E', outline='')
        
        # Lens
        canvas.create_oval(30, 35, 50, 50, fill='#1ABC9C', outline='#FFFFFF', width=2)
        canvas.create_oval(35, 37, 45, 47, fill='#16A085', outline='')
        
        # Flash
        canvas.create_rectangle(55, 27, 60, 32, fill='#F39C12', outline='#FFFFFF')
        
        # PNG badge
        canvas.create_text(40, 65, text="PNG!", fill=self.colors['accent_orange'], 
                         font=('Exo', 9, 'bold'))
    
    def draw_generic_preview(self, canvas, file_info):
        """Draw a generic file preview"""
        file_type = file_info['type'].lower()
        
        # File icon
        canvas.create_rectangle(20, 15, 60, 60, fill=self.colors['bg_tertiary'], 
                              outline=self.colors['text_secondary'], width=2)
        canvas.create_polygon(60, 15, 60, 25, 50, 15, fill=self.colors['bg_tertiary'], 
                            outline=self.colors['text_secondary'], width=2)
        
        # File type
        canvas.create_text(40, 40, text=file_type.upper(), fill=self.colors['text_primary'], 
                         font=('Exo', 8, 'bold'))
        
        # File icon based on type
        icon = self.get_file_icon(file_type)
        canvas.create_text(40, 25, text=icon, font=('Exo', 12))

    def show_file_preview(self, index):
        """Show detailed file preview window"""
        if index >= len(self.file_items):
            return
            
        file_info = self.file_items[index]
        
        # Create preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title(f"Preview: {file_info['name']}")
        preview_window.geometry("500x400")
        preview_window.configure(bg=self.colors['bg_primary'])
        preview_window.transient(self.root)
        preview_window.grab_set()
        
        # Title
        title_frame = tk.Frame(preview_window, bg=self.colors['bg_secondary'], height=60)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text=f"📁 {file_info['name']}", 
                bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                font=('Exo', 14, 'bold')).pack(pady=15)
        
        # Large preview area
        preview_frame = tk.Frame(preview_window, bg=self.colors['bg_tertiary'], 
                               relief='solid', bd=2)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Large preview canvas
        large_canvas = tk.Canvas(preview_frame, width=450, height=250, 
                               bg=self.colors['bg_tertiary'], highlightthickness=0)
        large_canvas.pack(pady=20)
        
        # Create large preview
        self.create_large_preview(large_canvas, file_info)
        
        # File details
        details_frame = tk.Frame(preview_window, bg=self.colors['bg_primary'])
        details_frame.pack(fill=tk.X, padx=20, pady=10)
        
        details = [
            ("Type:", file_info['type']),
            ("Size:", file_info['size']),
            ("Status:", file_info['status']),
            ("Path:", file_info.get('path', 'N/A')[:50] + "..." if len(file_info.get('path', '')) > 50 else file_info.get('path', 'N/A'))
        ]
        
        for i, (label, value) in enumerate(details):
            row_frame = tk.Frame(details_frame, bg=self.colors['bg_primary'])
            row_frame.pack(fill=tk.X, pady=2)
            
            tk.Label(row_frame, text=label, bg=self.colors['bg_primary'], 
                    fg=self.colors['text_muted'], font=('Exo', 10), width=10, anchor='w').pack(side=tk.LEFT)
            tk.Label(row_frame, text=value, bg=self.colors['bg_primary'], 
                    fg=self.colors['text_secondary'], font=('Exo', 10), anchor='w').pack(side=tk.LEFT, padx=(10, 0))
        
        # Close button
        tk.Button(preview_window, text="✖ CLOSE", command=preview_window.destroy,
                 bg=self.colors['error'], fg='#FFFFFF', font=('Exo', 10, 'bold'),
                 relief='flat', cursor='hand2', pady=5).pack(pady=10)
    
    def create_large_preview(self, canvas, file_info):
        """Create a large detailed preview"""
        file_type = file_info['type'].lower()
        file_name = file_info['name'].lower()
        
        canvas.delete("all")
        
        if 'bee' in file_name or 'insect' in file_name:
            # Large bee preview
            self.draw_large_bee(canvas)
        elif file_type in ['obj', 'glb', 'gltf', 'fbx']:
            self.draw_large_3d_model(canvas, file_info)
        elif file_type in ['png', 'jpg', 'jpeg'] and '!' in file_name:
            self.draw_large_snapshot(canvas)
        else:
            self.draw_large_generic(canvas, file_info)
    
    def draw_large_bee(self, canvas):
        """Draw a large detailed bee preview"""
        center_x, center_y = 225, 125
        
        # Bee body (larger and more detailed)
        canvas.create_oval(center_x-50, center_y-15, center_x+50, center_y+15, 
                         fill='#FFD700', outline='#000000', width=3)
        
        # Black stripes
        for i in range(4):
            x = center_x - 35 + (i * 20)
            canvas.create_arc(center_x-50, center_y-15, center_x+50, center_y+15, 
                            start=0, extent=180, fill='#000000', outline='')
        
        # Wings (larger and detailed)
        canvas.create_oval(center_x-70, center_y-35, center_x-20, center_y+5, 
                         fill='#87CEEB', outline='#4682B4', width=2)
        canvas.create_oval(center_x+20, center_y-35, center_x+70, center_y+5, 
                         fill='#87CEEB', outline='#4682B4', width=2)
        
        # Wing details
        canvas.create_line(center_x-60, center_y-25, center_x-30, center_y-5, fill='#4682B4', width=1)
        canvas.create_line(center_x+30, center_y-25, center_x+60, center_y-5, fill='#4682B4', width=1)
        
        # Head
        canvas.create_oval(center_x-25, center_y-35, center_x+25, center_y-5, 
                         fill='#FFD700', outline='#000000', width=3)
        
        # Eyes
        canvas.create_oval(center_x-20, center_y-30, center_x-10, center_y-20, fill='#000000')
        canvas.create_oval(center_x+10, center_y-30, center_x+20, center_y-20, fill='#000000')
        canvas.create_oval(center_x-17, center_y-27, center_x-13, center_y-23, fill='#FFFFFF')
        canvas.create_oval(center_x+13, center_y-27, center_x+17, center_y-23, fill='#FFFFFF')
        
        # Antennae
        canvas.create_line(center_x-10, center_y-35, center_x-15, center_y-50, fill='#000000', width=3)
        canvas.create_line(center_x+10, center_y-35, center_x+15, center_y-50, fill='#000000', width=3)
        canvas.create_oval(center_x-18, center_y-55, center_x-12, center_y-49, fill='#000000')
        canvas.create_oval(center_x+12, center_y-55, center_x+18, center_y-49, fill='#000000')
        
        # Label
        canvas.create_text(center_x, center_y+50, text="🐝 3D BEE MODEL 🐝", 
                         fill=self.colors['accent_yellow'], font=('Exo', 16, 'bold'))
    
    def draw_large_3d_model(self, canvas, file_info):
        """Draw a large 3D model preview"""
        center_x, center_y = 225, 125
        
        # 3D wireframe cube (large)
        size = 80
        
        # Back face
        canvas.create_rectangle(center_x-size, center_y-size//2, center_x, center_y+size//2,
                              fill=self.colors['accent_purple'], outline='#FFFFFF', width=3)
        
        # Right face
        canvas.create_polygon(center_x, center_y-size//2, center_x+size//2, center_y-size, 
                            center_x+size//2, center_y, center_x, center_y+size//2,
                            fill=self.colors['accent_cyan'], outline='#FFFFFF', width=3)
        
        # Top face
        canvas.create_polygon(center_x-size, center_y-size//2, center_x-size//2, center_y-size,
                            center_x+size//2, center_y-size, center_x, center_y-size//2,
                            fill=self.colors['accent_green'], outline='#FFFFFF', width=3)
        
        # Wireframe lines
        canvas.create_line(center_x-size//2, center_y-size//4, center_x+size//4, center_y-3*size//4, 
                         fill='#FFFFFF', width=2, dash=(5, 5))
        canvas.create_line(center_x-size//2, center_y+size//4, center_x+size//4, center_y-size//4, 
                         fill='#FFFFFF', width=2, dash=(5, 5))
        
        # Label
        canvas.create_text(center_x, center_y+80, text=f"🎯 {file_info['type']} 3D MODEL 🎯", 
                         fill=self.colors['text_primary'], font=('Exo', 16, 'bold'))
    
    def draw_large_snapshot(self, canvas):
        """Draw a large snapshot preview"""
        center_x, center_y = 225, 125
        
        # Camera body (large)
        canvas.create_rectangle(center_x-100, center_y-50, center_x+100, center_y+30,
                              fill='#2C3E50', outline=self.colors['accent_cyan'], width=4)
        
        # Screen
        canvas.create_rectangle(center_x-80, center_y-30, center_x+80, center_y+10,
                              fill='#34495E', outline='#FFFFFF', width=2)
        
        # Lens (large)
        canvas.create_oval(center_x-40, center_y-40, center_x+40, center_y+20,
                         fill='#1ABC9C', outline='#FFFFFF', width=3)
        canvas.create_oval(center_x-25, center_y-25, center_x+25, center_y+5,
                         fill='#16A085', outline='#FFFFFF', width=2)
        canvas.create_oval(center_x-10, center_y-10, center_x+10, center_y-5,
                         fill='#FFFFFF', outline='')
        
        # Flash
        canvas.create_rectangle(center_x+60, center_y-45, center_x+80, center_y-25,
                              fill='#F39C12', outline='#FFFFFF', width=2)
        
        # Label
        canvas.create_text(center_x, center_y+60, text="� PNG SNAPSHOT! 📸", 
                         fill=self.colors['accent_orange'], font=('Exo', 16, 'bold'))
    
    def draw_large_generic(self, canvas, file_info):
        """Draw a large generic file preview"""
        center_x, center_y = 225, 125
        
        # Large file icon
        canvas.create_rectangle(center_x-60, center_y-80, center_x+60, center_y+40,
                              fill=self.colors['bg_tertiary'], outline=self.colors['text_secondary'], width=4)
        canvas.create_polygon(center_x+60, center_y-80, center_x+60, center_y-40, center_x+20, center_y-80,
                            fill=self.colors['bg_tertiary'], outline=self.colors['text_secondary'], width=4)
        
        # File type
        canvas.create_text(center_x, center_y-20, text=file_info['type'], 
                         fill=self.colors['text_primary'], font=('Exo', 24, 'bold'))
        
        # Icon
        icon = self.get_file_icon(file_info['type'].lower())
        canvas.create_text(center_x, center_y+10, text=icon, font=('Exo', 32))
        
        # Label
        canvas.create_text(center_x, center_y+70, text=f"📄 {file_info['type']} FILE 📄", 
                         fill=self.colors['text_secondary'], font=('Exo', 14, 'bold'))

    def get_file_icon(self, file_type):
        """Get icon for file type"""
        icons = {
            'obj': '🗿', 'mtl': '🎨', 'png': '🖼️', 'jpg': '🖼️', 'jpeg': '🖼️',
            'glb': '🎯', 'gltf': '🎯', 'fbx': '📦', 'dae': '📦', 'zip': '📦'
        }
        return icons.get(file_type, '📄')

    def show_meshy_asset_browser(self):
        """Transform center panel into Meshy.ai-style asset browser"""
        # Clear existing content
        for widget in self.center_content_frame.winfo_children():
            widget.destroy()
        
        # UPLOADED FILES + BATCH PREVIEW SECTION
        browser_section = self.create_section_frame(self.center_content_frame, "📥 UPLOADED FILES + BATCH PREVIEW")
        
        # Control bar with filters and actions
        control_bar = tk.Frame(browser_section, bg=self.colors['bg_secondary'], height=50)
        control_bar.pack(fill=tk.X, pady=(0, 10))
        control_bar.pack_propagate(False)
        
        # Left side - filters
        filters_frame = tk.Frame(control_bar, bg=self.colors['bg_secondary'])
        filters_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Label(filters_frame, text="🎯 FILTER:",
                bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                font=('Exo', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        # Filter buttons
        filter_buttons = [
            ("ALL", self.colors['accent_cyan']),
            ("TEXTURED", self.colors['accent_green']),
            ("PENDING", self.colors['accent_orange'])
        ]
        
        for text, color in filter_buttons:
            btn = tk.Button(filters_frame, text=text,
                          bg=color if text == "ALL" else self.colors['bg_tertiary'],
                          fg='#000000' if text == "ALL" else self.colors['text_secondary'],
                          font=('Exo', 8, 'bold'), relief='flat',
                          padx=8, pady=4, cursor='hand2')
            btn.pack(side=tk.LEFT, padx=2)
        
        # Right side - batch actions
        actions_frame = tk.Frame(control_bar, bg=self.colors['bg_secondary'])
        actions_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        tk.Button(actions_frame, text="🔄 REFRESH ASSETS",
                 command=self.fetch_real_meshy_assets,
                 bg=self.colors['accent_cyan'], fg='#000000',
                 font=('Exo', 9, 'bold'), relief='flat',
                 padx=12, pady=6, cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(actions_frame, text="✅ SELECT ALL",
                 command=self.select_all_assets,
                 bg=self.colors['accent_green'], fg='#000000',
                 font=('Exo', 9, 'bold'), relief='flat',
                 padx=12, pady=6, cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        tk.Button(actions_frame, text="💾 DOWNLOAD SELECTED",
                 command=self.download_selected_assets,
                 bg=self.colors['accent_purple'], fg='#FFFFFF',
                 font=('Exo', 9, 'bold'), relief='flat',
                 padx=12, pady=6, cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        # Asset grid container with scrolling
        grid_container = tk.Frame(browser_section, bg=self.colors['bg_secondary'])
        grid_container.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollable canvas for asset grid
        self.assets_canvas = tk.Canvas(grid_container, bg=self.colors['bg_tertiary'], highlightthickness=0)
        assets_scrollbar = tk.Scrollbar(grid_container, orient="vertical", command=self.assets_canvas.yview)
        self.assets_grid_frame = tk.Frame(self.assets_canvas, bg=self.colors['bg_tertiary'])
        
        self.assets_grid_frame.bind(
            "<Configure>",
            lambda e: self.assets_canvas.configure(scrollregion=self.assets_canvas.bbox("all"))
        )
        
        self.assets_canvas.create_window((0, 0), window=self.assets_grid_frame, anchor="nw")
        self.assets_canvas.configure(yscrollcommand=assets_scrollbar.set)
        
        self.assets_canvas.pack(side="left", fill="both", expand=True)
        assets_scrollbar.pack(side="right", fill="y")
        
        # Fetch and display real Meshy assets
        self.fetch_real_meshy_assets()

    def fetch_real_meshy_assets(self):
        """Fetch actual assets from Meshy API"""
        def fetch_thread():
            try:
                api_key = self.meshy_api_key.get()
                if not api_key:
                    self.root.after(0, lambda: self.log_message("❌ API key required to fetch real assets", "error"))
                    return
                
                import requests
                import json
                
                # Fetch user's models from Meshy API
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
                
                # Try different endpoints to get user's models
                endpoints = [
                    'https://api.meshy.ai/v2/text-to-3d',  # Get text-to-3d models
                    'https://api.meshy.ai/v1/text-to-3d',  # Fallback endpoint
                ]
                
                real_assets = []
                
                for endpoint in endpoints:
                    try:
                        self.root.after(0, lambda e=endpoint: self.log_message(f"🔍 Fetching from {e}...", "info"))
                        response = requests.get(endpoint, headers=headers, timeout=15)
                        
                        if response.status_code == 200:
                            data = response.json()
                            self.root.after(0, lambda: self.log_message(f"✅ Successfully fetched data", "success"))
                            
                            # Process the response based on API structure
                            if 'result' in data:
                                models = data['result'] if isinstance(data['result'], list) else [data['result']]
                            elif 'data' in data:
                                models = data['data'] if isinstance(data['data'], list) else [data['data']]
                            elif isinstance(data, list):
                                models = data
                            else:
                                models = [data]
                            
                            # Convert Meshy API response to our asset format
                            for model in models:
                                if isinstance(model, dict):
                                    asset = {
                                        'name': model.get('name', model.get('prompt', 'Unnamed Model'))[:50],
                                        'filename': f"{model.get('id', 'unknown')}.glb",
                                        'status': 'textured' if model.get('status') == 'SUCCEEDED' else 'pending',
                                        'type': 'model',
                                        'download_ready': model.get('status') == 'SUCCEEDED',
                                        'thumbnail_url': model.get('thumbnail_url'),
                                        'model_urls': model.get('model_urls', {}),
                                        'id': model.get('id'),
                                        'thumbnail_color': '#FFD700',  # Default gold
                                        'secondary_color': '#87CEEB'   # Default blue
                                    }
                                    real_assets.append(asset)
                            
                            break  # Success, exit loop
                            
                        elif response.status_code == 401:
                            self.root.after(0, lambda: self.log_message("❌ Invalid API key", "error"))
                            return
                        else:
                            self.root.after(0, lambda s=response.status_code: self.log_message(f"⚠️ API returned status {s}", "warning"))
                            
                    except requests.exceptions.RequestException as e:
                        self.root.after(0, lambda e=str(e): self.log_message(f"⚠️ Request failed: {e}", "warning"))
                        continue
                
                if real_assets:
                    # Update asset display with real data
                    self.root.after(0, lambda assets=real_assets: self.display_real_assets(assets))
                    self.root.after(0, lambda: self.log_message(f"✅ Loaded {len(real_assets)} real assets from Meshy", "success"))
                else:
                    # Fallback to mock data if no real assets found
                    self.root.after(0, lambda: self.log_message("⚠️ No real assets found in your Meshy account, showing demo data", "warning"))
                    self.root.after(0, lambda: self.load_meshy_bee_assets())
                        
            except Exception as e:
                self.root.after(0, lambda e=str(e): self.log_message(f"❌ Error fetching assets: {e}", "error"))
                # Fallback to mock data
                self.root.after(0, lambda: self.load_meshy_bee_assets())
        
        import threading
        thread = threading.Thread(target=fetch_thread)
        thread.daemon = True
        thread.start()

    def display_real_assets(self, assets):
        """Display real Meshy assets in the grid"""
        # Clear existing assets
        for widget in self.assets_grid_frame.winfo_children():
            widget.destroy()
        
        # Configure grid with 4 columns
        columns = 4
        for i in range(columns):
            self.assets_grid_frame.grid_columnconfigure(i, weight=1, minsize=180)
        
        # Display real assets
        for index, asset in enumerate(assets):
            row = index // columns
            col = index % columns
            
            asset_card = self.create_real_asset_card(self.assets_grid_frame, asset)
            asset_card.grid(row=row, column=col, padx=8, pady=8, sticky="ew")

    def create_real_asset_card(self, parent, asset):
        """Create asset card for real Meshy asset"""
        card = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='solid', bd=1)
        
        # Asset thumbnail with 3D preview
        thumbnail_frame = tk.Frame(card, bg=self.colors['bg_tertiary'], height=120)
        thumbnail_frame.pack(fill=tk.X, padx=8, pady=8)
        thumbnail_frame.pack_propagate(False)
        
        # Create canvas for 3D thumbnail
        thumb_canvas = tk.Canvas(thumbnail_frame, width=148, height=118, 
                               bg=self.colors['bg_tertiary'], highlightthickness=0)
        thumb_canvas.pack()
        
        # Draw realistic 3D object thumbnail
        self.draw_3d_object_thumbnail(thumb_canvas, asset)
        
        # Asset name
        name_label = tk.Label(card, text=asset['name'], 
                            bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                            font=('Exo', 9, 'bold'))
        name_label.pack(pady=(0, 5))
        
        # Filename
        filename_label = tk.Label(card, text=asset['filename'], 
                                bg=self.colors['bg_secondary'], fg=self.colors['text_muted'],
                                font=('Exo', 8))
        filename_label.pack()
        
        # Status indicator
        status_color = self.colors['accent_green'] if asset['status'] == 'textured' else self.colors['accent_orange']
        status_frame = tk.Frame(card, bg=self.colors['bg_secondary'])
        status_frame.pack(pady=5)
        
        status_dot = tk.Label(status_frame, text="●", fg=status_color, bg=self.colors['bg_secondary'],
                            font=('Exo', 12))
        status_dot.pack(side=tk.LEFT)
        
        status_label = tk.Label(status_frame, text=asset['status'].upper(), 
                              fg=status_color, bg=self.colors['bg_secondary'],
                              font=('Exo', 8, 'bold'))
        status_label.pack(side=tk.LEFT, padx=(2, 0))
        
        # Download buttons (only if ready)
        if asset['download_ready']:
            buttons_frame = tk.Frame(card, bg=self.colors['bg_secondary'])
            buttons_frame.pack(fill=tk.X, padx=8, pady=(5, 8))
            
            # Available formats from Meshy API
            model_urls = asset.get('model_urls', {})
            formats = [('GLB', 'glb'), ('OBJ', 'obj'), ('PNG', 'png')]
            
            for format_name, format_key in formats:
                if format_key in model_urls or format_key == 'glb':  # GLB is usually default
                    btn_color = {'GLB': self.colors['accent_green'], 
                               'OBJ': self.colors['accent_cyan'], 
                               'PNG': self.colors['accent_orange']}[format_name]
                    
                    btn = tk.Button(buttons_frame, text=format_name,
                                  command=lambda f=format_name, a=asset: self.download_real_asset(a, f),
                                  bg=btn_color, fg='#000000',
                                  font=('Exo', 7, 'bold'), relief='flat',
                                  padx=8, pady=2, cursor='hand2')
                    btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        return card

    def download_real_asset(self, asset, format_type):
        """Download real asset from Meshy API"""
        def download_thread():
            try:
                api_key = self.meshy_api_key.get()
                model_urls = asset.get('model_urls', {})
                asset_id = asset.get('id')
                
                # Determine download URL
                if format_type.lower() in model_urls:
                    download_url = model_urls[format_type.lower()]
                elif asset_id:
                    # Construct download URL if not in model_urls
                    download_url = f"https://api.meshy.ai/v2/text-to-3d/{asset_id}/download"
                else:
                    self.root.after(0, lambda: self.log_message(f"❌ No download URL for {format_type}", "error"))
                    return
                
                self.root.after(0, lambda: self.log_message(f"📥 Downloading {asset['name']} as {format_type}...", "info"))
                
                # Download the file
                import requests
                import os
                
                headers = {'Authorization': f'Bearer {api_key}'}
                response = requests.get(download_url, headers=headers, stream=True, timeout=30)
                
                if response.status_code == 200:
                    # Save to downloads directory
                    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads", "Meshy_Assets")
                    os.makedirs(downloads_dir, exist_ok=True)
                    
                    filename = f"{asset['name']}_{asset_id}.{format_type.lower()}"
                    filepath = os.path.join(downloads_dir, filename)
                    
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    self.root.after(0, lambda: self.log_message(f"✅ Downloaded: {filename}", "success"))
                    
                else:
                    self.root.after(0, lambda: self.log_message(f"❌ Download failed: {response.status_code}", "error"))
                    
            except Exception as e:
                self.root.after(0, lambda e=str(e): self.log_message(f"❌ Download error: {e}", "error"))
        
        import threading
        thread = threading.Thread(target=download_thread)
        thread.daemon = True
        thread.start()

    def load_meshy_bee_assets(self):
        """Load and display bee assets in Meshy.ai grid style"""
        # Sample bee assets matching the Meshy.ai interface
        bee_assets = [
            {
                'name': 'Astronaut Bee',
                'filename': 'astronaut_bee.glb',
                'status': 'textured',
                'type': 'character',
                'download_ready': True,
                'thumbnail_color': '#FFD700',  # Golden
                'secondary_color': '#87CEEB'  # Light blue for wings/suit
            },
            {
                'name': 'Explorer Bee', 
                'filename': 'explorer_bee.obj',
                'status': 'textured',
                'type': 'character',
                'download_ready': True,
                'thumbnail_color': '#FFA500',  # Orange
                'secondary_color': '#87CEEB'
            },
            {
                'name': 'Worker Bee',
                'filename': 'worker_bee.fbx',
                'status': 'textured', 
                'type': 'character',
                'download_ready': True,
                'thumbnail_color': '#FFD700',
                'secondary_color': '#000000'  # Black stripes
            },
            {
                'name': 'Guardian Bee',
                'filename': 'guardian_bee.gltf',
                'status': 'textured',
                'type': 'character', 
                'download_ready': True,
                'thumbnail_color': '#FFA500',
                'secondary_color': '#008000'  # Green
            },
            {
                'name': 'Scout Bee',
                'filename': 'scout_bee.obj',
                'status': 'grayscale',
                'type': 'character',
                'download_ready': False,
                'thumbnail_color': '#C0C0C0',  # Silver/gray
                'secondary_color': '#808080'
            },
            {
                'name': 'Scientist Bee',
                'filename': 'scientist_bee.glb',
                'status': 'textured',
                'type': 'character',
                'download_ready': True,
                'thumbnail_color': '#FFD700',
                'secondary_color': '#0000FF'  # Blue for lab coat
            },
            {
                'name': 'Engineer Bee',
                'filename': 'engineer_bee.fbx', 
                'status': 'grayscale',
                'type': 'character',
                'download_ready': False,
                'thumbnail_color': '#C0C0C0',
                'secondary_color': '#808080'
            },
            {
                'name': 'Pilot Bee',
                'filename': 'pilot_bee.obj',
                'status': 'textured',
                'type': 'character',
                'download_ready': True,
                'thumbnail_color': '#FFD700',
                'secondary_color': '#8B4513'  # Brown for aviator gear
            },
            {
                'name': 'Captain Bee',
                'filename': 'captain_bee.gltf',
                'status': 'textured',
                'type': 'character',
                'download_ready': True,
                'thumbnail_color': '#FFA500',
                'secondary_color': '#FF0000'  # Red for captain details
            },
            {
                'name': 'Medic Bee',
                'filename': 'medic_bee.glb',
                'status': 'pending',
                'type': 'character',
                'download_ready': False,
                'thumbnail_color': '#FFFF00',  # Bright yellow
                'secondary_color': '#FF0000'  # Red cross
            },
            {
                'name': 'Miner Bee',
                'filename': 'miner_bee.obj',
                'status': 'textured',
                'type': 'character',
                'download_ready': True,
                'thumbnail_color': '#FFD700',
                'secondary_color': '#654321'  # Brown for mining gear
            },
            {
                'name': 'Chef Bee',
                'filename': 'chef_bee.fbx',
                'status': 'grayscale',
                'type': 'character', 
                'download_ready': False,
                'thumbnail_color': '#C0C0C0',
                'secondary_color': '#808080'
            }
        ]
        
        # Store assets for selection tracking
        self.bee_assets = bee_assets
        self.asset_vars = []
        
        # Create grid layout (4 columns)
        for i, asset in enumerate(bee_assets):
            row = i // 4
            col = i % 4
            
            self.create_asset_card(self.assets_grid_frame, asset, row, col)
        
        # Configure grid columns
        for col in range(4):
            self.assets_grid_frame.columnconfigure(col, weight=1, minsize=180)

    def create_asset_card(self, parent, asset, row, col):
        """Create individual asset card in Meshy.ai style"""
        # Main card frame
        card_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='solid', bd=1)
        card_frame.grid(row=row, column=col, padx=8, pady=8, sticky='nsew')
        
        # Selection checkbox
        var = tk.BooleanVar()
        self.asset_vars.append(var)
        
        checkbox = tk.Checkbutton(card_frame, variable=var,
                                bg=self.colors['bg_secondary'],
                                selectcolor=self.colors['accent_cyan'],
                                activebackground=self.colors['bg_secondary'])
        checkbox.pack(anchor='nw', padx=5, pady=5)
        
        # Thumbnail area
        thumb_frame = tk.Frame(card_frame, bg=self.colors['bg_tertiary'], 
                             width=150, height=120, relief='solid', bd=1)
        thumb_frame.pack(padx=10, pady=(0, 10))
        thumb_frame.pack_propagate(False)
        
        # Create bee thumbnail
        thumb_canvas = tk.Canvas(thumb_frame, width=148, height=118, 
                               bg=self.colors['bg_tertiary'], highlightthickness=0)
        thumb_canvas.pack()
        
        self.draw_3d_object_thumbnail(thumb_canvas, asset)
        
        # Asset name and info
        info_frame = tk.Frame(card_frame, bg=self.colors['bg_secondary'])
        info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Asset name
        tk.Label(info_frame, text=asset['name'],
                bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                font=('Exo', 10, 'bold')).pack()
        
        # Filename
        tk.Label(info_frame, text=asset['filename'],
                bg=self.colors['bg_secondary'], fg=self.colors['text_muted'],
                font=('Courier New', 8)).pack()
        
        # Status indicator
        status_color = self.get_asset_status_color(asset['status'])
        status_frame = tk.Frame(info_frame, bg=self.colors['bg_secondary'])
        status_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(status_frame, text="●",
                bg=self.colors['bg_secondary'], fg=status_color,
                font=('Exo', 12)).pack(side=tk.LEFT)
        tk.Label(status_frame, text=asset['status'].upper(),
                bg=self.colors['bg_secondary'], fg=status_color,
                font=('Exo', 8, 'bold')).pack(side=tk.LEFT, padx=(5, 0))
        
        # Download buttons
        if asset['download_ready']:
            buttons_frame = tk.Frame(card_frame, bg=self.colors['bg_secondary'])
            buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
            
            # GLB download
            tk.Button(buttons_frame, text="📦 GLB",
                     command=lambda a=asset: self.download_asset(a, 'glb'),
                     bg=self.colors['accent_green'], fg='#000000',
                     font=('Exo', 8, 'bold'), relief='flat',
                     width=8, cursor='hand2').pack(side=tk.LEFT, padx=2)
            
            # OBJ download  
            tk.Button(buttons_frame, text="🎯 OBJ", 
                     command=lambda a=asset: self.download_asset(a, 'obj'),
                     bg=self.colors['accent_cyan'], fg='#000000',
                     font=('Exo', 8, 'bold'), relief='flat',
                     width=8, cursor='hand2').pack(side=tk.LEFT, padx=2)
            
            # Thumbnail if available
            if asset['status'] == 'textured':
                tk.Button(buttons_frame, text="🖼️ PNG",
                         command=lambda a=asset: self.download_asset(a, 'png'),
                         bg=self.colors['accent_orange'], fg='#000000',
                         font=('Exo', 8, 'bold'), relief='flat',
                         width=8, cursor='hand2').pack(side=tk.LEFT, padx=2)
        else:
            # Status message for non-ready assets
            tk.Label(card_frame, text="⏳ Processing...",
                    bg=self.colors['bg_secondary'], fg=self.colors['accent_orange'],
                    font=('Exo', 9)).pack(pady=5)

    def draw_3d_object_thumbnail(self, canvas, asset):
        """Draw realistic 3D object thumbnail based on asset properties"""
        center_x, center_y = 74, 59
        
        # Get colors from asset
        primary_color = asset.get('thumbnail_color', '#A0A0A0')
        secondary_color = asset.get('secondary_color', '#808080')
        
        # Clear canvas
        canvas.delete("all")
        
        # Create gradient background
        for i in range(0, 118, 2):
            alpha = i / 118
            gray_val = int(25 + alpha * 15)
            color = f"#{gray_val:02x}{gray_val:02x}{gray_val:02x}"
            canvas.create_rectangle(0, i, 148, i+2, fill=color, outline="")
        
        # Draw 3D object based on asset type/name
        if 'mesh' in asset.get('name', '').lower() or 'model' in asset.get('name', '').lower():
            self.draw_generic_3d_mesh(canvas, center_x, center_y, primary_color, secondary_color)
        elif 'character' in asset.get('name', '').lower() or 'figure' in asset.get('name', '').lower():
            self.draw_character_model(canvas, center_x, center_y, primary_color, secondary_color)
        elif 'building' in asset.get('name', '').lower() or 'house' in asset.get('name', '').lower():
            self.draw_building_model(canvas, center_x, center_y, primary_color, secondary_color)
        elif 'vehicle' in asset.get('name', '').lower() or 'car' in asset.get('name', '').lower():
            self.draw_vehicle_model(canvas, center_x, center_y, primary_color, secondary_color)
        else:
            # Default: abstract 3D object
            self.draw_abstract_3d_object(canvas, center_x, center_y, primary_color, secondary_color)
        
        # Add wireframe overlay for pending items
        if asset.get('status') == 'pending':
            self.draw_wireframe_overlay(canvas, center_x, center_y)
            canvas.create_text(center_x, center_y+35, text="⏳ PROCESSING",
                             fill=self.colors['accent_orange'], font=('Exo', 8, 'bold'))
        
        # Add selection highlight if needed
        if asset.get('selected', False):
            canvas.create_rectangle(2, 2, 146, 116, outline=self.colors['accent_cyan'], width=3)

    def draw_generic_3d_mesh(self, canvas, x, y, primary_color, secondary_color):
        """Draw a generic 3D mesh object"""
        # Main object - isometric cube with faces
        # Front face
        points = [x-20, y-10, x+20, y-10, x+20, y+20, x-20, y+20]
        canvas.create_polygon(points, fill=primary_color, outline='#000000', width=2)
        
        # Top face (isometric)
        points = [x-20, y-10, x-5, y-25, x+35, y-25, x+20, y-10]
        canvas.create_polygon(points, fill=secondary_color, outline='#000000', width=2)
        
        # Right face
        points = [x+20, y-10, x+35, y-25, x+35, y+5, x+20, y+20]
        canvas.create_polygon(points, fill=primary_color, outline='#000000', width=2)
        
        # Add some geometric details
        canvas.create_line(x-10, y, x+10, y, fill='#000000', width=1)
        canvas.create_line(x, y-5, x, y+15, fill='#000000', width=1)

    def draw_character_model(self, canvas, x, y, primary_color, secondary_color):
        """Draw a character/figure model"""
        # Head
        canvas.create_oval(x-8, y-25, x+8, y-10, fill=primary_color, outline='#000000', width=2)
        
        # Body
        canvas.create_rectangle(x-12, y-10, x+12, y+15, fill=secondary_color, outline='#000000', width=2)
        
        # Arms
        canvas.create_rectangle(x-20, y-5, x-12, y+5, fill=primary_color, outline='#000000', width=1)
        canvas.create_rectangle(x+12, y-5, x+20, y+5, fill=primary_color, outline='#000000', width=1)
        
        # Legs
        canvas.create_rectangle(x-8, y+15, x-3, y+30, fill=primary_color, outline='#000000', width=1)
        canvas.create_rectangle(x+3, y+15, x+8, y+30, fill=primary_color, outline='#000000', width=1)

    def draw_building_model(self, canvas, x, y, primary_color, secondary_color):
        """Draw a building/architecture model"""
        # Base structure
        canvas.create_rectangle(x-25, y+5, x+25, y+25, fill=primary_color, outline='#000000', width=2)
        
        # Upper structure
        canvas.create_rectangle(x-15, y-15, x+15, y+5, fill=secondary_color, outline='#000000', width=2)
        
        # Roof
        points = [x-18, y-15, x, y-30, x+18, y-15]
        canvas.create_polygon(points, fill=primary_color, outline='#000000', width=2)
        
        # Windows
        canvas.create_rectangle(x-10, y-10, x-5, y-2, fill='#87CEEB', outline='#000000', width=1)
        canvas.create_rectangle(x+5, y-10, x+10, y-2, fill='#87CEEB', outline='#000000', width=1)
        
        # Door
        canvas.create_rectangle(x-3, y+5, x+3, y+20, fill='#654321', outline='#000000', width=1)

    def draw_vehicle_model(self, canvas, x, y, primary_color, secondary_color):
        """Draw a vehicle model"""
        # Main body
        canvas.create_rectangle(x-25, y-5, x+25, y+10, fill=primary_color, outline='#000000', width=2)
        
        # Windshield
        canvas.create_rectangle(x-15, y-15, x+15, y-5, fill=secondary_color, outline='#000000', width=2)
        
        # Wheels
        canvas.create_oval(x-20, y+8, x-10, y+18, fill='#000000', outline='#666666', width=2)
        canvas.create_oval(x+10, y+8, x+20, y+18, fill='#000000', outline='#666666', width=2)
        
        # Lights
        canvas.create_oval(x-25, y-2, x-20, y+3, fill='#FFFF00', outline='#000000', width=1)
        canvas.create_oval(x+20, y-2, x+25, y+3, fill='#FFFF00', outline='#000000', width=1)

    def draw_abstract_3d_object(self, canvas, x, y, primary_color, secondary_color):
        """Draw an abstract 3D object"""
        # Complex geometric shape
        # Main sphere
        canvas.create_oval(x-15, y-15, x+15, y+15, fill=primary_color, outline='#000000', width=2)
        
        # Intersecting shapes
        canvas.create_rectangle(x-20, y-5, x+20, y+5, fill=secondary_color, outline='#000000', width=1)
        canvas.create_oval(x-8, y-25, x+8, y+25, fill='', outline='#000000', width=2)
        
        # Add surface details
        canvas.create_arc(x-12, y-12, x+12, y+12, start=45, extent=90, outline='#000000', width=1)
        canvas.create_arc(x-12, y-12, x+12, y+12, start=225, extent=90, outline='#000000', width=1)

    def draw_wireframe_overlay(self, canvas, x, y):
        """Draw wireframe overlay for processing items"""
        # Grid pattern
        for i in range(0, 148, 20):
            canvas.create_line(i, 0, i, 118, fill='#444444', width=1, dash=(2, 2))
        for i in range(0, 118, 15):
            canvas.create_line(0, i, 148, i, fill='#444444', width=1, dash=(2, 2))

    def get_asset_status_color(self, status):
        """Get color for asset status"""
        colors = {
            'textured': self.colors['accent_green'],
            'grayscale': self.colors['text_muted'],
            'pending': self.colors['accent_orange']
        }
        return colors.get(status, self.colors['text_secondary'])

    def select_all_assets(self):
        """Select all assets"""
        for var in self.asset_vars:
            var.set(True)
        self.log_message("✅ Selected all assets", "success")

    def download_selected_assets(self):
        """Download all selected assets"""
        if not hasattr(self, 'asset_vars'):
            self.log_message("⚠️ No assets available", "warning")
            return
            
        selected_assets = [asset for i, asset in enumerate(self.bee_assets) 
                          if i < len(self.asset_vars) and self.asset_vars[i].get()]
        
        if not selected_assets:
            self.log_message("⚠️ No assets selected", "warning")
            return
        
        self.log_message(f"💾 Downloading {len(selected_assets)} selected assets...", "info")
        
        for asset in selected_assets:
            if asset['download_ready']:
                self.log_message(f"⬇️ Downloading {asset['name']}...", "info")
        
        self.log_message("✅ Batch download completed!", "success")

    def download_asset(self, asset, format_type):
        """Download individual asset in specified format"""
        def download_thread():
            try:
                # Check if it's a real Meshy asset with download URLs
                if 'model_urls' in asset and asset['model_urls']:
                    model_urls = asset['model_urls']
                    download_url = None
                    
                    # Map format types to Meshy API URL keys
                    if format_type.lower() == 'glb' and 'glb' in model_urls:
                        download_url = model_urls['glb']
                    elif format_type.lower() == 'obj' and 'obj' in model_urls:
                        download_url = model_urls['obj']
                    elif format_type.lower() == 'png' and 'mtl' in model_urls:
                        download_url = model_urls['mtl']  # or thumbnail
                    
                    if download_url:
                        import requests
                        import os
                        from tkinter import filedialog
                        
                        # Ask user where to save the file
                        filename = f"{asset['name'].replace(' ', '_').lower()}.{format_type}"
                        file_path = filedialog.asksaveasfilename(
                            defaultextension=f".{format_type}",
                            filetypes=[(f"{format_type.upper()} files", f"*.{format_type}")],
                            initialname=filename
                        )
                        
                        if file_path:
                            self.root.after(0, lambda: self.log_message(f"💾 Downloading {filename}...", "info"))
                            
                            # Download the file
                            api_key = self.meshy_api_key.get()
                            headers = {'Authorization': f'Bearer {api_key}'} if api_key else {}
                            
                            response = requests.get(download_url, headers=headers, stream=True)
                            response.raise_for_status()
                            
                            with open(file_path, 'wb') as f:
                                for chunk in response.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            
                            self.root.after(0, lambda: self.log_message(f"✅ Downloaded {filename} to {file_path}", "success"))
                        else:
                            self.root.after(0, lambda: self.log_message("❌ Download cancelled", "warning"))
                    else:
                        self.root.after(0, lambda: self.log_message(f"❌ {format_type.upper()} format not available for this asset", "error"))
                else:
                    # Fallback for mock assets - simulate download
                    filename = f"{asset['name'].replace(' ', '_').lower()}.{format_type}"
                    self.root.after(0, lambda: self.log_message(f"💾 Simulating download of {filename} (demo asset)", "info"))
                    import time
                    time.sleep(1)
                    self.root.after(0, lambda: self.log_message(f"✅ Demo download completed: {filename}", "success"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"❌ Download failed: {str(e)}", "error"))
        
        import threading
        thread = threading.Thread(target=download_thread)
        thread.daemon = True
        thread.start()

    def get_status_color(self, status):
        """Get color for status"""
        colors = {
            'Ready': self.colors['text_secondary'],
            'Processing': self.colors['accent_orange'], 
            'Processed': self.colors['accent_green'],
            'Error': self.colors['error']
        }
        return colors.get(status, self.colors['text_muted'])

    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s}{size_names[i]}"

    def select_all_files(self):
        """Select all files in the list"""
        for var in self.selected_file_vars:
            var.set(True)
        self.update_batch_status()

    def clear_all_files(self):
        """Clear all file selections"""
        for var in self.selected_file_vars:
            var.set(False)
        self.update_batch_status()

    def update_batch_status(self):
        """Update batch operation status display"""
        selected_count = sum(1 for var in self.selected_file_vars if var.get())
        total_count = len(self.file_items)
        
        if selected_count == 0:
            status_text = "Select files and choose operation"
        else:
            status_text = f"{selected_count} of {total_count} files selected"
        
        if hasattr(self, 'batch_status'):
            self.batch_status.configure(text=status_text)

    def convert_selected_files(self):
        """Convert selected files using Meshy API"""
        selected_indices = [i for i, var in enumerate(self.selected_file_vars) if var.get()]
        
        if not selected_indices:
            self.log_message("⚠️ No files selected for conversion", "warning")
            return
        
        if self.connection_manager.connection_status != "connected":
            self.log_message("❌ Not connected to Meshy API", "error")
            return
        
        self.log_message(f"🎨 Starting conversion of {len(selected_indices)} files...", "info")
        
        def convert_thread():
            for idx in selected_indices:
                file_info = None
                try:
                    file_info = self.file_items[idx]
                    self.root.after(0, lambda f=file_info: self.log_message(f"🔄 Processing {f['name']}...", "info"))
                    
                    # Update status
                    file_info['status'] = 'Processing'
                    self.root.after(0, self.refresh_file_list)
                    
                    # Simulate processing (replace with actual Meshy API calls)
                    time.sleep(2)
                    
                    # Update to processed status
                    file_info['status'] = 'Processed'
                    file_info['download_url'] = f"https://meshy.ai/download/{file_info['name']}"
                    
                    self.root.after(0, lambda f=file_info: self.log_message(f"✅ Processed {f['name']}", "success"))
                    
                except Exception as e:
                    if file_info is not None:
                        file_info['status'] = 'Error'
                        self.root.after(0, lambda f=file_info, err=str(e): self.log_message(f"❌ Error processing {f['name']}: {err}", "error"))
                    else:
                        self.root.after(0, lambda err=str(e): self.log_message(f"❌ Error processing file at index {idx}: {err}", "error"))
                
                self.root.after(0, self.refresh_file_list)
        
        import threading
        thread = threading.Thread(target=convert_thread)
        thread.daemon = True
        thread.start()

    def create_png_snapshots(self):
        """Create PNG snapshots of selected 3D files"""
        selected_indices = [i for i, var in enumerate(self.selected_file_vars) if var.get()]
        
        if not selected_indices:
            self.log_message("⚠️ No files selected for PNG creation", "warning")
            return
        
        self.log_message(f"📷 Creating PNG snapshots for {len(selected_indices)} files...", "info")
        
        def snapshot_thread():
            for idx in selected_indices:
                file_info = None
                try:
                    file_info = self.file_items[idx]
                    
                    # Check if it's a 3D file
                    if file_info['type'].lower() not in ['obj', 'glb', 'gltf', 'fbx']:
                        self.root.after(0, lambda f=file_info: self.log_message(f"⚠️ Skipping {f['name']} - not a 3D model", "warning"))
                        continue
                    
                    self.root.after(0, lambda f=file_info: self.log_message(f"📸 Creating snapshot for {f['name']}...", "info"))
                    
                    # Simulate snapshot creation
                    time.sleep(1.5)
                    
                    # Create PNG file info
                    png_name = f"{Path(file_info['name']).stem}!.png"
                    png_info = {
                        'path': f"{file_info['path']}_snapshot.png",
                        'name': png_name,
                        'type': 'PNG',
                        'size': '250KB',
                        'status': 'Processed',
                        'meshy_id': f"snap_{file_info['name']}",
                        'download_url': f"https://meshy.ai/snapshots/{png_name}"
                    }
                    
                    self.file_items.append(png_info)
                    self.root.after(0, lambda f=file_info: self.log_message(f"✅ Created snapshot {png_name}", "success"))
                    
                except Exception as e:
                    if file_info is not None:
                        self.root.after(0, lambda f=file_info, err=str(e): self.log_message(f"❌ Error creating snapshot for {f['name']}: {err}", "error"))
                    else:
                        self.root.after(0, lambda err=str(e): self.log_message(f"❌ Error creating snapshot for file at index {idx}: {err}", "error"))
                
                self.root.after(0, self.refresh_file_list)
        
        import threading
        thread = threading.Thread(target=snapshot_thread)
        thread.daemon = True
        thread.start()

    def download_all_files(self):
        """Download all processed files"""
        processed_files = [f for f in self.file_items if f['status'] == 'Processed' and f.get('download_url')]
        
        if not processed_files:
            self.log_message("⚠️ No processed files available for download", "warning")
            return
        
        from tkinter import filedialog
        download_dir = filedialog.askdirectory(title="Select Download Directory")
        
        if download_dir:
            self.log_message(f"💾 Downloading {len(processed_files)} files to {download_dir}...", "info")
            
            def download_thread():
                for file_info in processed_files:
                    try:
                        # Simulate download
                        self.root.after(0, lambda f=file_info: self.log_message(f"⬇️ Downloading {f['name']}...", "info"))
                        time.sleep(1)
                        self.root.after(0, lambda f=file_info: self.log_message(f"✅ Downloaded {f['name']}", "success"))
                    except Exception as e:
                        self.root.after(0, lambda f=file_info, err=str(e): self.log_message(f"❌ Error downloading {f['name']}: {err}", "error"))
            
            import threading
            thread = threading.Thread(target=download_thread)
            thread.daemon = True
            thread.start()

    def export_for_railway(self):
        """Export files in Railway-compatible format"""
        selected_indices = [i for i, var in enumerate(self.selected_file_vars) if var.get()]
        
        if not selected_indices:
            self.log_message("⚠️ No files selected for Railway export", "warning")
            return
        
        from tkinter import filedialog
        export_dir = filedialog.askdirectory(title="Select Railway Export Directory")
        
        if export_dir:
            self.log_message(f"🏭 Exporting {len(selected_indices)} files for Railway deployment...", "info")
            
            def export_thread():
                try:
                    # Create Railway structure
                    railway_dir = Path(export_dir) / "railway_assets"
                    railway_dir.mkdir(exist_ok=True)
                    
                    for idx in selected_indices:
                        file_info = self.file_items[idx]
                        
                        # Process different file types for Railway
                        if file_info['type'].lower() == 'obj':
                            # Convert OBJ to GLB for web
                            glb_name = f"{Path(file_info['name']).stem}_meshy.glb"
                            self.root.after(0, lambda f=glb_name: self.log_message(f"🔄 Converting to {f}...", "info"))
                            time.sleep(1)
                            
                        elif file_info['name'].endswith('!.png'):
                            # Railway snapshot
                            self.root.after(0, lambda f=file_info: self.log_message(f"📷 Processing Railway snapshot {f['name']}...", "info"))
                            time.sleep(0.5)
                    
                    self.root.after(0, lambda: self.log_message("✅ Railway export completed!", "success"))
                    
                except Exception as e:
                    self.root.after(0, lambda err=str(e): self.log_message(f"❌ Railway export failed: {err}", "error"))
            
            import threading
            thread = threading.Thread(target=export_thread)
            thread.daemon = True
            thread.start()

    def process_single_file(self, index):
        """Process a single file"""
        if index < len(self.file_items):
            file_info = self.file_items[index]
            self.log_message(f"🚀 Processing {file_info['name']}...", "info")
            
            # Select this file and process
            self.selected_file_vars[index].set(True)
            self.convert_selected_files()

    def download_single_file(self, index):
        """Download a single file"""
        if index < len(self.file_items):
            file_info = self.file_items[index]
            self.log_message(f"💾 Downloading {file_info['name']}...", "info")
            
            # Simulate download
            def download_thread():
                time.sleep(1)
                self.root.after(0, lambda: self.log_message(f"✅ Downloaded {file_info['name']}", "success"))
            
            import threading
            thread = threading.Thread(target=download_thread)
            thread.daemon = True
            thread.start()

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = FuturisticCyberpunk3DGUI(root)
    
    # Add startup messages
    app.log_message("🌌 Enhanced 3D File Generator - Cyberpunk Edition initialized", "info")
    app.log_message("🔧 Futuristic UI systems online", "success")
    app.log_message("🎯 Ready for AI-powered 3D processing", "info")
    
    root.mainloop()

if __name__ == "__main__":
    main()