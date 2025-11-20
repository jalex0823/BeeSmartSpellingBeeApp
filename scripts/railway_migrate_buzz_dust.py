"""
Railway Database Migration for Buzz Dust Fields
Adds the 5 new Buzz Dust columns to the users table in Railway PostgreSQL
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text, inspect
from config import get_config

def migrate_buzz_dust_fields():
    """Add Buzz Dust fields to users table if they don't exist"""
    
    print("=" * 60)
    print("Railway Buzz Dust Migration")
    print("=" * 60)
    
    # Get database URL from config
    config = get_config()
    database_url = config.SQLALCHEMY_DATABASE_URI
    
    if not database_url or 'sqlite' in database_url.lower():
        print("⚠️ Not a Railway PostgreSQL database, skipping migration")
        return True
    
    print(f"📊 Connecting to Railway database...")
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if users table exists
            inspector = inspect(engine)
            if 'users' not in inspector.get_table_names():
                print("⚠️ Users table doesn't exist yet - will be created by db.create_all()")
                return True
            
            # Get existing columns
            existing_columns = [col['name'] for col in inspector.get_columns('users')]
            print(f"📋 Found {len(existing_columns)} existing columns in users table")
            
            # Define new columns to add
            new_columns = {
                'total_buzz_dust': 'INTEGER DEFAULT 0 NULL',
                'bee_class': 'VARCHAR(20) DEFAULT \'novice\' NULL',
                'last_rank_up_at': 'TIMESTAMP NULL',
                'current_streak': 'INTEGER DEFAULT 0 NULL',
                'longest_streak': 'INTEGER DEFAULT 0 NULL'
            }
            
            # Add missing columns
            added_count = 0
            for column_name, column_def in new_columns.items():
                if column_name not in existing_columns:
                    print(f"   ➕ Adding column: {column_name}")
                    try:
                        conn.execute(text(f"ALTER TABLE users ADD COLUMN {column_name} {column_def}"))
                        conn.commit()
                        added_count += 1
                        print(f"   ✅ Added {column_name}")
                    except Exception as e:
                        print(f"   ⚠️ Could not add {column_name}: {e}")
                else:
                    print(f"   ✓ Column {column_name} already exists")
            
            # Create indexes for performance
            if 'total_buzz_dust' in new_columns and 'total_buzz_dust' not in existing_columns:
                try:
                    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_users_total_buzz_dust ON users (total_buzz_dust)"))
                    conn.execute(text("CREATE INDEX IF NOT EXISTS ix_users_bee_class ON users (bee_class)"))
                    conn.commit()
                    print("   ✅ Created indexes for Buzz Dust fields")
                except Exception as e:
                    print(f"   ⚠️ Index creation warning: {e}")
            
            print()
            print("=" * 60)
            if added_count > 0:
                print(f"✅ Migration complete! Added {added_count} new columns")
            else:
                print("✅ All Buzz Dust columns already exist")
            print("=" * 60)
            
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = migrate_buzz_dust_fields()
    sys.exit(0 if success else 1)
