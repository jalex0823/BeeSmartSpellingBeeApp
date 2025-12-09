#!/usr/bin/env python3
import sqlite3

db_path = r'c:\Temp\BeeSmartSpellingBeeApp\instance\beesmart.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check wordbank_storage table
cursor.execute("SELECT COUNT(*) FROM wordbank_storage")
count = cursor.fetchone()[0]
print(f"Rows in instance/beesmart.db wordbank_storage: {count}")

if count > 0:
    cursor.execute("""
    SELECT id, storage_id, word_count, created_at FROM wordbank_storage
    ORDER BY created_at DESC LIMIT 5
    """)
    
    print(f"\nLatest 5 wordbanks:")
    for row in cursor.fetchall():
        print(f"  ID {row[0]}: storage_id={row[1]}, words={row[2]}, created={row[3]}")

conn.close()
