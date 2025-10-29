#!/usr/bin/env python3
"""
Initialize GLB avatars in database (runs automatically on startup)
This is idempotent - safe to run multiple times
"""
import os
from AjaSpellBApp import app, db
from models import Avatar

# GLB avatars to ensure exist
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
    }
]

def init_glb_avatars():
    """Initialize GLB avatars - safe to call multiple times"""
    with app.app_context():
        added = 0
        updated = 0
        
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
        
        if added > 0 or updated > 0:
            db.session.commit()
            print(f"✅ GLB Avatars initialized: {added} added, {updated} updated")
        else:
            print(f"✅ GLB Avatars already initialized")

if __name__ == "__main__":
    init_glb_avatars()
