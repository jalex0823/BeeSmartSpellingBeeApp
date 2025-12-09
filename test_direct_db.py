#!/usr/bin/env python3
"""
Direct test of WordBankStorage.save_wordbank()
"""
import sys
import os
os.chdir(r'c:\Temp\BeeSmartSpellingBeeApp')
sys.path.insert(0, r'c:\Temp\BeeSmartSpellingBeeApp')

from AjaSpellBApp import app, db
from models import WordBankStorage
import uuid
import json

print("=" * 60)
print("DIRECT DATABASE TEST")
print("=" * 60)

with app.app_context():
    # Test 1: Create a wordbank directly
    print("\n1. Creating wordbank directly via WordBankStorage.save_wordbank()...")
    
    storage_id = str(uuid.uuid4())
    test_words = [
        {"word": "happy", "sentence": "The happy child laughed.", "hint": "feeling joy"},
        {"word": "mountain", "sentence": "The tall mountain touches the clouds.", "hint": "high peak"},
        {"word": "butterfly", "sentence": "A colorful butterfly landed on the flower.", "hint": "insect with wings"},
    ]
    
    try:
        WordBankStorage.save_wordbank(storage_id, test_words, user_id=None)
        print(f"   ✓ save_wordbank() executed without error")
        print(f"   storage_id: {storage_id}")
        print(f"   word_count: {len(test_words)}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Query database to verify
    print("\n2. Querying database to verify...")
    try:
        count = WordBankStorage.query.count()
        print(f"   ✓ WordBankStorage.query.count() = {count}")
        
        if count > 0:
            wb = WordBankStorage.query.filter_by(storage_id=storage_id).first()
            if wb:
                print(f"   ✓ Found wordbank with storage_id={storage_id}")
                print(f"   word_count field: {wb.word_count}")
                words = json.loads(wb.words_data)
                print(f"   Words: {[w['word'] for w in words]}")
            else:
                print(f"   ✗ Wordbank NOT found with storage_id={storage_id}")
        
    except Exception as e:
        print(f"   ✗ Query error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Check with raw SQLite
    print("\n3. Raw SQLite check...")
    import sqlite3
    conn = sqlite3.connect('beesmart.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM wordbank_storage")
    count = cursor.fetchone()[0]
    print(f"   wordbank_storage row count: {count}")
    
    if count > 0:
        cursor.execute("SELECT storage_id, word_count FROM wordbank_storage ORDER BY created_at DESC LIMIT 1")
        row = cursor.fetchone()
        print(f"   Latest: storage_id={row[0]}, word_count={row[1]}")
    
    conn.close()

print("\n" + "=" * 60)
