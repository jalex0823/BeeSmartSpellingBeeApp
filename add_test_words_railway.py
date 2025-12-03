#!/usr/bin/env python3
"""
Add test words to Railway PostgreSQL wordbank_storage table.
This simulates user uploads for testing wordbank persistence.
"""

import psycopg2
import json
import uuid
from datetime import datetime

# Railway PostgreSQL connection string
RAILWAY_DB_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

# Test word sets
TEST_WORDBANKS = [
    {
        "name": "Spelling Test - Grade 3",
        "words": [
            {"word": "apple", "sentence": "I ate a red _____.", "hint": "A round fruit"},
            {"word": "banana", "sentence": "The _____ is yellow.", "hint": "Long yellow fruit"},
            {"word": "cherry", "sentence": "A _____ is small and red.", "hint": "Small red fruit"},
            {"word": "elephant", "sentence": "The _____ has a long trunk.", "hint": "Large gray animal"},
            {"word": "giraffe", "sentence": "A _____ has a very long neck.", "hint": "Tall spotted animal"},
        ]
    },
    {
        "name": "Science Vocabulary",
        "words": [
            {"word": "photosynthesis", "sentence": "Plants use _____ to make food.", "hint": "Process using sunlight"},
            {"word": "molecule", "sentence": "A _____ is made of atoms.", "hint": "Tiny particle"},
            {"word": "gravity", "sentence": "_____ pulls things down to Earth.", "hint": "Force that attracts"},
            {"word": "ecosystem", "sentence": "A forest is an example of an _____.", "hint": "Community of organisms"},
            {"word": "habitat", "sentence": "A polar bear's _____ is the Arctic.", "hint": "Natural home"},
        ]
    },
    {
        "name": "Math Terms",
        "words": [
            {"word": "addition", "sentence": "_____ means putting numbers together.", "hint": "Math operation with +"},
            {"word": "subtraction", "sentence": "_____ means taking away.", "hint": "Math operation with -"},
            {"word": "multiplication", "sentence": "_____ is repeated addition.", "hint": "Math operation with ×"},
            {"word": "division", "sentence": "_____ means splitting into equal parts.", "hint": "Math operation with ÷"},
            {"word": "fraction", "sentence": "1/2 is an example of a _____.", "hint": "Part of a whole"},
        ]
    },
    {
        "name": "Common Words - Grade 2",
        "words": [
            {"word": "because", "sentence": "I stayed home _____ it was raining.", "hint": "Gives a reason"},
            {"word": "beautiful", "sentence": "The sunset was _____.", "hint": "Very pretty"},
            {"word": "friend", "sentence": "My best _____ is kind.", "hint": "Someone you like"},
            {"word": "family", "sentence": "I love my _____.", "hint": "Parents and siblings"},
            {"word": "together", "sentence": "We play _____ at recess.", "hint": "With each other"},
        ]
    }
]

def add_test_wordbanks():
    """Add test wordbanks to Railway PostgreSQL database."""
    print("=" * 70)
    print("🐝 Adding Test Wordbanks to Railway PostgreSQL")
    print("=" * 70)
    
    try:
        # Connect to Railway PostgreSQL
        print("\n🔧 Connecting to Railway PostgreSQL...")
        conn = psycopg2.connect(RAILWAY_DB_URL)
        cursor = conn.cursor()
        print("✅ Connected to Railway PostgreSQL")
        
        # Check if wordbank_storage table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'wordbank_storage'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("\n❌ ERROR: wordbank_storage table does not exist!")
            print("Run create_railway_wordbank_table.py first.")
            return
        
        print(f"\n📝 Adding {len(TEST_WORDBANKS)} test wordbanks...")
        
        added_count = 0
        for wordbank_data in TEST_WORDBANKS:
            # Generate unique storage_id (UUID)
            storage_id = str(uuid.uuid4())
            words = wordbank_data["words"]
            word_count = len(words)
            
            # Convert words to JSONB format
            words_json = json.dumps(words)
            
            # Insert into database
            cursor.execute("""
                INSERT INTO wordbank_storage 
                (storage_id, words_data, word_count, user_id, created_at, last_accessed)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                storage_id,
                words_json,
                word_count,
                None,  # No user_id (guest wordbank)
                datetime.utcnow(),
                datetime.utcnow()
            ))
            
            added_count += 1
            print(f"  ✅ Added: {wordbank_data['name']} ({word_count} words) - storage_id: {storage_id[:8]}...")
        
        # Commit all inserts
        conn.commit()
        
        print(f"\n✅ Successfully added {added_count} test wordbanks!")
        
        # Show current database stats
        cursor.execute("SELECT COUNT(*) FROM wordbank_storage")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(word_count) FROM wordbank_storage")
        total_words = cursor.fetchone()[0] or 0
        
        print("\n" + "=" * 70)
        print("📊 Railway WordBank Storage Statistics")
        print("=" * 70)
        print(f"Total Wordbanks: {total_count}")
        print(f"Total Words: {total_words}")
        print("=" * 70)
        
        # Show sample of stored wordbanks
        print("\n📋 Sample Wordbanks:")
        cursor.execute("""
            SELECT storage_id, word_count, created_at 
            FROM wordbank_storage 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        for row in cursor.fetchall():
            storage_id, word_count, created_at = row
            print(f"  • {storage_id[:12]}... - {word_count} words - {created_at}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("\n✅ Done! Test wordbanks are ready for testing.")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_test_wordbanks()
