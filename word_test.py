#!/usr/bin/env python3
"""
Test uploading the 10-word list and see what definitions are generated
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"
session = requests.Session()

print("🐝 Testing 10-Word List Upload and Definition Generation")
print("=" * 60)

# Create test using the provided word list
test_words = """Admire
Brisk
Curious
Dazzle
Eager
Fragile
Glimpse
Humble
Mingle
Timid"""

print("1️⃣  Testing dictionary API first...")
try:
    dict_test = session.get(f"{BASE_URL}/api/test-dictionary")
    print(f"   Dictionary API test: {dict_test.status_code}")
    if dict_test.status_code == 200:
        dict_data = dict_test.json()
        print(f"   Status: {dict_data.get('status')}")
        print(f"   Message: {dict_data.get('message')}")
        if dict_data.get('result'):
            print(f"   Test result: {dict_data['result'].get('definition', 'No definition')}")
    else:
        print(f"   Error: {dict_test.text}")
except Exception as e:
    print(f"   Error testing dictionary: {e}")

print("\n2️⃣  Uploading 10-word list...")
try:
    files = {'file': ('10words.txt', test_words.encode())}
    upload_response = session.post(f"{BASE_URL}/api/upload", files=files)
    
    print(f"   Upload status: {upload_response.status_code}")
    if upload_response.status_code == 200:
        upload_data = upload_response.json()
        print(f"   Words uploaded: {upload_data.get('count', 0)}")
        
        # Wait a moment for enrichment
        time.sleep(1)
        
        print("\n3️⃣  Checking wordbank after upload...")
        wordbank_response = session.get(f"{BASE_URL}/api/wordbank")
        if wordbank_response.status_code == 200:
            wordbank_data = wordbank_response.json()
            words = wordbank_data.get('words', [])
            print(f"   Words in wordbank: {len(words)}")
            
            if words:
                print(f"\n   First word example:")
                first_word = words[0]
                print(f"   - Word: {first_word.get('word')}")
                print(f"   - Sentence: {first_word.get('sentence')}")
                print(f"   - Hint: {first_word.get('hint')}")
                
                print(f"\n4️⃣  Testing /api/next...")
                next_response = session.post(f"{BASE_URL}/api/next")
                if next_response.status_code == 200:
                    next_data = next_response.json()
                    print(f"   Quiz word: {next_data.get('word')}")
                    print(f"   Definition: {next_data.get('definition')}")
                    print(f"   Sentence: {next_data.get('sentence')}")
                    print(f"   Source: {next_data.get('definitionSource')}")
                    
                    if next_data.get('sentence') and 'Practice spelling this' not in next_data.get('sentence', ''):
                        print("   ✅ SUCCESS: Real definition found!")
                    else:
                        print("   ❌ FAIL: Still showing fallback")
                else:
                    print(f"   /api/next failed: {next_response.text}")
        else:
            print(f"   Wordbank check failed: {wordbank_response.text}")
    else:
        print(f"   Upload failed: {upload_response.text}")
        
except Exception as e:
    print(f"❌ Test failed: {e}")

print("\n" + "=" * 60)