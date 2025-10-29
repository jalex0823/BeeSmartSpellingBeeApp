#!/usr/bin/env python3
"""
Add GLB-based avatars to the database
These are the non-working OBJ avatars reimplemented with GLB format
"""
from AjaSpellBApp import app, db
from models import Avatar

# GLB avatars to add (these use GLB format instead of OBJ)
GLB_AVATARS = [
    {
        "slug": "astro-bee",
        "name": "Astro Bee",
        "description": "Space explorer bee! Ready for cosmic spelling adventures.",
        "category": "adventure",
        "folder_path": "glb_files",
        "obj_file": "AstroBee.glb",  # GLB file instead of OBJ
        "mtl_file": None,
        "texture_file": None,
        "thumbnail_file": "AvatarThumbnails/AstroBee!.png",
        "sort_order": 100,
        "is_active": True
    },
    {
        "slug": "brother-bee",
        "name": "Brother Bee",
        "description": "Cool brother bee! Friendly and laid-back.",
        "category": "fun",
        "folder_path": "glb_files",
        "obj_file": "BrotherBee.glb",
        "mtl_file": None,
        "texture_file": None,
        "thumbnail_file": "AvatarThumbnails/BrotherBee!.png",
        "sort_order": 101,
        "is_active": True
    },
    {
        "slug": "builder-bee",
        "name": "Builder Bee",
        "description": "Construction bee! Building stronger spelling skills.",
        "category": "profession",
        "folder_path": "glb_files",
        "obj_file": "BuilderBee.glb",
        "mtl_file": None,
        "texture_file": None,
        "thumbnail_file": "AvatarThumbnails/BuilderBee!.png",
        "sort_order": 102,
        "is_active": True
    },
    {
        "slug": "cool-bee",
        "name": "Cool Bee",
        "description": "Cool dude bee with attitude!",
        "category": "fun",
        "folder_path": "glb_files",
        "obj_file": "CoolBee.glb",
        "mtl_file": None,
        "texture_file": None,
        "thumbnail_file": "AvatarThumbnails/CoolBee!.png",
        "sort_order": 103,
        "is_active": True
    },
    {
        "slug": "cutie-bee",
        "name": "Cutie Bee",
        "description": "Adorable and sweet spelling companion!",
        "category": "fun",
        "folder_path": "glb_files",
        "obj_file": "CutieBee.glb",
        "mtl_file": None,
        "texture_file": None,
        "thumbnail_file": "AvatarThumbnails/CutieBee!.png",
        "sort_order": 104,
        "is_active": True
    },
    {
        "slug": "detective-bee",
        "name": "Detective Bee",
        "description": "Solving spelling mysteries one word at a time!",
        "category": "profession",
        "folder_path": "glb_files",
        "obj_file": "DetectiveBee.glb",
        "mtl_file": None,
        "texture_file": None,
        "thumbnail_file": "AvatarThumbnails/DetectiveBee!.png",
        "sort_order": 105,
        "is_active": True
    },
    {
        "slug": "doctor-bee",
        "name": "Doctor Bee",
        "description": "Medical professional bee healing with words!",
        "category": "profession",
        "folder_path": "glb_files",
        "obj_file": "DocBee.glb",
        "mtl_file": None,
        "texture_file": None,
        "thumbnail_file": "AvatarThumbnails/DoctorBee!.png",
        "sort_order": 106,
        "is_active": True
    },
    {
        "slug": "franken-bee",
        "name": "Franken Bee",
        "description": "Mad scientist bee creating spelling spells!",
        "category": "fantasy",
        "folder_path": "glb_files",
        "obj_file": "Frankenbee.glb",
        "mtl_file": None,
        "texture_file": None,
        "thumbnail_file": "AvatarThumbnails/FrankenBee!.png",
        "sort_order": 107,
        "is_active": True
    },
    {
        "slug": "knight-bee",
        "name": "Knight Bee",
        "description": "Brave knight bee defending the spelling realm!",
        "category": "fantasy",
        "folder_path": "glb_files",
        "obj_file": "BeeKnight.glb",  # Fixed: was incorrectly using QueenBee.glb
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
        "slug": "motorcycle-bee",
        "name": "Motorcycle Bee",
        "description": "Speedy motorcycle-riding bee!",
        "category": "entertainment",
        "folder_path": "glb_files",
        "obj_file": "MotorBee.glb",
        "mtl_file": None,
        "texture_file": None,
        "thumbnail_file": "AvatarThumbnails/MotorBee!.png",
        "sort_order": 110,
        "is_active": True
    },
    {
        "slug": "motorcycle-bee",
        "name": "Motorcycle Bee",
        "description": "Speedy motorcycle-riding bee!",
        "category": "entertainment",
        "folder_path": "glb_files",
        "obj_file": "MotorBee.glb",
        "mtl_file": None,
        "texture_file": None,
        "thumbnail_file": "AvatarThumbnails/MotorBee!.png",
        "sort_order": 110,
        "is_active": True
    },
    {
        "slug": "queen-bee",
        "name": "Queen Bee",
        "description": "Majestic queen bee royalty!",
        "category": "fantasy",
        "folder_path": "glb_files",
        "obj_file": "QueenBee.glb",
        "mtl_file": None,
        "texture_file": None,
        "thumbnail_file": "AvatarThumbnails/QueenBee!.png",
        "sort_order": 111,
        "is_active": True
    },
    {
        "slug": "robo-bee",
        "name": "Robo Bee",
        "description": "Futuristic robot bee with mechanical precision!",
        "category": "technology",
        "folder_path": "glb_files",
        "obj_file": "RoboBee.glb",
        "mtl_file": None,
        "texture_file": None,
        "thumbnail_file": "AvatarThumbnails/RoboBee!.png",
        "sort_order": 112,
        "is_active": True
    },
    {
        "slug": "sea-bee",
        "name": "Sea Bee",
        "description": "Ocean-loving sea bee explorer!",
        "category": "adventure",
        "folder_path": "glb_files",
        "obj_file": "SeaBee.glb",
        "mtl_file": None,
        "texture_file": None,
        "thumbnail_file": "AvatarThumbnails/SeaBee!.png",
        "sort_order": 113,
        "is_active": True
    },
    {
        "slug": "space-bee",
        "name": "Space Bee",
        "description": "Interstellar space bee explorer!",
        "category": "adventure",
        "folder_path": "glb_files",
        "obj_file": "SpaceBee.glb",
        "mtl_file": None,
        "texture_file": None,
        "thumbnail_file": "AvatarThumbnails/AstroBee!.png",  # Using astro thumbnail
        "sort_order": 114,
        "is_active": True
    },
    {
        "slug": "super-bee",
        "name": "Super Bee",
        "description": "Superhero bee with amazing powers!",
        "category": "entertainment",
        "folder_path": "glb_files",
        "obj_file": "SuperBee.glb",
        "mtl_file": None,
        "texture_file": None,
        "thumbnail_file": "AvatarThumbnails/SuperBee!.png",
        "sort_order": 115,
        "is_active": True
    }
]

with app.app_context():
    added = 0
    for avatar_data in GLB_AVATARS:
        # Check if already exists
        existing = Avatar.query.filter_by(slug=avatar_data["slug"]).first()
        if existing:
            print(f"✅ {avatar_data['slug']} already exists")
            continue
        
        # Create new avatar
        avatar = Avatar(**avatar_data)
        db.session.add(avatar)
        print(f"➕ Added: {avatar_data['slug']}")
        added += 1
    
    db.session.commit()
    print(f"\n✅ Added {added} new GLB avatars!")
    
    # Show all avatars
    all_avatars = Avatar.query.filter_by(is_active=True).order_by(Avatar.sort_order).all()
    print(f"\n📋 Total active avatars: {len(all_avatars)}")
    for a in all_avatars:
        print(f"  - {a.slug}: {a.name}")
