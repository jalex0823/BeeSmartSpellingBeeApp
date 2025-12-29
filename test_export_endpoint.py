#!/usr/bin/env python3
"""
Test the new /api/export endpoint for Issue #7
"""
import requests

BASE_URL = "http://localhost:5000"

def test_export_endpoint():
    """Test the export endpoint with both JSON and CSV formats"""
    
    print("\n🧪 Testing /api/export endpoint...")
    print("=" * 60)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Step 1: Clear any existing wordbank
    print("\n1️⃣  Clearing existing wordbank...")
    response = session.post(f"{BASE_URL}/api/clear", json={"confirmed": True})
    print(f"   Status: {response.status_code}")
    
    # Step 2: Upload test words
    print("\n2️⃣  Uploading test word list...")
    test_csv = """word,sentence,hint
apple,I ate a red apple,fruit
banana,Yellow bananas are sweet,fruit
cat,The cat meowed loudly,animal
dog,My dog likes to play,animal
elephant,The elephant is huge,animal"""
    
    files = {"file": ("test_words.csv", test_csv, "text/csv")}
    response = session.post(f"{BASE_URL}/api/upload", files=files)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Words uploaded: {data.get('count', 0)}")
    
    # Step 3: Test JSON export
    print("\n3️⃣  Testing JSON export...")
    response = session.get(f"{BASE_URL}/api/export?format=json")
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('Content-Type')}")
    print(f"   Content-Disposition: {response.headers.get('Content-Disposition')}")
    
    if response.status_code == 200:
        print(f"   ✅ JSON export successful!")
        print(f"   File size: {len(response.content)} bytes")
        # Try to parse JSON
        try:
            import json
            data = json.loads(response.text)
            print(f"   Word count in export: {data.get('word_count', 0)}")
            print(f"   First word: {data['words'][0]['word']}")
        except Exception as e:
            print(f"   ⚠️  Could not parse JSON: {e}")
    else:
        print(f"   ❌ JSON export failed: {response.text}")
    
    # Step 4: Test CSV export
    print("\n4️⃣  Testing CSV export...")
    response = session.get(f"{BASE_URL}/api/export?format=csv")
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('Content-Type')}")
    print(f"   Content-Disposition: {response.headers.get('Content-Disposition')}")
    
    if response.status_code == 200:
        print(f"   ✅ CSV export successful!")
        print(f"   File size: {len(response.content)} bytes")
        print(f"   First 200 characters:")
        print(f"   {response.text[:200]}")
    else:
        print(f"   ❌ CSV export failed: {response.text}")
    
    # Step 5: Test empty wordbank export (should fail gracefully)
    print("\n5️⃣  Testing empty wordbank export...")
    session.post(f"{BASE_URL}/api/clear", json={"confirmed": True})
    response = session.get(f"{BASE_URL}/api/export?format=json")
    print(f"   Status: {response.status_code}")
    if response.status_code == 400:
        print(f"   ✅ Correctly rejected empty wordbank")
        print(f"   Error message: {response.json().get('error')}")
    else:
        print(f"   ⚠️  Expected 400 status, got {response.status_code}")
    
    print("\n" + "=" * 60)
    print("✅ Export endpoint tests completed!")
    print("\nTo test in browser:")
    print(f"   1. Upload words at {BASE_URL}/app")
    print(f"   2. Visit {BASE_URL}/api/export?format=json")
    print(f"   3. Visit {BASE_URL}/api/export?format=csv")

if __name__ == "__main__":
    print("\n🐝 BeeSmart Export Endpoint Test")
    print("Make sure the Flask app is running at http://localhost:5000")
    
    try:
        test_export_endpoint()
    except requests.ConnectionError:
        print("\n❌ ERROR: Could not connect to Flask app")
        print("   Please start the app with: python AjaSpellBApp.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
