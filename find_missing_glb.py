#!/usr/bin/env python3
"""
Find which catalog avatars don't have GLB files yet.
"""

import os
import re
from avatar_catalog import AVATAR_CATALOG

# Get existing GLB files
glb_dir = 'static/assets/avatars/glb_files'
existing_glb = set()

if os.path.isdir(glb_dir):
    for fname in os.listdir(glb_dir):
        if fname.lower().endswith('.glb'):
            base = fname[:-4]
            # Convert CamelCase to kebab-case
            slug = re.sub(r'(?<!^)([A-Z])', r'-\1', base).lower()
            existing_glb.add(slug)

print(f"📦 Currently have {len(existing_glb)} GLB files\n")
print("Existing GLB avatars:")
for slug in sorted(existing_glb):
    print(f"  ✅ {slug}")

# Find missing
print(f"\n📋 Catalog has {len(AVATAR_CATALOG)} avatars total\n")

missing_glb = []
for avatar in AVATAR_CATALOG:
    avatar_id = avatar['id']
    if avatar_id not in existing_glb:
        missing_glb.append(avatar)

print(f"❌ Missing GLB files ({len(missing_glb)} avatars):\n")
for avatar in sorted(missing_glb, key=lambda x: x['id']):
    tier = avatar.get('tier', 'unknown')
    name = avatar.get('name', avatar['id'])
    print(f"  {avatar['id']:20} | {tier:15} | {name}")

print(f"\n" + "="*70)
print(f"SUMMARY")
print("="*70)
print(f"Total in catalog: {len(AVATAR_CATALOG)}")
print(f"Have GLB files: {len(existing_glb)}")
print(f"Need GLB files: {len(missing_glb)}")
