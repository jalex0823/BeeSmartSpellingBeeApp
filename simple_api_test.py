import requests
import time

# Create session
session = requests.Session()

# Wait for app to be ready
time.sleep(1)

print("🔄 Testing upload to running Flask app...")

# Upload
try:
    with open('PlainWordList50.txt', 'rb') as f:
        files = {'file': ('PlainWordList50.txt', f, 'text/plain')}
        response = session.post('http://127.0.0.1:5000/api/upload', files=files, timeout=10)
    
    print(f"Upload: {response.status_code} - {response.json()}")
except Exception as e:
    print(f"Upload error: {e}")
    exit(1)

# Check wordbank
try:
    response = session.get('http://127.0.0.1:5000/api/wordbank', timeout=10)
    data = response.json()
    print(f"Wordbank: {len(data['words'])} words")
    print(f"First word: '{data['words'][0]['word']}' → {data['words'][0]['sentence'][:50]}...")
except Exception as e:
    print(f"Wordbank error: {e}")

# Test current word
try:
    response = session.get('http://127.0.0.1:5000/api/current', timeout=10)
    print(f"Current API: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Current word challenge: {data.get('sentence', 'MISSING')[:80]}...")
    else:
        print(f"Current failed: {response.text[:100]}...")
except Exception as e:
    print(f"Current error: {e}")

print("✅ Test complete!")