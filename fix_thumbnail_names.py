#!/usr/bin/env python3
"""
Fix thumbnail filename mismatch in database
The database contains incorrect thumbnail filenames like "Al Bee!.png" 
while actual files are named "AlBee!.png"
"""

import os
import sys
from AjaSpellBApp import app, db
from models import Avatar
from avatar_catalog import get_avatar_info

def fix_thumbnail_names():
    """Fix thumbnail filename mismatch between database and filesystem"""
    with app.app_context():
        print("🔧 Fixing thumbnail filename mismatch...")
        
        # Get all avatars from database
        avatars = Avatar.query.all()
        print(f"Found {len(avatars)} avatars in database")
        
        fixed_count = 0
        errors = []
        
        for avatar in avatars:
            try:
                # Get correct filename from avatar_catalog
                info = get_avatar_info(avatar.slug)
                # Extract filename from thumbnail_url (e.g., "/static/assets/avatars/al-bee/AlBee!.png" -> "AlBee!.png")
                thumbnail_url = info['thumbnail_url']
                correct_thumbnail = thumbnail_url.split('/')[-1]
                current_thumbnail = avatar.thumbnail_file
                
                if current_thumbnail != correct_thumbnail:
                    print(f"🔄 Fixing {avatar.slug}:")
                    print(f"   Current: {current_thumbnail}")
                    print(f"   Correct: {correct_thumbnail}")
                    
                    # Update database record
                    avatar.thumbnail_file = correct_thumbnail
                    fixed_count += 1
                else:
                    print(f"✅ {avatar.slug}: already correct ({current_thumbnail})")
                    
            except Exception as e:
                error_msg = f"❌ Error fixing {avatar.slug}: {e}"
                print(error_msg)
                errors.append(error_msg)
        
        if fixed_count > 0:
            try:
                db.session.commit()
                print(f"✅ Successfully fixed {fixed_count} thumbnail filenames")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Failed to commit changes: {e}")
                return False
        else:
            print("ℹ️ No fixes needed - all thumbnail filenames are correct")
        
        if errors:
            print(f"⚠️ {len(errors)} errors occurred:")
            for error in errors:
                print(f"   {error}")
        
        return True

def verify_fix():
    """Verify that the fix worked by checking a few key avatars"""
    with app.app_context():
        print("\n🔍 Verifying fix...")
        
        test_slugs = ['al-bee', 'anxious-bee', 'bee-diva', 'boss-bee', 'busy-bee']
        
        for slug in test_slugs:
            avatar = Avatar.query.filter_by(slug=slug).first()
            if avatar:
                info = get_avatar_info(slug)
                # Extract filename from thumbnail_url
                thumbnail_url = info['thumbnail_url']
                expected = thumbnail_url.split('/')[-1]
                actual = avatar.thumbnail_file
                
                if actual == expected:
                    print(f"✅ {slug}: {actual}")
                else:
                    print(f"❌ {slug}: expected '{expected}', got '{actual}'")
            else:
                print(f"⚠️ {slug}: not found in database")

if __name__ == "__main__":
    print("🐝 BeeSmart Avatar Thumbnail Filename Fix")
    print("=" * 50)
    
    # Show current state first
    print("\n📊 Current state check:")
    verify_fix()
    
    # Ask for confirmation
    print("\n🔧 Ready to fix thumbnail filenames in database?")
    response = input("Type 'yes' to proceed: ").strip().lower()
    
    if response != 'yes':
        print("❌ Fix cancelled by user")
        sys.exit(0)
    
    # Perform the fix
    print("\n🚀 Starting fix...")
    success = fix_thumbnail_names()
    
    if success:
        print("\n🎉 Fix completed! Verifying results...")
        verify_fix()
        
        print("\n✅ Thumbnail filename fix complete!")
        print("The avatar grid should now render properly.")
    else:
        print("\n❌ Fix failed. Please check the errors above.")
        sys.exit(1)