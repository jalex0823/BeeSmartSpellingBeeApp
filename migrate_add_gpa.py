"""
Database Migration: Add GPA tracking fields to User model
Run this script to add cumulative_gpa, average_accuracy, best_grade, best_streak columns
"""
from AjaSpellBApp import app, db
from models import User
from sqlalchemy import text

def migrate_add_gpa_fields():
    """Add GPA tracking columns to users table"""
    with app.app_context():
        print("=" * 80)
        print("DATABASE MIGRATION: Adding GPA Tracking Fields")
        print("=" * 80)
        
        try:
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            print(f"\nCurrent columns in users table: {len(columns)}")
            
            # Add columns if they don't exist
            new_columns = []
            
            if 'cumulative_gpa' not in columns:
                db.session.execute(text(
                    "ALTER TABLE users ADD COLUMN cumulative_gpa NUMERIC(3, 2) DEFAULT 0.0"
                ))
                new_columns.append('cumulative_gpa')
                print("✅ Added column: cumulative_gpa")
            
            if 'average_accuracy' not in columns:
                db.session.execute(text(
                    "ALTER TABLE users ADD COLUMN average_accuracy NUMERIC(5, 2) DEFAULT 0.0"
                ))
                new_columns.append('average_accuracy')
                print("✅ Added column: average_accuracy")
            
            if 'best_grade' not in columns:
                db.session.execute(text(
                    "ALTER TABLE users ADD COLUMN best_grade VARCHAR(5)"
                ))
                new_columns.append('best_grade')
                print("✅ Added column: best_grade")
            
            if 'best_streak' not in columns:
                db.session.execute(text(
                    "ALTER TABLE users ADD COLUMN best_streak INTEGER DEFAULT 0"
                ))
                new_columns.append('best_streak')
                print("✅ Added column: best_streak")
            
            if new_columns:
                db.session.commit()
                print(f"\n💾 Added {len(new_columns)} new columns to users table")
            else:
                print("\n✅ All GPA tracking columns already exist")
            
            # Update GPA for all existing users
            print("\n" + "=" * 80)
            print("UPDATING GPA FOR EXISTING USERS")
            print("=" * 80)
            
            users = User.query.all()
            print(f"\nFound {len(users)} users")
            
            updated_count = 0
            for user in users:
                try:
                    user.update_gpa_and_accuracy()
                    updated_count += 1
                    if user.cumulative_gpa > 0:
                        print(f"✅ Updated {user.username}: GPA={user.cumulative_gpa}, Accuracy={user.average_accuracy}%, Best Grade={user.best_grade}")
                except Exception as e:
                    print(f"⚠️  Failed to update {user.username}: {e}")
            
            db.session.commit()
            print(f"\n💾 Successfully updated GPA for {updated_count} users")
            
            print("\n" + "=" * 80)
            print("MIGRATION COMPLETE!")
            print("=" * 80)
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()


if __name__ == "__main__":
    migrate_add_gpa_fields()
