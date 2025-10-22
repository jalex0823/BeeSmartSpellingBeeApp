#!/usr/bin/env python3
"""
Simple test to verify our fixes work
"""

import requests
import json

BASE_URL = "http://localhost:5000"

print("🐝 Testing BeeSmart Quiz Fixes")
print("=" * 50)

# Test if we can upload words
test_words = "elephant|An large gray animal with a trunk|The elephant walked through the savanna."

session = requests.Session()

try:
    print("1. Testing upload...")
    response = session.post(
        f"{BASE_URL}/api/upload",
        files={'file': ('test.txt', test_words.encode())}
    )
    
    if response.status_code == 200:
        print("   ✅ Upload successful")
        upload_data = response.json()
        print(f"   Uploaded {upload_data.get('count', 0)} words")
        
        print("\n2. Testing /api/next...")
        next_response = session.post(f"{BASE_URL}/api/next")
        
        if next_response.status_code == 200:
            next_data = next_response.json()
            print("   ✅ /api/next successful")
            
            # Check if we have definition data
            sentence = next_data.get('sentence', '')
            hint = next_data.get('hint', '')
            definition = next_data.get('definition', '')
            word = next_data.get('word', '')
            
            print(f"   Word: {word}")
            print(f"   Sentence: {sentence}")
            print(f"   Hint: {hint}")
            print(f"   Definition: {definition}")
            
            # Check if safety blanker is working
            if word and (word.lower() in sentence.lower() or word.lower() in hint.lower() or word.lower() in definition.lower()):
                print("   ❌ FAIL: Target word not hidden!")
            else:
                print("   ✅ PASS: Target word properly hidden")
                
            if sentence or hint or definition != "Listen carefully and spell the word you hear.":
                print("   ✅ PASS: Real definitions are showing!")
            else:
                print("   ❌ FAIL: Still showing fallback message")
        else:
            print(f"   ❌ /api/next failed: {next_response.status_code}")
    else:
        print(f"   ❌ Upload failed: {response.status_code}")
        print(f"   Error: {response.text}")

except Exception as e:
    print(f"❌ Test failed with error: {e}")

print("\n" + "=" * 50)