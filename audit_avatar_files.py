#!/usr/bin/env python3
"""
Audit all avatar files to find mismatches between database and actual files
"""
from AjaSpellBApp import app, db
from models import Avatar
import os

app.app_context().push()

print("=" * 80)
print("AVATAR FILE AUDIT")
print("=" * 80)

avatars = Avatar.query.order_by(Avatar.slug).all()

for avatar in avatars:
    folder = f"static/assets/avatars/{avatar.folder_path}"
    
    if not os.path.exists(folder):
        print(f"\n❌ {avatar.slug}: FOLDER MISSING")
        continue
    
    actual_files = sorted(os.listdir(folder))
    png_files = [f for f in actual_files if f.endswith('.png')]
    
    print(f"\n{'='*80}")
    print(f"📁 {avatar.slug} ({avatar.name})")
    print(f"{'='*80}")
    print(f"Database:")
    print(f"  OBJ:       {avatar.obj_file}")
    print(f"  MTL:       {avatar.mtl_file}")
    print(f"  TEXTURE:   {avatar.texture_file}")
    print(f"  THUMBNAIL: {avatar.thumbnail_file}")
    print(f"\nActual files in folder:")
    for f in actual_files:
        print(f"  - {f}")
    
    # Check for issues
    issues = []
    
    # Check if thumbnail exists
    if avatar.thumbnail_file not in actual_files:
        issues.append(f"❌ THUMBNAIL NOT FOUND: {avatar.thumbnail_file}")
        print(f"\n  Available PNGs: {png_files}")
    
    # Check if texture exists
    if avatar.texture_file and avatar.texture_file not in actual_files:
        issues.append(f"❌ TEXTURE NOT FOUND: {avatar.texture_file}")
    
    # Check if OBJ exists
    if avatar.obj_file not in actual_files:
        issues.append(f"❌ OBJ NOT FOUND: {avatar.obj_file}")
    
    # Check if MTL exists
    if avatar.mtl_file and avatar.mtl_file not in actual_files:
        issues.append(f"❌ MTL NOT FOUND: {avatar.mtl_file}")
    
    if issues:
        print(f"\n⚠️  ISSUES:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print(f"\n✅ All files match database")

print("\n" + "=" * 80)
print("AUDIT COMPLETE")
print("=" * 80)
