#!/usr/bin/env python3
"""
Force database initialization with all tables
"""
import sys
import os

# Ensure we're in the right directory
os.chdir(r'c:\Temp\BeeSmartSpellingBeeApp')
sys.path.insert(0, r'c:\Temp\BeeSmartSpellingBeeApp')

print("=" * 60)
print("DATABASE INITIALIZATION")
print("=" * 60)

# Import the app and db AFTER changing directory
from AjaSpellBApp import app, db

print(f"\n1. App created with database: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Create all tables with app context
with app.app_context():
    print("2. Creating all database tables...")
    
    try:
        # This should trigger SQLAlchemy to create tables
        db.create_all()
        print("   ✓ db.create_all() executed")
    except Exception as e:
        print(f"   ✗ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
    
    # Verify the database file exists and has content
    import os
    if os.path.exists('beesmart.db'):
        size = os.path.getsize('beesmart.db')
        print(f"3. Database file: beesmart.db ({size} bytes)")
        
        if size > 0:
            # Check tables
            import sqlite3
            conn = sqlite3.connect('beesmart.db')
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"\n✓ Tables created ({len(tables)}):")
            
            for t in tables:
                cursor.execute(f"SELECT COUNT(*) FROM '{t[0]}'")
                count = cursor.fetchone()[0]
                print(f"   - {t[0]} ({count} rows)")
            
            # Verify wordbank_storage specifically
            cursor.execute("PRAGMA table_info(wordbank_storage)")
            schema = cursor.fetchall()
            if schema:
                print(f"\n✓ wordbank_storage schema has {len(schema)} columns")
            
            conn.close()
            print("\n✓ Database initialization COMPLETE!")
        else:
            print(f"   ✗ ERROR: Database file is empty ({size} bytes)")
    else:
        print("   ✗ ERROR: Database file was not created!")
