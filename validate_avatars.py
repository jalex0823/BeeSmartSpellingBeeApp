#!/usr/bin/env python3
"""Validate all avatar paths and files"""

import os
from pathlib import Path
from avatar_catalog import AVATAR_CATALOG as AVATARS

print('=== Avatar Path Validation ===\n')
errors = []
warnings = []

for avatar in AVATARS:
    avatar_id = avatar['id']
    folder = avatar['folder']
    obj_file = avatar['obj_file']
    mtl_file = avatar['mtl_file']
    texture_file = avatar['texture_file']
    
    # Check if directory exists
    avatar_dir = Path(f'static/assets/avatars/{folder}')
    if not avatar_dir.exists():
        errors.append(f'❌ {avatar_id}: Directory not found: {avatar_dir}')
        continue
    
    # Check if files exist
    obj_path = avatar_dir / obj_file
    mtl_path = avatar_dir / mtl_file
    texture_path = avatar_dir / texture_file
    
    missing = []
    if not obj_path.exists():
        missing.append(f'{obj_file}')
    if not mtl_path.exists():
        missing.append(f'{mtl_file}')
    if not texture_path.exists():
        missing.append(f'{texture_file}')
    
    if missing:
        errors.append(f'❌ {avatar_id}: Missing files in {folder}/: {", ".join(missing)}')
    else:
        print(f'✅ {avatar_id}: All files present in {folder}/')

print(f'\n=== Summary ===')
print(f'Total avatars checked: {len(AVATARS)}')
print(f'Errors: {len(errors)}')

if errors:
    print(f'\n=== Errors ===')
    for err in errors:
        print(err)
else:
    print('\n🎉 All avatar files are present and paths match!')
