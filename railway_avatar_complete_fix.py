#!/usr/bin/env python3
"""
Complete avatar database fix for Railway deployment
- Deletes 15 broken avatars (files don't exist)
- Fixes filenames for 9 working avatars
"""
from AjaSpellBApp import app, db
from models import Avatar, User

# List of broken avatars to DELETE (files don't exist)
BROKEN_AVATARS = [
    'astro-bee', 'biker-bee', 'brother-bee', 'builder-bee', 'cool-bee',
    'detective-bee', 'diva-bee', 'doctor-bee', 'explorer-bee', 'franken-bee',
    'knight-bee', 'queen-bee', 'robo-bee', 'seabea', 'superbee'
]

# Complete mapping for the 9 WORKING avatars
AVATAR_FIXES = {
    'al-bee': {
        'obj_file': 'AlBee.obj',
        'mtl_file': 'AlBee.mtl',
        'texture_file': 'AlBee.png',
        'thumbnail_file': 'AlBee!.png'
    },
    'anxious-bee': {
        'obj_file': 'AnxiousBee.obj',
        'mtl_file': 'AnxiousBee.mtl',
        'texture_file': 'AnxiousBee.png',
        'thumbnail_file': 'AnxiousBee!.png'
    },
    'mascot-bee': {
        'obj_file': 'MascotBee.obj',
        'mtl_file': 'MascotBee.mtl',
        'texture_file': 'MascotBee.png',
        'thumbnail_file': 'MascotBee!.png'
    },
    'monster-bee': {
        'obj_file': 'MonsterBee.obj',
        'mtl_file': 'MonsterBee.mtl',
        'texture_file': 'MonsterBee.png',
        'thumbnail_file': 'MonsterBee!.png'
    },
    'professor-bee': {
        'obj_file': 'ProfessorBee.obj',
        'mtl_file': 'ProfessorBee.mtl',
        'texture_file': 'ProfessorBee.png',
        'thumbnail_file': 'ProfessorBee!.png'
    },
    'rocker-bee': {
        'obj_file': 'RockerBee.obj',
        'mtl_file': 'RockerBee.mtl',
        'texture_file': 'RockerBee.png',
        'thumbnail_file': 'RockerBee!.png'
    },
    'vamp-bee': {
        'obj_file': 'VampBee.obj',
        'mtl_file': 'VampBee.mtl',
        'texture_file': 'VampBee.png',
        'thumbnail_file': 'VampBee!.png'
    },
    'ware-bee': {
        'obj_file': 'WareBee.obj',
        'mtl_file': 'WareBee.mtl',
        'texture_file': 'WareBee.png',
        'thumbnail_file': 'WareBee!.png'
    },
    'zom-bee': {
        'obj_file': 'ZomBee.obj',
        'mtl_file': 'ZomBee.mtl',
        'texture_file': 'ZomBee.png',
        'thumbnail_file': 'ZomBee!.png'
    }
}

def delete_broken_avatars():
    """Delete avatars with broken/missing files from database"""
    with app.app_context():
        print("🗑️  Deleting broken avatars from database...")
        print("=" * 60)
        
        deleted_count = 0
        for slug in BROKEN_AVATARS:
            avatar = Avatar.query.filter_by(slug=slug).first()
            
            if avatar:
                avatar_id = avatar.id
                avatar_name = avatar.name
                
                # Update users who have this avatar (set to NULL)
                users_updated = User.query.filter_by(avatar_id=avatar_id).update({'avatar_id': None})
                
                # Delete the avatar
                db.session.delete(avatar)
                
                print(f"🗑️  Deleted: {avatar_name} ({slug})")
                if users_updated > 0:
                    print(f"   Updated {users_updated} user(s) to default avatar")
                
                deleted_count += 1
            else:
                print(f"⚠️  Avatar not found (already deleted): {slug}")
        
        # Commit deletions
        db.session.commit()
        
        print("=" * 60)
        print(f"✅ Deleted {deleted_count} broken avatars")
        print("=" * 60)

def fix_avatars():
    """Fix all avatar file references in database"""
    with app.app_context():
        print("🔧 Fixing avatar file references in database...")
        print("=" * 60)
        
        updated_count = 0
        for slug, fixes in AVATAR_FIXES.items():
            avatar = Avatar.query.filter_by(slug=slug).first()
            
            if not avatar:
                print(f"⚠️  Avatar not found: {slug}")
                continue
            
            # Update all file fields
            avatar.obj_file = fixes['obj_file']
            avatar.mtl_file = fixes['mtl_file']
            avatar.texture_file = fixes['texture_file']
            avatar.thumbnail_file = fixes['thumbnail_file']
            
            print(f"✅ {avatar.name} ({slug})")
            print(f"   OBJ: {fixes['obj_file']}")
            print(f"   MTL: {fixes['mtl_file']}")
            print(f"   TEX: {fixes['texture_file']}")
            print(f"   THUMB: {fixes['thumbnail_file']}")
            
            updated_count += 1
        
        # Commit all changes
        db.session.commit()
        
        print("=" * 60)
        print(f"✅ Successfully updated {updated_count} avatars!")
        print("=" * 60)

if __name__ == '__main__':
    # First delete broken avatars, then fix the remaining ones
    delete_broken_avatars()
    fix_avatars()
