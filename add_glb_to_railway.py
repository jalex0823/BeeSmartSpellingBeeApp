"""
Add the 17 new GLB avatars to Railway PostgreSQL database.
"""
import os
import sys

# Set Railway DATABASE_URL  
os.environ['DATABASE_URL'] = 'postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway'

sys.path.insert(0, os.path.dirname(__file__))

from AjaSpellBApp import app, db
from models import Avatar

# 17 new GLB avatars to add to Railway
GLB_AVATARS = [
    {
        "slug": "astro-bee",
        "name": "Astro Bee",
        "description": "An astronaut bee exploring space!",
        "category": "adventure",
        "folder_path": "glb_files",
        "obj_file": "AstroBee.glb",
        "thumbnail_file": "AvatarThumbnails/AstroBee.png",
        "sort_order": 10
    },
    {
        "slug": "biker-bee",
        "name": "Biker Bee",
        "description": "A cool bee on a motorcycle!",
        "category": "sports",
        "folder_path": "glb_files",
        "obj_file": "BikerBee.glb",
        "thumbnail_file": "AvatarThumbnails/BikerBee.png",
        "sort_order": 11
    },
    {
        "slug": "builder-bee",
        "name": "Builder Bee",
        "description": "A hardworking construction bee!",
        "category": "profession",
        "folder_path": "glb_files",
        "obj_file": "BuilderBee.glb",
        "thumbnail_file": "AvatarThumbnails/BuilderBee.png",
        "sort_order": 12
    },
    {
        "slug": "cool-bee",
        "name": "Cutie Bee",
        "description": "An adorable and stylish bee!",
        "category": "classic",
        "folder_path": "glb_files",
        "obj_file": "CoolBee.glb",
        "thumbnail_file": "AvatarThumbnails/CoolBee.png",
        "sort_order": 13
    },
    {
        "slug": "detective-bee",
        "name": "Detective Bee",
        "description": "A mystery-solving bee detective!",
        "category": "profession",
        "folder_path": "glb_files",
        "obj_file": "DetectiveBee.glb",
        "thumbnail_file": "AvatarThumbnails/DetectiveBee.png",
        "sort_order": 14
    },
    {
        "slug": "diva-bee",
        "name": "Diva Bee",
        "description": "A glamorous bee superstar!",
        "category": "entertainment",
        "folder_path": "glb_files",
        "obj_file": "DivaBee.glb",
        "thumbnail_file": "AvatarThumbnails/DivaBee.png",
        "sort_order": 15
    },
    {
        "slug": "doctor-bee",
        "name": "Doctor Bee",
        "description": "A caring medical bee!",
        "category": "profession",
        "folder_path": "glb_files",
        "obj_file": "DoctorBee.glb",
        "thumbnail_file": "AvatarThumbnails/DoctorBee.png",
        "sort_order": 16
    },
    {
        "slug": "explorer-bee",
        "name": "Explorer Bee",
        "description": "An adventurous exploring bee!",
        "category": "adventure",
        "folder_path": "glb_files",
        "obj_file": "ExplorerBee.glb",
        "thumbnail_file": "AvatarThumbnails/ExplorerBee.png",
        "sort_order": 17
    },
    {
        "slug": "franken-bee",
        "name": "Franken Bee",
        "description": "A spooky Frankenstein bee!",
        "category": "fantasy",
        "folder_path": "glb_files",
        "obj_file": "Frankenbee.glb",
        "thumbnail_file": "AvatarThumbnails/Frankenbee.png",
        "sort_order": 18
    },
    {
        "slug": "knight-bee",
        "name": "Knight Bee",
        "description": "A brave medieval knight bee!",
        "category": "fantasy",
        "folder_path": "glb_files",
        "obj_file": "KnightBee.glb",
        "thumbnail_file": "AvatarThumbnails/KnightBee.png",
        "sort_order": 19
    },
    {
        "slug": "motorcycle-bee",
        "name": "Motorcycle Bee",
        "description": "A bee riding a motorcycle!",
        "category": "sports",
        "folder_path": "glb_files",
        "obj_file": "MotorcycleBee.glb",
        "thumbnail_file": "AvatarThumbnails/MotorcycleBee.png",
        "sort_order": 20
    },
    {
        "slug": "queen-bee",
        "name": "Queen Bee Majesty",
        "description": "The royal queen of all bees!",
        "category": "classic",
        "folder_path": "glb_files",
        "obj_file": "QueenBee.glb",
        "thumbnail_file": "AvatarThumbnails/QueenBee.png",
        "sort_order": 21
    },
    {
        "slug": "robo-bee",
        "name": "Robo Bee",
        "description": "A high-tech robot bee!",
        "category": "fantasy",
        "folder_path": "glb_files",
        "obj_file": "RoboBee.glb",
        "thumbnail_file": "AvatarThumbnails/RoboBee.png",
        "sort_order": 22
    },
    {
        "slug": "sea-bee",
        "name": "Sea Bee",
        "description": "An underwater diving bee!",
        "category": "adventure",
        "folder_path": "glb_files",
        "obj_file": "Seabea.glb",
        "thumbnail_file": "AvatarThumbnails/Seabea.png",
        "sort_order": 23
    },
    {
        "slug": "space-bee",
        "name": "Space Bee Explorer",
        "description": "A bee exploring the cosmos!",
        "category": "adventure",
        "folder_path": "glb_files",
        "obj_file": "SpaceBee.glb",
        "thumbnail_file": "AvatarThumbnails/SpaceBee.png",
        "sort_order": 24
    },
    {
        "slug": "super-bee",
        "name": "Super Bee Hero",
        "description": "A superhero bee saving the day!",
        "category": "fantasy",
        "folder_path": "glb_files",
        "obj_file": "Superbee.glb",
        "thumbnail_file": "AvatarThumbnails/Superbee.png",
        "sort_order": 25
    },
    {
        "slug": "cutie-bee",
        "name": "Cutie Bee",
        "description": "The cutest bee around!",
        "category": "classic",
        "folder_path": "glb_files",
        "obj_file": "CutieBee.glb",
        "thumbnail_file": "AvatarThumbnails/CutieBee.png",
        "sort_order": 26
    }
]

def main():
    with app.app_context():
        print("=" * 70)
        print("🚂 Adding GLB Avatars to Railway PostgreSQL")
        print("=" * 70)
        
        print(f"\n📊 Will add {len(GLB_AVATARS)} GLB avatars to Railway\n")
        
        added_count = 0
        skipped_count = 0
        
        for glb_data in GLB_AVATARS:
            # Check if already exists
            existing = Avatar.query.filter_by(slug=glb_data['slug']).first()
            
            if existing:
                print(f"⏭️  Skipped: {glb_data['slug']} (already exists)")
                skipped_count += 1
                continue
            
            # Create new avatar
            new_avatar = Avatar(
                slug=glb_data['slug'],
                name=glb_data['name'],
                description=glb_data['description'],
                category=glb_data['category'],
                folder_path=glb_data['folder_path'],
                obj_file=glb_data['obj_file'],
                mtl_file=None,
                texture_file=None,
                thumbnail_file=glb_data['thumbnail_file'],
                unlock_level=1,
                points_required=0,
                is_premium=False,
                sort_order=glb_data['sort_order'],
                is_active=True
            )
            
            try:
                db.session.add(new_avatar)
                print(f"✅ Added: {glb_data['slug']} - {glb_data['name']}")
                added_count += 1
            except Exception as e:
                print(f"❌ Error adding {glb_data['slug']}: {e}")
        
        # Commit changes
        if added_count > 0:
            print(f"\n💾 Committing {added_count} new avatars to Railway...")
            try:
                db.session.commit()
                print(f"✅ Successfully added {added_count} GLB avatars to Railway!")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error committing: {e}")
                return
        
        print("\n" + "=" * 70)
        print("📊 Final Railway Database State:")
        print("-" * 70)
        
        all_avatars = Avatar.query.all()
        obj_count = len([a for a in all_avatars if a.obj_file and a.obj_file.endswith('.obj')])
        glb_count = len([a for a in all_avatars if a.obj_file and a.obj_file.endswith('.glb')])
        
        print(f"   Total: {len(all_avatars)} avatars")
        print(f"   OBJ format: {obj_count}")
        print(f"   GLB format: {glb_count}")
        print(f"   Active: {len([a for a in all_avatars if a.is_active])}")
        
        print("\n✅ Railway database updated! 🎉")

if __name__ == '__main__':
    main()
