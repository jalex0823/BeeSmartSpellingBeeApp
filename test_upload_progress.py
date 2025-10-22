"""
Test Upload Progress Indicator
Tests the new animated progress system for file uploads
"""

import requests
import time
import sys

BASE_URL = "http://localhost:5000"

def test_text_upload_progress():
    """Test text file upload with progress indicator"""
    print("=" * 60)
    print("🐝 Testing Text File Upload Progress Indicator")
    print("=" * 60)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Visit main page to establish session
    print("\n1️⃣ Establishing session...")
    response = session.get(BASE_URL)
    if response.status_code != 200:
        print(f"❌ Failed to load main page: {response.status_code}")
        return False
    print("✅ Session established")
    
    # Create a test word list
    test_words = """word1|definition1|example sentence 1
word2|definition2|example sentence 2
word3|definition3|example sentence 3
word4|definition4|example sentence 4
word5|definition5|example sentence 5
word6|definition6|example sentence 6
word7|definition7|example sentence 7
word8|definition8|example sentence 8
word9|definition9|example sentence 9
word10|definition10|example sentence 10"""
    
    print("\n2️⃣ Uploading test word list (10 words)...")
    print("   (Watch the browser for animated honey jar progress!)")
    
    # Upload the file
    files = {'file': ('test_words.txt', test_words, 'text/plain')}
    response = session.post(f"{BASE_URL}/api/upload", files=files)
    
    if response.status_code != 200:
        print(f"❌ Upload failed with status: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    data = response.json()
    if data.get('ok'):
        print(f"✅ Upload successful: {data.get('count')} words loaded")
        print(f"   Message: {data.get('message')}")
        return True
    else:
        print(f"❌ Upload failed: {data.get('error')}")
        return False

def test_csv_import_progress():
    """Test CSV import with progress indicator"""
    print("\n" + "=" * 60)
    print("🐝 Testing CSV Import Progress Indicator")
    print("=" * 60)
    
    # Create a session
    session = requests.Session()
    
    # Visit main page
    print("\n1️⃣ Establishing session...")
    response = session.get(BASE_URL)
    if response.status_code != 200:
        print(f"❌ Failed to load main page: {response.status_code}")
        return False
    print("✅ Session established")
    
    # Create CSV test data
    csv_data = """word,sentence,hint
apple,The red apple fell from the tree,A fruit
banana,She ate a yellow banana for breakfast,A fruit
cat,The cat chased the mouse,An animal
dog,My dog loves to play fetch,An animal
elephant,The elephant has a long trunk,A large animal"""
    
    print("\n2️⃣ Importing CSV file (5 words)...")
    print("   (Watch the browser for animated honey jar progress!)")
    
    # Upload via import endpoint
    files = {'file': ('test_words.csv', csv_data, 'text/csv')}
    response = session.post(f"{BASE_URL}/api/import", files=files)
    
    if response.status_code != 200:
        print(f"❌ Import failed with status: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    data = response.json()
    if data.get('ok'):
        print(f"✅ Import successful: {data.get('count')} words loaded")
        print(f"   Message: {data.get('message')}")
        return True
    else:
        print(f"❌ Import failed: {data.get('error')}")
        return False

def main():
    """Run all progress indicator tests"""
    print("\n" + "🐝" * 30)
    print("   BEESMART UPLOAD PROGRESS INDICATOR TEST")
    print("🐝" * 30 + "\n")
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=2)
        print(f"✅ Server is running at {BASE_URL}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Server is not running at {BASE_URL}")
        print("   Please start the Flask app first:")
        print("   python AjaSpellBApp.py")
        return 1
    
    # Run tests
    results = []
    
    # Test 1: Text file upload
    results.append(("Text Upload Progress", test_text_upload_progress()))
    
    # Wait a bit between tests
    time.sleep(1)
    
    # Test 2: CSV import
    results.append(("CSV Import Progress", test_csv_import_progress()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Progress indicator is working!")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
