"""
Modern Enhanced 3D File Generator GUI
Matches the design from the provided mockup
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import json
from typing import List, Optional
import threading
import time

# Try to import the enhanced functionality
try:
    from meshy_api_client import MeshyAPIClient, MeshyTask
    MESHY_AVAILABLE = True
except ImportError:
    MESHY_AVAILABLE = False
    print("⚠️ Meshy API client not available. Some features will be disabled.")

class ModernEnhanced3DGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Enhanced 3D File Generator")
        self.root.geometry("1200x800")
        self.root.configure(bg='#0a1425')  # Dark blue background
        self.root.resizable(True, True)
        
        # Application state
        self.selected_files = []
        self.processing_mode = tk.StringVar(value="standard")
        self.meshy_api_key = tk.StringVar(value="msy_t9FYfPHBWK1c8VBfX0pLxnEZMdWbg0DEc2qz")
        self.texture_style = tk.StringVar(value="Professional Realistic Textures")
        self.create_thumbnails = tk.BooleanVar(value=True)
        self.railway_ready = tk.BooleanVar(value=False)
        
        # Processing state
        self.current_step = 0
        self.total_steps = 4
        self.log_entries = []
        
        self.setup_modern_gui()
        
    def setup_modern_gui(self):
        """Create the modern GUI layout matching the mockup"""
        
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
        
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(main_frame)
        
        # Content area with three columns
        content_frame = tk.Frame(main_frame, bg=self.colors['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Left column - Controls
        self.create_left_panel(content_frame)
        
        # Center column - Log and Progress
        self.create_center_panel(content_frame)
        
        # Right column - Info and Requirements
        self.create_right_panel(content_frame)
        
    def create_header(self, parent):
        """Create the header with title and icon"""
        header_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title with icon
        title_frame = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        title_frame.pack(side=tk.LEFT)
        
        # Icon (using text for now, could be replaced with actual icon) 
        icon_label = tk.Label(title_frame, text="🗂️", font=('Arial', 24), 
                             bg=self.colors['bg_primary'], fg=self.colors['accent_cyan'])
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        title_label = tk.Label(title_frame, text="ENHANCED 3D FILE GENERATOR", 
                              font=('Arial', 18, 'bold'),
                              bg=self.colors['bg_primary'], fg=self.colors['text_primary'])
        title_label.pack(side=tk.LEFT)
        
    def create_left_panel(self, parent):
        """Create the left control panel"""
        left_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='raised', bd=1)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=0, ipadx=15, ipady=15)
        left_frame.configure(width=280)
        left_frame.pack_propagate(False)
        
        # Processing Mode Section
        mode_frame = self.create_section_frame(left_frame, "Processing Mode")
        
        # Radio buttons for processing mode
        tk.Radiobutton(mode_frame, text="Standard Processing", 
                      variable=self.processing_mode, value="standard",
                      bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                      selectcolor=self.colors['bg_tertiary'], 
                      activebackground=self.colors['bg_tertiary'],
                      font=('Arial', 10)).pack(anchor='w', pady=2)
        
        tk.Radiobutton(mode_frame, text="AI Processing with Meshy API", 
                      variable=self.processing_mode, value="meshy",
                      bg=self.colors['bg_secondary'], fg=self.colors['accent_cyan'],
                      selectcolor=self.colors['bg_tertiary'],
                      activebackground=self.colors['bg_tertiary'],
                      font=('Arial', 10, 'bold')).pack(anchor='w', pady=2)
        
        # API Key Section
        api_frame = self.create_section_frame(left_frame, "Meshy API Key")
        
        self.api_entry = tk.Entry(api_frame, textvariable=self.meshy_api_key,
                                 bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'],
                                 insertbackground=self.colors['accent_cyan'],
                                 relief='flat', font=('Courier', 10))
        self.api_entry.pack(fill=tk.X, pady=5)
        
        # Style Selection
        style_frame = self.create_section_frame(left_frame, "Texture Style")
        
        style_options = [
            "Professional Realistic Textures",
            "Create Thumbnails",
            "Railway Ready Output"
        ]
        
        for option in style_options:
            if option == "Professional Realistic Textures":
                var = tk.BooleanVar(value=True)
            elif option == "Create Thumbnails":
                var = self.create_thumbnails
            else:
                var = self.railway_ready
                
            cb = tk.Checkbutton(style_frame, text=option, variable=var,
                               bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                               selectcolor=self.colors['bg_tertiary'],
                               activebackground=self.colors['bg_tertiary'],
                               font=('Arial', 9))
            cb.pack(anchor='w', pady=2)
        
        # Action Buttons
        button_frame = tk.Frame(left_frame, bg=self.colors['bg_secondary'])
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Meshy Process Button (prominent)
        self.meshy_btn = tk.Button(button_frame, text="MESHY PROCESS",
                                  command=self.start_meshy_process,
                                  bg=self.colors['accent_cyan'], fg='white',
                                  font=('Arial', 12, 'bold'),
                                  relief='flat', pady=10)
        self.meshy_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Other action buttons
        actions = [
            ("📁 Uploading", self.select_files),
            ("▶ Select Output Directory", self.select_output_dir), 
            ("🔄 Convert Files", self.convert_files),
            ("🖼️ Create Thumbnails (Optional)", self.create_thumbnails_action)
        ]
        
        for text, command in actions:
            btn = tk.Button(button_frame, text=text, command=command,
                           bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'],
                           font=('Arial', 9), relief='flat', pady=5)
            btn.pack(fill=tk.X, pady=2)
        
        # Terminal info
        terminal_frame = tk.Frame(left_frame, bg=self.colors['bg_secondary'])
        terminal_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Label(terminal_frame, text="🗂️ python 3DFile_FileFolderGenerator.py",
                bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                font=('Courier', 8)).pack(anchor='w')
        
        tk.Label(terminal_frame, text="📁 python 3DFile_FileFolderGenera...",
                bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                font=('Courier', 8)).pack(anchor='w')
        
    def create_center_panel(self, parent):
        """Create the center panel with log and progress"""
        center_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 5))
        
        # Meshy API Features section
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
                    bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                    font=('Arial', 10)).pack(anchor='w', pady=2)
        
        # Log Code section
        log_frame = self.create_section_frame(center_frame, "LOG CODE")
        
        # Create text widget for log
        self.log_text = tk.Text(log_frame, height=12, 
                               bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'],
                               font=('Courier', 9), relief='flat',
                               insertbackground=self.colors['accent_cyan'])
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Initialize log with sample entries
        self.add_log_entry("1", "Upload OBJ IGIB roma.ip", "info")
        self.add_log_entry("2", "Select OBJ Conversion", "info")  
        self.add_log_entry("3", "Convert Filenames(2)", "info")
        self.add_log_entry("4", "Create Thumbnails", "info")
        
        # Completed section
        completed_frame = self.create_section_frame(center_frame, "COMPLETED")
        
        completed_items = [
            ("2022 10.01.33", "COMPLETED", "success"),
            ("2023 10.02.33", "Uploading processedObj", "info"),
            ("2022 10.03.33", "Texture styles", "info"),
            ("2023 10.02.30", "Creating thumbnails", "info"),
            ("2022 10.02.33", "Asset organization", "info")
        ]
        
        for timestamp, action, status in completed_items:
            item_frame = tk.Frame(completed_frame, bg=self.colors['bg_secondary'])
            item_frame.pack(fill=tk.X, pady=1)
            
            tk.Label(item_frame, text=timestamp,
                    bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                    font=('Courier', 8)).pack(side=tk.LEFT)
            
            color = self.colors['success'] if status == 'success' else self.colors['text_primary']
            tk.Label(item_frame, text=action,
                    bg=self.colors['bg_secondary'], fg=color,
                    font=('Arial', 9)).pack(side=tk.LEFT, padx=(10, 0))
        
    def create_right_panel(self, parent):
        """Create the right panel with requirements and file info"""
        right_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='raised', bd=1)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0), pady=0, ipadx=15, ipady=15)
        right_frame.configure(width=280)
        right_frame.pack_propagate(False)
        
        # Requirements section
        req_frame = self.create_section_frame(right_frame, "REQUIREMENTS")
        
        tk.Label(req_frame, text="Python\nDependencies:",
                bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                font=('Arial', 10, 'bold')).pack(anchor='w')
        
        deps = ["trimesh pyrender", "pillow-the.point"]
        for dep in deps:
            tk.Label(req_frame, text=dep,
                    bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                    font=('Arial', 9)).pack(anchor='w', padx=(10, 0))
        
        tk.Label(req_frame, text="\nMeshy API\nAccount:",
                bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                font=('Arial', 10, 'bold')).pack(anchor='w')
        
        tk.Label(req_frame, text="server.ai.meshy.ai",
                bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                font=('Arial', 9)).pack(anchor='w', padx=(10, 0))
        
        tk.Label(req_frame, text="python 3DFile_\nFileFolderGenerator.py",
                bg=self.colors['bg_secondary'], fg=self.colors['text_secondary'],
                font=('Courier', 8)).pack(anchor='w', padx=(10, 0))
        
        # Input Files section
        input_frame = self.create_section_frame(right_frame, "INPUT FILES")
        
        input_files = [
            ("📁", "your.model.zip"),
            ("📄", "ModelName.obj"),
            ("📄", "ModelName.mtl")
        ]
        
        for icon, filename in input_files:
            file_frame = tk.Frame(input_frame, bg=self.colors['bg_secondary'])
            file_frame.pack(fill=tk.X, pady=1)
            
            tk.Label(file_frame, text=icon,
                    bg=self.colors['bg_secondary'], fg=self.colors['accent_cyan'],
                    font=('Arial', 10)).pack(side=tk.LEFT)
            
            tk.Label(file_frame, text=filename,
                    bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                    font=('Arial', 9)).pack(side=tk.LEFT, padx=(5, 0))
        
        # Output Files section  
        output_frame = self.create_section_frame(right_frame, "OUTPUT FILES")
        
        output_files = [
            ("📁", "processed.models/"),
            ("📄", "ModelName.obj"),
            ("📄", "railway.assets")
        ]
        
        for icon, filename in output_files:
            file_frame = tk.Frame(output_frame, bg=self.colors['bg_secondary'])
            file_frame.pack(fill=tk.X, pady=1)
            
            tk.Label(file_frame, text=icon,
                    bg=self.colors['bg_secondary'], fg=self.colors['accent_cyan'],
                    font=('Arial', 10)).pack(side=tk.LEFT)
            
            tk.Label(file_frame, text=filename,
                    bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                    font=('Arial', 9)).pack(side=tk.LEFT, padx=(5, 0))
        
    def create_section_frame(self, parent, title):
        """Create a section frame with title"""
        section = tk.Frame(parent, bg=self.colors['bg_secondary'])
        section.pack(fill=tk.X, pady=(0, 15))
        
        # Section title
        title_label = tk.Label(section, text=title,
                              bg=self.colors['bg_secondary'], fg=self.colors['accent_cyan'],
                              font=('Arial', 10, 'bold'))
        title_label.pack(anchor='w', pady=(0, 8))
        
        # Content frame
        content_frame = tk.Frame(section, bg=self.colors['bg_secondary'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        return content_frame
        
    def add_log_entry(self, step, message, level="info"):
        """Add entry to log"""
        self.log_text.insert(tk.END, f"{step}    {message}\n")
        self.log_text.see(tk.END)
        
    def select_files(self):
        """Select input files"""
        files = filedialog.askopenfilenames(
            title="Select 3D Model Files",
            filetypes=[("ZIP files", "*.zip"), ("OBJ files", "*.obj"), ("All files", "*.*")]
        )
        if files:
            self.selected_files = list(files)
            self.add_log_entry("📁", f"Selected {len(files)} file(s)", "success")
            
    def select_output_dir(self):
        """Select output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir = Path(directory)
            self.add_log_entry("📂", f"Output: {self.output_dir.name}", "success")
            
    def convert_files(self):
        """Standard file conversion"""
        if not self.selected_files:
            messagebox.showwarning("No Files", "Please select files first")
            return
            
        self.add_log_entry("🔄", "Starting standard conversion...", "info")
        # Add actual conversion logic here
        
    def create_thumbnails_action(self):
        """Create thumbnails"""
        self.add_log_entry("🖼️", "Creating thumbnails...", "info")
        # Add thumbnail creation logic here
        
    def start_meshy_process(self):
        """Start Meshy API processing"""
        if not MESHY_AVAILABLE:
            messagebox.showerror("Error", "Meshy API not available")
            return
            
        if not self.meshy_api_key.get():
            messagebox.showwarning("No API Key", "Please enter your Meshy API key")
            return
            
        if not self.selected_files:
            messagebox.showwarning("No Files", "Please select files first")
            return
            
        # Start processing in separate thread
        threading.Thread(target=self.meshy_process_thread, daemon=True).start()
        
    def meshy_process_thread(self):
        """Meshy processing in separate thread"""
        try:
            self.add_log_entry("🎨", "Starting Meshy API processing...", "info")
            
            # Simulate processing steps
            steps = [
                ("Uploading to Meshy API...", 2),
                ("Generating textures...", 3),
                ("Processing mesh...", 2),
                ("Downloading results...", 1)
            ]
            
            for step_text, duration in steps:
                self.add_log_entry("⚙️", step_text, "info")
                time.sleep(duration)
                
            self.add_log_entry("✅", "Meshy processing completed!", "success")
            
        except Exception as e:
            self.add_log_entry("❌", f"Error: {str(e)}", "error")
            
    def run(self):
        """Start the GUI"""
        self.root.mainloop()

def main():
    """Main entry point"""
    app = ModernEnhanced3DGUI()
    app.run()

if __name__ == "__main__":
    main()