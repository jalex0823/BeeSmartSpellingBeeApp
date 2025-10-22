"""Test script to verify saved word lists are saving current wordbank, not defaults"""
import sys
import os

# Prevent Flask app from auto-starting
os.environ['FLASK_RUN_FROM_CLI'] = 'false'

from AjaSpellBApp import app, db
from models import WordList, WordListItem, User
import json

# Disable Flask debug mode for testing
app.config['DEBUG'] = False
app.config['TESTING'] = True

with app.test_client() as client:
    with app.app_context():
        print("=" * 70)
        print("TESTING SAVED WORD LIST FUNCTIONALITY")
        print("=" * 70)
        
        # Step 1: Upload a custom word list
        print("\n1. Uploading custom 3-word list...")
        custom_words = {
            "words": [
                {"word": "butterfly", "sentence": "The _____ landed on the flower.", "hint": "flying insect"},
                {"word": "telescope", "sentence": "We used a _____ to see the stars.", "hint": "tool for viewing far away"},
                {"word": "rainbow", "sentence": "A colorful _____ appeared after the rain.", "hint": "colorful arc in sky"}
            ]
        }
        
        response = client.post('/api/upload',
            data=json.dumps(custom_words),
            content_type='application/json'
        )
        
        print(f"   Upload status: {response.status_code}")
        upload_data = response.get_json()
        print(f"   Upload response: {upload_data}")
        
        if response.status_code != 200:
            print("   ❌ Upload failed!")
            exit(1)
        
        # Step 2: Check what's in the wordbank
        print("\n2. Checking current wordbank...")
        response = client.get('/api/wordbank')
        wordbank_data = response.get_json()
        print(f"   Wordbank count: {len(wordbank_data['words']) if 'words' in wordbank_data else 0}")
        
        if 'words' in wordbank_data:
            print(f"   Words in wordbank:")
            for w in wordbank_data['words']:
                print(f"     - {w['word']}")
        
        # Step 3: Save the list with a custom name
        print("\n3. Saving wordbank as 'My Test List'...")
        save_payload = {
            "list_name": "My Test List",
            "description": "Testing if it saves the correct words"
        }
        
        response = client.post('/api/saved-lists/save',
            data=json.dumps(save_payload),
            content_type='application/json'
        )
        
        print(f"   Save status: {response.status_code}")
        save_data = response.get_json()
        print(f"   Save response: {save_data}")
        
        if response.status_code != 200:
            print("   ❌ Save failed!")
            exit(1)
        
        saved_id = save_data['saved']['id']
        saved_name = save_data['saved']['name']
        saved_count = save_data['saved']['word_count']
        
        print(f"   ✓ Saved list ID: {saved_id}")
        print(f"   ✓ Saved name: '{saved_name}'")
        print(f"   ✓ Word count: {saved_count}")
        
        # Step 4: Verify what was actually saved in the database
        print("\n4. Verifying database contents...")
        word_list = WordList.query.get(saved_id)
        
        if not word_list:
            print("   ❌ WordList not found in database!")
            exit(1)
        
        print(f"   List name: '{word_list.list_name}'")
        print(f"   Word count: {word_list.word_count}")
        print(f"   Description: '{word_list.description}'")
        print(f"   Created by user_id: {word_list.created_by_user_id}")
        
        print(f"\n   Words saved in database:")
        items = WordListItem.query.filter_by(word_list_id=saved_id).order_by(WordListItem.position).all()
        for item in items:
            print(f"     - {item.word}: {item.sentence[:60]}...")
        
        # Step 5: Verification
        print("\n" + "=" * 70)
        print("VERIFICATION RESULTS")
        print("=" * 70)
        
        expected_words = ["butterfly", "telescope", "rainbow"]
        actual_words = [item.word for item in items]
        
        if saved_count == 3:
            print("✅ PASS: Word count is correct (3)")
        else:
            print(f"❌ FAIL: Word count is {saved_count}, expected 3")
        
        if saved_name == "My Test List":
            print("✅ PASS: List name matches input")
        else:
            print(f"❌ FAIL: List name is '{saved_name}', expected 'My Test List'")
        
        if actual_words == expected_words:
            print("✅ PASS: Saved words match uploaded words (not default list)")
        else:
            print(f"❌ FAIL: Words don't match!")
            print(f"   Expected: {expected_words}")
            print(f"   Actual: {actual_words}")
        
        # Check if it's the default 50-word list
        if saved_count == 50:
            print("❌ FAIL: Saved the default 50-word list instead of uploaded words!")
        
        print("\n" + "=" * 70)
        
        # Cleanup
        print("\nCleaning up test data...")
        db.session.delete(word_list)
        db.session.commit()
        print("✓ Test complete")
