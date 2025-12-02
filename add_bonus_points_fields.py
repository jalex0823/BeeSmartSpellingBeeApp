#!/usr/bin/env python3
"""
Database migration script to add bonus/extra points fields to QuizSession model
Adds: points_earned, badge_bonus_points, extra_points
Run this script to update the database schema.
"""

import os
import sys
from sqlalchemy import text

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from AjaSpellBApp import app, db

def add_bonus_points_fields():
    """Add new points tracking fields to quiz_sessions table"""
    
    print("🔧 Adding bonus points fields to quiz_sessions table...")
    
    with app.app_context():
        try:
            # Check if fields already exist
            inspector = db.inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('quiz_sessions')]
            
            migrations_needed = []
            
            if 'points_earned' not in existing_columns:
                migrations_needed.append(
                    "ALTER TABLE quiz_sessions ADD COLUMN points_earned INTEGER DEFAULT 0"
                )
            
            if 'badge_bonus_points' not in existing_columns:
                migrations_needed.append(
                    "ALTER TABLE quiz_sessions ADD COLUMN badge_bonus_points INTEGER DEFAULT 0"
                )
            
            if 'extra_points' not in existing_columns:
                migrations_needed.append(
                    "ALTER TABLE quiz_sessions ADD COLUMN extra_points INTEGER DEFAULT 0"
                )
            
            if not migrations_needed:
                print("✅ All fields already exist! No migration needed.")
                return True
            
            # Execute migrations
            for sql in migrations_needed:
                print(f"   Executing: {sql}")
                db.session.execute(text(sql))
            
            db.session.commit()
            print(f"✅ Successfully added {len(migrations_needed)} new field(s) to quiz_sessions table!")
            
            # Migrate existing data: copy total_points to points_earned if not already set
            print("📊 Migrating existing data...")
            result = db.session.execute(text("""
                UPDATE quiz_sessions 
                SET points_earned = total_points 
                WHERE points_earned = 0 AND total_points > 0
            """))
            db.session.commit()
            rows_updated = result.rowcount
            print(f"   Migrated {rows_updated} existing quiz session(s)")
            
            # Verify the changes
            print("\n✅ Migration complete! Verifying schema...")
            inspector = db.inspect(db.engine)
            updated_columns = [col['name'] for col in inspector.get_columns('quiz_sessions')]
            
            required_fields = ['points_earned', 'badge_bonus_points', 'extra_points']
            missing = [f for f in required_fields if f not in updated_columns]
            
            if missing:
                print(f"⚠️  WARNING: Some fields still missing: {missing}")
                return False
            else:
                print(f"✅ All required fields present: {', '.join(required_fields)}")
                return True
                
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("=" * 60)
    print("QuizSession Bonus Points Migration")
    print("=" * 60)
    print()
    
    success = add_bonus_points_fields()
    
    print()
    print("=" * 60)
    if success:
        print("✅ Migration completed successfully!")
        print()
        print("New fields added to quiz_sessions table:")
        print("  • points_earned - Total points from word answers (with bonuses)")
        print("  • badge_bonus_points - Points earned from badges/achievements")
        print("  • extra_points - Additional bonus points (events, milestones)")
        print("  • total_points - Cumulative sum of all point sources")
        print()
        print("These fields will now track the complete breakdown of points")
        print("earned in each quiz session, ensuring all bonuses are counted")
        print("in the cumulative score!")
    else:
        print("❌ Migration failed - please check errors above")
        sys.exit(1)
    print("=" * 60)
