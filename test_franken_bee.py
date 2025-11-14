#!/usr/bin/env python3
import os

print("=== FRANKEN BEE CONNECTION TEST ===")

# GLB file
glb_path = "static/assets/avatars/glb_files/FrankenBee.glb"
glb_exists = os.path.exists(glb_path)
print(f"GLB file: {glb_exists} - {glb_path}")
if glb_exists:
    size = os.path.getsize(glb_path)
    print(f"  Size: {size:,} bytes")

# Thumbnail file (based on our fix)
thumb_path = "static/assets/avatars/glb_files/AvatarThumbnails/FrankenBee!.png"
thumb_exists = os.path.exists(thumb_path)
print(f"Thumbnail: {thumb_exists} - {thumb_path}")
if thumb_exists:
    size = os.path.getsize(thumb_path)
    print(f"  Size: {size:,} bytes")

print("\n=== CONNECTION STATUS ===")
if glb_exists and thumb_exists:
    print("✅ BOTH FILES EXIST - Connection should work!")
    
    # Test the catalog mapping
    print("\n=== TESTING CATALOG MAPPING ===")
    from avatar_catalog import AVATAR_CATALOG
    
    franken_bee = None
    for avatar in AVATAR_CATALOG:
        if avatar['id'] == 'franken-bee':
            franken_bee = avatar
            break
    
    if franken_bee:
        print(f"Catalog entry found:")
        print(f"  ID: {franken_bee['id']}")
        print(f"  Name: {franken_bee['name']}")
        print(f"  GLB file: {franken_bee['obj_file']}")
        print(f"  Folder: {franken_bee['folder']}")
        
        # Check if thumbnail mapping works
        folder = franken_bee['id']
        if folder == 'franken-bee':
            expected_thumb = 'FrankenBee!.png'  # Our fix
            print(f"Expected thumbnail: {expected_thumb}")
            
            expected_path = f"static/assets/avatars/glb_files/AvatarThumbnails/{expected_thumb}"
            mapping_works = os.path.exists(expected_path)
            print(f"Mapping works: {mapping_works}")
            
            if mapping_works:
                print("✅ FRANKEN BEE FULLY CONNECTED!")
            else:
                print("❌ Mapping broken")
    else:
        print("❌ Franken Bee not found in catalog")
        
else:
    print("❌ MISSING FILES")
    if not glb_exists:
        print(f"  Missing GLB: {glb_path}")
    if not thumb_exists:
        print(f"  Missing thumbnail: {thumb_path}")

print("\n=== COMPARISON TEST ===")
# Test a working avatar for comparison
doc_glb = "static/assets/avatars/glb_files/DocBee.glb"
doc_thumb = "static/assets/avatars/glb_files/AvatarThumbnails/DocBee!.png"
print(f"Doc Bee GLB exists: {os.path.exists(doc_glb)}")
print(f"Doc Bee thumbnail exists: {os.path.exists(doc_thumb)}")