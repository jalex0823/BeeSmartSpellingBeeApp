#!/usr/bin/env python3
"""
Scan the 3D Avatar Files directory and generate the correct avatar catalog mapping
"""
import os
import re

# Path to the source avatar files
SOURCE_PATH = "C:/Users/jeff/Dropbox/BeeSmartSpellingBeeApp/Avatars/3D Avatar Files"
TARGET_PATH = "static/assets/avatars"

print("=" * 80)
print("🔍 SCANNING AVATAR FOLDERS")
print("=" * 80)

# Scan the source directory
if os.path.exists(SOURCE_PATH):
    folders = [f for f in os.listdir(SOURCE_PATH) if os.path.isdir(os.path.join(SOURCE_PATH, f))]
    folders.sort()
    
    print(f"\n✅ Found {len(folders)} avatar folders in source:\n")
    
    mapping = {}
    
    for folder in folders:
        folder_path = os.path.join(SOURCE_PATH, folder)
        
        # Convert folder name to avatar_id (lowercase, hyphens)
        # e.g., "ProfessorBee" -> "professor-bee"
        avatar_id = re.sub(r'([a-z])([A-Z])', r'\1-\2', folder).lower()
        
        # Check what files are in the folder
        files = os.listdir(folder_path)
        png_files = [f for f in files if f.endswith('.png')]
        obj_files = [f for f in files if f.endswith('.obj')]
        mtl_files = [f for f in files if f.endswith('.mtl')]
        
        # Look for the main texture file (should be folder_name.png)
        texture_file = f"{folder}.png" if f"{folder}.png" in png_files else None
        obj_file = f"{folder}.obj" if f"{folder}.obj" in obj_files else None
        mtl_file = f"{folder}.mtl" if f"{folder}.mtl" in mtl_files else None
        
        print(f"📁 {folder}")
        print(f"   ID: {avatar_id}")
        print(f"   OBJ: {obj_file or '❌ NOT FOUND'}")
        print(f"   MTL: {mtl_file or '❌ NOT FOUND'}")
        print(f"   Texture: {texture_file or '❌ NOT FOUND'}")
        print(f"   PNG files: {len(png_files)}")
        print()
        
        mapping[avatar_id] = {
            'folder': folder,
            'obj': obj_file,
            'mtl': mtl_file,
            'texture': texture_file,
            'png_count': len(png_files)
        }
    
    print("\n" + "=" * 80)
    print("📋 AVATAR ID MAPPING")
    print("=" * 80)
    
    for avatar_id, info in sorted(mapping.items()):
        status = "✅" if info['obj'] and info['mtl'] and info['texture'] else "⚠️"
        print(f"{status} {avatar_id:20} <- {info['folder']}")
    
    print("\n" + "=" * 80)
    print("🎯 SUGGESTED CATALOG ENTRIES")
    print("=" * 80)
    print("\nCopy this to avatar_catalog.py:\n")
    
    for avatar_id, info in sorted(mapping.items()):
        if info['obj'] and info['mtl']:
            # Generate nice name from folder (add spaces before capitals)
            nice_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', info['folder'])
            
            print(f'''    {{
        "id": "{avatar_id}",
        "name": "{nice_name}",
        "folder": "{info['folder']}",  # Source folder name
        "obj_file": "{info['obj']}",
        "mtl_file": "{info['mtl']}",
        "texture_file": "{info['texture']}",
        "description": "TODO: Add description",
        "variants": ["default"],
        "category": "classic"
    }},''')
    
else:
    print(f"\n❌ Source path not found: {SOURCE_PATH}")

print("\n" + "=" * 80)
