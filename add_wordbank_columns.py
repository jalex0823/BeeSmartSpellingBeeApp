#!/usr/bin/env python3
"""
Database Migration: Add wordbank persistence columns to users table

This migration adds:
- wordbank_storage_id: UUID pointer to WORD_STORAGE and disk cache
- wordbank_last_updated: Timestamp of last wordbank modification

These columns enable wordbank persistence recovery when sessions are lost
(mobile browser cookie clearing, session timeouts, etc.)

Usage:
    python add_wordbank_columns.py
"""

import os
import sys
from sqlalchemy import inspect, text

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from AjaSpellBApp import app, db

def add_wordbank_columns():
    """Add wordbank_storage_id and wordbank_last_updated columns to users table if not exists"""
    
    with app.app_context():
        inspector = inspect(db.engine)
        
        # Check if users table exists
        if not inspector.has_table('users'):
            print("❌ users table does not exist! Run database initialization first.")
            return False
        
        # Get existing columns
        columns = [col['name'] for col in inspector.get_columns('users')]
        print(f"✅ Found users table with {len(columns)} columns")
        
        migrations_needed = []
        
        # Check if wordbank_storage_id exists
        if 'wordbank_storage_id' not in columns:
            migrations_needed.append('wordbank_storage_id')
            print("⚠️  wordbank_storage_id column missing")
        else:
            print("✅ wordbank_storage_id column already exists")
        
        # Check if wordbank_last_updated exists
        if 'wordbank_last_updated' not in columns:
            migrations_needed.append('wordbank_last_updated')
            print("⚠️  wordbank_last_updated column missing")
        else:
            print("✅ wordbank_last_updated column already exists")
        
        # Apply migrations if needed
        if migrations_needed:
            print(f"\n🔧 Applying {len(migrations_needed)} migration(s)...")
            
            try:
                if 'wordbank_storage_id' in migrations_needed:
                    print("   Adding wordbank_storage_id column...")
                    db.session.execute(text(
                        "ALTER TABLE users ADD COLUMN wordbank_storage_id VARCHAR(36)"
                    ))
                    print("   ✅ Added wordbank_storage_id")
                
                if 'wordbank_last_updated' in migrations_needed:
                    print("   Adding wordbank_last_updated column...")
                    db.session.execute(text(
                        "ALTER TABLE users ADD COLUMN wordbank_last_updated TIMESTAMP"
                    ))
                    print("   ✅ Added wordbank_last_updated")
                
                # Add index on wordbank_storage_id for faster lookups
                if 'wordbank_storage_id' in migrations_needed:
                    try:
                        print("   Creating index on wordbank_storage_id...")
                        db.session.execute(text(
                            "CREATE INDEX idx_users_wordbank_storage_id ON users(wordbank_storage_id)"
                        ))
                        print("   ✅ Created index")
                    except Exception as e:
                        # Index might already exist, ignore error
                        print(f"   ⚠️  Index creation skipped: {e}")
                
                db.session.commit()
                print(f"\n✅ Migration completed successfully!")
                print(f"   Added columns: {', '.join(migrations_needed)}")
                return True
                
            except Exception as e:
                print(f"\n❌ Migration failed: {e}")
                db.session.rollback()
                return False
        else:
            print("\n✅ All columns already exist - no migration needed")
            return True

if __name__ == "__main__":
    print("="*60)
    print("🐝 BeeSmart Wordbank Persistence Migration")
    print("="*60)
    print()
    
    success = add_wordbank_columns()
    
    if success:
        print("\n" + "="*60)
        print("✅ Migration completed successfully!")
        print("="*60)
        print("\n📚 Wordbank persistence is now enabled:")
        print("   - Authenticated users' wordbanks will persist across sessions")
        print("   - Session loss will automatically recover from database")
        print("   - Disk cache provides additional durability layer")
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ Migration failed!")
        print("="*60)
        sys.exit(1)
