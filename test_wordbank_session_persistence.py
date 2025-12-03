"""
Test wordbank session persistence fix
Verifies that wordbank_storage_id persists across requests
"""
import requests
import time

BASE_URL = "http://localhost:5000"

def test_wordbank_persistence():
    """Test that wordbank session persists across multiple requests"""
    
    print("🧪 Testing wordbank session persistence...")
    print("=" * 60)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Step 1: Upload a small word list
    print("\n1️⃣ Uploading word list...")
    payload = {
        'rows': [
            {'word': 'bee', 'sentence': 'The bee buzzes.', 'hint': 'insect'},
            {'word': 'honey', 'sentence': 'Bees make honey.', 'hint': 'sweet'},
            {'word': 'comb', 'sentence': 'The honey comb.', 'hint': 'structure'},
            {'word': 'hive', 'sentence': 'Bees live in a hive.', 'hint': 'home'},
            {'word': 'buzz', 'sentence': 'Listen to the buzz.', 'hint': 'sound'}
        ]
    }
    
    try:
        r = session.post(f"{BASE_URL}/api/wordbank", json=payload, timeout=10)
        if r.status_code != 200:
            print(f"❌ Upload failed: {r.status_code}")
            print(f"Response: {r.text[:500]}")
            return False
        
        data = r.json()
        print(f"✅ Upload successful: {data}")
        
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False
    
    # Step 2: Wait a moment to simulate navigation delay
    print("\n2️⃣ Waiting 1 second (simulating navigation delay)...")
    time.sleep(1)
    
    # Step 3: Retrieve wordbank (simulates what /quiz route does)
    print("\n3️⃣ Retrieving wordbank...")
    try:
        r = session.get(f"{BASE_URL}/api/wordbank", timeout=10)
        if r.status_code != 200:
            print(f"❌ Retrieve failed: {r.status_code}")
            print(f"Response: {r.text[:500]}")
            return False
        
        data = r.json()
        # Check both 'words' and 'rows' keys (API returns 'rows' for some endpoints)
        words = data.get('words') or data.get('rows') or []
        word_count = len(words)
        
        if word_count == 0:
            print(f"❌ FAILED: Retrieved 0 words (session lost!)")
            print(f"Response: {data}")
            return False
        elif word_count != 5:
            print(f"⚠️ WARNING: Expected 5 words, got {word_count}")
            print(f"Response: {data}")
            return False
        else:
            print(f"✅ SUCCESS: Retrieved {word_count} words correctly")
            print(f"Words: {[w['word'] for w in words[:3]]}...")
        
    except Exception as e:
        print(f"❌ Retrieve error: {e}")
        return False
    
    # Step 4: Call /api/next to verify quiz can start
    print("\n4️⃣ Testing quiz start with /api/next...")
    try:
        r = session.post(f"{BASE_URL}/api/next", json={}, timeout=10)
        if r.status_code != 200:
            print(f"❌ Quiz start failed: {r.status_code}")
            print(f"Response: {r.text[:500]}")
            return False
        
        data = r.json()
        if 'error' in data:
            print(f"❌ Quiz start error: {data['error']}")
            print(f"Message: {data.get('message', 'N/A')}")
            return False
        
        word_info = data.get('word_info') or data.get('word')
        if word_info:
            word = word_info if isinstance(word_info, str) else word_info.get('word', 'unknown')
            print(f"✅ Quiz started successfully! First word: '{word}'")
        else:
            print(f"⚠️ Quiz started but no word info in response")
            print(f"Response: {data}")
        
    except Exception as e:
        print(f"❌ Quiz start error: {e}")
        return False
    
    # Step 5: Clean up
    print("\n5️⃣ Cleaning up...")
    try:
        r = session.post(f"{BASE_URL}/api/wordbank/clear", timeout=10)
        if r.status_code == 200:
            print("✅ Cleanup successful")
        else:
            print(f"⚠️ Cleanup returned {r.status_code} (non-fatal)")
    except Exception as e:
        print(f"⚠️ Cleanup error: {e} (non-fatal)")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - Session persistence working correctly!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    import sys
    
    # Check if server is specified
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
    
    print(f"Testing against: {BASE_URL}")
    print("Make sure the server is running first!\n")
    
    success = test_wordbank_persistence()
    sys.exit(0 if success else 1)
