"""
Script to organize avatar files from source directory to Flask static assets
Copies 3D models, textures, and creates thumbnails
"""

import os
import shutil
from pathlib import Path

# Source directory with all avatar files
SOURCE_DIR = r"C:\Users\JefferyAlexander\Dropbox\BeeSmartSpellingBeeApp\Avatars\3D Avatar Files"

# Destination directory in Flask app
DEST_DIR = r"C:\Users\JefferyAlexander\Dropbox\BeeSmartSpellingBeeApp\static\assets\avatars"

# Avatar mapping - maps folder names to clean avatar IDs
AVATAR_MAPPING = {
    "Anxious_Bee_1018233904_texture_obj": {
        "id": "anxious-bee",
        "name": "Anxious Bee",
        "category": "emotion"
    },
    "Bee_Diva_1018233551_texture_obj": {
        "id": "bee-diva",
        "name": "Bee Diva",
        "category": "entertainment"
    },
    "Bee_Doctor_1019001202_texture_obj": {
        "id": "doctor-bee",
        "name": "Doctor Bee",
        "category": "profession"
    },
    "Bee_Knight_1018184515_texture_obj": {
        "id": "knight-bee",
        "name": "Knight Bee",
        "category": "fantasy"
    },
    "Bee_Majesty_1018185557_texture_obj": {
        "id": "majesty-bee",
        "name": "Bee Majesty",
        "category": "royal"
    },
    "Bee_Scientist_1019002302_texture_obj": {
        "id": "scientist-bee",
        "name": "Scientist Bee",
        "category": "profession"
    },
    "Buzzbot_Bee_1018230253_texture_obj": {
        "id": "robot-bee",
        "name": "Robot Bee",
        "category": "tech"
    },
    "Buzzing_Menace_1018232544_texture_obj": {
        "id": "killer-bee",
        "name": "Killer Bee",
        "category": "action"
    },
    "Cool_Bee_1018181944_texture_obj": {
        "id": "cool-bee",
        "name": "Cool Bee",
        "category": "classic"
    },
    "Explorer_Bee_1018183500_texture_obj": {
        "id": "explorer-bee",
        "name": "Explorer Bee",
        "category": "adventure"
    },
    "Motorcycle_Buzz_Bee_1018234507_texture_obj": {
        "id": "biker-bee",
        "name": "Biker Bee",
        "category": "action"
    },
    "Professor_Bee_1019002841_texture_obj": {
        "id": "professor-bee",
        "name": "Professor Bee",
        "category": "profession"
    },
    "Queen_Bee_Majesty_1018235517_texture_obj": {
        "id": "queen-bee",
        "name": "Queen Bee",
        "category": "royal"
    },
    "Rockin_Bee_1018232006_texture_obj": {
        "id": "rockstar-bee",
        "name": "Rockstar Bee",
        "category": "entertainment"
    },
    "SeaBee_1019002514_texture_obj": {
        "id": "sea-bee",
        "name": "Sea Bee",
        "category": "adventure"
    },
    "Super_Bee_Hero_1018233012_texture_obj": {
        "id": "superhero-bee",
        "name": "Superhero Bee",
        "category": "fantasy"
    }
}


def organize_avatars():
    """Copy and organize avatar files into the proper structure"""
    
    print("🐝 Starting avatar file organization...")
    print(f"📁 Source: {SOURCE_DIR}")
    print(f"📁 Destination: {DEST_DIR}")
    print()
    
    # Create destination directory if it doesn't exist
    os.makedirs(DEST_DIR, exist_ok=True)
    
    copied_count = 0
    error_count = 0
    
    # Process each avatar folder
    for folder_name, avatar_info in AVATAR_MAPPING.items():
        avatar_id = avatar_info['id']
        source_folder = os.path.join(SOURCE_DIR, folder_name)
        dest_folder = os.path.join(DEST_DIR, avatar_id)
        
        if not os.path.exists(source_folder):
            print(f"⚠️  Source folder not found: {folder_name}")
            error_count += 1
            continue
        
        # Create destination subfolder
        os.makedirs(dest_folder, exist_ok=True)
        
        print(f"📦 Processing: {avatar_info['name']} ({avatar_id})")
        
        # Find and copy files
        files_copied = 0
        original_texture_name = None
        
        for filename in os.listdir(source_folder):
            source_file = os.path.join(source_folder, filename)
            
            # Determine destination filename based on file type
            if filename.endswith('.obj'):
                dest_file = os.path.join(dest_folder, 'model.obj')
                # Read OBJ file and update MTL reference
                try:
                    with open(source_file, 'r', encoding='utf-8') as f:
                        obj_content = f.read()
                    # Update mtl reference to use standardized name
                    obj_content = obj_content.replace(
                        filename.replace('.obj', '.mtl'),
                        'model.mtl'
                    )
                    with open(dest_file, 'w', encoding='utf-8') as f:
                        f.write(obj_content)
                    files_copied += 1
                    continue
                except Exception as e:
                    print(f"   ⚠️  Could not update OBJ file, copying as-is: {e}")
                    
            elif filename.endswith('.mtl'):
                dest_file = os.path.join(dest_folder, 'model.mtl')
                # Read MTL file and update texture reference
                try:
                    with open(source_file, 'r', encoding='utf-8') as f:
                        mtl_content = f.read()
                    
                    # Find the original texture name
                    if 'map_Kd' in mtl_content:
                        import re
                        match = re.search(r'map_Kd\s+(.+\.png)', mtl_content)
                        if match:
                            original_texture_name = match.group(1).strip()
                    
                    # Update texture reference to use standardized name
                    mtl_content = re.sub(
                        r'map_Kd\s+.+\.png',
                        'map_Kd texture.png',
                        mtl_content
                    )
                    
                    with open(dest_file, 'w', encoding='utf-8') as f:
                        f.write(mtl_content)
                    files_copied += 1
                    print(f"   🎨 Updated MTL to reference 'texture.png'")
                    continue
                except Exception as e:
                    print(f"   ⚠️  Could not update MTL file, copying as-is: {e}")
                    
            elif filename.endswith('.png'):
                dest_file = os.path.join(dest_folder, 'texture.png')
                # Copy file first
                try:
                    shutil.copy2(source_file, dest_file)
                    files_copied += 1
                    # Then create thumbnail copy
                    thumb_file = os.path.join(dest_folder, 'thumbnail.png')
                    shutil.copy2(source_file, thumb_file)
                    files_copied += 1
                except Exception as e:
                    print(f"   ❌ Error copying texture {filename}: {e}")
                    error_count += 1
                continue
            else:
                dest_file = os.path.join(dest_folder, filename)
                # Copy any other files
                try:
                    shutil.copy2(source_file, dest_file)
                    files_copied += 1
                except Exception as e:
                    print(f"   ❌ Error copying {filename}: {e}")
                    error_count += 1
                continue
        
        print(f"   ✅ Copied and processed {files_copied} files")
        copied_count += 1
    
    # Also copy the PNG images from main Avatars folder
    print("\n📸 Copying preview images...")
    avatars_main = r"C:\Users\JefferyAlexander\Dropbox\BeeSmartSpellingBeeApp\Avatars"
    
    png_mappings = {
        "CoolBee.png": "cool-bee",
        "ExplorerBee.png": "explorer-bee",
        "KillerBee.png": "killer-bee",
        "KingBee.png": "majesty-bee",
        "MissBee.png": "bee-diva",
        "MissBee2.png": "queen-bee",
        "NureseBee.png": "doctor-bee",
        "RoboBee.png": "robot-bee",
        "RockarBee.png": "rockstar-bee",
        "SeaBee.png": "sea-bee",
        "SmartieBee.png": "professor-bee",
        "SuperBee.png": "superhero-bee"
    }
    
    for png_file, avatar_id in png_mappings.items():
        source_png = os.path.join(avatars_main, png_file)
        if os.path.exists(source_png):
            dest_folder = os.path.join(DEST_DIR, avatar_id)
            if os.path.exists(dest_folder):
                dest_png = os.path.join(dest_folder, 'preview.png')
                try:
                    shutil.copy2(source_png, dest_png)
                    print(f"   ✅ Copied {png_file} → {avatar_id}/preview.png")
                except Exception as e:
                    print(f"   ❌ Error copying {png_file}: {e}")
    
    print()
    print("="*60)
    print(f"✅ Organization complete!")
    print(f"   Avatars processed: {copied_count}")
    print(f"   Errors: {error_count}")
    print(f"   Destination: {DEST_DIR}")
    print("="*60)
    
    return AVATAR_MAPPING


def create_fallback_images():
    """Create a simple fallback image if needed"""
    fallback_path = os.path.join(DEST_DIR, 'fallback.png')
    
    # For now, we'll rely on the existing images
    # Later you can add PIL to create a simple bee emoji/icon
    print(f"\n💡 Tip: Add a fallback.png image to {DEST_DIR} for error handling")


def list_organized_avatars():
    """List all organized avatars for verification"""
    print("\n📋 Organized Avatars:")
    print("-" * 60)
    
    for folder in sorted(os.listdir(DEST_DIR)):
        folder_path = os.path.join(DEST_DIR, folder)
        if os.path.isdir(folder_path):
            files = os.listdir(folder_path)
            print(f"\n🐝 {folder}/")
            for f in sorted(files):
                size = os.path.getsize(os.path.join(folder_path, f))
                size_kb = size / 1024
                print(f"   - {f} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    print("🐝 BeeSmart Avatar File Organizer")
    print("="*60)
    
    # Organize avatars
    avatar_mapping = organize_avatars()
    
    # Create fallback
    create_fallback_images()
    
    # List results
    list_organized_avatars()
    
    print("\n✨ Done! Your avatars are ready to use in the app.")
    print("   Next step: Update avatar_catalog.py with the correct avatar list")
