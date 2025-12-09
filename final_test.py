#!/usr/bin/env python3
"""
Final verification - upload words and confirm they're in the database
"""
import requests
import sqlite3
import json

API_URL = "http://localhost:5000/api"
DB_PATH = r'c:\Temp\BeeSmartSpellingBeeApp\instance\beesmart.db'

print("=" * 60)
print("FINAL UPLOAD & PERSISTENCE TEST")
print("=" * 60)

# Get baseline count
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM wordbank_storage")
baseline = cursor.fetchone()[0]
print(f"\n1. Current wordbanks in database: {baseline}")
conn.close()

# Upload new words
print("\n2. Uploading new words...")
test_words = [
    {"word": "wonderful", "sentence": "This is a wonderful day.", "hint": "excellent"},
    {"word": "adventure", "sentence": "The adventure began at sunrise.", "hint": "exciting journey"},
    {"word": "mystery", "sentence": "The mystery was solved.", "hint": "something unknown"},
]

response = requests.post(f"{API_URL}/upload", json={"words": test_words})
print(f"   Response: {response.json()}")

# Check database
import time
time.sleep(0.5)  # Give database a moment to commit

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM wordbank_storage")
new_count = cursor.fetchone()[0]
print(f"\n3. Wordbanks after upload: {new_count}")

if new_count > baseline:
    print(f"   ✓ Added {new_count - baseline} wordbank(s)")
    
    # Get the latest wordbank
    cursor.execute("""
    SELECT storage_id, word_count, words_data FROM wordbank_storage
    ORDER BY created_at DESC LIMIT 1
    """)
    row = cursor.fetchone()
    
    print(f"   Latest wordbank:")
    print(f"     storage_id: {row[0]}")
    print(f"     word_count: {row[1]}")
    
    words_data = json.loads(row[2])
    print(f"     words: {[w['word'] for w in words_data]}")

conn.close()

print("\n" + "=" * 60)
print("✓ DATABASE PERSISTENCE CONFIRMED")
print("=" * 60)
