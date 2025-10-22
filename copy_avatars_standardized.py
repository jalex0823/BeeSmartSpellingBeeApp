"""
Copy and Standardize Avatar Files
Copies avatars from source to target with both original and standardized names
"""
import os
import shutil
from pathlib import Path

SOURCE_DIR = Path("Avatars/3D Avatar Files")
TARGET_DIR = Path("static/assets/avatars")

AVATARS = [
    ("AlBee", "al-bee"),
    ("AnxiousBee", "anxious-bee"),
    ("AstroBee", "astro-bee"),
    ("BikerBee", "biker-bee"),
    ("BrotherBee", "brother-bee"),
    ("BuilderBee", "builder-bee"),
    ("CoolBee", "cool-bee"),
    ("DetectiveBee", "detective-bee"),
    ("DivaBee", "diva-bee"),
    ("DoctorBee", "doctor-bee"),
    ("ExplorerBee", "explorer-bee"),
    ("Frankenbee", "franken-bee"),
    ("KnightBee", "knight-bee"),
    ("MascotBee", "mascot-bee"),
    ("MonsterBee", "monster-bee"),
    ("ProfessorBee", "professor-bee"),
    ("QueenBee", "queen-bee"),
    ("RoboBee", "robo-bee"),
    ("RockerBee", "rocker-bee"),
    ("Seabea", "seabea"),
    ("Superbee", "superbee"),
    ("VampBee", "vamp-bee"),
    ("WareBee", "ware-bee"),
    ("ZomBee", "zom-bee"),
]

def copy_avatar(folder_name, avatar_id):
    """Copy avatar files with both original and standardized names"""
    source_path = SOURCE_DIR / folder_name
    target_path = TARGET_DIR / avatar_id
    
    if not source_path.exists():
        print(f"❌ Source missing: {source_path}")
        return False
    
    # Create target directory
    target_path.mkdir(parents=True, exist_ok=True)
    
    files_copied = 0
    
    # Define file mappings
    file_mappings = [
        (f"{folder_name}.obj", [f"{folder_name}.obj", "model.obj"]),
        (f"{folder_name}.mtl", [f"{folder_name}.mtl", "model.mtl"]),
        (f"{folder_name}.png", [f"{folder_name}.png", "texture.png"]),
        (f"{folder_name}!.png", [f"{folder_name}!.png", "thumbnail.png", "preview.png"]),
    ]
    
    for source_filename, target_filenames in file_mappings:
        source_file = source_path / source_filename
        
        if not source_file.exists():
            print(f"  ⚠️  Missing: {source_filename}")
            continue
        
        # Copy to all target names
        for target_filename in target_filenames:
            target_file = target_path / target_filename
            try:
                shutil.copy2(source_file, target_file)
                files_copied += 1
            except Exception as e:
                print(f"  ❌ Error copying to {target_filename}: {e}")
    
    print(f"✅ {folder_name} → {avatar_id} ({files_copied} files)")
    return True

def main():
    print("="*80)
    print("📦 Copying and Standardizing Avatar Files")
    print("="*80)
    print(f"Source: {SOURCE_DIR}")
    print(f"Target: {TARGET_DIR}\n")
    
    success_count = 0
    error_count = 0
    
    for folder_name, avatar_id in AVATARS:
        if copy_avatar(folder_name, avatar_id):
            success_count += 1
        else:
            error_count += 1
    
    print("\n" + "="*80)
    print(f"✅ Successfully copied: {success_count}")
    print(f"❌ Errors: {error_count}")
    print("="*80)
    
    # Verify total files
    total_files = sum(len(list(d.iterdir())) for d in TARGET_DIR.iterdir() if d.is_dir())
    print(f"\n📊 Total files in target: {total_files}")
    print(f"📊 Expected: ~{len(AVATARS) * 10} files (10 per avatar)")

if __name__ == "__main__":
    main()
