#!/usr/bin/env python3
"""
DELETE all files and database entries for broken avatars
This will completely remove the 15 non-working avatars
"""
from AjaSpellBApp import app, db
from models import Avatar
import os
import shutil

# List of broken avatars to DELETE
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

def delete_broken_avatars():
    """Delete all files and database records for broken avatars"""
    with app.app_context():
        print("=" * 80)
        print("🗑️  DELETING BROKEN AVATARS - THIS CANNOT BE UNDONE!")
        print("=" * 80)
        
        deleted_count = 0
        
        for slug in BROKEN_AVATARS:
            avatar = Avatar.query.filter_by(slug=slug).first()
            
            if not avatar:
                print(f"⚠️  Avatar not found in database: {slug}")
                continue
            
            folder_path = f"static/assets/avatars/{avatar.folder_path}"
            
            # Delete folder and all files
            if os.path.exists(folder_path):
                try:
                    shutil.rmtree(folder_path)
                    print(f"🗑️  Deleted folder: {folder_path}")
                except Exception as e:
                    print(f"❌ Error deleting folder {folder_path}: {e}")
            else:
                print(f"⚠️  Folder not found: {folder_path}")
            
            # Delete database entry
            try:
                db.session.delete(avatar)
                print(f"🗑️  Deleted database entry: {avatar.name} ({slug})")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Error deleting database entry for {slug}: {e}")
        
        # Commit all deletions
        db.session.commit()
        
        print("=" * 80)
        print(f"✅ Successfully deleted {deleted_count} broken avatars")
        print("=" * 80)
        print("\nRemaining working avatars:")
        remaining = Avatar.query.order_by(Avatar.name).all()
        for a in remaining:
            print(f"  ✅ {a.name} ({a.slug})")
        print(f"\nTotal remaining: {len(remaining)} avatars")

if __name__ == '__main__':
    confirm = input("\n⚠️  WARNING: This will permanently delete 15 avatars and all their files.\nType 'DELETE' to confirm: ")
    if confirm == 'DELETE':
        delete_broken_avatars()
    else:
        print("❌ Cancelled - nothing was deleted")
