import requests

# Create a session to maintain cookies
session = requests.Session()

print("🔄 Testing PlainWordList50.txt complete workflow with sessions...")

print("1️⃣ Uploading PlainWordList50.txt...")
try:
    with open('PlainWordList50.txt', 'rb') as f:
        files = {'file': ('PlainWordList50.txt', f, 'text/plain')}
        response = session.post('http://127.0.0.1:5000/api/upload', files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Upload success: {result}")
    else:
        print(f"❌ Upload failed: {response.text}")
        exit(1)

except Exception as e:
    print(f"❌ Upload error: {e}")
    exit(1)

print("\n2️⃣ Checking wordbank...")
try:
    response = session.get('http://127.0.0.1:5000/api/wordbank')
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Wordbank contains {len(data['words'])} words")
        
        # Display first few words with their full data
        for i, word in enumerate(data['words'][:3]):
            print(f"   {i+1}. Word: '{word['word']}'")
            print(f"      Sentence: '{word.get('sentence', 'MISSING')}'")
            print(f"      Hint: '{word.get('hint', 'MISSING')}'")
            print()
    else:
        print(f"❌ Failed to get wordbank: {response.text}")
        exit(1)

except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

print("3️⃣ Testing current word (should work after upload)...")
try:
    response = session.post('http://127.0.0.1:5000/api/next', json={})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}...")

    if response.status_code == 200:
        data = response.json()
        if data.get('done') is True:
            print("✅ Quiz is already complete (server returned done=true)")
            summary = data.get('summary') or {}
            print(f"   Summary: {summary.get('correct', 0)}/{summary.get('total', 0)} correct")
        else:
            print(f"✅ Current challenge: {data.get('sentence', 'MISSING')}")
            print(f"   Hint: {data.get('hint', 'MISSING')}")
            print(f"   Word length: {data.get('word_length', 'MISSING')}")
    else:
        print("❌ Failed to fetch next quiz word via /api/next")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n🎯 The issue was session management!")
print("   When you upload via browser, make sure to use the same session/tab")
print("   The Flask app uses sessions to store your word list")
print("\n🔗 Test in browser: http://127.0.0.1:5000/simple-quiz")