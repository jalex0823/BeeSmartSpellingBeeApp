#!/usr/bin/env python3
import sys
import os
os.chdir(r'c:\Temp\BeeSmartSpellingBeeApp')
sys.path.insert(0, r'c:\Temp\BeeSmartSpellingBeeApp')

from AjaSpellBApp import app
print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Check if DATABASE_URL env var is set
db_url = os.environ.get('DATABASE_URL')
print(f"DATABASE_URL env var: {db_url}")

# List local files
import glob
db_files = glob.glob('*.db')
print(f"\n.db files in directory: {db_files}")

# Check each file size
for f in db_files:
    import sqlite3
    try:
        conn = sqlite3.connect(f)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        count = cursor.fetchone()[0]
        size = os.path.getsize(f)
        print(f"  {f}: {size} bytes, {count} tables")
        conn.close()
    except Exception as e:
        print(f"  {f}: Error - {e}")
