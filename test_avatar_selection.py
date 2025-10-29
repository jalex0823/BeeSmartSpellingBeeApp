"""
Test script to verify avatar selection saves to user profile
"""
from AjaSpellBApp import app, db
from models import User, Avatar

def test_avatar_selection():
    """Test that avatar selection properly saves to user profile"""
    with app.app_context():
        # Get first user
        user = User.query.first()
        if not user:
            print("❌ No users found in database")
            return
        
        print(f"\n{'='*60}")
        print(f"Testing Avatar Selection for User: {user.username}")
        print(f"{'='*60}")
        
        # Get current avatar
        print(f"\n📍 Current State:")
        print(f"   Avatar ID: {user.avatar_id}")
        print(f"   Avatar Variant: {user.avatar_variant}")
        print(f"   Preferences: {user.preferences}")
        
        # Get an avatar to test with
        test_avatar = Avatar.query.filter_by(is_active=True).first()
        if not test_avatar:
            print("❌ No active avatars found")
            return
        
        print(f"\n🧪 Testing Selection:")
        print(f"   Attempting to select: {test_avatar.slug} ({test_avatar.name})")
        
        # Test the update_avatar method
        success, message = user.update_avatar(test_avatar.slug, 'default')
        
        if success:
            db.session.commit()
            print(f"✅ Success: {message}")
            
            # Verify the changes
            db.session.refresh(user)
            print(f"\n✅ Updated State:")
            print(f"   Avatar ID: {user.avatar_id}")
            print(f"   Avatar Variant: {user.avatar_variant}")
            print(f"   Avatar Last Updated: {user.avatar_last_updated}")
            print(f"   Preferences: {user.preferences}")
            print(f"   Avatar Selected Flag: {user.preferences.get('avatar_selected', False) if user.preferences else False}")
            
            # Get avatar data
            avatar_data = user.get_avatar_data()
            print(f"\n📊 Avatar Data:")
            print(f"   Name: {avatar_data.get('name')}")
            print(f"   ID: {avatar_data.get('id')}")
            print(f"   Category: {avatar_data.get('category')}")
            
            print(f"\n{'='*60}")
            print("✅ AVATAR SELECTION TEST PASSED")
            print(f"{'='*60}\n")
        else:
            print(f"❌ Failed: {message}")
            db.session.rollback()

if __name__ == "__main__":
    test_avatar_selection()
