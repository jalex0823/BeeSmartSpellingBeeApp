"""
Database Migration: Add Buzz Dust & Ranking Fields to User Model
Adds: total_buzz_dust, bee_class, last_rank_up_at, current_streak, longest_streak
"""

import sys
import os

# Add parent directory to path so we can import models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, User
from AjaSpellBApp import app
from sqlalchemy import text

def run_migration():
    """Add Buzz Dust fields to users table"""
    
    print("🔄 Starting Buzz Dust migration...")
    
    with app.app_context():
        inspector = db.inspect(db.engine)
        existing_columns = [col['name'] for col in inspector.get_columns('users')]
        
        migrations_needed = []
        
        # Check which columns need to be added
        if 'total_buzz_dust' not in existing_columns:
            migrations_needed.append(
                "ALTER TABLE users ADD COLUMN total_buzz_dust INTEGER DEFAULT 0"
            )
            print("  ✓ Will add: total_buzz_dust")
        
        if 'bee_class' not in existing_columns:
            migrations_needed.append(
                "ALTER TABLE users ADD COLUMN bee_class VARCHAR(20) DEFAULT 'novice'"
            )
            print("  ✓ Will add: bee_class")
        
        if 'last_rank_up_at' not in existing_columns:
            migrations_needed.append(
                "ALTER TABLE users ADD COLUMN last_rank_up_at TIMESTAMP NULL"
            )
            print("  ✓ Will add: last_rank_up_at")
        
        if 'current_streak' not in existing_columns:
            migrations_needed.append(
                "ALTER TABLE users ADD COLUMN current_streak INTEGER DEFAULT 0"
            )
            print("  ✓ Will add: current_streak")
        
        if 'longest_streak' not in existing_columns:
            migrations_needed.append(
                "ALTER TABLE users ADD COLUMN longest_streak INTEGER DEFAULT 0"
            )
            print("  ✓ Will add: longest_streak")
        
        if not migrations_needed:
            print("✅ All Buzz Dust columns already exist - no migration needed!")
            return
        
        # Execute migrations
        print(f"\n📝 Executing {len(migrations_needed)} migration(s)...")
        
        try:
            for sql in migrations_needed:
                print(f"  Running: {sql}")
                db.session.execute(text(sql))
            
            db.session.commit()
            print("\n✅ Migration completed successfully!")
            
            # Create indexes for performance
            print("\n🔍 Creating indexes...")
            try:
                index_sql = [
                    "CREATE INDEX IF NOT EXISTS idx_users_total_buzz_dust ON users(total_buzz_dust)",
                    "CREATE INDEX IF NOT EXISTS idx_users_bee_class ON users(bee_class)"
                ]
                
                for sql in index_sql:
                    db.session.execute(text(sql))
                
                db.session.commit()
                print("✅ Indexes created successfully!")
            except Exception as e:
                print(f"⚠️ Index creation failed (may already exist): {e}")
            
            # Verify the migration
            print("\n🔍 Verifying migration...")
            inspector = db.inspect(db.engine)
            new_columns = [col['name'] for col in inspector.get_columns('users')]
            
            required_columns = ['total_buzz_dust', 'bee_class', 'last_rank_up_at', 'current_streak', 'longest_streak']
            all_present = all(col in new_columns for col in required_columns)
            
            if all_present:
                print("✅ All columns verified successfully!")
                
                # Display sample data
                user_count = db.session.query(User).count()
                print(f"\n📊 Total users in database: {user_count}")
                
                if user_count > 0:
                    sample_user = db.session.query(User).first()
                    print(f"   Sample user buzz_dust: {sample_user.total_buzz_dust}")
                    print(f"   Sample user bee_class: {sample_user.bee_class}")
            else:
                print("❌ Verification failed - some columns are missing!")
                missing = [col for col in required_columns if col not in new_columns]
                print(f"   Missing columns: {missing}")
                
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == '__main__':
    print("=" * 60)
    print("BeeSmart Buzz Dust Migration Script")
    print("=" * 60)
    print()
    
    try:
        run_migration()
        print("\n" + "=" * 60)
        print("Migration completed! 🎉")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
