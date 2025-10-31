#!/usr/bin/env python
"""
Setup Admin User Script
This script sets up an admin user account with all necessary privileges.
"""

import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from AjaSpellBApp import app, db
from models import User

def migrate_database():
    """Add new monetization columns to the database"""
    with app.app_context():
        print("\n🔧 Checking database schema...")
        
        # Get database path/URL
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        is_postgres = 'postgresql://' in db_uri
        
        print(f"   Database: {'PostgreSQL (Railway)' if is_postgres else 'SQLite (Local)'}")
        
        try:
            # Use SQLAlchemy to add columns (works for both SQLite and PostgreSQL)
            from sqlalchemy import text
            
            # Define new columns
            new_columns = {
                'honey_points': 'INTEGER DEFAULT 0',
                'purchased_avatars': 'TEXT DEFAULT \'[]\'',
                'purchased_bundles': 'TEXT DEFAULT \'[]\'',
                'premium_member': 'BOOLEAN DEFAULT FALSE' if is_postgres else 'BOOLEAN DEFAULT 0',
                'admin_all_access': 'BOOLEAN DEFAULT FALSE' if is_postgres else 'BOOLEAN DEFAULT 0'
            }
            
            added = []
            skipped = []
            
            for column_name, column_def in new_columns.items():
                try:
                    with db.engine.connect() as conn:
                        # Try to add the column
                        sql = text(f"ALTER TABLE users ADD COLUMN {column_name} {column_def}")
                        conn.execute(sql)
                        conn.commit()
                        print(f"   ✅ Added column: {column_name}")
                        added.append(column_name)
                except Exception as e:
                    if 'already exists' in str(e).lower() or 'duplicate column' in str(e).lower():
                        print(f"   ✓ Column exists: {column_name}")
                        skipped.append(column_name)
                    else:
                        print(f"   ⚠️  Error adding {column_name}: {e}")
            
            if added:
                print(f"\n✅ Migration complete! Added {len(added)} new columns")
            elif skipped:
                print("\n✅ Database schema is up to date!")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Migration error: {e}")
            import traceback
            traceback.print_exc()
            return False

def setup_admin(username_or_email):
    """Set up a user as an admin with full privileges"""
    with app.app_context():
        # Find the user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | 
            (User.email == username_or_email)
        ).first()
        
        if not user:
            print(f"❌ User '{username_or_email}' not found!")
            print("\nAvailable users:")
            all_users = User.query.filter(User.role.in_(['admin', 'teacher', 'parent'])).all()
            for u in all_users:
                print(f"  - {u.username} ({u.email or 'no email'}) - Role: {u.role}")
            return False
        
        print(f"\n🔍 Found user: {user.username} (ID: {user.id})")
        print(f"   Current role: {user.role}")
        print(f"   Email: {user.email or 'none'}")
        print(f"   Admin all access: {user.admin_all_access if hasattr(user, 'admin_all_access') else 'N/A'}")
        
        # Check if columns exist
        has_admin_all_access = hasattr(user, 'admin_all_access')
        has_honey_points = hasattr(user, 'honey_points')
        
        if not has_admin_all_access or not has_honey_points:
            print("\n⚠️  WARNING: User model is missing new monetization fields!")
            print("   You need to run database migration first.")
            print("\n   Run this command:")
            print("   flask db upgrade")
            print("\n   Or manually add these columns to the users table:")
            print("   - honey_points (INTEGER, default 0)")
            print("   - purchased_avatars (JSON)")
            print("   - purchased_bundles (JSON)")
            print("   - premium_member (BOOLEAN, default False)")
            print("   - admin_all_access (BOOLEAN, default False)")
            return False
        
        # Update user to admin with full access
        user.role = 'admin'
        user.admin_all_access = True
        user.premium_member = True  # Give premium access too
        
        # Generate teacher key if doesn't have one
        if not user.teacher_key:
            user.generate_teacher_key()
            print(f"\n🔑 Generated teacher key: {user.teacher_key}")
        
        try:
            db.session.commit()
            print(f"\n✅ SUCCESS! {user.username} is now a full admin with all access!")
            print(f"\n   Role: admin")
            print(f"   Admin All Access: True")
            print(f"   Premium Member: True")
            print(f"   Teacher Key: {user.teacher_key}")
            print(f"\n   You can now access the admin dashboard at:")
            print(f"   /admin/dashboard")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error updating user: {e}")
            import traceback
            traceback.print_exc()
            return False

def create_new_admin(username, display_name, email, password):
    """Create a brand new admin user"""
    with app.app_context():
        # Check if user already exists
        existing = User.query.filter(
            (User.username == username) | 
            (User.email == email)
        ).first()
        
        if existing:
            print(f"❌ User already exists: {existing.username}")
            return False
        
        # Check if columns exist
        test_user = User.query.first()
        has_admin_all_access = hasattr(test_user, 'admin_all_access') if test_user else False
        
        if not has_admin_all_access:
            print("\n⚠️  WARNING: Database is missing new monetization fields!")
            print("   You need to run database migration first.")
            return False
        
        # Create new admin user
        new_admin = User(
            username=username,
            display_name=display_name,
            email=email,
            role='admin',
            admin_all_access=True,
            premium_member=True
        )
        new_admin.set_password(password)
        new_admin.generate_teacher_key()
        
        try:
            db.session.add(new_admin)
            db.session.commit()
            print(f"\n✅ SUCCESS! Created new admin user: {username}")
            print(f"   Teacher Key: {new_admin.teacher_key}")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error creating user: {e}")
            return False

if __name__ == '__main__':
    print("🐝 BeeSmart Admin Setup Tool\n")
    
    # Check if we're connected to Railway
    db_uri = os.environ.get('DATABASE_URL', 'not set')
    if 'postgresql' not in db_uri:
        print("⚠️  WARNING: Not connected to Railway PostgreSQL database!")
        print(f"   Current: {db_uri[:50]}...")
        print("\n   To connect to Railway:")
        print("   1. Get your DATABASE_URL from Railway dashboard")
        print("   2. Set it: $env:DATABASE_URL='your_railway_postgres_url'")
        print("   3. Run this script again")
        print("\n   Or deploy this script to Railway and run it there.\n")
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python setup_admin.py migrate                                    # Run database migration")
        print("  python setup_admin.py <username_or_email>                       # Make user an admin")
        print("  python setup_admin.py create <username> <display_name> <email> <password>")
        print("\nExample:")
        print("  python setup_admin.py migrate")
        print("  python setup_admin.py jeff")
        print("  python setup_admin.py create bigdaddy 'Big Daddy' admin@beesmart.com mypassword")
        sys.exit(1)
    
    if sys.argv[1] == 'migrate':
        migrate_database()
    elif sys.argv[1] == 'create':
        if len(sys.argv) != 6:
            print("❌ Error: create requires username, display_name, email, and password")
            print("Usage: python setup_admin.py create <username> <display_name> <email> <password>")
            sys.exit(1)
        migrate_database()  # Run migration first
        create_new_admin(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    else:
        username_or_email = sys.argv[1]
        migrate_database()  # Run migration first
        setup_admin(username_or_email)
