#!/usr/bin/env python3
"""
Compare Avatar Names: Catalog vs. Picker Display
Identifies any mismatches between what's in the catalog and what would show in the picker
"""

from avatar_catalog import AVATAR_CATALOG
import os
import re
from pathlib import Path

print("=" * 80)
print("🐝 AVATAR PICKER vs SALES CATALOG NAME COMPARISON")
print("=" * 80)
print()

# Helper function matching the API logic
def _slug_from_base(base: str):
    name_with_spaces = re.sub(r'(?<!^)([A-Z])', r' \1', base).strip()
    return re.sub(r'[^a-z0-9]+', '-', name_with_spaces.lower()).strip('-'), name_with_spaces

# Check GLB files
static_root = Path('static/assets/avatars')
glb_dir = static_root / 'glb_files'

print("CHECKING GLB FILES (filesystem-derived names):")
print("-" * 80)

glb_names = {}
if glb_dir.exists():
    for fname in os.listdir(glb_dir):
        if not fname.lower().endswith('.glb'):
            continue
        base = fname[:-4]
        slug, name_with_spaces = _slug_from_base(base)
        glb_names[slug] = {
            'filename': fname,
            'base': base,
            'derived_name': name_with_spaces,
            'in_catalog': False,
            'catalog_name': None
        }

# Cross-reference with catalog
catalog_by_id = {av['id']: av for av in AVATAR_CATALOG}

for slug, info in glb_names.items():
    if slug in catalog_by_id:
        info['in_catalog'] = True
        info['catalog_name'] = catalog_by_id[slug]['name']

print(f"{'Slug':<20} | {'GLB Filename':<25} | {'Derived Name':<25} | {'Catalog Name':<30} | {'Match':<10}")
print("-" * 140)

mismatches = []
for slug, info in sorted(glb_names.items()):
    derived = info['derived_name']
    catalog = info['catalog_name'] or 'NOT IN CATALOG'
    
    # Check if names match (ignoring case and "Avatar" suffix)
    derived_clean = derived.replace(' Avatar', '').strip().lower()
    catalog_clean = catalog.replace(' Avatar', '').strip().lower() if catalog != 'NOT IN CATALOG' else ''
    
    if info['in_catalog']:
        match = "✅ MATCH" if derived_clean == catalog_clean else "⚠️ MISMATCH"
        if derived_clean != catalog_clean:
            mismatches.append({
                'slug': slug,
                'filename': info['filename'],
                'derived': derived,
                'catalog': catalog
            })
    else:
        match = "❌ MISSING"
        mismatches.append({
            'slug': slug,
            'filename': info['filename'],
            'derived': derived,
            'catalog': catalog
        })
    
    print(f"{slug:<20} | {info['filename']:<25} | {derived:<25} | {catalog:<30} | {match:<10}")

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total GLB files found: {len(glb_names)}")
print(f"GLB files in catalog: {sum(1 for i in glb_names.values() if i['in_catalog'])}")
print(f"Name mismatches/missing: {len(mismatches)}")
print()

if mismatches:
    print("⚠️ ISSUES FOUND:")
    print()
    for issue in mismatches:
        print(f"  Slug: {issue['slug']}")
        print(f"    Filename: {issue['filename']}")
        print(f"    Picker shows: '{issue['derived']}'")
        print(f"    Catalog has: '{issue['catalog']}'")
        if issue['catalog'] != 'NOT IN CATALOG':
            print(f"    → Recommendation: Update catalog to match filename, OR rename GLB file")
        else:
            print(f"    → Recommendation: Add this avatar to catalog")
        print()
else:
    print("✅ All GLB avatar names match between picker and catalog!")
    print()

# Also check OBJ avatars from catalog
print()
print("=" * 80)
print("CHECKING OBJ AVATARS (catalog entries with folder != 'glb_files'):")
print("-" * 80)

obj_avatars = [av for av in AVATAR_CATALOG if av.get('folder') != 'glb_files']
print(f"{'ID':<20} | {'Name':<35} | {'Folder':<25}")
print("-" * 80)
for av in obj_avatars:
    print(f"{av['id']:<20} | {av['name']:<35} | {av['folder']:<25}")

print()
print(f"Total OBJ avatars: {len(obj_avatars)}")
print("These names come directly from the catalog, so they should be consistent.")
print()
