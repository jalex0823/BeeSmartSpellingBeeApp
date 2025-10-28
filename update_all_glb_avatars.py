#!/usr/bin/env python3
"""
Update all avatars to use GLB files instead of OBJ
Adds all 15 GLB avatars to the database
"""
from AjaSpellBApp import app, db
from models import Avatar

# ALL 15 GLB avatars (9 working OBJ + 6 more GLB)
ALL_GLB_AVATARS = [
    # 9 Working OBJ avatars - UPDATE to keep as they are
    {
        "slug": "al-bee",
        "name": "Al Bee",
        "description": "Classic bee! Always ready to help with spelling.",
        "category": "classic",
        "folder_path": "al-bee",
        "obj_file": "AlBee.obj",  # Keep as OBJ
        "mtl_file": "AlBee.mtl",
        "texture_file": "AlBee.png",
        "thumbnail_file": "AlBee!.png",
        "sort_order": 1,
        "is_active": True,
        "skip": True  # Don't update, keep OBJ
    },
    {
        "slug": "anxious-bee",
        "name": "Anxious Bee",
        "description": "A little nervous but eager to learn!",
        "category": "emotion",
        "folder_path": "anxious-bee",
        "obj_file": "AnxiousBee.obj",
        "mtl_file": "AnxiousBee.mtl",
        "texture_file": "AnxiousBee.png",
        "thumbnail_file": "AnxiousBee!.png",
        "sort_order": 2,
        "is_active": True,
        "skip": True
    },
    {
        "slug": "mascot-bee",
        "name": "Mascot Bee",
        "description": "The original BeeSmart mascot! Cheerful and encouraging.",
        "category": "classic",
        "folder_path": "mascot-bee",
        "obj_file": "MascotBee.obj",
        "mtl_file": "MascotBee.mtl",
        "texture_file": "MascotBee.png",
        "thumbnail_file": "MascotBee!.png",
        "sort_order": 3,
        "is_active": True,
        "skip": True
    },
    {
        "slug": "monster-bee",
        "name": "Monster Bee",
        "description": "Not scary, just misunderstood! Friendly monster bee.",
        "category": "fantasy",
        "folder_path": "monster-bee",
        "obj_file": "MonsterBee.obj",
        "mtl_file": "MonsterBee.mtl",
        "texture_file": "MonsterBee.png",
        "thumbnail_file": "MonsterBee!.png",
        "sort_order": 4,
        "is_active": True,
        "skip": True
    },
    {
        "slug": "professor-bee",
        "name": "Professor Bee",
        "description": "Wise and knowledgeable! The scholarly bee.",
        "category": "profession",
        "folder_path": "professor-bee",
        "obj_file": "ProfessorBee.obj",
        "mtl_file": "ProfessorBee.mtl",
        "texture_file": "ProfessorBee.png",
        "thumbnail_file": "ProfessorBee!.png",
        "sort_order": 5,
        "is_active": True,
        "skip": True
    },
    {
        "slug": "rocker-bee",
        "name": "Rocker Bee",
        "description": "Rock and roll! Music-loving bee with attitude.",
        "category": "entertainment",
        "folder_path": "rocker-bee",
        "obj_file": "RockerBee.obj",
        "mtl_file": "RockerBee.mtl",
        "texture_file": "RockerBee.png",
        "thumbnail_file": "RockerBee!.png",
        "sort_order": 6,
        "is_active": True,
        "skip": True
    },
    {
        "slug": "vamp-bee",
        "name": "Vamp Bee",
        "description": "Spooky vampire bee! Perfect for Halloween.",
        "category": "fantasy",
        "folder_path": "vamp-bee",
        "obj_file": "VampBee.obj",
        "mtl_file": "VampBee.mtl",
        "texture_file": "VampBee.png",
        "thumbnail_file": "VampBee!.png",
        "sort_order": 7,
        "is_active": True,
        "skip": True
    },
    {
        "slug": "ware-bee",
        "name": "Ware Bee",
        "description": "Howling good at spelling! Werewolf bee.",
        "category": "fantasy",
        "folder_path": "ware-bee",
        "obj_file": "WareBee.obj",
        "mtl_file": "WareBee.mtl",
        "texture_file": "WareBee.png",
        "thumbnail_file": "WareBee!.png",
        "sort_order": 8,
        "is_active": True,
        "skip": True
    },
    {
        "slug": "zom-bee",
        "name": "Zom Bee",
        "description": "Brainy zombie bee! Loves learning words.",
        "category": "fantasy",
        "folder_path": "zom-bee",
        "obj_file": "ZomBee.obj",
        "mtl_file": "ZomBee.mtl",
        "texture_file": "ZomBee.png",
        "thumbnail_file": "ZomBee!.png",
        "sort_order": 9,
        "is_active": True,
        "skip": True
    },
    
    # 6 NEW GLB avatars
    {
        "slug": "astro-bee",
        "name": "Astro Bee",
        "description": "Space explorer bee! Ready for cosmic spelling adventures.",
        "category": "adventure",
        "folder_path": "glb_files",
        "obj_file": "AstroBee.glb",
        "mtl_file": None,
        "texture_file": None,
        "thumbnail_file": "AvatarThumbnails/AstroBee!.png",
        "sort_order": 10,
        "is_active": True
    },
    {
        "slug": "biker-bee",
        "name": "Biker Bee",
        "description": "Cool biker bee with attitude!",
        "category": "fun",
        "folder_path": "glb_files",
        "obj_file": "BrotherBee.glb",
        "mtl_file": None,
        "texture_file": None,
        "thumbnail_file": "AvatarThumbnails/BrotherBee!.png",
        "sort_order": 11,
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
        "sort_order": 12,
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
        "sort_order": 13,
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
        "sort_order": 14,
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
        "sort_order": 15,
        "is_active": True
    },
    {
        "slug": "diva-bee",
        "name": "Diva Bee",
        "description": "Fabulous and glamorous diva bee!",
        "category": "entertainment",
        "folder_path": "glb_files",
        "obj_file": "DivaBee.glb",
        "mtl_file": None,
        "texture_file": None,
        "thumbnail_file": "AvatarThumbnails/DoctorBee!.png",
        "sort_order": 16,
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
        "sort_order": 17,
        "is_active": True
    },
    {
        "slug": "explorer-bee",
        "name": "Explorer Bee",
        "description": "Adventure explorer bee discovering new words!",
        "category": "adventure",
        "folder_path": "glb_files",
        "obj_file": "ExplorerBee.glb",
        "mtl_file": None,
        "texture_file": None,
        "thumbnail_file": "AvatarThumbnails/DetectiveBee!.png",
        "sort_order": 18,
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
        "sort_order": 19,
        "is_active": True
    },
    {
        "slug": "knight-bee",
        "name": "Knight Bee",
        "description": "Brave knight bee defending the spelling realm!",
        "category": "fantasy",
        "folder_path": "glb_files",
        "obj_file": "QueenBee.glb",
        "mtl_file": None,
        "texture_file": None,
        "thumbnail_file": "AvatarThumbnails/KnightBee!.png",
        "sort_order": 20,
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
        "sort_order": 21,
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
        "sort_order": 22,
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
        "sort_order": 23,
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
        "sort_order": 24,
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
        "thumbnail_file": "AvatarThumbnails/AstroBee!.png",
        "sort_order": 25,
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
        "sort_order": 26,
        "is_active": True
    }
]

with app.app_context():
    added = 0
    updated = 0
    for avatar_data in ALL_GLB_AVATARS:
        skip = avatar_data.pop("skip", False)
        existing = Avatar.query.filter_by(slug=avatar_data["slug"]).first()
        
        if existing:
            if skip:
                print(f"⏭️  Skipping {avatar_data['slug']} (keeping OBJ)")
                continue
            # Update existing avatar to use GLB
            for key, value in avatar_data.items():
                setattr(existing, key, value)
            print(f"🔄 Updated: {avatar_data['slug']} to GLB")
            updated += 1
        else:
            # Create new avatar
            avatar = Avatar(**avatar_data)
            db.session.add(avatar)
            print(f"➕ Added: {avatar_data['slug']}")
            added += 1
    
    db.session.commit()
    print(f"\n✅ Added {added} new avatars, Updated {updated} to GLB format!")
    
    # Show all avatars
    all_avatars = Avatar.query.filter_by(is_active=True).order_by(Avatar.sort_order).all()
    print(f"\n📋 Total active avatars: {len(all_avatars)}")
    for a in all_avatars:
        format_type = "OBJ" if a.obj_file.endswith('.obj') else "GLB"
        print(f"  - {a.slug}: {a.name} [{format_type}]")
