#!/usr/bin/env python3
"""
Manually create the database with explicit SQL statements
"""
import sqlite3
import os

db_path = r'c:\Temp\BeeSmartSpellingBeeApp\beesmart.db'

# Create database file first
print("Creating SQLite database file...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the wordbank_storage table with all required columns
print("Creating wordbank_storage table...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS wordbank_storage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    storage_id VARCHAR(36) NOT NULL UNIQUE,
    words_data JSON NOT NULL,
    word_count INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER
);
""")

# Create indexes for faster queries
print("Creating indexes...")
cursor.execute("""CREATE INDEX IF NOT EXISTS ix_wordbank_storage_storage_id ON wordbank_storage(storage_id);""")
cursor.execute("""CREATE INDEX IF NOT EXISTS ix_wordbank_storage_word_count ON wordbank_storage(word_count);""")
cursor.execute("""CREATE INDEX IF NOT EXISTS ix_wordbank_storage_created_at ON wordbank_storage(created_at);""")
cursor.execute("""CREATE INDEX IF NOT EXISTS ix_wordbank_storage_user_id ON wordbank_storage(user_id);""")

# Commit and verify
conn.commit()

# Check if table was created
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"\nTables in database:")
for table in tables:
    print(f"  - {table[0]}")

# Check wordbank_storage schema
cursor.execute("PRAGMA table_info(wordbank_storage)")
schema = cursor.fetchall()
print(f"\nwordbank_storage columns:")
for col in schema:
    print(f"  - {col[1]} ({col[2]})")

conn.close()

# Verify file size
file_size = os.path.getsize(db_path)
print(f"\n✓ Database file created: {db_path}")
print(f"✓ File size: {file_size} bytes")
print("✓ Database initialization complete!")
