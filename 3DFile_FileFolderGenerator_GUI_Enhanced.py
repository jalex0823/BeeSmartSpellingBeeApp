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
import subprocess

# Check for rendering dependencies
NUMPY_AVAILABLE = False
RENDERING_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np = None

try:
    import trimesh
    import pyrender
    from PIL import Image
    if NUMPY_AVAILABLE:
        RENDERING_AVAILABLE = True
    else:
        trimesh = None
        pyrender = None
        Image = None
except ImportError:
    trimesh = None
    pyrender = None
    Image = None

class Enhanced3DProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced 3D File Processor & Thumbnail Generator")
        self.root.geometry("900x750")
        
        # Modern dark theme setup
        self.setup_dark_theme()
        
        # Processing settings
        self.input_folder = tk.StringVar()
        self.recursive = tk.BooleanVar(value=True)
        self.ask_names = tk.BooleanVar(value=False)
        self.extract_zips = tk.BooleanVar(value=True)
        self.generate_thumbnails = tk.BooleanVar(value=RENDERING_AVAILABLE)
        self.install_deps = tk.BooleanVar(value=False)
        
        # Track selected files
        self.selected_zip_files = None
        self.processing_mode = "folder"  # "folder" or "zip"
        
        # Constants from original script - Enhanced to remove more trailing numbers
        self.NUM_SUFFIX = re.compile(r"(?:[_-]\d{4,})+$", re.IGNORECASE)  # Remove 4+ digit suffixes
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
        self.BACKGROUND_COLOR = (0, 0, 0, 255)  # Black background instead of transparent
        self.CAMERA_DISTANCE_MULT = 2.2
        self.LIGHT_INTENSITY = 6.0
        
        # Queue for thread communication
        self.message_queue = queue.Queue()
        
        self.setup_ui()
    
    def setup_dark_theme(self):
        """Configure modern dark theme styling"""
        # Configure root window
        self.root.configure(bg='#0f0f0f')
        
        # Configure ttk styles
        style = ttk.Style()
        
        # Set theme to alt (better customization base)
        style.theme_use('alt')
        
        # Configure colors
        colors = {
            'bg': '#0f0f0f',          # Darker background (almost black)
            'fg': '#ffffff',           # White text
            'select_bg': '#0d7377',    # Teal selection
            'select_fg': '#ffffff',    # White selected text
            'button_bg': '#2d2d2d',    # Button background
            'button_active': '#404040', # Button active
            'entry_bg': '#2d2d2d',     # Entry background
            'entry_select': '#0d7377', # Entry selection
            'frame_bg': '#0f0f0f',     # Frame background (darker)
            'accent': '#14a085',       # Accent color (green-teal)
            'warning': '#ff6b6b',      # Warning red
            'success': '#51cf66',      # Success green
            'checkbox_bg': '#2d2d2d',  # Checkbox background
            'checkbox_fg': '#00ff00',  # Bright green checkmarks
        }
        
        # Configure ttk widget styles
        style.configure('TFrame', background=colors['bg'])
        style.configure('TLabel', background=colors['bg'], foreground=colors['fg'])
        style.configure('TLabelFrame', background=colors['bg'], foreground=colors['fg'])
        style.configure('TLabelFrame.Label', background=colors['bg'], foreground=colors['fg'])
        
        # Buttons
        style.configure('TButton', 
                       background=colors['button_bg'], 
                       foreground=colors['fg'],
                       borderwidth=1,
                       focuscolor='none')
        style.map('TButton',
                  background=[('active', colors['button_active']),
                             ('pressed', colors['select_bg'])])
        
        # Accent button for important actions
        style.configure('Accent.TButton',
                       background=colors['accent'],
                       foreground='white',
                       borderwidth=1,
                       focuscolor='none')
        style.map('Accent.TButton',
                  background=[('active', '#0d7377'),
                             ('pressed', '#0a5d61')])
        
        # Restart button (special styling)
        style.configure('Restart.TButton',
                       background=colors['warning'],
                       foreground='white',
                       borderwidth=1,
                       focuscolor='none')
        style.map('Restart.TButton',
                  background=[('active', '#ff5252'),
                             ('pressed', '#d32f2f')])
        
        # Entry fields
        style.configure('TEntry',
                       background=colors['entry_bg'],
                       foreground=colors['fg'],
                       fieldbackground=colors['entry_bg'],
                       borderwidth=1,
                       insertcolor=colors['fg'])
        style.map('TEntry',
                  selectbackground=[('focus', colors['entry_select'])])
        
        # Checkbuttons
        style.configure('TCheckbutton',
                       background=colors['bg'],
                       foreground=colors['fg'],
                       focuscolor='none',
                       indicatorcolor=colors['checkbox_bg'],
                       indicatoron=True)
        style.map('TCheckbutton',
                  background=[('active', colors['button_active'])],
                  indicatorcolor=[('selected', colors['checkbox_fg']),
                                ('active', colors['button_active'])])
        
        # Notebook
        style.configure('TNotebook', background=colors['bg'], borderwidth=0)
        style.configure('TNotebook.Tab',
                       background=colors['button_bg'],
                       foreground=colors['fg'],
                       borderwidth=1)
        style.map('TNotebook.Tab',
                  background=[('selected', colors['accent']),
                             ('active', colors['button_active'])])
        
        # Progressbar
        style.configure('TProgressbar',
                       background=colors['accent'],
                       troughcolor=colors['button_bg'],
                       borderwidth=0)
                       
        # Store colors for later use
        self.theme_colors = colors
        
    def setup_ui(self):
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Main Processing Tab
        main_tab = ttk.Frame(notebook)
        notebook.add(main_tab, text="File Processing")
        
        # Dependencies Tab
        deps_tab = ttk.Frame(notebook)
        notebook.add(deps_tab, text="Dependencies & Thumbnails")
        
        self.setup_main_tab(main_tab)
        self.setup_deps_tab(deps_tab)
        
        # Start checking message queue
        self.check_queue()
        
    def setup_main_tab(self, parent):
        # Main frame
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Input selection
        ttk.Label(main_frame, text="Select Input:").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(main_frame, textvariable=self.input_folder, width=50).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_input).grid(row=0, column=2, padx=5)
        
        # Processing options frame
        options_frame = ttk.LabelFrame(main_frame, text="Processing Options", padding="10")
        options_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=10)
        
        ttk.Checkbutton(options_frame, text="Process subfolders recursively", 
                       variable=self.recursive).grid(row=0, column=0, sticky='w')
        ttk.Checkbutton(options_frame, text="Extract ZIP files automatically", 
                       variable=self.extract_zips).grid(row=1, column=0, sticky='w')
        ttk.Checkbutton(options_frame, text="Ask for custom names (interactive mode)", 
                       variable=self.ask_names).grid(row=2, column=0, sticky='w')
        
        # Process buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, columnspan=3, pady=20)
        
        self.process_btn = ttk.Button(buttons_frame, text="🚀 Process Files", 
                                    command=self.start_processing,
                                    style='Accent.TButton')
        self.process_btn.grid(row=0, column=0, padx=5)
        
        self.thumbnail_btn = ttk.Button(buttons_frame, text="🖼️ Generate Thumbnails", 
                                      command=self.start_thumbnail_generation,
                                      style='Accent.TButton',
                                      state='disabled' if not RENDERING_AVAILABLE else 'normal')
        self.thumbnail_btn.grid(row=0, column=1, padx=5)
        
        self.restart_btn = ttk.Button(buttons_frame, text="🔄 Restart App", 
                                    command=self.restart_application,
                                    style='Restart.TButton')
        self.restart_btn.grid(row=0, column=2, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=3, sticky="ew", pady=5)
        
        # Log output
        ttk.Label(main_frame, text="📄 Processing Log:").grid(row=4, column=0, sticky='w', pady=(10, 0))
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, width=80,
                                                bg='#1a1a1a', fg='#ffffff',
                                                insertbackground='#ffffff',
                                                selectbackground='#0d7377',
                                                selectforeground='#ffffff',
                                                font=('Consolas', 9))
        self.log_text.grid(row=5, column=0, columnspan=3, sticky="news", pady=5)
        
        # Configure row weights for text expansion
        main_frame.rowconfigure(5, weight=1)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(5, 0))
        
    def setup_deps_tab(self, parent):
        # Dependencies frame
        deps_frame = ttk.Frame(parent, padding="20")
        deps_frame.pack(fill='both', expand=True)
        
        # Status section
        status_frame = ttk.LabelFrame(deps_frame, text="Dependency Status", padding="15")
        status_frame.pack(fill='x', pady=(0, 20))
        
        # NumPy status
        numpy_color = "#51cf66" if NUMPY_AVAILABLE else "#ff6b6b"  # Use theme colors
        numpy_status = "✅ Installed" if NUMPY_AVAILABLE else "❌ Missing"
        numpy_label = tk.Label(status_frame, text=f"NumPy: {numpy_status}", 
                              foreground=numpy_color, background='#0f0f0f')
        numpy_label.pack(anchor='w')
        
        # Rendering dependencies status
        if RENDERING_AVAILABLE:
            for dep in ["✅ Trimesh: Installed", "✅ PyRender: Installed", "✅ PIL/Pillow: Installed"]:
                lbl = tk.Label(status_frame, text=dep, 
                              foreground="#51cf66", background='#0f0f0f')
                lbl.pack(anchor='w')
            success_lbl = tk.Label(status_frame, text="🎉 Thumbnail generation is AVAILABLE!", 
                                 foreground="#51cf66", background='#0f0f0f',
                                 font=('TkDefaultFont', 10, 'bold'))
            success_lbl.pack(anchor='w', pady=5)
        else:
            missing_deps = ["❌ Trimesh: Missing", "❌ PyRender: Missing"]
            if not Image:
                missing_deps.append("❌ PIL/Pillow: Missing")
            for dep in missing_deps:
                lbl = tk.Label(status_frame, text=dep, 
                              foreground="#ff6b6b", background='#0f0f0f')
                lbl.pack(anchor='w')
            warning_lbl = tk.Label(status_frame, text="⚠️ Thumbnail generation is NOT available", 
                                 foreground="#ff6b6b", background='#0f0f0f',
                                 font=('TkDefaultFont', 10, 'bold'))
            warning_lbl.pack(anchor='w', pady=5)
        
        # Installation section
        install_frame = ttk.LabelFrame(deps_frame, text="Install Dependencies", padding="15")
        install_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(install_frame, 
                 text="To enable thumbnail generation, install the following packages:",
                 font=('TkDefaultFont', 9, 'bold')).pack(anchor='w', pady=(0, 10))
        
        deps_text = """Required packages:
• numpy - Mathematical operations
• trimesh - 3D mesh processing
• pyrender - 3D rendering engine
• pillow - Image processing
• pyglet<2 - OpenGL support (required for pyrender)"""
        
        ttk.Label(install_frame, text=deps_text, justify='left').pack(anchor='w', pady=(0, 10))
        
        # Installation buttons
        install_btn_frame = ttk.Frame(install_frame)
        install_btn_frame.pack(fill='x', pady=10)
        
        self.install_basic_btn = ttk.Button(install_btn_frame, text="📦 Install Basic Dependencies", 
                                          command=self.install_basic_deps,
                                          style='Accent.TButton')
        self.install_basic_btn.pack(side='left', padx=(0, 10))
        
        self.install_all_btn = ttk.Button(install_btn_frame, text="🔥 Install All Dependencies", 
                                        command=self.install_all_deps,
                                        style='Accent.TButton')
        self.install_all_btn.pack(side='left', padx=(0, 10))
        
        self.restart_deps_btn = ttk.Button(install_btn_frame, text="🔄 Restart After Install", 
                                         command=self.restart_application,
                                         style='Restart.TButton')
        self.restart_deps_btn.pack(side='left', padx=(0, 10))
        
        # Manual installation instructions
        manual_frame = ttk.LabelFrame(deps_frame, text="Manual Installation", padding="15")
        manual_frame.pack(fill='both', expand=True)
        
        manual_text = """Manual installation commands:

Basic processing (no thumbnails):
pip install numpy pillow

Full processing with thumbnails:
pip install numpy trimesh pyrender pillow "pyglet<2"

Or install one by one:
pip install numpy
pip install trimesh
pip install pyrender
pip install pillow
pip install "pyglet<2" """
        
        manual_label = tk.Text(manual_frame, height=12, wrap='word', 
                              font=('Consolas', 9), 
                              bg='#1a1a1a', fg='#ffffff',
                              insertbackground='#ffffff',
                              selectbackground='#0d7377',
                              selectforeground='#ffffff')
        manual_label.pack(fill='both', expand=True)
        manual_label.insert('1.0', manual_text)
        manual_label.config(state='disabled')
        
    def browse_input(self):
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
                self.processing_mode = "zip"
                self.selected_zip_files = files
                # Display first file's directory
                self.input_folder.set(f"ZIP files: {len(files)} selected")
                self.log_message(f"Selected {len(files)} ZIP files for processing")
        else:  # NO - Folder
            folder = filedialog.askdirectory(title="Select folder containing 3D model exports")
            if folder:
                self.processing_mode = "folder"
                self.selected_zip_files = None
                self.input_folder.set(folder)
                
    def install_basic_deps(self):
        """Install basic dependencies (numpy, pillow)"""
        self.install_dependencies(["numpy", "pillow"])
        
    def install_all_deps(self):
        """Install all dependencies including rendering"""
        self.install_dependencies(["numpy", "trimesh", "pyrender", "pillow", "pyglet<2"])
        
    def install_dependencies(self, packages):
        """Install dependencies in a separate thread"""
        def install_worker():
            try:
                self.message_queue.put("🔄 Installing dependencies...")
                self.message_queue.put(f"📦 Packages: {', '.join(packages)}")
                
                for package in packages:
                    self.message_queue.put(f"Installing {package}...")
                    result = subprocess.run([
                        sys.executable, "-m", "pip", "install", package
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        self.message_queue.put(f"✅ {package} installed successfully")
                    else:
                        self.message_queue.put(f"❌ Failed to install {package}: {result.stderr}")
                
                self.message_queue.put("🔄 Checking installation status...")
                self.message_queue.put("⚠️ Please restart the application to use new dependencies")
                self.message_queue.put("INSTALL_DONE")
                
            except Exception as e:
                self.message_queue.put(f"❌ Installation failed: {e}")
                self.message_queue.put("INSTALL_ERROR")
        
        # Disable install buttons
        self.install_basic_btn.config(state='disabled')
        self.install_all_btn.config(state='disabled')
        self.status_var.set("Installing dependencies...")
        
        # Start installation thread
        thread = Thread(target=install_worker)
        thread.daemon = True
        thread.start()
        
    def restart_application(self):
        """Restart the application to reload dependencies"""
        result = messagebox.askyesno("Restart Application", 
                                   "This will restart the application to reload any newly installed dependencies.\n\n"
                                   "Continue with restart?",
                                   icon='question')
        if result:
            self.log_message("🔄 Restarting application...")
            self.root.after(1000, self._perform_restart)
    
    def _perform_restart(self):
        """Perform the actual restart"""
        try:
            # Get the current script path
            script_path = os.path.abspath(sys.argv[0])
            
            # Close current window
            self.root.quit()
            self.root.destroy()
            
            # Start new instance
            if sys.platform == "win32":
                # Windows
                subprocess.Popen([sys.executable, script_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                # Unix-like systems
                subprocess.Popen([sys.executable, script_path])
            
            # Exit current process
            sys.exit(0)
            
        except Exception as e:
            messagebox.showerror("Restart Failed", f"Could not restart application: {e}")
        
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
                    if RENDERING_AVAILABLE:
                        self.thumbnail_btn.config(state='normal')
                    self.status_var.set("Processing complete")
                elif message == "THUMBNAIL_DONE":
                    self.progress.stop()
                    self.thumbnail_btn.config(state='normal')
                    self.process_btn.config(state='normal')
                    self.status_var.set("Thumbnail generation complete")
                elif message == "ERROR":
                    self.progress.stop()
                    self.process_btn.config(state='normal')
                    if RENDERING_AVAILABLE:
                        self.thumbnail_btn.config(state='normal')
                    self.status_var.set("Processing failed")
                elif message == "INSTALL_DONE":
                    self.install_basic_btn.config(state='normal')
                    self.install_all_btn.config(state='normal')
                    self.status_var.set("Installation complete - restart required")
                elif message == "INSTALL_ERROR":
                    self.install_basic_btn.config(state='normal')
                    self.install_all_btn.config(state='normal')
                    self.status_var.set("Installation failed")
                else:
                    self.log_message(message)
        except queue.Empty:
            pass
        self.root.after(100, self.check_queue)
        
    def start_processing(self):
        """Start file processing in a separate thread"""
        if self.processing_mode == "zip" and not self.selected_zip_files:
            messagebox.showerror("Error", "Please select ZIP files")
            return
        elif self.processing_mode == "folder" and not self.input_folder.get():
            messagebox.showerror("Error", "Please select an input folder")
            return
            
        self.process_btn.config(state='disabled')
        self.thumbnail_btn.config(state='disabled')
        self.progress.start(10)
        self.status_var.set("Processing files...")
        self.log_text.delete(1.0, tk.END)
        
        # Start processing thread
        thread = Thread(target=self.process_files)
        thread.daemon = True
        thread.start()
        
    def start_thumbnail_generation(self):
        """Start thumbnail generation for existing processed files"""
        if not RENDERING_AVAILABLE:
            messagebox.showerror("Error", "Rendering dependencies not available. Please install them first.")
            return
            
        if self.processing_mode == "zip" and not self.selected_zip_files:
            messagebox.showerror("Error", "Please select ZIP files or process files first")
            return
        elif self.processing_mode == "folder" and not self.input_folder.get():
            messagebox.showerror("Error", "Please select an input folder")
            return
            
        self.thumbnail_btn.config(state='disabled')
        self.process_btn.config(state='disabled')
        self.progress.start(10)
        self.status_var.set("Generating thumbnails...")
        
        # Start thumbnail thread
        thread = Thread(target=self.generate_thumbnails_worker)
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
            if self.processing_mode == "zip":
                # Process ZIP files
                if not self.selected_zip_files:
                    self.message_queue.put("❌ No ZIP files selected")
                    self.message_queue.put("ERROR")
                    return
                
                # Use parent directory of first ZIP file as base
                base_path = Path(self.selected_zip_files[0]).parent
                out_root = base_path / "Converted"
                
                self.message_queue.put(f"🗜️ Processing {len(self.selected_zip_files)} ZIP file(s)")
                self.message_queue.put(f"📁 Output folder: {out_root}")
                
            else:
                # Process folder
                in_root = Path(self.input_folder.get()).resolve()
                if not in_root.exists():
                    self.message_queue.put(f"❌ Input folder not found: {in_root}")
                    self.message_queue.put("ERROR")
                    return
                
                out_root = in_root / "Converted"
                self.message_queue.put(f"📁 Input folder: {in_root}")
                self.message_queue.put(f"📁 Output folder: {out_root}")
            
            out_root.mkdir(parents=True, exist_ok=True)
            
            # Handle ZIP extraction
            processing_folders = []
            
            if self.processing_mode == "zip":
                # Extract selected ZIP files
                extract_root = out_root.parent / "Extracted_ZIPs"
                extract_root.mkdir(parents=True, exist_ok=True)
                
                extracted_folders = self.extract_zip_files(self.selected_zip_files, extract_root)
                
                # Find all subfolders in extracted content
                for extracted_folder in extracted_folders:
                    subfolders = self.iter_source_folders(extracted_folder, True)
                    processing_folders.extend(subfolders)
                    
            else:
                # Handle folder input
                in_root = Path(self.input_folder.get()).resolve()
                
                if self.extract_zips.get():
                    # Check for ZIP files in the folder
                    zip_files_in_folder = self.find_zip_files_in_folder(in_root)
                    
                    if zip_files_in_folder:
                        self.message_queue.put(f"🗜️ Found {len(zip_files_in_folder)} ZIP file(s) in folder")
                        
                        # Extract ZIP files
                        extract_root = in_root / "Extracted_ZIPs"
                        extract_root.mkdir(parents=True, exist_ok=True)
                        
                        zip_paths = [str(zip_file) for zip_file in zip_files_in_folder]
                        extracted_folders = self.extract_zip_files(zip_paths, extract_root)
                        
                        # Get both regular folders and extracted folders
                        regular_folders = self.iter_source_folders(in_root, self.recursive.get())
                        for extracted_folder in extracted_folders:
                            subfolders = self.iter_source_folders(extracted_folder, True)
                            processing_folders.extend(subfolders)
                        processing_folders.extend(regular_folders)
                    else:
                        # No ZIP files found
                        processing_folders = self.iter_source_folders(in_root, self.recursive.get())
                else:
                    # Skip ZIP extraction
                    processing_folders = self.iter_source_folders(in_root, self.recursive.get())
            
            # Load overrides
            if self.processing_mode == "folder":
                merged_overrides = self.load_overrides_file(Path(self.input_folder.get()))
            else:
                merged_overrides = {}
            
            # Filter and count candidate folders
            candidate_folders = []
            for folder in processing_folders:
                if folder == out_root or out_root in folder.parents:
                    continue  # Skip the output folder itself
                    
                has_candidate = any(folder.glob("*.obj")) or any(folder.glob("*.mtl")) or any(
                    p.suffix.lower() in self.IMG_EXTS for p in folder.iterdir() if p.is_file()
                )
                if has_candidate:
                    candidate_folders.append(folder)
                    
            total_candidates = len(candidate_folders)
            self.message_queue.put(f"🔍 Found {total_candidates} folders with 3D assets to process")
            
            # Process each folder
            count = 0
            for folder in candidate_folders:
                count += 1
                self.message_queue.put(f"\n📦 Processing {count}/{total_candidates}: {folder.name}")
                self.process_model_folder(folder, out_root, merged_overrides, skip_thumbnails=True)
                
            self.message_queue.put(f"\n✅ File processing complete! Processed {count} folder(s).")
            self.message_queue.put(f"📂 Files saved to: {out_root}")
            
            if RENDERING_AVAILABLE:
                self.message_queue.put("💡 You can now generate thumbnails using the 'Generate Thumbnails' button")
            else:
                self.message_queue.put("💡 Install rendering dependencies to generate thumbnails")
            
            self.message_queue.put("DONE")
            
        except Exception as e:
            self.message_queue.put(f"❌ Error during processing: {str(e)}")
            self.message_queue.put("ERROR")

    def generate_thumbnails_worker(self):
        """Generate thumbnails for processed OBJ files"""
        try:
            if self.processing_mode == "zip":
                base_path = Path(self.selected_zip_files[0]).parent
                converted_root = base_path / "Converted"
            else:
                in_root = Path(self.input_folder.get()).resolve()
                converted_root = in_root / "Converted"
            
            if not converted_root.exists():
                self.message_queue.put("❌ No converted files found. Please process files first.")
                self.message_queue.put("ERROR")
                return
            
            # Find all OBJ files in converted folders
            obj_files = list(converted_root.rglob("*.obj"))
            
            if not obj_files:
                self.message_queue.put("❌ No OBJ files found in converted folders")
                self.message_queue.put("ERROR")
                return
            
            self.message_queue.put(f"🎨 Generating thumbnails for {len(obj_files)} OBJ files")
            
            count = 0
            for obj_file in obj_files:
                count += 1
                self.message_queue.put(f"📸 Creating thumbnail {count}/{len(obj_files)}: {obj_file.stem}")
                
                # Create thumbnail filename
                thumb_path = obj_file.parent / f"{obj_file.stem}!.png"
                self.render_thumbnail_black_bg(obj_file, thumb_path)
            
            self.message_queue.put(f"\n🎉 Thumbnail generation complete! Created {count} thumbnails.")
            self.message_queue.put("THUMBNAIL_DONE")
            
        except Exception as e:
            self.message_queue.put(f"❌ Error during thumbnail generation: {str(e)}")
            self.message_queue.put("ERROR")

    # All the helper methods from the original script (with modifications)
    def camel_no_underscores(self, s: str) -> str:
        """Remove underscores/dashes and convert to compact CamelCase-ish."""
        parts = [p for p in self.SEP_SPLIT.split(s) if p]
        if not parts:
            return s.replace("_", "").replace("-", "")
        return "".join(p[:1].upper() + p[1:] for p in parts)

    def clean_base_from_stem(self, stem: str) -> str:
        """Derive a clean base from a filename stem - Enhanced number removal."""
        # Remove trailing numeric suffixes (like _1022223231)
        stem = self.NUM_SUFFIX.sub("", stem)
        
        # Split into parts and clean
        parts = [p for p in self.SEP_SPLIT.split(stem) if p]
        
        # Remove trailing junk tokens
        while parts and parts[-1].lower() in self.DROP_TRAILING_TOKENS:
            parts.pop()
            
        # Remove any remaining pure numeric parts at the end
        while parts and parts[-1].isdigit():
            parts.pop()
            
        # Remove common suffixes that might remain
        while parts and parts[-1].lower() in {"export", "meshy", "model", "3d"}:
            parts.pop()
            
        if not parts:
            parts = [stem.split('_')[0] if '_' in stem else stem]  # Use first part if available
            
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

    def render_thumbnail_black_bg(self, obj_path: Path, thumb_path: Path):
        """Render OBJ to a PNG with black background using pyrender OffscreenRenderer."""
        if not RENDERING_AVAILABLE or trimesh is None or pyrender is None or Image is None or np is None:
            self.message_queue.put(f"  ⚠️ Thumbnail generation skipped - dependencies not available")
            return
            
        try:
            # Load mesh with better processing
            mesh = trimesh.load_mesh(str(obj_path), process=True)  # Enable processing for better results
            if isinstance(mesh, trimesh.Scene):
                mesh = trimesh.util.concatenate(mesh.dump())

            # Ensure mesh is valid
            if mesh.is_empty:
                self.message_queue.put(f"  ⚠️ Empty mesh: {obj_path.name}")
                return

            # Create scene with black background
            scene = pyrender.Scene(
                bg_color=self.BACKGROUND_COLOR,  # (0,0,0,255) for black background
                ambient_light=[0.4, 0.4, 0.4]   # Slightly brighter ambient
            )
            
            # Add mesh with material for better rendering
            mesh_node = pyrender.Mesh.from_trimesh(mesh, smooth=True)
            scene.add(mesh_node)

            # Enhanced camera placement
            bounds = mesh.bounds
            center = bounds.mean(axis=0)
            extents = mesh.extents
            radius = np.linalg.norm(extents) * 0.5
            distance = max(0.1, radius * self.CAMERA_DISTANCE_MULT)

            # Create camera with better field of view
            cam = pyrender.PerspectiveCamera(yfov=np.pi / 3.5)  # Slightly wider FOV
            cam_pose = np.eye(4)
            
            # Position camera at slight angle for better 3D view
            angle_offset = np.pi / 6  # 30 degrees
            cam_pos = center + np.array([
                distance * np.sin(angle_offset), 
                distance * 0.3,  # Slightly above
                distance * np.cos(angle_offset)
            ])
            cam_pose[:3, 3] = cam_pos
            
            # Look at center
            forward = (center - cam_pos)
            forward /= (np.linalg.norm(forward) + 1e-7)
            up = np.array([0.0, 1.0, 0.0])
            right = np.cross(up, forward)
            right /= (np.linalg.norm(right) + 1e-7)
            up = np.cross(forward, right)
            up /= (np.linalg.norm(up) + 1e-7)
            cam_pose[:3, :3] = np.vstack([right, up, forward]).T
            scene.add(cam, pose=cam_pose)

            # Enhanced lighting setup
            key_light = pyrender.DirectionalLight(color=np.ones(3), intensity=self.LIGHT_INTENSITY * 1.2)
            fill_light = pyrender.DirectionalLight(color=np.ones(3), intensity=self.LIGHT_INTENSITY * 0.4)
            rim_light = pyrender.DirectionalLight(color=np.ones(3), intensity=self.LIGHT_INTENSITY * 0.6)
            
            # Key light from camera position
            scene.add(key_light, pose=cam_pose)
            
            # Fill light from opposite side
            fill_pose = np.array(cam_pose)
            fill_pose[:3, 3] = center + np.array([-distance, distance * 0.5, distance])
            scene.add(fill_light, pose=fill_pose)
            
            # Rim light for definition
            rim_pose = np.array(cam_pose)
            rim_pose[:3, 3] = center + np.array([distance, -distance * 0.2, -distance])
            scene.add(rim_light, pose=rim_pose)

            # Render with higher quality
            r = pyrender.OffscreenRenderer(*self.RENDER_SIZE)
            color, depth = r.render(scene)
            r.delete()

            # Convert to RGB for black background
            img = Image.fromarray(color, 'RGB')
            
            # Save with PNG compression
            img.save(thumb_path, 'PNG', optimize=True)
            
            self.message_queue.put(f"  📸 Black background thumbnail: {thumb_path.name}")
            
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

    def process_model_folder(self, src_folder: Path, out_parent: Path, overrides: Dict[str, str], skip_thumbnails: bool = False):
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

        # Skip thumbnail generation during initial processing
        if not skip_thumbnails and out_obj and out_obj.exists() and RENDERING_AVAILABLE:
            thumb_path = out_folder / f"{base}!.png"
            self.render_thumbnail_black_bg(out_obj, thumb_path)

    def iter_source_folders(self, root: Path, recursive: bool) -> List[Path]:
        """Iterate over source folders to process."""
        if not recursive:
            return [p for p in root.iterdir() if p.is_dir()]
        return [p for p in root.rglob("*") if p.is_dir()]


def main():
    root = tk.Tk()
    app = Enhanced3DProcessorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()