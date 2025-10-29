#!/usr/bin/env python3
"""
Initialize GLB avatars in database (runs automatically on startup)
This is idempotent - safe to run multiple times

🔒 LOCKED GLB FILES - DO NOT MODIFY!
These filenames are validated against actual filesystem and locked to prevent overwrites.
"""
import os
from AjaSpellBApp import app, db
from models import Avatar

# GLB avatars to ensure exist - ALL 16 GLB files
GLB_AVATARS = [
    {
        "slug": "knight-bee",
        "name": "Knight Bee",
        "description": "Brave knight bee defending the spelling realm!",
        "category": "fantasy",
        "folder_path": "glb_files",
        "obj_file": "BeeKnight.glb",
        "mtl_file": None,
        "texture_file": None,
        "thumbnail_file": "AvatarThumbnails/KnightBee!.png",
        "sort_order": 108,
        "is_active": True
    },
    {
        "slug": "obee",
        "name": "O'Bee",
        "description": "The original O'Bee! A classic bee friend.",
        "category": "classic",
        "folder_path": "glb_files",
        "obj_file": "OBee.glb",
        "mtl_file": None,
        "texture_file": None,
        "thumbnail_file": "AvatarThumbnails/OBee!.png",
        "sort_order": 109,
        "is_active": True
    },
    {
        "slug": "diva-bee",
        "name": "Diva Bee",
        "description": "Glamorous and fabulous! Star of the hive.",
        "category": "entertainment",
        "folder_path": "glb_files",
        "obj_file": "DivaBee.glb",
        "mtl_file": None,
        "texture_file": None,
        "thumbnail_file": "AvatarThumbnails/DivaBee!.png",
        "sort_order": 105,
        "is_active": True
    },
    {
        "slug": "explorer-bee",
        "name": "Explorer Bee",
        "description": "Adventure awaits! Ready to discover new horizons.",
        "category": "adventure",
        "folder_path": "glb_files",
        "obj_file": "ExplorerBee.glb",
        "mtl_file": None,
        "texture_file": None,
        "thumbnail_file": "AvatarThumbnails/ExplorerBee!.png",
        "sort_order": 106,
        "is_active": True
    }
]

# Avatars that need obj_file corrections
GLB_CORRECTIONS = {
    "astro-bee": "SpaceBee.glb",  # Was AstroBee.glb, but file is actually SpaceBee.glb
    "space-bee": "SpaceBee.glb",  # Ensure space-bee also points correctly
}

# 🔒 LOCKED: Correct GLB filenames validated against filesystem
# These are the ONLY valid GLB files - prevents accidental overwrites
LOCKED_GLB_FILES = {
    'BeeKnight.glb', 'BrotherBee.glb', 'BudaBee.glb', 'BuilderBee.glb',
    'CoolBee.glb', 'CutieBee.glb', 'DetectiveBee.glb', 'DivaBee.glb',
    'DocBee.glb', 'ExplorerBee.glb', 'Frankenbee.glb', 'OBee.glb',
    'QueenBee.glb', 'RoboBee.glb', 'SeaBee.glb', 'SpaceBee.glb', 'SuperBee.glb',
    # Newly added, verified GLB assets
    'MotorBee.glb', 'HoneyComb.glb'
}

# 🔒 LOCKED: Avatar name to correct GLB filename mapping
AVATAR_GLB_MAPPING = {
    'Knight Bee': 'BeeKnight.glb',
    'Brother Bee': 'BrotherBee.glb',
    'BudaBee': 'BudaBee.glb',
    'Builder Bee': 'BuilderBee.glb',
    'Cool Bee': 'CoolBee.glb',
    'Cutie Bee': 'CutieBee.glb',
    'Detective Bee': 'DetectiveBee.glb',
    'Diva Bee': 'DivaBee.glb',
    'Doctor Bee': 'DocBee.glb',
    'Explorer Bee': 'ExplorerBee.glb',
    'Franken Bee': 'Frankenbee.glb',
    "O'Bee": 'OBee.glb',
    'Queen Bee': 'QueenBee.glb',
    'Robo Bee': 'RoboBee.glb',
    'Sea Bee': 'SeaBee.glb',
    'Space Bee': 'SpaceBee.glb',
    'Astro Bee': 'SpaceBee.glb',  # Astro uses same file as Space
    'Super Bee': 'SuperBee.glb'
}
# Extend mapping for newly added GLB avatars
AVATAR_GLB_MAPPING.update({
    'Motorcycle Bee': 'MotorBee.glb',
    'HoneyComb': 'HoneyComb.glb'
})

def validate_glb_files():
    """
    🔒 VALIDATION: Ensure all GLB avatars point to correct files
    Prevents accidental overwrites or incorrect file references
    """
    with app.app_context():
        # Get all GLB avatars from database
        glb_avatars = Avatar.query.filter_by(folder_path='glb_files', is_active=True).all()
        
        issues_found = []
        fixes_applied = []
        
        for avatar in glb_avatars:
            correct_file = AVATAR_GLB_MAPPING.get(avatar.name)
            current_file = avatar.obj_file
            
            # Check if file is in locked set
            if current_file not in LOCKED_GLB_FILES:
                issues_found.append(f"⚠️ {avatar.name}: {current_file} NOT in locked set")
            
            # Check if file matches correct mapping
            if correct_file and current_file != correct_file:
                issues_found.append(f"❌ {avatar.name}: Expected {correct_file}, got {current_file}")
                # Auto-fix the issue
                avatar.obj_file = correct_file
                fixes_applied.append(f"✅ Fixed {avatar.name}: {current_file} → {correct_file}")
        
        if fixes_applied:
            db.session.commit()
            print("🔒 GLB FILE VALIDATION - FIXES APPLIED:")
            for fix in fixes_applied:
                print(f"  {fix}")
        
        if issues_found and not fixes_applied:
            print("🚨 GLB FILE VALIDATION - ISSUES DETECTED:")
            for issue in issues_found:
                print(f"  {issue}")
            return False
        
        if not issues_found and not fixes_applied:
            print("✅ GLB FILE VALIDATION PASSED - All files correct!")
        
        return True

def init_glb_avatars():
    """Initialize GLB avatars - safe to call multiple times"""
    with app.app_context():
        # 🔒 FIRST: Validate all existing GLB files
        validate_glb_files()
        
        added = 0
        updated = 0
        
        # Add missing avatars
        for avatar_data in GLB_AVATARS:
            existing = Avatar.query.filter_by(slug=avatar_data["slug"]).first()
            
            if existing:
                # Update if obj_file is wrong
                if existing.obj_file != avatar_data["obj_file"]:
                    existing.obj_file = avatar_data["obj_file"]
                    existing.folder_path = avatar_data["folder_path"]
                    updated += 1
                    print(f"✅ Updated: {avatar_data['slug']} -> {avatar_data['obj_file']}")
            else:
                # Create new avatar
                avatar = Avatar(**avatar_data)
                db.session.add(avatar)
                print(f"➕ Added: {avatar_data['slug']}")
                added += 1
        
        # Fix incorrect obj_file references
        for slug, correct_file in GLB_CORRECTIONS.items():
            avatar = Avatar.query.filter_by(slug=slug).first()
            if avatar and avatar.obj_file != correct_file:
                print(f"🔧 Correcting {slug}: {avatar.obj_file} -> {correct_file}")
                avatar.obj_file = correct_file
                avatar.folder_path = "glb_files"
                updated += 1
        
        # Ensure motorcycle-bee activation reflects filesystem reality
        motorcycle = Avatar.query.filter_by(slug="motorcycle-bee").first()
        if motorcycle and motorcycle.obj_file == "MotorBee.glb":
            model_path = os.path.join(app.static_folder, 'assets', 'avatars', 'glb_files', 'MotorBee.glb')
            if not os.path.exists(model_path):
                print(f"⚠️ Deactivating motorcycle-bee (file MotorBee.glb not found)")
                motorcycle.is_active = False
                updated += 1
            else:
                if not motorcycle.is_active:
                    print(f"✅ Activating motorcycle-bee (MotorBee.glb present)")
                    motorcycle.is_active = True
                    updated += 1
        
        if added > 0 or updated > 0:
            db.session.commit()
            print(f"✅ GLB Avatars initialized: {added} added, {updated} updated")
        else:
            print(f"✅ GLB Avatars already initialized")

if __name__ == "__main__":
    init_glb_avatars()
