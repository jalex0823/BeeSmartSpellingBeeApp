"""
Batch validate all avatars and find which ones have OBJ/MTL mismatches
"""

import os
from validate_obj_mtl_connections import validate_avatar_connections

# All avatar folders
avatar_folders = [
    'al-bee',
    'anxious-bee', 
    'mascot-bee',
    'monster-bee',
    'professor-bee',
    'rocker-bee',
    'vamp-bee',
    'ware-bee',
    'zom-bee',
    'bee-diva',
    # New avatars
    'beedoctor',
    'beeknight',
    'builderbee',
    'buzzbotbee',
    'buzzhero',
    'detectivebee',
    'explorerbee',
    'frankenbee',
    'motorcyclebuzzbee',
    'queenbeemajesty',
    'seabee',
    'spacebeeexplorer',
    'superbeehero'
]

print("="*70)
print("BATCH AVATAR VALIDATION")
print("="*70)
print(f"Checking {len(avatar_folders)} avatars...\n")

valid_avatars = []
invalid_avatars = []
missing_avatars = []

for folder in avatar_folders:
    folder_path = os.path.join('static', 'assets', 'avatars', folder)
    
    if not os.path.exists(folder_path):
        print(f"❌ {folder:30} FOLDER MISSING")
        missing_avatars.append(folder)
        continue
    
    try:
        is_valid = validate_avatar_connections(folder, verbose=False)
        if is_valid:
            print(f"✅ {folder:30} VALID")
            valid_avatars.append(folder)
        else:
            print(f"❌ {folder:30} INVALID")
            invalid_avatars.append(folder)
    except Exception as e:
        print(f"⚠️  {folder:30} ERROR: {str(e)[:40]}")
        invalid_avatars.append(folder)

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"✅ Valid avatars: {len(valid_avatars)}")
print(f"❌ Invalid avatars: {len(invalid_avatars)}")
print(f"❓ Missing avatars: {len(missing_avatars)}")

if invalid_avatars:
    print(f"\n🔧 Avatars needing fixes:")
    for avatar in invalid_avatars:
        print(f"   - {avatar}")

if missing_avatars:
    print(f"\n❓ Missing avatar folders:")
    for avatar in missing_avatars:
        print(f"   - {avatar}")
