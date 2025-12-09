#!/usr/bin/env python3
"""
Test word upload and database persistence
"""
import json
import requests

API_URL = "http://localhost:5000/api"

print("=" * 60)
print("WORD UPLOAD & DATABASE PERSISTENCE TEST")
print("=" * 60)

# Test 1: Upload some words via API
print("\n1. Uploading 5 test words via /api/upload...")
test_words = [
    {"word": "happy", "sentence": "The happy child laughed.", "hint": "feeling joy"},
    {"word": "mountain", "sentence": "The tall mountain touches the clouds.", "hint": "high peak"},
    {"word": "butterfly", "sentence": "A colorful butterfly landed on the flower.", "hint": "insect with wings"},
    {"word": "celebrate", "sentence": "We celebrate our birthday with cake.", "hint": "have a party"},
    {"word": "discover", "sentence": "Scientists discover new species.", "hint": "find something new"},
]

payload = {"words": test_words}
response = requests.post(f"{API_URL}/upload", json=payload)

print(f"   Status: {response.status_code}")
if response.ok:
    data = response.json()
    print(f"   Response: {data}")
    if data.get('ok'):
        print(f"   ✓ {data['count']} words uploaded successfully")
else:
    print(f"   ✗ Error: {response.text}")

# Test 2: Check the database directly
print("\n2. Checking database for persisted words...")
import sqlite3
conn = sqlite3.connect(r'c:\Temp\BeeSmartSpellingBeeApp\beesmart.db')
cursor = conn.cursor()

# Get wordbanks from database
cursor.execute("SELECT COUNT(*) FROM wordbank_storage")
count = cursor.fetchone()[0]
print(f"   Wordbanks in database: {count}")

if count > 0:
    cursor.execute("SELECT id, storage_id, word_count FROM wordbank_storage ORDER BY created_at DESC LIMIT 1")
    row = cursor.fetchone()
    print(f"   Latest wordbank ID: {row[0]}, storage_id: {row[1]}, word_count: {row[2]}")
    
    # Get the words data
    cursor.execute("SELECT words_data FROM wordbank_storage ORDER BY created_at DESC LIMIT 1")
    words_json = cursor.fetchone()[0]
    words_data = json.loads(words_json)
    print(f"\n   ✓ Words in latest wordbank ({len(words_data)}):")
    for w in words_data:
        print(f"     - {w['word']}: {w['sentence'][:40]}...")

conn.close()

print("\n" + "=" * 60)
print("✓ TEST COMPLETE")
print("=" * 60)
