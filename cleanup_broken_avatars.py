"""
Cleanup Broken Avatars from Database
Removes all non-working avatars and resets affected users to al-bee (default)
"""

from AjaSpellBApp import app, db
from models import Avatar, User
from avatar_catalog import AVATAR_CATALOG

# List of 9 working avatars to keep
WORKING_AVATARS = [
    'al-bee',
    'anxious-bee',
    'mascot-bee',
    'monster-bee',
    'professor-bee',
    'rocker-bee',
    'vamp-bee',
    'ware-bee',
    'zom-bee'
]

# List of broken avatars to remove (these render as white blobs or are incomplete)
BROKEN_AVATARS = [
    'builder-bee',
    'buzzbot-bee',
    'buzzhero-bee',
    'detective-bee',
    'doctor-bee',
    'explorer-bee',
    'franken-bee',
    'frankenbee',
    'knight-bee',
    'motorcyclebuzz-bee',
    'motorcyclebuzzbee',
    'queen-bee',
    'queenbeemajesty',
    'sea-bee',
    'seabee',
    'space-bee',
    'spacebeeexplorer',
    'super-bee',
    'superbeehero',
    'bee-diva',
    'diva-bee',
    'astro-bee',
    'biker-bee',
    'brother-bee',
    'cool-bee',
    'robot-bee',
    'robo-bee',
    'buzzbot',
    'buzzhero'
]

DEFAULT_AVATAR = 'al-bee'


def cleanup_broken_avatars():
    """Remove broken avatars from database and reset affected users"""
    
    with app.app_context():
        print("🐝 BeeSmart Avatar Cleanup")
        print("=" * 70)
        print(f"✅ Working avatars to keep: {len(WORKING_AVATARS)}")
        print(f"❌ Broken avatars to remove: {len(BROKEN_AVATARS)}")
        print()
        
        # Step 1: Find all broken avatars in database
        broken_in_db = Avatar.query.filter(Avatar.slug.in_(BROKEN_AVATARS)).all()
        print(f"📊 Found {len(broken_in_db)} broken avatars in database:")
        for avatar in broken_in_db:
            print(f"   - {avatar.name} ({avatar.slug})")
        print()
        
        # Step 2: Find users with broken avatars
        users_with_broken = User.query.filter(User.avatar_id.in_(BROKEN_AVATARS)).all()
        print(f"👥 Found {len(users_with_broken)} users with broken avatars:")
        for user in users_with_broken:
            print(f"   - {user.username} (ID: {user.id}) has {user.avatar_id}")
        print()
        
        # Step 3: Reset users to default avatar
        if users_with_broken:
            print(f"🔧 Resetting {len(users_with_broken)} users to default avatar ({DEFAULT_AVATAR})...")
            for user in users_with_broken:
                old_avatar = user.avatar_id
                user.avatar_id = DEFAULT_AVATAR
                print(f"   ✓ {user.username}: {old_avatar} → {DEFAULT_AVATAR}")
            db.session.commit()
            print("✅ User avatars reset successfully\n")
        
        # Step 4: Delete broken avatars from database
        if broken_in_db:
            print(f"🗑️  Deleting {len(broken_in_db)} broken avatars from database...")
            for avatar in broken_in_db:
                print(f"   🗑️  Deleting {avatar.name} ({avatar.slug})")
                db.session.delete(avatar)
            db.session.commit()
            print("✅ Broken avatars deleted successfully\n")
        
        # Step 5: Verify only working avatars remain
        remaining_avatars = Avatar.query.all()
        print(f"📋 Remaining avatars in database: {len(remaining_avatars)}")
        for avatar in remaining_avatars:
            status = "✅" if avatar.slug in WORKING_AVATARS else "⚠️ "
            print(f"   {status} {avatar.name} ({avatar.slug})")
        print()
        
        # Step 6: Check for any avatars not in working list
        non_working_remaining = [a for a in remaining_avatars if a.slug not in WORKING_AVATARS]
        if non_working_remaining:
            print(f"⚠️  WARNING: {len(non_working_remaining)} unexpected avatars still in database:")
            for avatar in non_working_remaining:
                print(f"   ⚠️  {avatar.name} ({avatar.slug})")
            print("   Consider adding these to BROKEN_AVATARS list if they don't work.\n")
        
        # Step 7: Ensure all working avatars are in database
        db_slugs = {a.slug for a in remaining_avatars}
        missing_working = [slug for slug in WORKING_AVATARS if slug not in db_slugs]
        if missing_working:
            print(f"⚠️  WARNING: {len(missing_working)} working avatars missing from database:")
            for slug in missing_working:
                print(f"   ⚠️  {slug}")
            print("   Run migrate_avatars_to_db.py to populate missing avatars.\n")
        
        # Summary
        print("=" * 70)
        print("✨ Cleanup Complete!")
        print(f"   ✅ {len(broken_in_db)} broken avatars removed")
        print(f"   ✅ {len(users_with_broken)} users reset to default avatar")
        print(f"   📊 {len(remaining_avatars)} avatars remain in database")
        print(f"   🎯 Target: {len(WORKING_AVATARS)} working avatars")
        
        if len(remaining_avatars) == len(WORKING_AVATARS) and not non_working_remaining:
            print("\n🎉 SUCCESS: Database contains exactly the 9 working avatars!")
        else:
            print(f"\n⚠️  Database state: {len(remaining_avatars)} avatars (expected: {len(WORKING_AVATARS)})")


if __name__ == '__main__':
    print("\n" + "🐝" * 35)
    print("BeeSmart Broken Avatar Cleanup")
    print("🐝" * 35 + "\n")
    
    response = input("⚠️  This will remove broken avatars and reset affected users. Continue? (yes/no): ")
    if response.lower() == 'yes':
        cleanup_broken_avatars()
    else:
        print("❌ Cleanup cancelled")
