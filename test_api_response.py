"""Test what the /api/avatars endpoint is actually serving"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from avatar_catalog import AVATAR_CATALOG

# Find Builder Bee in catalog
builder = next((a for a in AVATAR_CATALOG if a.get('id') == 'builder-bee'), None)

if builder:
    print("✅ Found Builder Bee in catalog:")
    print(f"  - ID: {builder.get('id')}")
    print(f"  - Name: {builder.get('name')}")
    print(f"  - obj_file: {builder.get('obj_file')}")
    print(f"  - Expected URL: /static/assets/avatars/glb_files/{builder.get('obj_file')}")
    
    # Check if it's .glb or .obj
    obj_file = builder.get('obj_file', '')
    if obj_file.endswith('.glb'):
        print("  ✅ Correct! Using GLB format")
    elif obj_file.endswith('.obj'):
        print("  ❌ ERROR! Still using OBJ format")
    else:
        print("  ⚠️ Unknown format")
else:
    print("❌ Builder Bee not found in catalog")

# Count GLB vs OBJ files in catalog
glb_count = sum(1 for a in AVATAR_CATALOG if str(a.get('obj_file', '')).endswith('.glb'))
obj_count = sum(1 for a in AVATAR_CATALOG if str(a.get('obj_file', '')).endswith('.obj'))
total = len(AVATAR_CATALOG)

print(f"\n📊 Avatar Catalog Summary:")
print(f"  - Total avatars: {total}")
print(f"  - GLB format: {glb_count}")
print(f"  - OBJ format: {obj_count}")
print(f"  - Other/None: {total - glb_count - obj_count}")
