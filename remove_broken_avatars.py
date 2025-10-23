#!/usr/bin/env python3
"""
Remove all files and database entries for broken avatars
"""
from AjaSpellBApp import app, db
from models import Avatar
import os
import shutil

# List of broken avatars to completely remove
BROKEN_AVATARS = [
    'astro-bee',
    'biker-bee',
    'brother-bee',
    'builder-bee',
    'cool-bee',
    'detective-bee',
    'diva-bee',
    'doctor-bee',
    'explorer-bee',
    'franken-bee',
    'knight-bee',
    'queen-bee',
    'robo-bee',
    'seabea',
    'superbee'
]

def remove_broken_avatars():
    """Remove all files and deactivate broken avatars in database"""
    with app.app_context():
        print("🗑️  Removing broken avatars...")
        print("=" * 60)
        
        for slug in BROKEN_AVATARS:
            avatar = Avatar.query.filter_by(slug=slug).first()
            
            if not avatar:
                print(f"⚠️  Avatar not found in database: {slug}")
                continue
            
            folder_path = f"static/assets/avatars/{avatar.folder_path}"
            
            # Delete entire folder
            if os.path.exists(folder_path):
                try:
                    shutil.rmtree(folder_path)
                    print(f"✅ Deleted folder: {folder_path}")
                except Exception as e:
                    print(f"❌ Error deleting {folder_path}: {e}")
            else:
                print(f"⚠️  Folder not found: {folder_path}")
            
            # Deactivate in database (don't delete, just hide)
            avatar.is_active = False
            print(f"✅ Deactivated: {avatar.name} ({slug})")
        
        # Commit all changes
        db.session.commit()
        
        print("=" * 60)
        print(f"✅ Removed {len(BROKEN_AVATARS)} broken avatars!")
        print("=" * 60)
        
        # Show remaining active avatars
        active = Avatar.query.filter_by(is_active=True).count()
        print(f"📊 Remaining active avatars: {active}")

if __name__ == '__main__':
    remove_broken_avatars()
