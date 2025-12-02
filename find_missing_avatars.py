#!/usr/bin/env python3
"""
Compare catalog to actual avatars (DB + GLB files) to find what's missing.
"""

import os
import sys

# Set up Flask app context
from AjaSpellBApp import app, db
from models import Avatar
from avatar_catalog import AVATAR_CATALOG

# Get all catalog IDs
catalog_ids = {a['id'] for a in AVATAR_CATALOG}
print(f"📋 Catalog has {len(catalog_ids)} avatars\n")

# Get DB avatars
with app.app_context():
    avatars = Avatar.query.filter_by(is_active=True).order_by(Avatar.slug).all()
    db_avatars = {a.slug: a.name for a in avatars}

print(f"💾 Database has {len(db_avatars)} active avatars:")
for slug, name in sorted(db_avatars.items()):
    print(f"   {slug:20} → {name}")

# Get GLB files
glb_dir = 'static/assets/avatars/glb_files'
glb_files = []
if os.path.isdir(glb_dir):
    for fname in sorted(os.listdir(glb_dir)):
        if fname.lower().endswith('.glb'):
            base = fname[:-4]
            # Convert CamelCase to kebab-case
            import re
            slug = re.sub(r'(?<!^)([A-Z])', r'-\1', base).lower()
            glb_files.append((slug, base))

print(f"\n📦 GLB files ({len(glb_files)}):")
for slug, base in glb_files:
    print(f"   {slug:20} ← {base}.glb")

# Combined actual avatars
actual_ids = set(db_avatars.keys()) | {slug for slug, _ in glb_files}
print(f"\n✅ Total actual avatars: {len(actual_ids)}")

# Find missing
missing = catalog_ids - actual_ids
print(f"\n❌ Missing from filesystem/DB ({len(missing)}):")
for catalog_id in sorted(missing):
    catalog_entry = next(a for a in AVATAR_CATALOG if a['id'] == catalog_id)
    tier = catalog_entry.get('tier', 'unknown')
    name = catalog_entry.get('name', catalog_id)
    print(f"   {catalog_id:20} | {tier:15} | {name}")

# Find extras (not in catalog)
extras = actual_ids - catalog_ids
if extras:
    print(f"\n⚠️  In DB/filesystem but NOT in catalog ({len(extras)}):")
    for extra_id in sorted(extras):
        name = db_avatars.get(extra_id, 'GLB file')
        print(f"   {extra_id:20} → {name}")
