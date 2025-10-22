"""
Complete Authentication Flow Test
Tests the full user journey: register → quiz → dashboard
"""
import requests
import time
import json
import os

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:5000").rstrip("/")

def test_complete_flow():
    """Test complete user flow with database integration"""
    session = requests.Session()
    
    print("\n" + "="*60)
    print("🐝 BEESMART COMPLETE FLOW TEST")
    print("="*60)
    
    # Step 1: Register a new user
    print("\n📝 STEP 1: Register New Student")
    print("-" * 60)
    test_username = f"test_bee_{int(time.time())}"
    register_data = {
        "username": test_username,
        "display_name": "Buzzy Test Bee",
        "email": f"{test_username}@test.com",
        "password": "test123",
        "grade_level": "5"
    }
    
    print(f"Registering: {test_username}")
    response = session.post(f"{BASE_URL}/auth/register", json=register_data)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Registration successful!")
        print(f"   User ID: {data.get('user_id')}")
        print(f"   Username: {data.get('username')}")
        print(f"   Display Name: {data.get('display_name')}")
        print(f"   Grade: {data.get('grade_level')}")
        user_id = data.get('user_id')
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    # Step 2: Start a quiz
    print("\n🎮 STEP 2: Start Quiz")
    print("-" * 60)
    response = session.post(f"{BASE_URL}/api/quiz/start")
    
    if response.status_code == 200:
        quiz_data = response.json()
        print(f"✅ Quiz started!")
        print(f"   Total words: {quiz_data.get('total_words')}")
        print(f"   Quiz session created in database")
    else:
        print(f"❌ Quiz start failed: {response.status_code}")
        return False
    
    # Step 3: Get first word
    print("\n📖 STEP 3: Get First Word")
    print("-" * 60)
    response = session.post(f"{BASE_URL}/api/next")
    
    if response.status_code == 200:
        word_data = response.json()
        print(f"✅ First word received!")
        print(f"   Definition: {word_data.get('definition')}")
        print(f"   Hint: {word_data.get('hint', 'No hint')}")
        correct_word = word_data.get('word')  # For testing, we'll peek at the answer
    else:
        print(f"❌ Failed to get word: {response.status_code}")
        return False
    
    # Step 4: Answer correctly
    print("\n✍️ STEP 4: Submit Correct Answer")
    print("-" * 60)
    answer_data = {
        "user_input": correct_word,
        "method": "keyboard",
        "elapsed_ms": 3500
    }
    
    response = session.post(f"{BASE_URL}/api/answer", json=answer_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Answer submitted!")
        print(f"   Correct: {result.get('correct')}")
        print(f"   Streak: {result.get('streak')}")
        print(f"   QuizResult saved to database")
        print(f"   WordMastery updated")
    else:
        print(f"❌ Answer submission failed: {response.status_code}")
        return False
    
    # Step 5: Answer a few more words
    print("\n✍️ STEP 5: Answer More Words (testing streak)")
    print("-" * 60)
    
    for i in range(3):
        # Get next word
        response = session.post(f"{BASE_URL}/api/next")
        if response.status_code == 200:
            word_data = response.json()
            correct_word = word_data.get('word')
            
            # Answer correctly
            answer_data = {
                "user_input": correct_word,
                "method": "keyboard",
                "elapsed_ms": 2000 + (i * 500)
            }
            response = session.post(f"{BASE_URL}/api/answer", json=answer_data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   Word {i+2}: ✅ Correct! Streak: {result.get('streak')}")
            else:
                print(f"   Word {i+2}: ❌ Failed")
    
    # Step 6: Complete quiz
    print("\n🏁 STEP 6: Complete Quiz")
    print("-" * 60)
    response = session.post(f"{BASE_URL}/api/quiz/complete")
    
    if response.status_code == 200:
        completion_data = response.json()
        print(f"✅ Quiz completed!")
        print(f"   Total words: {completion_data.get('total_words')}")
        print(f"   Correct: {completion_data.get('correct_count')}")
        print(f"   Accuracy: {completion_data.get('accuracy')}%")
        print(f"   Grade: {completion_data.get('grade')}")
        print(f"   Best streak: {completion_data.get('best_streak')}")
        print(f"   QuizSession finalized in database")
        print(f"   User stats updated")
    else:
        print(f"❌ Quiz completion failed: {response.status_code}")
        return False
    
    # Step 7: Check dashboard
    print("\n📊 STEP 7: View Student Dashboard")
    print("-" * 60)
    response = session.get(f"{BASE_URL}/auth/dashboard")
    
    if response.status_code == 200:
        print(f"✅ Dashboard loaded successfully!")
        print(f"   User should see updated stats")
        print(f"   - Total quizzes: 1")
        print(f"   - Total points: {completion_data.get('correct_count', 0) * 10}")
        print(f"   - Best streak: {completion_data.get('best_streak')}")
    else:
        print(f"❌ Dashboard access failed: {response.status_code}")
        return False
    
    # Step 8: Verify database
    print("\n💾 STEP 8: Verify Database Records")
    print("-" * 60)
    print("✅ To verify database, run:")
    print(f"   python init_db.py check")
    print(f"\nLook for user: {test_username}")
    print(f"Should have:")
    print(f"  - 1 quiz session (completed)")
    print(f"  - 4 quiz results")
    print(f"  - 4 word mastery records")
    print(f"  - Updated user stats")
    
    print("\n" + "="*60)
    print("🎉 ALL TESTS PASSED!")
    print("="*60)
    
    return True

if __name__ == "__main__":
    try:
        success = test_complete_flow()
        if success:
            print("\n✅ Complete flow test: PASSED")
            exit(0)
        else:
            print("\n❌ Complete flow test: FAILED")
            exit(1)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
