"""
Copy Avatar Files from Source to Deployment Directory
Copies properly named files from source (Avatars/3D Avatar Files/) to static/assets/avatars/
"""

import os
import shutil
from avatar_catalog import AVATAR_CATALOG

# Paths
SOURCE_BASE = "C:/Users/jeff/Dropbox/BeeSmartSpellingBeeApp/Avatars/3D Avatar Files"
TARGET_BASE = "static/assets/avatars"

def copy_avatar_files():
    """Copy avatar files from source to deployment directory"""
    
    print("=" * 80)
    print("📦 COPYING AVATAR FILES")
    print("=" * 80)
    print()
    
    copied_count = 0
    failed_count = 0
    
    for avatar in AVATAR_CATALOG:
        avatar_id = avatar['id']
        folder_name = avatar.get('folder', avatar_id)
        obj_file = avatar.get('obj_file', 'model.obj')
        mtl_file = avatar.get('mtl_file', 'model.mtl')
        texture_file = avatar.get('texture_file', 'texture.png')
        
        # Create target directory
        target_dir = os.path.join(TARGET_BASE, avatar_id)
        os.makedirs(target_dir, exist_ok=True)
        
        print(f"📁 {avatar['name']} ({avatar_id})")
        print(f"   Source: {folder_name}/")
        print(f"   Target: {target_dir}/")
        
        # Define file mappings (source -> target)
        files_to_copy = [
            (obj_file, obj_file),
            (mtl_file, mtl_file),
            (texture_file, texture_file),
        ]
        
        # Copy each file
        for src_file, dst_file in files_to_copy:
            src_path = os.path.join(SOURCE_BASE, folder_name, src_file)
            dst_path = os.path.join(target_dir, dst_file)
            
            if os.path.exists(src_path):
                try:
                    shutil.copy2(src_path, dst_path)
                    size_mb = os.path.getsize(dst_path) / (1024 * 1024)
                    print(f"   ✅ {src_file} ({size_mb:.2f} MB)")
                    copied_count += 1
                except Exception as e:
                    print(f"   ❌ {src_file} - ERROR: {e}")
                    failed_count += 1
            else:
                print(f"   ⚠️ {src_file} - NOT FOUND in source")
                failed_count += 1
        
        # Check for thumbnails/previews
        thumbnail_files = []
        for file in os.listdir(os.path.join(SOURCE_BASE, folder_name)):
            if file.lower().endswith('.png') and file != texture_file:
                thumbnail_files.append(file)
        
        # Copy first PNG as thumbnail if available
        if thumbnail_files:
            src_thumb = os.path.join(SOURCE_BASE, folder_name, thumbnail_files[0])
            dst_thumb = os.path.join(target_dir, 'thumbnail.png')
            try:
                shutil.copy2(src_thumb, dst_thumb)
                print(f"   ✅ thumbnail.png (from {thumbnail_files[0]})")
                copied_count += 1
            except Exception as e:
                print(f"   ⚠️ thumbnail copy failed: {e}")
        
        # Create preview.png as copy of thumbnail if not exists
        preview_path = os.path.join(target_dir, 'preview.png')
        if os.path.exists(dst_thumb) and not os.path.exists(preview_path):
            shutil.copy2(dst_thumb, preview_path)
            print(f"   ✅ preview.png (copy of thumbnail)")
            copied_count += 1
        
        print()
    
    print("=" * 80)
    print(f"✅ COPY COMPLETE: {copied_count} files copied")
    if failed_count > 0:
        print(f"⚠️ WARNING: {failed_count} files failed or not found")
    print("=" * 80)

if __name__ == "__main__":
    copy_avatar_files()
