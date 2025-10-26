#!/usr/bin/env python3
"""
Verify that the thumbnail filename fix worked
"""
from AjaSpellBApp import app
from models import Avatar

def verify_database_fix():
    """Verify that the database thumbnail filenames are correct"""
    with app.app_context():
        # Check a few specific avatars in the database
        test_avatars = ['al-bee', 'anxious-bee', 'mascot-bee', 'rocker-bee', 'monster-bee']
        
        print('🔍 Checking thumbnail filenames in database after fix:')
        
        fixed_count = 0
        total_count = 0
        
        for slug in test_avatars:
            total_count += 1
            avatar = Avatar.query.filter_by(slug=slug).first()
            if avatar:
                print(f'✅ {slug}: {avatar.thumbnail_file}')
                
                # Check if filename has spaces (should not)
                if ' ' in avatar.thumbnail_file:
                    print(f'   ⚠️ Still has spaces!')
                else:
                    print(f'   ✅ No spaces - looks correct')
                    fixed_count += 1
            else:
                print(f'❌ {slug}: not found in database')
        
        print(f'\n📊 Summary: {fixed_count}/{total_count} avatars have correct filenames')
        
        # Check all avatars in database
        all_avatars = Avatar.query.all()
        space_issues = []
        
        for avatar in all_avatars:
            if ' ' in avatar.thumbnail_file:
                space_issues.append(f"{avatar.slug}: {avatar.thumbnail_file}")
        
        if space_issues:
            print(f"\n⚠️ Found {len(space_issues)} avatars with spaces in thumbnail filenames:")
            for issue in space_issues:
                print(f"   {issue}")
        else:
            print(f"\n🎉 All {len(all_avatars)} avatars have correct thumbnail filenames (no spaces)!")

if __name__ == "__main__":
    verify_database_fix()