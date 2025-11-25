#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test that avatar thumbnail mappings are correct in avatar_catalog.py
"""

import os
import sys
from pathlib import Path
from avatar_catalog import AVATAR_CATALOG, get_avatar_info

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    print("🔍 Testing Avatar Thumbnail Mappings")
    print("=" * 70)
    
    # Get all GLB files
    static_root = os.path.join('static', 'assets', 'avatars')
    glb_dir = os.path.join(static_root, 'glb_files')
    thumb_dir = os.path.join(glb_dir, 'AvatarThumbnails')
    
    glb_files = set(f[:-4] for f in os.listdir(glb_dir) if f.lower().endswith('.glb'))
    thumb_files = set(f[:-8] for f in os.listdir(thumb_dir) if f.endswith('!.png'))
    
    # Get all GLB avatar IDs from catalog
    glb_avatar_ids = [a['id'] for a in AVATAR_CATALOG if a.get('folder') == 'glb_files']
    
    print(f"Total GLB avatars in catalog: {len(glb_avatar_ids)}")
    print(f"Total GLB files: {len(glb_files)}")
    print(f"Total thumbnails: {len(thumb_files)}")
    print()
    
    errors = []
    successes = []
    
    for avatar_id in sorted(glb_avatar_ids):
        try:
            info = get_avatar_info(avatar_id)
            thumb_url = info.get('thumbnail_url', '')
            thumb_file = thumb_url.split('/')[-1]  # e.g., "KnightBee!.png"
            thumb_name = thumb_file[:-8] if thumb_file.endswith('!.png') else thumb_file[:-4]
            
            # Check if thumbnail exists
            thumb_path = os.path.join(thumb_dir, thumb_file)
            if os.path.exists(thumb_path):
                successes.append((avatar_id, thumb_file, thumb_name))
            else:
                errors.append(f"❌ {avatar_id}: missing thumbnail {thumb_file} (expected in {thumb_path})")
        except Exception as e:
            errors.append(f"❌ {avatar_id}: {str(e)}")
    
    # Show results
    print("RESULTS:")
    print("=" * 70)
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for err in errors:
            print(f"  {err}")
    else:
        print(f"\n✅ All {len(successes)} avatar thumbnails are correctly mapped!")
    
    # Detailed list
    print(f"\n📋 DETAILED MAPPING ({len(successes)} SUCCESS):")
    for avatar_id, thumb_file, thumb_name in successes[:15]:
        print(f"  ✅ {avatar_id:20} → {thumb_file} ({thumb_name})")
    if len(successes) > 15:
        print(f"  ... and {len(successes) - 15} more")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    main()
