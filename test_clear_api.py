"""Test the new clear API with authorization"""
import urllib.request
import json

def test_clear_api():
    print("Testing Clear API with Authorization")
    print("=" * 50)
    
    # Test 1: Try without authorization (should fail)
    print("\n1. Testing without authorization (should fail):")
    try:
        data = json.dumps({}).encode('utf-8')
        req = urllib.request.Request(
            'http://127.0.0.1:5000/api/clear',
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode('utf-8'))
        print(f"❌ Unexpected success: {result}")
    except urllib.error.HTTPError as e:
        error_data = json.loads(e.read().decode('utf-8'))
        print(f"✅ Expected error: {error_data}")
    
    # Test 2: Try with authorization (should succeed)
    print("\n2. Testing with authorization (should succeed):")
    try:
        data = json.dumps({"confirmed": True}).encode('utf-8')
        req = urllib.request.Request(
            'http://127.0.0.1:5000/api/clear',
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode('utf-8'))
        print(f"✅ Success: {result}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print("\n" + "=" * 50)
    print("Test complete!")

if __name__ == "__main__":
    test_clear_api()