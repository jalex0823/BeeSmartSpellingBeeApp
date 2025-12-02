#!/usr/bin/env python3
"""
Migration script to add bonus points fields to Railway PostgreSQL database
Run this script on Railway or with DATABASE_URL environment variable set
"""

import os
import sys
from sqlalchemy import create_engine, text

def run_migration():
    """Add bonus points columns to quiz_sessions table"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        print("This script must be run on Railway or with DATABASE_URL set")
        sys.exit(1)
    
    print("=" * 70)
    print("🐝 BeeSmart - Bonus Points Migration for Railway PostgreSQL")
    print("=" * 70)
    print(f"Database: {database_url[:50]}...")
    print()
    
    try:
        # Create engine
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if columns already exist
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'quiz_sessions' 
                AND column_name IN ('points_earned', 'badge_bonus_points', 'extra_points')
            """)
            
            result = conn.execute(check_query)
            existing_columns = [row[0] for row in result]
            
            print(f"Existing bonus points columns: {existing_columns if existing_columns else 'None'}")
            print()
            
            migrations_applied = []
            
            # Add points_earned column
            if 'points_earned' not in existing_columns:
                print("Adding points_earned column...")
                conn.execute(text("""
                    ALTER TABLE quiz_sessions 
                    ADD COLUMN points_earned INTEGER DEFAULT 0
                """))
                migrations_applied.append('points_earned')
                print("✅ Added points_earned column")
            else:
                print("⏭️  points_earned column already exists")
            
            # Add badge_bonus_points column
            if 'badge_bonus_points' not in existing_columns:
                print("Adding badge_bonus_points column...")
                conn.execute(text("""
                    ALTER TABLE quiz_sessions 
                    ADD COLUMN badge_bonus_points INTEGER DEFAULT 0
                """))
                migrations_applied.append('badge_bonus_points')
                print("✅ Added badge_bonus_points column")
            else:
                print("⏭️  badge_bonus_points column already exists")
            
            # Add extra_points column
            if 'extra_points' not in existing_columns:
                print("Adding extra_points column...")
                conn.execute(text("""
                    ALTER TABLE quiz_sessions 
                    ADD COLUMN extra_points INTEGER DEFAULT 0
                """))
                migrations_applied.append('extra_points')
                print("✅ Added extra_points column")
            else:
                print("⏭️  extra_points column already exists")
            
            # Commit the transaction
            conn.commit()
            
            print()
            print("=" * 70)
            if migrations_applied:
                print(f"✅ Migration completed successfully!")
                print(f"   Columns added: {', '.join(migrations_applied)}")
            else:
                print("✅ All columns already exist - no migration needed")
            print("=" * 70)
            
            return True
            
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ MIGRATION FAILED: {str(e)}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
