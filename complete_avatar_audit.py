#!/usr/bin/env python3
"""
Complete Avatar Audit - Match picker to catalog and identify ALL gaps
"""

from avatar_catalog import AVATAR_CATALOG
import os
import re
from pathlib import Path
import json

print("=" * 80)
print("🐝 COMPLETE AVATAR AUDIT - PICKER vs CATALOG")
print("=" * 80)
print()

# Helper function matching the API logic
def _slug_from_base(base: str):
    name_with_spaces = re.sub(r'(?<!^)([A-Z])', r' \1', base).strip()
    return re.sub(r'[^a-z0-9]+', '-', name_with_spaces.lower()).strip('-'), name_with_spaces

# Get all avatars from catalog
catalog_by_id = {av['id']: av for av in AVATAR_CATALOG}
print(f"📋 Catalog has {len(AVATAR_CATALOG)} entries")

# Count OBJ vs GLB in catalog
obj_in_catalog = [av for av in AVATAR_CATALOG if av.get('folder') != 'glb_files']
glb_in_catalog = [av for av in AVATAR_CATALOG if av.get('folder') == 'glb_files']
print(f"   - OBJ avatars: {len(obj_in_catalog)}")
print(f"   - GLB avatars: {len(glb_in_catalog)}")
print()

# Check ALL GLB files in directory
static_root = Path('static/assets/avatars')
glb_dir = static_root / 'glb_files'

all_glb_files = []
if glb_dir.exists():
    for fname in sorted(os.listdir(glb_dir)):
        if fname.lower().endswith('.glb'):
            base = fname[:-4]
            slug, display_name = _slug_from_base(base)
            all_glb_files.append({
                'filename': fname,
                'base': base,
                'slug': slug,
                'display_name': display_name,
                'in_catalog': slug in catalog_by_id,
                'catalog_name': catalog_by_id.get(slug, {}).get('name', None)
            })

print(f"📁 Found {len(all_glb_files)} GLB files in glb_files directory")
print()

# Now check OBJ folders
obj_folders = []
avatar_base = static_root
if avatar_base.exists():
    for item in sorted(os.listdir(avatar_base)):
        item_path = avatar_base / item
        if item_path.is_dir() and item != 'glb_files':
            # Check if this folder has OBJ files
            has_obj = any(f.endswith('.obj') for f in os.listdir(item_path) if os.path.isfile(item_path / f))
            if has_obj:
                obj_folders.append({
                    'folder': item,
                    'slug': item,
                    'in_catalog': item in catalog_by_id,
                    'catalog_name': catalog_by_id.get(item, {}).get('name', None)
                })

print(f"📁 Found {len(obj_folders)} OBJ folders")
print()

print("=" * 80)
print("DETAILED BREAKDOWN")
print("=" * 80)
print()

print("GLB FILES:")
print("-" * 80)
print(f"{'#':<4} {'Filename':<25} {'Slug':<20} {'Picker Shows':<25} {'In Catalog?':<12}")
print("-" * 80)

glb_missing = []
for i, glb in enumerate(all_glb_files, 1):
    status = "✅ YES" if glb['in_catalog'] else "❌ NO"
    print(f"{i:<4} {glb['filename']:<25} {glb['slug']:<20} {glb['display_name']:<25} {status:<12}")
    if not glb['in_catalog']:
        glb_missing.append(glb)

print()
print("OBJ FOLDERS:")
print("-" * 80)
print(f"{'#':<4} {'Folder':<25} {'Slug':<20} {'In Catalog?':<12}")
print("-" * 80)

obj_missing = []
for i, obj in enumerate(obj_folders, 1):
    status = "✅ YES" if obj['in_catalog'] else "❌ NO"
    print(f"{i:<4} {obj['folder']:<25} {obj['slug']:<20} {status:<12}")
    if not obj['in_catalog']:
        obj_missing.append(obj)

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total avatars in picker: {len(all_glb_files) + len(obj_folders)}")
print(f"Total in catalog: {len(AVATAR_CATALOG)}")
print(f"GLB files: {len(all_glb_files)}")
print(f"  - In catalog: {len(all_glb_files) - len(glb_missing)}")
print(f"  - Missing: {len(glb_missing)}")
print(f"OBJ folders: {len(obj_folders)}")
print(f"  - In catalog: {len(obj_folders) - len(obj_missing)}")
print(f"  - Missing: {len(obj_missing)}")
print()

if glb_missing:
    print("⚠️ GLB FILES NOT IN CATALOG:")
    for glb in glb_missing:
        print(f"  • {glb['filename']} → {glb['slug']} → '{glb['display_name']}'")
        print(f"    Should be: '{glb['display_name']} Avatar'")
    print()

if obj_missing:
    print("⚠️ OBJ FOLDERS NOT IN CATALOG:")
    for obj in obj_missing:
        print(f"  • {obj['folder']}")
    print()

# Generate entries to add
print("=" * 80)
print("🔧 ENTRIES TO ADD TO CATALOG")
print("=" * 80)
print()

entries_to_add = []
for glb in glb_missing:
    entry = {
        'id': glb['slug'],
        'name': f"{glb['display_name']} Avatar",
        'folder': 'glb_files',
        'obj_file': glb['filename'],
        'mtl_file': '',
        'texture_file': '',
        'description': f"{glb['display_name']} is ready to spell! 🐝",
        'variants': ['default'],
        'category': 'classic',
        'tier': 'default_free',  # You can change this
        'is_default_free': True,
        'is_purchasable': False,
        'unlock_points': 0,
        'price': 0.00
    }
    entries_to_add.append(entry)

if entries_to_add:
    print("Add these entries to avatar_catalog.py:")
    print()
    print(json.dumps(entries_to_add, indent=4))
    print()

# Save to file
with open('missing_avatars_to_add.json', 'w') as f:
    json.dump({
        'glb_missing': glb_missing,
        'obj_missing': obj_missing,
        'suggested_entries': entries_to_add,
        'stats': {
            'total_in_picker': len(all_glb_files) + len(obj_folders),
            'total_in_catalog': len(AVATAR_CATALOG),
            'glb_count': len(all_glb_files),
            'obj_count': len(obj_folders),
            'missing_count': len(glb_missing) + len(obj_missing)
        }
    }, f, indent=2)

print(f"📝 Full report saved to: missing_avatars_to_add.json")
