"""
Database Migration Script for Railway
Adds missing columns to existing users table (avatar system, GPA tracking)
"""

import os
import sys
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import OperationalError, ProgrammingError

# Get database URL from environment or use local SQLite
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///beesmart.db')

# Fix Railway's postgres:// to postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print(f"🔧 Connecting to database...")
print(f"   {DATABASE_URL[:50]}...")

try:
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    # Check if users table exists
    if not inspector.has_table('users'):
        print("❌ Users table doesn't exist. Run db.create_all() first.")
        sys.exit(1)
    
    print("✅ Users table exists")
    
    # Get current columns
    existing_columns = {col['name'] for col in inspector.get_columns('users')}
    print(f"📊 Found {len(existing_columns)} existing columns")
    
    # Define new columns to add (if missing)
    migrations = [
        # 3D Avatar System
        ("avatar_id", "VARCHAR(50) DEFAULT 'cool-bee'", "3D avatar identifier"),
        ("avatar_variant", "VARCHAR(10) DEFAULT 'default'", "Avatar variant (always 'default')"),
        ("avatar_locked", "BOOLEAN DEFAULT FALSE", "Parental control lock"),
        ("avatar_last_updated", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "Last avatar change time"),
        
        # GPA Tracking
        ("cumulative_gpa", "NUMERIC(3, 2) DEFAULT 0.0", "GPA on 4.0 scale"),
        ("average_accuracy", "NUMERIC(5, 2) DEFAULT 0.0", "Average quiz accuracy percentage"),
        ("best_grade", "VARCHAR(5)", "Best grade achieved (A+, A, etc)"),
        ("best_streak", "INTEGER DEFAULT 0", "Best quiz streak"),
    ]
    
    with engine.connect() as conn:
        added_count = 0
        skipped_count = 0
        
        for col_name, col_def, description in migrations:
            if col_name in existing_columns:
                print(f"⏭️  {col_name:25s} - already exists")
                skipped_count += 1
            else:
                try:
                    # Add column (PostgreSQL and SQLite compatible)
                    sql = f"ALTER TABLE users ADD COLUMN {col_name} {col_def}"
                    conn.execute(text(sql))
                    conn.commit()
                    print(f"✅ {col_name:25s} - added ({description})")
                    added_count += 1
                except (OperationalError, ProgrammingError) as e:
                    print(f"❌ {col_name:25s} - failed: {e}")
        
        print(f"\n📊 Migration complete:")
        print(f"   ✅ {added_count} columns added")
        print(f"   ⏭️  {skipped_count} columns already existed")
        
        # Create indexes for avatar_id (if not exists)
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_avatar_id ON users(avatar_id)"))
            conn.commit()
            print("✅ Avatar index created")
        except Exception as e:
            print(f"⚠️  Avatar index: {e}")
    
    print("\n🎉 Database migration successful!")
    
except Exception as e:
    print(f"\n❌ Migration failed: {e}")
    sys.exit(1)
