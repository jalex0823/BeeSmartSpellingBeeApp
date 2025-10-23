"""
Railway Avatar Cleanup Script
Run this on Railway to delete the 15 broken avatars from the database
"""
from AjaSpellBApp import app, db
from models import Avatar, User

# List of broken avatars to delete
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

def cleanup_railway_avatars():
    """Delete broken avatars from Railway database"""
    with app.app_context():
        print("\n" + "="*60)
        print("🧹 RAILWAY AVATAR CLEANUP")
        print("="*60)
        
        # Check current avatar count
        total_before = Avatar.query.count()
        active_before = Avatar.query.filter_by(is_active=True).count()
        print(f"\n📊 Before cleanup:")
        print(f"   Total avatars: {total_before}")
        print(f"   Active avatars: {active_before}")
        
        # Find avatars to delete
        avatars_to_delete = Avatar.query.filter(Avatar.slug.in_(BROKEN_AVATARS)).all()
        print(f"\n🔍 Found {len(avatars_to_delete)} avatars to delete:")
        for avatar in avatars_to_delete:
            print(f"   - {avatar.slug}: {avatar.name}")
        
        if not avatars_to_delete:
            print("\n✅ No broken avatars found - database already clean!")
            return
        
        # Get list of avatar IDs to delete
        avatar_ids_to_delete = [a.id for a in avatars_to_delete]
        
        # Update users who have these avatars assigned
        users_updated = User.query.filter(User.avatar_id.in_([a.slug for a in avatars_to_delete])).all()
        print(f"\n👥 Found {len(users_updated)} users with deleted avatars")
        
        for user in users_updated:
            print(f"   - {user.username}: {user.avatar_id} → NULL")
            user.avatar_id = None
        
        # Delete the avatars
        print(f"\n🗑️ Deleting {len(avatars_to_delete)} avatars...")
        for avatar in avatars_to_delete:
            db.session.delete(avatar)
        
        # Commit changes
        try:
            db.session.commit()
            print("\n✅ Database changes committed successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error committing changes: {e}")
            return
        
        # Verify cleanup
        total_after = Avatar.query.count()
        active_after = Avatar.query.filter_by(is_active=True).count()
        print(f"\n📊 After cleanup:")
        print(f"   Total avatars: {total_after}")
        print(f"   Active avatars: {active_after}")
        print(f"   Avatars deleted: {total_before - total_after}")
        print(f"   Users updated: {len(users_updated)}")
        
        # List remaining avatars
        remaining = Avatar.query.filter_by(is_active=True).order_by(Avatar.slug).all()
        print(f"\n✅ Remaining {len(remaining)} active avatars:")
        for avatar in remaining:
            print(f"   - {avatar.slug}: {avatar.name}")
        
        print("\n" + "="*60)
        print("🎉 CLEANUP COMPLETE!")
        print("="*60 + "\n")

if __name__ == "__main__":
    cleanup_railway_avatars()
