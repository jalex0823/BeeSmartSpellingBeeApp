"""Simple test to check session persistence"""
import requests
import json

BASE_URL = "http://localhost:5000"
session = requests.Session()

print("1. Uploading 2 words...")
upload_resp = session.post(f"{BASE_URL}/api/upload-manual-words", json={"words": ["test", "quiz"]})
print(f"   Upload: {upload_resp.status_code}")

print("\n2. Getting first word...")
next_resp = session.post(f"{BASE_URL}/api/next")
next_data = next_resp.json()
word = next_data.get("word")
print(f"   Word: {word}")
print(f"   Progress before: {json.dumps(next_data.get('progress'), indent=2)}")

print("\n3. Submitting correct answer...")
answer_resp = session.post(f"{BASE_URL}/api/answer", json={
    "user_input": word,
    "method": "typed",
    "elapsed_ms": 5000
})
answer_data = answer_resp.json()
print(f"   Result: {answer_data.get('result')}")
print(f"   Progress after: {json.dumps(answer_data.get('progress'), indent=2)}")

print("\n4. Checking quiz status...")
status_resp = session.get(f"{BASE_URL}/api/quiz/status")
status_data = status_resp.json()
print(f"   Status: {json.dumps(status_data, indent=2)}")

if status_data.get("can_resume"):
    print("\n✅ SUCCESS: Modal would show (progress detected)")
else:
    print("\n❌ FAIL: Modal would NOT show")
    print(f"   Expected: can_resume=True (because correct={answer_data.get('progress', {}).get('correct')} > 0)")
    print(f"   Got: can_resume=False")
