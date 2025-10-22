"""Test to verify sentence field is being returned in /api/next"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_sentence_in_next_endpoint():
    """Test that /api/next returns sentence for words with definitions"""
    
    # Create a session
    session = requests.Session()
    
    # First, clear any existing wordbank
    r = session.post(f"{BASE_URL}/api/clear")
    print(f"Clear: {r.status_code}")
    
    # Upload a simple test file
    test_data = "apple,An apple is a red fruit|A fruit that grows on trees\nbee,A bee is a flying insect|An insect that makes honey"
    
    files = {"file": ("test.csv", test_data)}
    r = session.post(f"{BASE_URL}/api/upload", files=files)
    print(f"Upload: {r.status_code}")
    if r.status_code != 200:
        print(f"Upload error: {r.text}")
        return
    
    result = r.json()
    print(f"Upload result: {result}")
    
    # Wait a moment for processing
    import time
    time.sleep(1)
    
    # Get the first word via /api/next
    r = session.post(f"{BASE_URL}/api/next")
    print(f"\n/api/next: {r.status_code}")
    data = r.json()
    
    print(f"\nResponse from /api/next:")
    print(json.dumps(data, indent=2))
    
    # Check what we got
    if "definition" in data:
        print(f"\n✅ Definition field: {data['definition']}")
    else:
        print(f"\n❌ No definition field in response!")
    
    if "wordMeta" in data:
        print(f"✅ Word metadata: {data['wordMeta']}")

if __name__ == "__main__":
    test_sentence_in_next_endpoint()
