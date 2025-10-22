#!/usr/bin/env python3
"""Debug test to see what's stored in wordbank"""
import requests
import json

BASE_URL = "http://localhost:5000"

session = requests.Session()

# Clear
r = session.post(f"{BASE_URL}/api/clear")
print(f"Clear: {r.status_code}")

# Upload test CSV
test_csv = """word,definition,sentence
apple,A red fruit,Apples grow on trees
bee,An insect that makes honey,The bee buzzed around the flower
brisk,Quick and energetic,He took a brisk walk this morning"""

files = {"file": ("test.csv", test_csv)}
r = session.post(f"{BASE_URL}/api/upload", files=files)
print(f"Upload: {r.status_code}")
print(f"Upload response: {r.json()}")

import time
time.sleep(2)

# Check wordbank
r = session.get(f"{BASE_URL}/api/wordbank")
if r.status_code == 200:
    wordbank = r.json()
    print(f"\n✅ Wordbank retrieved ({len(wordbank)} words):")
    for i, word in enumerate(wordbank):
        print(f"\n  [{i}] {word.get('word', 'N/A')}")
        print(f"      sentence: {word.get('sentence', 'N/A')[:80]}...")
        print(f"      hint: {word.get('hint', 'N/A')}")
else:
    print(f"❌ Failed to get wordbank: {r.status_code}")

# Call /api/next
r = session.post(f"{BASE_URL}/api/next")
print(f"\n/api/next response:")
print(json.dumps(r.json(), indent=2))
