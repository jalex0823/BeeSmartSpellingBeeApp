"""
Railway Migration Script - Create WordBankStorage Table
Run this in Railway's terminal to add the wordbank_storage table to production PostgreSQL.

USAGE IN RAILWAY:
1. Go to Railway dashboard → Your project → Shell
2. Run: python railway_add_wordbank_table.py
"""

import os
import sys

def create_wordbank_storage_table():
    """Create wordbank_storage table in Railway PostgreSQL database"""
    
    print("🔧 Railway Migration: Creating wordbank_storage table...")
    print(f"📍 Environment: {os.getenv('RAILWAY_ENVIRONMENT', 'unknown')}")
    
    # Import app and db (this will use Railway's DATABASE_URL automatically)
    try:
        from AjaSpellBApp import app, db
        from models import WordBankStorage
    except Exception as e:
        print(f"❌ Failed to import app/models: {e}")
        return False
    
    with app.app_context():
        try:
            # Check if table already exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if 'wordbank_storage' in existing_tables:
                print("✅ Table wordbank_storage already exists!")
                
                # Show current row count
                count = db.session.query(WordBankStorage).count()
                print(f"📊 Current entries: {count}")
                
                # Show table schema
                columns = inspector.get_columns('wordbank_storage')
                print("\n📋 Table schema:")
                for col in columns:
                    print(f"   - {col['name']}: {col['type']}")
                
                return True
            
            # Create the table
            print("🔨 Creating wordbank_storage table...")
            db.create_all()
            
            # Verify creation
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'wordbank_storage' in tables:
                print("✅ Successfully created wordbank_storage table!")
                
                # Show table schema
                columns = inspector.get_columns('wordbank_storage')
                print("\n📋 Table schema:")
                for col in columns:
                    print(f"   - {col['name']}: {col['type']}")
                
                # Show indexes
                indexes = inspector.get_indexes('wordbank_storage')
                if indexes:
                    print("\n🔑 Indexes:")
                    for idx in indexes:
                        print(f"   - {idx['name']}: {idx['column_names']}")
                
                return True
            else:
                print("❌ Table creation failed - table not found after creation")
                return False
                
        except Exception as e:
            print(f"❌ Error creating table: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("=" * 70)
    print("🚂 Railway Migration: WordBankStorage Table")
    print("=" * 70)
    
    # Verify we're on Railway
    if not os.getenv('RAILWAY_ENVIRONMENT'):
        print("⚠️  WARNING: RAILWAY_ENVIRONMENT not detected!")
        print("   This script should be run on Railway, not locally.")
        response = input("   Continue anyway? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Migration cancelled")
            sys.exit(1)
    
    success = create_wordbank_storage_table()
    
    print("=" * 70)
    if success:
        print("✅ Migration completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Upload a word list to test")
        print("   2. Check Railway logs for: '✅ Saved X words to database'")
        print("   3. Restart Railway service")
        print("   4. Verify words persist after restart")
    else:
        print("❌ Migration failed - check errors above")
    print("=" * 70)
    
    sys.exit(0 if success else 1)
