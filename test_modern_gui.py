"""
Test script for the modern Enhanced 3D GUI
"""

import tkinter as tk
from pathlib import Path
import sys

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def test_gui():
    """Test the modern GUI"""
    try:
        print("🧪 Testing Modern Enhanced 3D GUI...")
        print("=" * 50)
        
        # Test basic tkinter functionality
        print("✓ Testing tkinter...")
        root = tk.Tk()
        root.withdraw()  # Hide test window
        root.destroy()
        
        # Try to import our GUI
        print("✓ Testing GUI import...")
        from enhanced_3d_gui_modern import ModernEnhanced3DGUI
        
        print("✓ Testing GUI initialization...")
        app = ModernEnhanced3DGUI()
        
        print("✅ All tests passed!")
        print("\nStarting the modern GUI...")
        print("=" * 50)
        
        # Run the actual GUI
        app.run()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nFalling back to enhanced demo...")
        try:
            import demo_enhanced_3d_app
        except ImportError:
            print("❌ Enhanced demo also failed. Running original...")
            try:
                exec(open("3DFile_FileFolderGenerator.py").read())
            except Exception as e2:
                print(f"❌ Original also failed: {e2}")
                
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        print("\nTrying fallback options...")
        
        # Try the demo
        try:
            import demo_enhanced_3d_app
        except:
            print("Demo failed, check your installation")

if __name__ == "__main__":
    test_gui()