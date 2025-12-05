"""Clear session and upload fresh test words"""
import requests

session = requests.Session()

print("Step 1: Clearing quiz session...")
try:
    response = session.post('http://localhost:5000/api/clear')
    print(f"Clear response: {response.status_code} - {response.json()}")
except Exception as e:
    print(f"Clear error: {e}")

print("\nStep 2: Uploading fresh words (correct format)...")
upload_data = {'words': ['apple', 'bee', 'cat']}
try:
    response = session.post('http://localhost:5000/api/upload-manual-words', json=upload_data)
    print(f"Upload response: {response.status_code}")
    if response.status_code == 200:
        print(f"Success: {response.json()}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Upload error: {e}")

print("\nStep 3: Testing /api/next...")
try:
    response = session.post('http://localhost:5000/api/next')
    if response.status_code == 200:
        data = response.json()
        print(f"✅ First word loaded successfully!")
        print(f"   Word: {data.get('word')}")
        print(f"   Sentence: {data.get('sentence')[:50]}..." if data.get('sentence') else "   No sentence")
        print(f"   Definition type: {type(data.get('definition')).__name__}")
        
        if isinstance(data.get('definition'), dict):
            print(f"   ❌ Still a dict: {data.get('definition')}")
        else:
            print(f"   ✅ Correctly a string!")
    else:
        print(f"Error {response.status_code}: {response.text}")
except Exception as e:
    print(f"API error: {e}")

print("\nDone! Now refresh your browser and try the quiz.")
