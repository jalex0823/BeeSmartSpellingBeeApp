#!/usr/bin/env python3
"""Visible GUI test with a clear window."""

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import time

def test_visible_gui():
    print("Creating a VISIBLE test window...")
    
    # Create a visible main window first
    root = tk.Tk()
    root.title("3D File Processor - Folder Selection")
    root.geometry("400x200")
    root.configure(bg='lightblue')
    
    # Center the window
    root.eval('tk::PlaceWindow . center')
    
    # Make it stay on top
    root.attributes('-topmost', True)
    root.lift()
    root.focus_force()
    
    # Add a label
    label = tk.Label(root, text="Click the button to select your source folder", 
                     bg='lightblue', font=('Arial', 12))
    label.pack(pady=20)
    
    selected_folder = None
    
    def select_folder():
        nonlocal selected_folder
        folder_path = filedialog.askdirectory(
            title="Select Source Folder (containing 3D models)",
            initialdir=str(Path.home() / "Downloads"),
            parent=root
        )
        if folder_path:
            selected_folder = folder_path
            messagebox.showinfo("Success", f"Selected:\n{folder_path}")
            root.quit()
        else:
            messagebox.showwarning("Cancelled", "No folder selected")
    
    def close_app():
        root.quit()
    
    # Add buttons
    btn_select = tk.Button(root, text="📁 Select Folder", command=select_folder,
                          font=('Arial', 14), bg='lightgreen', width=15)
    btn_select.pack(pady=10)
    
    btn_close = tk.Button(root, text="❌ Cancel", command=close_app,
                         font=('Arial', 12), bg='lightcoral', width=15)
    btn_close.pack(pady=5)
    
    print("GUI window should be visible now!")
    print("Look for a light blue window titled '3D File Processor'")
    
    # Run the GUI
    root.mainloop()
    root.destroy()
    
    if selected_folder:
        print(f"✅ You selected: {selected_folder}")
        return selected_folder
    else:
        print("❌ No folder selected")
        return None

if __name__ == "__main__":
    result = test_visible_gui()
    print(f"Final result: {result}")
    input("Press Enter to exit...")