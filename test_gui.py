#!/usr/bin/env python3
"""Simple test to verify GUI folder selection works."""

import tkinter as tk
from tkinter import filedialog
from pathlib import Path

def test_gui():
    print("Testing GUI folder selection...")
    
    try:
        # Create tkinter root
        root = tk.Tk()
        root.withdraw()  # Hide main window
        root.attributes('-topmost', True)  # Stay on top
        root.lift()
        root.focus_force()
        
        print("Opening folder dialog... (check your taskbar if not visible)")
        
        # Open folder dialog
        folder_path = filedialog.askdirectory(
            title="Test - Select any folder",
            initialdir=str(Path.home()),
            parent=root
        )
        
        root.destroy()
        
        if folder_path:
            print(f"✅ SUCCESS! Selected: {folder_path}")
            return True
        else:
            print("❌ No folder selected (cancelled)")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    test_gui()
    input("Press Enter to exit...")