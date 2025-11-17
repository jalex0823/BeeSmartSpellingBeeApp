#!/usr/bin/env python3
"""
Clean up GLB files that aren't in the official 39 avatar catalog.
Moves unwanted GLB files to a backup folder instead of deleting them.
"""

import os
import shutil

# Official 39 avatars from avatar_catalog.py
OFFICIAL_CATALOG_IDS = {
    'knight-bee', 'super-bee', 'robo-bee', 'queen-bee', 'mascot-bee',
    'builder-bee', 'detective-bee', 'singer-bee', 'o-bee', 'motor-bee',
    'brother-bee', 'cool-bee', 'space-bee',  # earn_or_buy tier
    'professor-bee', 'pharaoh-bee', 'vamp-bee', 'nerd-bee', 'franken-bee',
    'angel-bee', 'fire-bee', 'cyber-bee', 'sheriff-bee', 'biker-bee',
    'dragon-bee', 'chef-bee', 'pirate-bee'  # premium tier
}

# Map GLB filename base to catalog ID
GLB_TO_CATALOG = {
    'BeeKnight': 'knight-bee',
    'BrotherBee': 'brother-bee',
    'BuilderBee': 'builder-bee',
    'BuzzBee': None,  # Not in catalog
    'CoolBee': 'cool-bee',
    'DetectiveBee': 'detective-bee',
    'MotorBee': 'motor-bee',
    'OBee': 'o-bee',
    'QueenBee': 'queen-bee',
    'RoboBee': 'robo-bee',
    'SingerBee': 'singer-bee',
    'SpaceBee': 'space-bee',
    'SuperBee': 'super-bee',
    
    # These should be REMOVED (not in catalog):
    'BudaBee': None,
    'CutieBee': None,
    'DivaBee': None,
    'DocBee': None,  # Duplicate of doctor-bee DB avatar
    'ExplorerBee': None,
    'Frankenbee': None,  # Duplicate of franken-bee DB avatar
    'HoneyComb': None,
    'JRockBee': None,  # We have rocker-bee in DB
    'SeaBee': None,
    'SelfieBee': None,
}

def main():
    glb_dir = 'static/assets/avatars/glb_files'
    backup_dir = 'static/assets/avatars/glb_files_backup'
    
    if not os.path.isdir(glb_dir):
        print(f"❌ GLB directory not found: {glb_dir}")
        return
    
    # Create backup directory
    os.makedirs(backup_dir, exist_ok=True)
    
    print("🧹 Cleaning up GLB files...\n")
    
    moved_count = 0
    kept_count = 0
    
    for fname in sorted(os.listdir(glb_dir)):
        if not fname.lower().endswith('.glb'):
            continue
        
        base = fname[:-4]
        catalog_id = GLB_TO_CATALOG.get(base)
        
        src_path = os.path.join(glb_dir, fname)
        
        if catalog_id is None:
            # Move to backup
            dst_path = os.path.join(backup_dir, fname)
            shutil.move(src_path, dst_path)
            print(f"🗑️  Moved: {fname} (not in catalog)")
            moved_count += 1
        else:
            print(f"✅ Kept:  {fname} → {catalog_id}")
            kept_count += 1
    
    print(f"\n📊 Summary:")
    print(f"   Kept: {kept_count} GLB files")
    print(f"   Moved to backup: {moved_count} GLB files")
    print(f"\n💾 Backup location: {backup_dir}")

if __name__ == '__main__':
    main()
