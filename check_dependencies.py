"""
Test script to check rendering dependencies
"""

print("🔍 Checking rendering dependencies...")

try:
    import numpy as np
    print("✅ NumPy: Available")
    NUMPY_AVAILABLE = True
except ImportError:
    print("❌ NumPy: Missing")
    NUMPY_AVAILABLE = False

try:
    import trimesh
    print("✅ Trimesh: Available")
except ImportError:
    print("❌ Trimesh: Missing")

try:
    import pyrender
    print("✅ PyRender: Available")
except ImportError:
    print("❌ PyRender: Missing")

try:
    from PIL import Image
    print("✅ PIL/Pillow: Available")
except ImportError:
    print("❌ PIL/Pillow: Missing")

print("\n📋 Summary:")
if NUMPY_AVAILABLE:
    try:
        import trimesh
        import pyrender
        from PIL import Image
        print("🎉 All rendering dependencies are available!")
        print("   Thumbnail generation should work!")
    except ImportError:
        print("⚠️ Some rendering dependencies are missing")
        print("   Install with: pip install trimesh pyrender pillow")
else:
    print("⚠️ NumPy is required for rendering")
    print("   Install with: pip install numpy trimesh pyrender pillow")