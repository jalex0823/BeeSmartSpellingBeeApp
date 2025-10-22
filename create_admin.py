#!/usr/bin/env python3
"""
Create or promote admin user for BeeSmart app
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from AjaSpellBApp import app, db, User
from werkzeug.security import generate_password_hash
import uuid

def list_users():
    """List all existing users"""
    with app.app_context():
        users = User.query.all()
        print(f"\n👥 Found {len(users)} users:")
        for user in users:
            print(f"   {user.id}: {user.username} ({user.email}) - Role: {user.role}")
        return users

def promote_user_to_admin(user_id):
    """Promote existing user to admin"""
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            print(f"❌ User with ID {user_id} not found")
            return False
            
        user.role = 'admin'
        # Ensure admin has a teacher key for managing students
        if not user.teacher_key:
            user.teacher_key = f"ADMIN_{user.username.upper()}"
            
        db.session.commit()
        print(f"✅ Promoted {user.username} to admin with teacher key: {user.teacher_key}")
        return True

def create_admin_user():
    """Create a new admin user"""
    with app.app_context():
        # Check if BigDaddy already exists
        existing = User.query.filter_by(username='BigDaddy').first()
        if existing:
            print(f"⚠️  User 'BigDaddy' already exists with role: {existing.role}")
            choice = input("Promote to admin? (y/n): ").lower()
            if choice == 'y':
                return promote_user_to_admin(existing.id)
            return False
            
        # Create new admin user
        admin_password = "AdminPass123!"  # You should change this
        
        new_admin = User(
            uuid=str(uuid.uuid4()),
            username='BigDaddy',
            display_name='BigDaddy Admin',
            email='admin@beesmartapp.com',
            password_hash=generate_password_hash(admin_password),
            role='admin',
            teacher_key='ADMIN_BIGDADDY',
            is_active=True,
            email_verified=True
        )
        
        db.session.add(new_admin)
        db.session.commit()
        
        print(f"✅ Created admin user:")
        print(f"   Username: BigDaddy")
        print(f"   Email: admin@beesmartapp.com")
        print(f"   Password: {admin_password}")
        print(f"   Teacher Key: ADMIN_BIGDADDY")
        print(f"⚠️  IMPORTANT: Change the password after first login!")
        
        return True

def main():
    print("🐝 BeeSmart Admin User Management")
    print("=" * 40)
    
    # List existing users
    users = list_users()
    
    if not users:
        print("\n🆕 No users found. Creating admin user...")
        create_admin_user()
        return
    
    print("\nWhat would you like to do?")
    print("1. Create new admin user 'BigDaddy'")
    print("2. Promote existing user to admin")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        create_admin_user()
    elif choice == '2':
        try:
            user_id = int(input("Enter user ID to promote: "))
            promote_user_to_admin(user_id)
        except ValueError:
            print("❌ Invalid user ID")
    elif choice == '3':
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()