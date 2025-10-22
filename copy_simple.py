"""Simple avatar file copier without emojis"""
import os
import shutil
from avatar_catalog import AVATAR_CATALOG

SOURCE_BASE = "C:/Users/jeff/Dropbox/BeeSmartSpellingBeeApp/Avatars/3D Avatar Files"
TARGET_BASE = "static/assets/avatars"

print("=" * 80)
print("COPYING AVATAR FILES")
print("=" * 80)

copied = 0
for avatar in AVATAR_CATALOG:
    avatar_id = avatar['id']
    folder = avatar.get('folder', avatar_id)
    obj_file = avatar.get('obj_file', 'model.obj')
    mtl_file = avatar.get('mtl_file', 'model.mtl')
    tex_file = avatar.get('texture_file', 'texture.png')
    
    src_dir = os.path.join(SOURCE_BASE, folder)
    dst_dir = os.path.join(TARGET_BASE, avatar_id)
    os.makedirs(dst_dir, exist_ok=True)
    
    print(f"\n{avatar['name']} -> {avatar_id}")
    
    for filename in [obj_file, mtl_file, tex_file]:
        src = os.path.join(src_dir, filename)
        dst = os.path.join(dst_dir, filename)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            mb = os.path.getsize(dst) / (1024 * 1024)
            print(f"  [OK] {filename} ({mb:.1f} MB)")
            copied += 1
        else:
            print(f"  [SKIP] {filename} not found")
    
    # Copy thumbnails
    pngs = [f for f in os.listdir(src_dir) if f.endswith('.png') and f != tex_file]
    if pngs:
        shutil.copy2(os.path.join(src_dir, pngs[0]), os.path.join(dst_dir, 'thumbnail.png'))
        shutil.copy2(os.path.join(dst_dir, 'thumbnail.png'), os.path.join(dst_dir, 'preview.png'))
        print(f"  [OK] thumbnail + preview")
        copied += 2

print(f"\n{'=' * 80}")
print(f"DONE: {copied} files copied to {TARGET_BASE}")
print("=" * 80)
