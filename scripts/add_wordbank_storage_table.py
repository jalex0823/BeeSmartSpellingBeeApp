"""
Database migration script to add WordBankStorage table for Railway deployment.
Fixes the ephemeral filesystem issue where wordbanks get deleted on container restart.

Run this script after deploying the updated models.py to create the new table.
"""

import sys
import os

# Add parent directory to path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AjaSpellBApp import app, db
from models import WordBankStorage

def add_wordbank_storage_table():
    """Create the wordbank_storage table in the database"""
    with app.app_context():
        try:
            # Create the table
            db.create_all()
            print("✅ Successfully created wordbank_storage table")
            
            # Verify table exists
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            if 'wordbank_storage' in tables:
                print("✅ Verified: wordbank_storage table exists")
                
                # Show table schema
                columns = inspector.get_columns('wordbank_storage')
                print("\n📋 Table schema:")
                for col in columns:
                    print(f"   - {col['name']}: {col['type']}")
            else:
                print("⚠️ Warning: wordbank_storage table not found after creation")
            
        except Exception as e:
            print(f"❌ Error creating table: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == '__main__':
    print("🔧 Adding WordBankStorage table to database...")
    success = add_wordbank_storage_table()
    sys.exit(0 if success else 1)
