"""
Add is_favorite column to word_lists table
Run this once to update existing databases
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import after setting up path
import AjaSpellBApp
app = AjaSpellBApp.app
db = AjaSpellBApp.db

with app.app_context():
    try:
        # Check if column already exists
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('word_lists')]
        
        if 'is_favorite' in columns:
            print("ℹ️  Column is_favorite already exists - no changes needed")
        else:
            # Add the column - syntax varies by database
            with db.engine.connect() as conn:
                # PostgreSQL and SQLite compatible syntax
                conn.execute(db.text("""
                    ALTER TABLE word_lists 
                    ADD COLUMN is_favorite BOOLEAN DEFAULT FALSE
                """))
                conn.commit()
                print("✅ Added is_favorite column to word_lists table")
    except Exception as e:
        if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
            print("ℹ️  Column is_favorite already exists - no changes needed")
        else:
            print(f"❌ Error adding column: {e}")
            raise

    # Verify the column exists
    from models import WordList
    try:
        test_list = WordList.query.first()
        if test_list:
            print(f"✅ Verified: is_favorite = {getattr(test_list, 'is_favorite', 'NOT FOUND')}")
        else:
            print("ℹ️  No word lists in database to test")
    except Exception as e:
        print(f"⚠️  Verification failed: {e}")

print("\n🎉 Migration complete!")
