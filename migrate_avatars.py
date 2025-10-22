"""
Database Migration: Add Avatar Columns to User Table
Run this script to add avatar support to existing users
"""

from AjaSpellBApp import app, db
from models import User
from sqlalchemy import text

def migrate_avatar_columns():
    """Add avatar columns to existing users table"""
    
    with app.app_context():
        try:
            # Check if columns already exist
            result = db.session.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result]
            
            print("📋 Current columns:", columns)
            
            migrations_needed = []
            
            # Check which columns need to be added
            if 'avatar_id' not in columns:
                migrations_needed.append('avatar_id')
            
            if 'avatar_variant' not in columns:
                migrations_needed.append('avatar_variant')
            
            if 'avatar_locked' not in columns:
                migrations_needed.append('avatar_locked')
            
            if 'avatar_last_updated' not in columns:
                migrations_needed.append('avatar_last_updated')
            
            if not migrations_needed:
                print("✅ All avatar columns already exist!")
                return
            
            print(f"🔧 Need to add columns: {migrations_needed}")
            
            # Add missing columns
            if 'avatar_id' in migrations_needed:
                print("Adding avatar_id column...")
                db.session.execute(text(
                    "ALTER TABLE users ADD COLUMN avatar_id VARCHAR(50) DEFAULT 'cool-bee'"
                ))
            
            if 'avatar_variant' in migrations_needed:
                print("Adding avatar_variant column...")
                db.session.execute(text(
                    "ALTER TABLE users ADD COLUMN avatar_variant VARCHAR(10) DEFAULT 'default'"
                ))
            
            if 'avatar_locked' in migrations_needed:
                print("Adding avatar_locked column...")
                db.session.execute(text(
                    "ALTER TABLE users ADD COLUMN avatar_locked BOOLEAN DEFAULT 0"
                ))
            
            if 'avatar_last_updated' in migrations_needed:
                print("Adding avatar_last_updated column...")
                db.session.execute(text(
                    "ALTER TABLE users ADD COLUMN avatar_last_updated DATETIME"
                ))
            
            db.session.commit()
            print("✅ Migration completed successfully!")
            
            # Verify columns were added
            result = db.session.execute(text("PRAGMA table_info(users)"))
            new_columns = [row[1] for row in result]
            print("📋 Updated columns:", new_columns)
            
            # Count users
            user_count = User.query.count()
            print(f"👥 Total users with default avatars: {user_count}")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    print("🐝 BeeSmart Avatar System - Database Migration")
    print("=" * 50)
    migrate_avatar_columns()
    print("=" * 50)
    print("✨ Migration complete! All users now have avatar support.")
