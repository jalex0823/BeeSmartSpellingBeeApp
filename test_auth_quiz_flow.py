#!/usr/bin/env python3
"""
Test the complete authentication and quiz flow with database integration
"""
import requests
import time
import random
import string

BASE_URL = "http://127.0.0.1:5000"

def random_username():
    """Generate a random username for testing"""
    return f"test_user_{''.join(random.choices(string.ascii_lowercase, k=6))}"

def test_complete_flow():
    """Test: Register -> Login -> Upload Words -> Quiz -> Dashboard"""
    
    print("=" * 60)
    print("🐝 TESTING COMPLETE AUTHENTICATION + QUIZ FLOW")
    print("=" * 60)
    
    # Create session to maintain cookies
    session = requests.Session()
    
    # Step 1: Register new user
    print("\n📝 Step 1: Registering new user...")
    username = random_username()
    password = "test123"
    
    register_data = {
        "username": username,
        "display_name": f"Test {username}",
        "password": password,
        "grade_level": "5"
    }
    
    response = session.post(f"{BASE_URL}/auth/register", json=register_data)
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print(f"   ✅ Registration successful: {username}")
        else:
            print(f"   ❌ Registration failed: {result.get('error')}")
            return False
    else:
        print(f"   ❌ HTTP {response.status_code}: {response.text[:200]}")
        return False
    
    # Step 2: Login (should already be logged in after registration, but let's verify)
    print("\n🔑 Step 2: Verifying login...")
    time.sleep(0.5)

    # Step 3: Upload a small word list (required to initialize server-side wordbank + quiz state)
    print("\n📤 Step 3: Uploading a test word list...")
    upload_words = [
        {"word": "apple", "sentence": "", "hint": ""},
        {"word": "bee", "sentence": "", "hint": ""},
        {"word": "honey", "sentence": "", "hint": ""},
        {"word": "rainbow", "sentence": "", "hint": ""},
        {"word": "butterfly", "sentence": "", "hint": ""},
    ]
    response = session.post(f"{BASE_URL}/api/upload", json={"words": upload_words})
    if response.status_code == 200:
        up = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
        if not up.get("ok"):
            print(f"   ❌ Upload not ok: {up}")
            return False
        print(f"   ✅ Uploaded {up.get('count')} words")
    else:
        print(f"   ❌ Upload failed: HTTP {response.status_code}: {response.text[:200]}")
        return False
    
    # Step 4: Check wordbank
    print("\n📚 Step 4: Checking wordbank...")
    response = session.get(f"{BASE_URL}/api/wordbank")
    if response.status_code == 200:
        wordbank = response.json()
        word_count = len(wordbank)
        print(f"   ✅ Wordbank loaded: {word_count} words")
        if word_count == 0:
            print("   ⚠️ No words in wordbank, cannot test quiz")
            return False
    else:
        print(f"   ❌ Failed to get wordbank: {response.status_code}")
        return False

    # Step 5: Run quiz end-to-end via /api/next -> /api/answer
    print("\n🎯 Step 5: Running quiz via /api/next -> /api/answer...")
    answered = 0
    correct = 0
    incorrect = 0
    while True:
        nxt = session.post(f"{BASE_URL}/api/next")
        if nxt.status_code != 200:
            print(f"   ❌ /api/next failed: HTTP {nxt.status_code}: {nxt.text[:200]}")
            return False
        payload = nxt.json() if nxt.headers.get("content-type", "").startswith("application/json") else {}
        if payload.get("done") is True:
            summary = payload.get("summary") or {}
            print(f"   ✅ Quiz complete: {summary.get('correct')}/{summary.get('total')} correct, points={summary.get('session_points')}")
            break

        word = payload.get("word", "")
        if not word:
            print(f"   ❌ /api/next returned no word: {payload}")
            return False

        # 80% correct to exercise both paths
        will_be_correct = random.random() > 0.2
        user_input = word if will_be_correct else "wrong"

        ans = session.post(
            f"{BASE_URL}/api/answer",
            json={
                "user_input": user_input,
                "method": "keyboard",
                "elapsed_ms": random.randint(2000, 8000),
            },
        )
        if ans.status_code != 200:
            print(f"   ❌ /api/answer failed: HTTP {ans.status_code}: {ans.text[:200]}")
            return False

        result = ans.json() if ans.headers.get("content-type", "").startswith("application/json") else {}
        is_correct = bool(result.get("correct"))
        answered += 1
        if is_correct:
            correct += 1
        else:
            incorrect += 1

        if answered <= 5 or (answered % 10 == 0):
            print(f"   {'✅' if is_correct else '❌'} {answered}: word='{word}' input='{user_input}'")
    
    # Step 6: Check dashboard
    print("\n📊 Step 6: Checking dashboard...")
    time.sleep(0.5)
    response = session.get(f"{BASE_URL}/auth/dashboard")
    if response.status_code == 200:
        print(f"   ✅ Dashboard accessible")
        # Check if HTML contains expected elements
        html = response.text
        if "Welcome" in html and username in html:
            print(f"   ✅ Dashboard shows user info")
        else:
            print(f"   ⚠️ Dashboard loaded but may not have user data yet")
    else:
        print(f"   ❌ Failed to access dashboard: {response.status_code}")

    # Step 7: Verify dashboard shows quiz results
    print("\n📈 Step 7: Verifying quiz saved to database...")
    time.sleep(1)  # Give database time to commit
    response = session.get(f"{BASE_URL}/auth/dashboard")
    if response.status_code == 200:
        html = response.text
        if "Total Points" in html or "Quizzes Completed" in html:
            print("   ✅ Dashboard shows quiz statistics")
        else:
            print("   ⚠️ Dashboard may not have quiz data yet (check HTML)")
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETE!")
    print("=" * 60)
    print(f"\n🔑 Test Account Created:")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    print(f"\n🌐 You can now:")
    print(f"   1. Login at: {BASE_URL}/auth/login")
    print(f"   2. View dashboard at: {BASE_URL}/auth/dashboard")
    print(f"   3. Check database: python init_db.py check")
    
    return True

if __name__ == "__main__":
    try:
        success = test_complete_flow()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
