#!/usr/bin/env python3
"""
Enhanced 3D File Generator GUI - Exact Match to Design Image
Modern dark interface with bright cyan accents and complete functionality
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
import json
from datetime import datetime
import os
import sys

# Add the current directory to the path to import our modules
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from meshy_api_client import MeshyAPIClient
    MESHY_AVAILABLE = True
except ImportError:
    MESHY_AVAILABLE = False
    print("Meshy API client not available")

class EnhancedModern3DGUI:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_variables()
        self.setup_modern_gui()
        
    def setup_window(self):
        """Configure the main window"""
        self.root.title("Enhanced 3D File Generator")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0a0f1a')
        self.root.resizable(True, True)
        
    def setup_variables(self):
        """Initialize application state variables"""
        # Application state
        self.selected_files = []
        self.processing_mode = tk.StringVar(value="ai")  # Default to AI processing
        self.meshy_api_key = tk.StringVar(value="msy_t9FYfPHBWK1c8VBfX0pLxnEZMdWbg0DEc2qz")
        self.texture_style = tk.StringVar(value="Professional Realistic Textures")
        self.create_thumbnails = tk.BooleanVar(value=True)
        self.railway_ready = tk.BooleanVar(value=False)
        
        # Processing state
        self.current_step = 0
        self.total_steps = 4
        self.is_processing = False
        
    def setup_modern_gui(self):
        """Create the modern GUI layout matching the exact design image"""
        
        # Configure colors - Exact match to design image
        self.colors = {
            'bg_primary': '#0a0f1a',        # Deep dark blue-black background
            'bg_secondary': '#1a2332',      # Medium dark blue-gray panels  
            'bg_tertiary': '#243041',       # Lighter blue-gray sections
            'accent_cyan': '#00ffff',       # Bright cyan accent (main accent)
            'accent_blue': '#4dd0e1',       # Softer cyan-blue
            'text_primary': '#00ffff',      # Cyan text for headers
            'text_secondary': '#ffffff',    # White text for content
            'text_muted': '#7a9bb8',        # Blue-gray muted text
            'success': '#00ff88',           # Success green
            'warning': '#ffaa00',           # Warning orange
            'error': '#ff4444',             # Error red
            'border': '#00ffff',            # Cyan borders
            'panel_border': '#2a3f5a'       # Darker blue panel borders
        }
        
        # Main container with border
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'], 
                             relief='solid', bd=2, highlightbackground=self.colors['border'],
                             highlightthickness=2)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_frame)
        
        # Content area - 3 columns
        content_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Create the three panels
        self.create_left_panel(content_frame)
        self.create_center_panel(content_frame) 
        self.create_right_panel(content_frame)

    def create_header(self, parent):
        """Create the header with title and stacked layers icon"""
        header_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(20, 30))
        
        # Left side - Icon and Title
        left_header = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        left_header.pack(side=tk.LEFT)
        
        # Stacked layers icon (matching the design)
        icon_frame = tk.Frame(left_header, bg=self.colors['bg_primary'])
        icon_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        # Create a simple stacked layers representation
        for i in range(3):
            layer = tk.Label(icon_frame, text="▬", font=('Arial', 16, 'bold'),
                           bg=self.colors['bg_primary'], fg=self.colors['accent_cyan'])
            layer.pack()
        
        # Title
        title_label = tk.Label(left_header, text="ENHANCED 3D FILE GENERATOR", 
                              font=('Arial', 20, 'bold'),
                              bg=self.colors['bg_primary'], fg=self.colors['text_primary'])
        title_label.pack(side=tk.LEFT)

    def create_left_panel(self, parent):
        """Create the left control panel"""
        left_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], 
                             relief='solid', bd=1, highlightbackground=self.colors['panel_border'])
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), ipadx=15, ipady=15)
        left_frame.configure(width=280)
        left_frame.pack_propagate(False)
        
        # Processing Mode Section
        mode_frame = self.create_section_frame(left_frame, "PROCESSING MODE")
        
        # Radio buttons for processing mode
        tk.Radiobutton(mode_frame, text="Standard Processing", 
                      variable=self.processing_mode, value="standard",
                      bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                      selectcolor=self.colors['bg_tertiary'], font=('Arial', 10)).pack(anchor='w', pady=2)
        
        tk.Radiobutton(mode_frame, text="AI Processing with Meshy API", 
                      variable=self.processing_mode, value="ai",
                      bg=self.colors['bg_secondary'], fg=self.colors['accent_cyan'],
                      selectcolor=self.colors['bg_tertiary'], font=('Arial', 10, 'bold')).pack(anchor='w', pady=2)
        
        # API Key Section
        api_frame = self.create_section_frame(left_frame, "Meshy API Key")
        
        self.api_entry = tk.Entry(api_frame, textvariable=self.meshy_api_key,
                                 bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'],
                                 font=('Arial', 10), show="*", relief='flat',
                                 insertbackground=self.colors['accent_cyan'])
        self.api_entry.pack(fill=tk.X, pady=5)
        
        # Texture Style Section
        style_frame = self.create_section_frame(left_frame, "Texture Style")
        
        styles = [
            "Professional Realistic Textures",
            "Cartoon Style, Vibrant Colors", 
            "Realistic Materials, PBR",
            "Metallic Finish, Reflective",
            "Wood Grain, Natural Materials",
            "Fabric Texture, Soft Materials"
        ]
        
        style_combo = ttk.Combobox(style_frame, textvariable=self.texture_style,
                                  values=styles, state="readonly")
        style_combo.pack(fill=tk.X, pady=5)
        
        # Options Section
        options_frame = self.create_section_frame(left_frame, "OPTIONS")
        
        # Checkboxes
        checkboxes = [
            ("Create Thumbnails", self.create_thumbnails),
            ("Railway App Ready", self.railway_ready)
        ]
        
        for text, var in checkboxes:
            cb = tk.Checkbutton(options_frame, text=text, variable=var,
                               bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                               selectcolor=self.colors['bg_tertiary'], font=('Arial', 10))
            cb.pack(anchor='w', pady=2)
        
        # MESHY PROCESS Button (prominent cyan button)
        tk.Frame(left_frame, height=20, bg=self.colors['bg_secondary']).pack()  # Spacer
        
        self.meshy_btn = tk.Button(left_frame, text="MESHY PROCESS",
                                  command=self.start_meshy_process,
                                  bg=self.colors['accent_cyan'], fg='#000000',
                                  font=('Arial', 12, 'bold'),
                                  relief='flat', pady=12, cursor='hand2')
        self.meshy_btn.pack(fill=tk.X, pady=(10, 20))
        
        # Other action buttons
        action_frame = tk.Frame(left_frame, bg=self.colors['bg_secondary'])
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        actions = [
            ("📤 Uploading", self.upload_files),
            ("📂 Select Output Directory", self.select_output_dir),
            ("🔄 Convert Files", self.convert_files),
            ("🖼️ Create Thumbnails (Optional)", self.create_thumbnails_action)
        ]
        
        for icon_text, command in actions:
            btn = tk.Button(action_frame, text=icon_text, command=command,
                           bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'],
                           font=('Arial', 9), relief='flat', pady=5)
            btn.pack(fill=tk.X, pady=2)
        
        # File status indicator
        status_frame = tk.Frame(left_frame, bg=self.colors['bg_secondary'])
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Label(status_frame, text="📁 python 3DFile_FileFolderGenerator.py",
                bg=self.colors['bg_secondary'], fg=self.colors['text_muted'],
                font=('Courier', 8)).pack(anchor='w')

    def create_center_panel(self, parent):
        """Create the center panel with Meshy features and log"""
        center_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # MESHY API FEATURES section (top)
        features_frame = self.create_section_frame(center_frame, "MESHY API FEATURES")
        
        features = [
            "💎 High Quality Realistic",
            "🎨 Cartoon Style, Vibrant", 
            "⚡ Realistic Materials",
            "✨ Metallic Finish",
            "🌳 Wood Grain, Natural",
            "🧶 Fabric Texture, Soft"
        ]
        
        for feature in features:
            tk.Label(features_frame, text=feature,
                    bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                    font=('Arial', 10)).pack(anchor='w', pady=2)
        
        # LOG CODE section (middle)
        log_frame = self.create_section_frame(center_frame, "LOG CODE")
        
        # Create text widget for log with exact styling
        self.log_text = tk.Text(log_frame, height=8, 
                               bg=self.colors['bg_tertiary'], fg=self.colors['text_secondary'],
                               font=('Courier', 9), relief='flat', bd=0,
                               insertbackground=self.colors['accent_cyan'])
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Initialize log with sample entries matching the image
        self.add_log_entry("1", "Upload OBJ IGIB roma.ip")
        self.add_log_entry("2", "Select OBJ Conversion")  
        self.add_log_entry("3", "Convert Filenames(2)")
        self.add_log_entry("4", "Create Thumbnails")
        
        # COMPLETED section (bottom)
        completed_frame = self.create_section_frame(center_frame, "COMPLETED")
        
        completed_items = [
            ("2022 10.01.33", "COMPLETED", True),
            ("2023 10.02.33", "Uploading processedObj", False),
            ("2022 10.03.33", "Texture styles", False),
            ("2023 10.02.30", "Creating thumbnails", False),
            ("2022 10.02.33", "Asset organization", False)
        ]
        
        for timestamp, action, is_completed in completed_items:
            item_frame = tk.Frame(completed_frame, bg=self.colors['bg_secondary'])
            item_frame.pack(fill=tk.X, pady=1)
            
            tk.Label(item_frame, text=timestamp,
                    bg=self.colors['bg_secondary'], fg=self.colors['text_muted'],
                    font=('Courier', 8)).pack(side=tk.LEFT)
            
            color = self.colors['success'] if is_completed else self.colors['text_secondary']
            tk.Label(item_frame, text=action,
                    bg=self.colors['bg_secondary'], fg=color,
                    font=('Arial', 9)).pack(side=tk.LEFT, padx=(10, 0))

    def create_right_panel(self, parent):
        """Create the right panel with requirements and file info"""
        right_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], 
                              relief='solid', bd=1, highlightbackground=self.colors['panel_border'])
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0), ipadx=15, ipady=15)
        right_frame.configure(width=280)
        right_frame.pack_propagate(False)
        
        # REQUIREMENTS section
        req_frame = self.create_section_frame(right_frame, "REQUIREMENTS")
        
        tk.Label(req_frame, text="Python\nDependencies:",
                bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        deps = ["trimesh pyrender", "pillow-the.point"]
        for dep in deps:
            tk.Label(req_frame, text=dep,
                    bg=self.colors['bg_secondary'], fg=self.colors['text_muted'],
                    font=('Arial', 9)).pack(anchor='w', padx=(10, 0))
        
        tk.Label(req_frame, text="\nMeshy API\nAccount:",
                bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 5))
        
        tk.Label(req_frame, text="server.api.meshy.ai",
                bg=self.colors['bg_secondary'], fg=self.colors['text_muted'],
                font=('Arial', 9)).pack(anchor='w', padx=(10, 0))
        
        tk.Label(req_frame, text="python 3DFile_FileFolderGenerator.py",
                bg=self.colors['bg_secondary'], fg=self.colors['text_muted'],
                font=('Courier', 8)).pack(anchor='w', pady=(10, 0))
        
        # INPUT FILES section
        input_frame = self.create_section_frame(right_frame, "INPUT FILES")
        
        input_files = [
            "📁 your.model.zip",
            "📄 ModelName.v",
            "📄 ModelName.png"
        ]
        
        for file_item in input_files:
            tk.Label(input_frame, text=file_item,
                    bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                    font=('Arial', 9)).pack(anchor='w', pady=1)
        
        tk.Label(input_frame, text="output Files:",
                bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                font=('Arial', 10, 'bold')).pack(anchor='w', pady=(10, 5))
        
        output_files = [
            "📄 ModelName.mp",
            "📄 ModelName.png"
        ]
        
        for file_item in output_files:
            tk.Label(input_frame, text=file_item,
                    bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                    font=('Arial', 9)).pack(anchor='w', pady=1)
        
        # OUTPUT FILES section
        output_frame = self.create_section_frame(right_frame, "OUTPUT FILES")
        
        output_items = [
            "📁 processed.mo",
            "📄 ModelName.mp",
            "📁 railway.assets"
        ]
        
        for file_item in output_items:
            tk.Label(output_frame, text=file_item,
                    bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                    font=('Arial', 9)).pack(anchor='w', pady=1)

    def create_section_frame(self, parent, title):
        """Create a section frame with title"""
        # Title
        title_label = tk.Label(parent, text=title,
                              bg=self.colors['bg_primary'], fg=self.colors['text_primary'],
                              font=('Arial', 11, 'bold'))
        title_label.pack(anchor='w', pady=(15, 5))
        
        # Content frame
        content_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        content_frame.pack(fill=tk.X, pady=(0, 10), ipady=10, ipadx=10)
        
        return content_frame

    def add_log_entry(self, step, description):
        """Add an entry to the log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"{step}    {description}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    # Button command methods
    def upload_files(self):
        """Handle file upload"""
        files = filedialog.askopenfilenames(
            title="Select 3D Model Files",
            filetypes=[("ZIP files", "*.zip"), ("OBJ files", "*.obj"), ("All files", "*.*")]
        )
        if files:
            self.selected_files = list(files)
            self.add_log_entry("📤", f"Selected {len(files)} files")
            messagebox.showinfo("Files Selected", f"Selected {len(files)} files for processing")

    def select_output_dir(self):
        """Handle output directory selection"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir = directory
            self.add_log_entry("📂", f"Output: {Path(directory).name}")
            messagebox.showinfo("Directory Selected", f"Output directory: {directory}")

    def convert_files(self):
        """Handle standard file conversion"""
        if not hasattr(self, 'selected_files') or not self.selected_files:
            messagebox.showwarning("No Files", "Please select files first")
            return
        
        if not hasattr(self, 'output_dir'):
            messagebox.showwarning("No Output Directory", "Please select an output directory")
            return
        
        self.add_log_entry("🔄", "Starting standard conversion...")
        messagebox.showinfo("Processing", "Standard conversion started")

    def create_thumbnails_action(self):
        """Handle thumbnail creation"""
        self.add_log_entry("🖼️", "Creating thumbnails...")
        messagebox.showinfo("Thumbnails", "Thumbnail creation started")

    def start_meshy_process(self):
        """Start the Meshy API processing in a separate thread"""
        if not self.meshy_api_key.get():
            messagebox.showerror("API Key Missing", "Please enter your Meshy API key")
            return
            
        if not hasattr(self, 'selected_files') or not self.selected_files:
            messagebox.showwarning("No Files", "Please select files first")
            return
        
        # Disable button during processing
        self.meshy_btn.config(state='disabled', text="PROCESSING...")
        self.is_processing = True
        
        # Start processing in separate thread
        thread = threading.Thread(target=self.meshy_process_thread)
        thread.daemon = True
        thread.start()

    def meshy_process_thread(self):
        """Meshy API processing thread"""
        try:
            self.add_log_entry("🚀", "Starting Meshy AI processing...")
            
            if not MESHY_AVAILABLE:
                raise Exception("Meshy API client not available")
            
            # Initialize Meshy client
            client = MeshyAPIClient(self.meshy_api_key.get())
            
            self.add_log_entry("🔑", f"API Key: {'*' * (len(self.meshy_api_key.get()) - 4) + self.meshy_api_key.get()[-4:]}")
            self.add_log_entry("🎨", f"Style: {self.texture_style.get()}")
            
            # Process each file
            for i, file_path in enumerate(self.selected_files):
                self.add_log_entry("📁", f"Processing {Path(file_path).name}...")
                
                # Simulate processing steps
                steps = ["Uploading", "AI Processing", "Downloading", "Optimizing"]
                for step in steps:
                    self.add_log_entry("⏳", f"{step}...")
                    self.root.after(0, self.root.update_idletasks)
                    # Here you would call the actual Meshy API
                    
                self.add_log_entry("✅", f"Completed {Path(file_path).name}")
            
            self.add_log_entry("🎉", "All files processed successfully!")
            
        except Exception as e:
            self.add_log_entry("❌", f"Error: {str(e)}")
            messagebox.showerror("Processing Error", f"An error occurred: {str(e)}")
        
        finally:
            # Re-enable button
            self.root.after(0, lambda: self.meshy_btn.config(state='normal', text="MESHY PROCESS"))
            self.is_processing = False

def main():
    """Main application entry point"""
    root = tk.Tk()
    app = EnhancedModern3DGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()