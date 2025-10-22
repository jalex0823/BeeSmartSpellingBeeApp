"""
Test Quiz Completion and Stats Tracking
This script tests if quiz sessions are properly completed and stats are updated
"""
import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def test_quiz_completion():
    """Test complete quiz flow with stats tracking"""
    print("=" * 80)
    print("QUIZ COMPLETION & STATS TRACKING TEST")
    print("=" * 80)
    
    # Create session to maintain cookies
    session = requests.Session()
    
    # Step 1: Login as admin
    print("\n1️⃣ Logging in as admin...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    response = session.post(f"{BASE_URL}/auth/login", data=login_data, allow_redirects=False)
    
    if response.status_code in [200, 302]:
        print("   ✅ Login successful")
    else:
        print(f"   ❌ Login failed: {response.status_code}")
        return False
    
    # Step 2: Upload a small word list (3 words for quick test)
    print("\n2️⃣ Uploading test word list...")
    test_words = "apple|A red or green fruit|It grows on trees\ndog|A pet animal|Man's best friend\ncat|A furry pet|Says meow"
    files = {'file': ('test.txt', test_words, 'text/plain')}
    response = session.post(f"{BASE_URL}/api/upload", files=files)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Uploaded {len(data.get('words', []))} words")
    else:
        print(f"   ❌ Upload failed: {response.status_code}")
        return False
    
    # Step 3: Start quiz (loads quiz page)
    print("\n3️⃣ Starting quiz...")
    response = session.get(f"{BASE_URL}/quiz")
    if response.status_code == 200:
        print("   ✅ Quiz page loaded")
    else:
        print(f"   ❌ Quiz page failed: {response.status_code}")
        return False
    
    # Step 4: Answer all words
    print("\n4️⃣ Answering all words...")
    word_list = ["apple", "dog", "cat"]
    
    for i, word in enumerate(word_list, 1):
        print(f"\n   Word {i}/{len(word_list)}: '{word}'")
        
        # Get next word
        response = session.post(f"{BASE_URL}/api/next")
        if response.status_code == 200:
            data = response.json()
            print(f"   📖 Definition: {data.get('definition', 'N/A')[:50]}...")
        
        # Submit answer
        answer_data = {
            "user_input": word,  # Correct answer
            "method": "keyboard",
            "elapsed_ms": 3000
        }
        response = session.post(f"{BASE_URL}/api/answer", json=answer_data)
        
        if response.status_code == 200:
            data = response.json()
            is_correct = data.get('correct', False)
            quiz_complete = data.get('quiz_complete', False)
            progress = data.get('progress', {})
            
            print(f"   {'✅' if is_correct else '❌'} Answer: {is_correct}")
            print(f"   📊 Progress: {progress.get('correct', 0)}/{progress.get('total', 0)} correct")
            
            if quiz_complete:
                print(f"\n   🎉 QUIZ COMPLETE!")
                print(f"   📈 Final Score: {progress.get('correct', 0)}/{progress.get('total', 0)}")
                
                # Check if level up happened
                if 'level_up' in data:
                    print(f"   🎊 LEVEL UP! {data['level_up']}")
        else:
            print(f"   ❌ Answer submission failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        time.sleep(0.5)  # Small delay between words
    
    # Step 5: Check dashboard stats
    print("\n5️⃣ Checking dashboard stats...")
    response = session.get(f"{BASE_URL}/")
    
    if response.status_code == 200:
        html = response.text
        
        # Parse stats from HTML (crude but effective)
        if 'total_lifetime_points' in html or 'total_quizzes_completed' in html:
            print("   ✅ Dashboard loaded with stats")
            
            # Try to extract numbers (this is rough parsing)
            import re
            points_match = re.search(r'(\d+)\s*🏆', html)
            quizzes_match = re.search(r'(\d+)\s*📝', html)
            
            if points_match:
                print(f"   📊 Total Points: {points_match.group(1)}")
            if quizzes_match:
                print(f"   📊 Total Quizzes: {quizzes_match.group(1)}")
        else:
            print("   ⚠️  Stats not found in dashboard")
    else:
        print(f"   ❌ Dashboard failed: {response.status_code}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE!")
    print("=" * 80)
    print("\n💡 Check the Flask server logs for detailed debug output:")
    print("   - Look for '📊 Quiz Status' messages")
    print("   - Look for '✅ Saved QuizResult' messages")
    print("   - Look for '📈 STATS UPDATE' messages")
    print("   - Look for '💾 DATABASE COMMITTED' messages")
    print("\n")
    
    return True


if __name__ == "__main__":
    try:
        test_quiz_completion()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
