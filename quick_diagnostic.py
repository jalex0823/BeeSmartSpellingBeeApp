#!/usr/bin/env python3
"""
Quick test to diagnose why definitions aren't showing in the quiz.
This script:
1. Uploads a test word list
2. Checks the API response from /api/next
3. Verifies the word data is stored correctly
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"
SESSION = requests.Session()

print("=" * 60)
print("🐝 BeeSmart Quiz Definition Diagnostic Test")
print("=" * 60)

# Create test word list content
test_words = """elephant|An large gray animal with a long trunk|The elephant walked through the savanna.
butterfly|A flying insect with colorful wings|The butterfly landed on the flower.
bicycle|A vehicle with two wheels|She rode her bicycle to school.
dinosaur|An extinct prehistoric reptile|Scientists study dinosaur fossils.
telescope|An instrument for viewing distant stars|I looked through the telescope at the moon."""

print("\n1️⃣  Uploading test word list...")

# Upload the file
files = {'file': ('test_words.txt', test_words.encode())}
upload_response = SESSION.post(
    f"{BASE_URL}/api/upload",
    files=files
)

print(f"   Upload status: {upload_response.status_code}")
if upload_response.status_code != 200:
    print(f"   Error: {upload_response.text}")
    exit(1)

upload_data = upload_response.json()
print(f"   Uploaded {upload_data.get('count', 0)} words")
print(f"   Storage ID: {upload_data.get('storage_id', 'N/A')}")

# Wait a moment for session to settle
time.sleep(0.5)

print("\n2️⃣  Checking /api/wordbank...")

# Get wordbank to verify it's stored
wordbank_response = SESSION.get(f"{BASE_URL}/api/wordbank")
wordbank_data = wordbank_response.json()

print(f"   Status: {wordbank_response.status_code}")
print(f"   Word count: {len(wordbank_data.get('words', []))}")

if len(wordbank_data.get('words', [])) > 0:
    first_word = wordbank_data['words'][0]
    print(f"\n   First word data:")
    print(f"   - Word: {first_word.get('word')}")
    print(f"   - Sentence: {first_word.get('sentence')}")
    print(f"   - Hint: {first_word.get('hint')}")
    print(f"   - Definition: {first_word.get('definition')}")

print("\n3️⃣  Calling /api/next (first word)...")

# Get the first word via /api/next
next_response = SESSION.post(f"{BASE_URL}/api/next")
next_data = next_response.json()

print(f"   Status: {next_response.status_code}")
print(f"\n   Full /api/next response:")
print(json.dumps(next_data, indent=2))

print("\n" + "=" * 60)
if next_data.get('sentence') or next_data.get('definition') or next_data.get('hint'):
    print("✅ PASS: Definition/sentence data IS being returned by API")
else:
    print("❌ FAIL: Definition/sentence data is EMPTY from API")
print("=" * 60)
