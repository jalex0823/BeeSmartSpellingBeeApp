#!/usr/bin/env python3
"""
Quick script to check a user's permission fields in the database.
Usage: python check_user_permissions.py <username>
"""

import sys
from AjaSpellBApp import app, db
from models import User

def check_user(username):
    """Check user's permission-related fields"""
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"❌ User '{username}' not found!")
            return
        
        print(f"\n🔍 User: {user.username} (ID: {user.id})")
        print(f"   Display Name: {user.display_name}")
        print(f"   Email: {user.email}")
        print(f"   Role: {user.role}")
        print(f"   admin_all_access: {user.admin_all_access}")
        print(f"   premium_member: {user.premium_member}")
        print(f"   honey_points: {user.honey_points}")
        print(f"   purchased_avatars: {user.purchased_avatars}")
        print(f"\n🧮 is_admin_or_premium() = {user.is_admin_or_premium()}")
        
        # Check what should unlock all avatars
        if user.role == 'admin':
            print("   ✅ Has admin role")
        if user.admin_all_access:
            print("   ✅ Has admin_all_access flag")
        if user.premium_member:
            print("   ✅ Has premium_member flag")
        
        if not user.is_admin_or_premium():
            print("   ℹ️ This user should see locked avatars")
        else:
            print("   ⚠️ This user has full avatar access!")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python check_user_permissions.py <username>")
        sys.exit(1)
    
    username = sys.argv[1]
    check_user(username)
