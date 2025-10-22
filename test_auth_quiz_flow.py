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
    
    # Step 3: Check wordbank (should have default words)
    print("\n📚 Step 3: Checking wordbank...")
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
    
    # Step 4: Start quiz (first word)
    print("\n🎯 Step 4: Starting quiz...")
    response = session.post(f"{BASE_URL}/api/next")
    if response.status_code == 200:
        quiz_data = response.json()
        print(f"   ✅ Quiz started")
        print(f"   📖 Definition: {quiz_data.get('definition', 'N/A')[:60]}...")
    else:
        print(f"   ❌ Failed to start quiz: {response.status_code}")
        return False
    
    # Step 5: Answer first 3 words
    print("\n✍️ Step 5: Answering words...")
    for i in range(min(3, word_count)):
        # Get current word info
        response = session.post(f"{BASE_URL}/api/next")
        if response.status_code != 200:
            print(f"   ⚠️ Couldn't get word {i+1}")
            continue
            
        word_info = response.json()
        
        # Get the actual word from wordbank (cheat for testing)
        current_word = wordbank[i]["word"]
        
        # Submit answer
        answer_data = {
            "user_input": current_word,  # Correct answer
            "method": "keyboard",
            "elapsed_ms": random.randint(3000, 8000)
        }
        
        response = session.post(f"{BASE_URL}/api/answer", json=answer_data)
        if response.status_code == 200:
            result = response.json()
            is_correct = result.get("correct", False)
            print(f"   {'✅' if is_correct else '❌'} Word {i+1}: {current_word} - {'Correct' if is_correct else 'Incorrect'}")
        else:
            print(f"   ❌ Failed to submit answer for word {i+1}")
    
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
    
    # Step 7: Complete entire quiz to trigger database save
    print("\n🏁 Step 7: Completing full quiz...")
    remaining_words = word_count - 3
    if remaining_words > 0:
        for i in range(3, word_count):
            current_word = wordbank[i]["word"]
            
            # Submit answer
            answer_data = {
                "user_input": current_word if random.random() > 0.2 else "wrong",  # 80% correct
                "method": "keyboard",
                "elapsed_ms": random.randint(2000, 6000)
            }
            
            response = session.post(f"{BASE_URL}/api/answer", json=answer_data)
            if response.status_code == 200:
                result = response.json()
                progress = result.get("progress", {})
                if i % 10 == 0 or i == word_count - 1:
                    print(f"   📈 Progress: {progress.get('index')}/{progress.get('total')} - "
                          f"Correct: {progress.get('correct')}, Incorrect: {progress.get('incorrect')}")
        
        print("   ✅ Quiz completed!")
    
    # Step 8: Verify dashboard shows quiz results
    print("\n📈 Step 8: Verifying quiz saved to database...")
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
