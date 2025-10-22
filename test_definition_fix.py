#!/usr/bin/env python3
"""Test to verify definition/sentence issue is fixed"""

import sys
import os
sys.path.insert(0, '.')

# Set environment to suppress emoji output
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Minimal imports to avoid emoji in startup
from AjaSpellBApp import app, get_word_info
import json

print("=" * 70)
print("TESTING: Definition/Sentence Issue Fix")
print("=" * 70)

# Test 1: Check get_word_info() behavior
print("\n[Test 1] Testing get_word_info() function")
print("-" * 70)

with app.test_request_context():
    # Clear any existing cache for test
    test_words = ["brisk", "running", "happy"]
    
    for word in test_words:
        result = get_word_info(word)
        print(f"\n  Word: {word}")
        print(f"  Result: {result[:100]}...")
        
        # Check that it's NOT a placeholder
        is_placeholder = "A placeholder definition" in result
        if is_placeholder:
            print(f"  ❌ FAILED: Got placeholder definition!")
        else:
            print(f"  ✅ PASSED: Got real definition (not placeholder)")
        
        # Check that it contains the fill-in-the-blank format
        if "Fill in the blank:" in result:
            print(f"  ✅ PASSED: Contains fill-in-the-blank format")
        else:
            print(f"  ❌ FAILED: Missing fill-in-the-blank format")

# Test 2: Check upload with words that need auto-definition
print("\n\n[Test 2] Testing upload with auto-definition words")
print("-" * 70)

with app.test_client() as client:
    # Create a test CSV
    csv_data = b"word\napple\nbee\nbrisk\nrunning"
    
    # Upload
    response = client.post(
        '/api/upload',
        data={'file': (csv_data, 'test.csv')},
        content_type='multipart/form-data'
    )
    
    print(f"  Upload response: {response.status_code}")
    if response.status_code == 200:
        print(f"  ✅ Upload successful")
    
    # Check wordbank
    with client.session_transaction() as sess:
        print(f"  Session keys: {list(sess.keys())}")
    
    # Get wordbank data
    response = client.get('/api/wordbank')
    if response.status_code == 200:
        wordbank = response.get_json()
        print(f"  ✅ Got wordbank with {len(wordbank)} words")
        
        for word_rec in wordbank[:3]:
            word = word_rec.get('word', 'N/A')
            sentence = word_rec.get('sentence', 'N/A')[:70]
            print(f"\n    [{word}]")
            print(f"      sentence: {sentence}...")
            
            # Check for placeholders
            if "A placeholder definition" in sentence:
                print(f"      ❌ FAILED: Contains placeholder!")
            else:
                print(f"      ✅ PASSED: No placeholder detected")
    else:
        print(f"  ❌ Failed to get wordbank: {response.status_code}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
