#!/usr/bin/env python3
"""
Create a test user for local development and avatar testing
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import get_config
from models import db, User

def create_test_user():
    """Create a test user for local development"""
    print("\n🐝 Creating Test User for Local Development")
    print("=" * 60)
    
    app = Flask(__name__)
    app.config.from_object(get_config())
    db.init_app(app)
    
    with app.app_context():
        try:
            # Check if BigDaddy2 already exists
            existing_user = User.query.filter_by(username='BigDaddy2').first()
            if existing_user:
                print("✅ BigDaddy2 user already exists!")
                print(f"   Username: {existing_user.username}")
                print(f"   Email: {existing_user.email}")
                print(f"   Role: {existing_user.role}")
                print(f"   Display Name: {existing_user.display_name}")
                return True
            
            # Create new test user
            print("🔧 Creating BigDaddy2 test user...")
            
            test_user = User(
                username='BigDaddy2',
                email='bigdaddy2@beesmart.test',
                display_name='Test Admin',
                role='admin',  # Give admin role for full access
                grade_level='Adult',
                school_name='BeeSmart Test School',
                is_active=True,
                email_verified=True
            )
            
            # Set password
            test_user.set_password('Aja123!!')
            
            # Add to database
            db.session.add(test_user)
            db.session.commit()
            
            print("✅ Test user created successfully!")
            print("\n📋 Login Credentials:")
            print("   Username: BigDaddy2")
            print("   Password: Aja123!!")
            print("   Role: admin")
            print("   Email: bigdaddy2@beesmart.test")
            
            print("\n🚀 You can now:")
            print("   1. Go to http://127.0.0.1:5000/auth/login")
            print("   2. Login with the credentials above")
            print("   3. Test avatar picker at /test/avatar-picker")
            print("   4. Test avatar selection and grid rendering")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating test user: {e}")
            db.session.rollback()
            return False

def create_additional_test_users():
    """Create additional test users for different roles"""
    print("\n🔧 Creating additional test users...")
    
    app = Flask(__name__)
    app.config.from_object(get_config())
    db.init_app(app)
    
    test_users = [
        {
            'username': 'student1',
            'email': 'student1@beesmart.test',
            'password': 'test123',
            'display_name': 'Test Student',
            'role': 'student',
            'grade_level': '3rd Grade'
        },
        {
            'username': 'teacher1',
            'email': 'teacher1@beesmart.test', 
            'password': 'test123',
            'display_name': 'Test Teacher',
            'role': 'teacher',
            'grade_level': 'Adult'
        }
    ]
    
    with app.app_context():
        try:
            for user_data in test_users:
                # Check if user exists
                existing = User.query.filter_by(username=user_data['username']).first()
                if existing:
                    print(f"   ✅ {user_data['username']} already exists")
                    continue
                
                # Create user
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    display_name=user_data['display_name'],
                    role=user_data['role'],
                    grade_level=user_data['grade_level'],
                    school_name='BeeSmart Test School',
                    is_active=True,
                    email_verified=True
                )
                
                user.set_password(user_data['password'])
                db.session.add(user)
                print(f"   ✅ Created {user_data['username']} ({user_data['role']})")
            
            db.session.commit()
            print("✅ Additional test users created!")
            
        except Exception as e:
            print(f"❌ Error creating additional users: {e}")
            db.session.rollback()

if __name__ == "__main__":
    print("🐝 BeeSmart Test User Setup")
    
    success = create_test_user()
    
    if success:
        # Ask if user wants additional test accounts
        print("\n❓ Create additional test users (student1, teacher1)?")
        response = input("Type 'yes' to create them: ").strip().lower()
        
        if response == 'yes':
            create_additional_test_users()
    
    print("\n🎉 Setup complete! Your local app now has test users for avatar testing.")