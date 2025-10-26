#!/usr/bin/env python3
"""
Simple test to understand the current avatar system status without requiring a running server.
"""

import os
import sys
from pathlib import Path

def check_project_structure():
    """Check the basic project structure for avatar system"""
    
    print("🐝 BeeSmart Avatar System Status Check")
    print("=" * 50)
    
    # Check main files
    main_files = [
        "AjaSpellBApp.py",
        "models.py", 
        "static/assets/avatars"
    ]
    
    print("📁 Project Structure:")
    for item in main_files:
        path = Path(item)
        if path.exists():
            if path.is_dir():
                count = len(list(path.iterdir()))
                print(f"   ✅ {item}/ ({count} items)")
            else:
                print(f"   ✅ {item}")
        else:
            print(f"   ❌ {item} - NOT FOUND")
    
    # Check avatar assets
    assets_dir = Path("static/assets/avatars")
    if assets_dir.exists():
        print(f"\n🎨 Avatar Assets:")
        avatar_folders = [d for d in assets_dir.iterdir() if d.is_dir()]
        print(f"   Found {len(avatar_folders)} avatar folders")
        
        # Check a few examples
        for folder in sorted(avatar_folders)[:5]:
            png_files = list(folder.glob("*.png"))
            obj_files = list(folder.glob("*.obj"))
            mtl_files = list(folder.glob("*.mtl"))
            
            total_files = len(png_files) + len(obj_files) + len(mtl_files)
            print(f"   📦 {folder.name}: {total_files} files ({len(png_files)} PNG, {len(obj_files)} OBJ, {len(mtl_files)} MTL)")
            
            # Check for thumbnail files specifically
            thumbnail_candidates = [f for f in png_files if '!' in f.name or 'thumbnail' in f.name.lower()]
            if thumbnail_candidates:
                for thumb in thumbnail_candidates:
                    has_spaces = ' ' in thumb.name
                    status = " (HAS SPACES)" if has_spaces else " (NO SPACES)"
                    print(f"      🖼️ Thumbnail: {thumb.name}{status}")
    
    # Check key Python files for avatar system
    print(f"\n🔍 Avatar System Components:")
    
    # Check if we can import key components
    try:
        sys.path.insert(0, '.')
        
        # Try to see if the Avatar model exists
        if Path("models.py").exists():
            print("   ✅ models.py exists")
            # Try to check for Avatar class (basic grep)
            with open("models.py", "r", encoding="utf-8") as f:
                content = f.read()
                if "class Avatar" in content:
                    print("   ✅ Avatar model class found")
                else:
                    print("   ❌ Avatar model class not found")
        
        # Check main app file
        if Path("AjaSpellBApp.py").exists():
            print("   ✅ AjaSpellBApp.py exists")
            with open("AjaSpellBApp.py", "r", encoding="utf-8") as f:
                content = f.read()
                if "/api/avatars" in content:
                    print("   ✅ Avatar API endpoint found")
                else:
                    print("   ❌ Avatar API endpoint not found")
                    
                if "thumbnail_file" in content:
                    print("   ✅ Thumbnail file handling found")
                else:
                    print("   ❌ Thumbnail file handling not found")
    
    except Exception as e:
        print(f"   ⚠️ Error checking components: {e}")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   This appears to be a Flask app with avatar system")
    print(f"   The avatar assets directory exists with {len(avatar_folders) if 'avatar_folders' in locals() else 0} avatars")
    print(f"   Database will be created when app starts for the first time")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Start the Flask app: python AjaSpellBApp.py")
    print(f"   2. Visit the avatar picker page to test the grid")
    print(f"   3. Check if new avatars appear correctly")
    print(f"   4. Verify avatar selection replaces the default mascot")

if __name__ == "__main__":
    check_project_structure()