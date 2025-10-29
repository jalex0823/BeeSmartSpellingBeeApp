"""
Cleanup script to remove OLD broken OBJ avatar files from legacy folder.
These were replaced with GLB versions.
"""
import os
import shutil

# Legacy folder path
LEGACY_FOLDER = "static/Avatars/3D Avatar Files"

# The 9 working OBJ avatars we want to KEEP
WORKING_OBJ_AVATARS = [
    'AlBee',
    'AnxiousBee', 
    'MascotBee',
    'MonsterBee',
    'ProfessorBee',
    'RockerBee',
    'VampBee',
    'WareBee',
    'ZomBee'
]

# Broken OBJ avatars that were replaced with GLB - REMOVE THESE
BROKEN_OBJ_TO_REMOVE = [
    'AstroBee',        # → astro-bee.glb
    'BikerBee',        # → biker-bee.glb
    'BuilderBee',      # → builder-bee.glb
    'CoolBee',         # → cool-bee.glb
    'DetectiveBee',    # → detective-bee.glb
    'DivaBee',         # → diva-bee.glb
    'DoctorBee',       # → doctor-bee.glb
    'ExplorerBee',     # → explorer-bee.glb
    'Frankenbee',      # → franken-bee.glb
    'KnightBee',       # → knight-bee.glb
    'QueenBee',        # → queen-bee.glb
    'RoboBee',         # → robo-bee.glb (motorcycle)
    'Seabea',          # → sea-bee.glb
    'Superbee',        # → super-bee.glb
    'BrotherBee',      # Extra - not in use
]

def main():
    if not os.path.exists(LEGACY_FOLDER):
        print(f"❌ Legacy folder not found: {LEGACY_FOLDER}")
        return
    
    print(f"🔍 Scanning legacy folder: {LEGACY_FOLDER}")
    print("=" * 60)
    
    # Get all folders
    all_folders = [f for f in os.listdir(LEGACY_FOLDER) 
                   if os.path.isdir(os.path.join(LEGACY_FOLDER, f))]
    
    print(f"\n📊 Found {len(all_folders)} total avatar folders")
    print(f"✅ Keeping {len(WORKING_OBJ_AVATARS)} working OBJ avatars")
    print(f"🗑️  Removing {len(BROKEN_OBJ_TO_REMOVE)} broken OBJ avatars")
    
    # Confirm before deletion
    print("\n⚠️  FOLDERS TO DELETE:")
    folders_to_delete = []
    for folder in all_folders:
        if folder in BROKEN_OBJ_TO_REMOVE:
            folder_path = os.path.join(LEGACY_FOLDER, folder)
            # Count files
            file_count = sum(len(files) for _, _, files in os.walk(folder_path))
            print(f"   - {folder} ({file_count} files)")
            folders_to_delete.append(folder)
    
    print(f"\n✅ FOLDERS TO KEEP:")
    for folder in all_folders:
        if folder in WORKING_OBJ_AVATARS:
            print(f"   ✓ {folder}")
    
    if not folders_to_delete:
        print("\n✅ No folders to delete!")
        return
    
    # Ask for confirmation
    print("\n" + "=" * 60)
    response = input(f"\n⚠️  Delete {len(folders_to_delete)} folders? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("❌ Aborted - no changes made")
        return
    
    # Delete folders
    print("\n🗑️  Deleting folders...")
    deleted_count = 0
    
    for folder in folders_to_delete:
        folder_path = os.path.join(LEGACY_FOLDER, folder)
        try:
            shutil.rmtree(folder_path)
            print(f"   ✓ Deleted: {folder}")
            deleted_count += 1
        except Exception as e:
            print(f"   ❌ Error deleting {folder}: {e}")
    
    print("\n" + "=" * 60)
    print(f"✅ Cleanup complete!")
    print(f"   Deleted: {deleted_count} folders")
    print(f"   Kept: {len(WORKING_OBJ_AVATARS)} working OBJ avatars")
    
    # Verify remaining folders
    remaining = [f for f in os.listdir(LEGACY_FOLDER) 
                 if os.path.isdir(os.path.join(LEGACY_FOLDER, f))]
    print(f"\n📊 Remaining folders: {len(remaining)}")
    for folder in sorted(remaining):
        print(f"   - {folder}")

if __name__ == '__main__':
    main()
