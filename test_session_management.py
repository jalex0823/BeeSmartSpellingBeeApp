"""
Test session management and resume modal logic
Verifies that fresh uploads don't show modal, but quizzes with progress do.
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_fresh_upload_no_modal():
    """Test that uploading new words creates fresh quiz state without showing modal"""
    print("\n" + "="*70)
    print("TEST 1: Fresh Upload Should Not Show Modal")
    print("="*70)
    
    session = requests.Session()
    
    # Step 1: Upload 2 test words
    print("\n📤 Uploading 2 test words...")
    upload_data = {
        "words": ["apple", "banana"]
    }
    
    resp = session.post(f"{BASE_URL}/api/upload-manual-words", json=upload_data)
    print(f"Upload response: {resp.status_code}")
    if resp.status_code == 200:
        print("✅ Words uploaded successfully")
    else:
        print(f"❌ Upload failed: {resp.text}")
        return
    
    # Step 2: Check quiz status (should NOT be resumable)
    print("\n🔍 Checking quiz status...")
    status_resp = session.get(f"{BASE_URL}/api/quiz/status")
    status = status_resp.json()
    print(f"Quiz status: {json.dumps(status, indent=2)}")
    
    if status.get("can_resume"):
        print("❌ FAIL: Modal would show on fresh upload (no progress yet)")
        print(f"   Stats: correct={status.get('correct')}, incorrect={status.get('incorrect')}, index={status.get('index')}")
        return False
    else:
        print("✅ PASS: No modal shown (fresh quiz, no progress)")
        return True

def test_progress_shows_modal():
    """Test that answering a question makes the modal appear on refresh"""
    print("\n" + "="*70)
    print("TEST 2: Quiz With Progress Should Show Modal")
    print("="*70)
    
    session = requests.Session()
    
    # Step 1: Upload 2 test words
    print("\n📤 Uploading 2 test words...")
    upload_data = {
        "words": ["hello", "world"]
    }
    
    resp = session.post(f"{BASE_URL}/api/upload-manual-words", json=upload_data)
    if resp.status_code != 200:
        print(f"❌ Upload failed: {resp.text}")
        return False
    print("✅ Words uploaded")
    
    # Step 2: Get first word
    print("\n📖 Loading first word...")
    next_resp = session.post(f"{BASE_URL}/api/next")
    next_data = next_resp.json()
    word = next_data.get("word", "")
    print(f"Current word: {word}")
    print(f"Initial stats: correct={next_data.get('progress', {}).get('correct')}, incorrect={next_data.get('progress', {}).get('incorrect')}")
    
    # Step 3: Answer first question
    print("\n✍️ Submitting answer...")
    answer_resp = session.post(f"{BASE_URL}/api/answer", json={
        "user_input": word,  # Correct answer
        "method": "typed",
        "elapsed_ms": 5000
    })
    answer_data = answer_resp.json()
    print(f"Answer result: {answer_data.get('result')}")
    print(f"Updated stats: correct={answer_data.get('progress', {}).get('correct')}, incorrect={answer_data.get('progress', {}).get('incorrect')}")
    
    # Step 4: Check quiz status (SHOULD be resumable now)
    print("\n🔍 Checking quiz status after answering...")
    status_resp = session.get(f"{BASE_URL}/api/quiz/status")
    status = status_resp.json()
    print(f"Quiz status: {json.dumps(status, indent=2)}")
    
    if status.get("can_resume"):
        print("✅ PASS: Modal would show (quiz has progress)")
        print(f"   Stats: correct={status.get('correct')}, incorrect={status.get('incorrect')}, index={status.get('index')}/{status.get('total')}")
        return True
    else:
        print("❌ FAIL: Modal would NOT show despite having progress")
        return False

def test_restart_clears_stats():
    """Test that clicking Restart button fully clears all stats"""
    print("\n" + "="*70)
    print("TEST 3: Restart Should Clear All Stats")
    print("="*70)
    
    session = requests.Session()
    
    # Setup: Upload and answer 1 question
    print("\n📤 Setting up quiz with progress...")
    session.post(f"{BASE_URL}/api/upload-manual-words", json={"words": ["cat", "dog"]})
    next_resp = session.post(f"{BASE_URL}/api/next")
    word = next_resp.json().get("word")
    session.post(f"{BASE_URL}/api/answer", json={"user_input": word, "method": "typed", "elapsed_ms": 3000})
    
    # Check stats before reset
    status_before = session.get(f"{BASE_URL}/api/quiz/status").json()
    print(f"Stats before reset: correct={status_before.get('correct')}, incorrect={status_before.get('incorrect')}")
    
    # Call reset endpoint
    print("\n🔄 Calling /api/quiz/reset...")
    reset_resp = session.post(f"{BASE_URL}/api/quiz/reset")
    print(f"Reset response: {reset_resp.status_code}")
    
    # Check stats after reset
    status_after = session.get(f"{BASE_URL}/api/quiz/status").json()
    print(f"Stats after reset: {json.dumps(status_after, indent=2)}")
    
    # Should NOT be resumable (fresh state)
    if not status_after.get("can_resume"):
        print("✅ PASS: Stats fully cleared, no modal would show")
        return True
    else:
        print("❌ FAIL: Stats not cleared properly")
        print(f"   Remaining stats: correct={status_after.get('correct')}, incorrect={status_after.get('incorrect')}")
        return False

if __name__ == "__main__":
    print("\n🐝 BeeSmart Session Management Test Suite")
    print("Testing resume modal logic and quiz state management\n")
    
    results = []
    
    # Run all tests
    results.append(("Fresh upload (no modal)", test_fresh_upload_no_modal()))
    results.append(("Progress exists (show modal)", test_progress_shows_modal()))
    results.append(("Restart clears stats", test_restart_clears_stats()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Session management is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Review the output above for details.")
