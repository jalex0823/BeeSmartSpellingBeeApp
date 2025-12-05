"""Test what /api/next actually returns"""
import requests
import json

# Connect to the already-running Flask app
session = requests.Session()

print("Testing /api/next endpoint...")
print("="*60)

# Upload test words
upload_data = {'words': 'apple\nbee'}
try:
    upload_response = session.post('http://localhost:5000/api/upload-manual-words', json=upload_data)
    print(f"Upload: {upload_response.status_code}")
    if upload_response.status_code != 200:
        print(f"Upload failed: {upload_response.text}")
except Exception as e:
    print(f"Upload error: {e}")

# Get first word
try:
    next_response = session.post('http://localhost:5000/api/next')
    print("\n" + "="*60)
    print("FIRST WORD - /api/next response:")
    print("="*60)
    
    if next_response.status_code == 200:
        data = next_response.json()

        print(f"word: {repr(data.get('word'))} (type: {type(data.get('word')).__name__})")
        print(f"sentence: {repr(data.get('sentence'))} (type: {type(data.get('sentence')).__name__})")
        print(f"definition: {repr(data.get('definition'))} (type: {type(data.get('definition')).__name__})")
        print(f"hint: {repr(data.get('hint'))} (type: {type(data.get('hint')).__name__})")
        print(f"index: {data.get('index')}")
        print(f"total: {data.get('total')}")
        
        # Check if definition is a dict (the bug)
        if isinstance(data.get('definition'), dict):
            print("\n❌ BUG FOUND: definition is a dict instead of string!")
            print(f"   Dict contents: {data.get('definition')}")
        else:
            print("\n✅ definition is correctly a string")
    else:
        print(f"Error {next_response.status_code}: {next_response.text}")
        
except Exception as e:
    print(f"API error: {e}")
