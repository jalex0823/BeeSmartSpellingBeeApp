"""
Demo script for the enhanced 3D File Generator with Meshy API integration
"""

import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from meshy_api_client import MeshyAPIClient, MeshyTask
    from importlib import import_module
    
    # Import the main application
    app_module = import_module('3DFile_FileFolderGenerator')
    Dark3DProcessorGUI = app_module.Dark3DProcessorGUI
    
    print("🎉 Enhanced 3D File Generator with Meshy API Integration")
    print("=" * 60)
    print()
    print("NEW FEATURES:")
    print("✅ Meshy API integration for advanced 3D processing")
    print("✅ Enhanced PNG snapshot generation with '!' naming")
    print("✅ Railway app compatibility features")
    print("✅ Multiple texture style options")
    print("✅ Automatic file organization for deployment")
    print()
    print("MESHY API FEATURES:")
    print("🎨 Texture generation with customizable styles")
    print("🔧 Mesh refinement and optimization")
    print("📸 High-quality thumbnail generation")
    print("🚂 Railway deployment-ready output")
    print()
    print("HOW TO USE:")
    print("1. Get your Meshy API key from https://meshy.ai")
    print("2. Select ZIP files containing OBJ models")
    print("3. Choose processing options:")
    print("   - Standard conversion (existing functionality)")
    print("   - Meshy API processing (new AI-enhanced features)")
    print("4. Generated files will include:")
    print("   - Original OBJ files (cleaned and organized)")
    print("   - Enhanced textures from Meshy API")
    print("   - PNG snapshots with '!' in filename")
    print("   - Railway-ready asset structure")
    print()
    print("RAILWAY APP INTEGRATION:")
    print("📁 Files are automatically organized for Railway deployment")
    print("🖼️ Snapshots use '!' naming to distinguish from materials")
    print("📦 Supporting files are properly referenced")
    print("🔗 GLB/OBJ files are optimized for web viewing")
    print()
    print("Starting the enhanced GUI...")
    print("=" * 60)
    
    # Start the GUI
    app = Dark3DProcessorGUI()
    app.run()
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print()
    print("SETUP INSTRUCTIONS:")
    print("1. Make sure you have all required dependencies:")
    print("   pip install trimesh pyrender pillow numpy matplotlib requests")
    print()
    print("2. Ensure meshy_api_client.py is in the same directory")
    print()
    print("3. Your Meshy API key should be configured in the settings")
    print()
    print("If you continue to have issues, try running the original GUI:")
    print("python 3DFile_FileFolderGenerator.py")

except Exception as e:
    print(f"❌ Error starting application: {e}")
    print()
    print("Falling back to basic functionality...")
    
    try:
        # Try to run without Meshy integration
        import importlib
        app_module = importlib.import_module('3DFile_FileFolderGenerator')
        main_func = getattr(app_module, 'main', None)
        if main_func:
            main_func()
        else:
            print("Please run the application directly:")
            print("python 3DFile_FileFolderGenerator.py")
    except Exception as fallback_error:
        print(f"❌ Fallback failed: {fallback_error}")
        print("Please check your Python environment and try again.")