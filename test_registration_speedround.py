"""
Test script for Registration and Speed Round functionality
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5001"

def test_registration():
    """Test the registration endpoint"""
    print("\n" + "="*60)
    print("🧪 TESTING REGISTRATION FUNCTIONALITY")
    print("="*60)
    
    # Generate unique username
    timestamp = int(time.time())
    test_user = {
        "username": f"testuser{timestamp}",
        "display_name": "Test User",
        "password": "TestPass123!",
        "email": f"test{timestamp}@example.com",
        "grade_level": "5",
        "teacher_key": ""
    }
    
    print(f"\n📝 Attempting to register user: {test_user['username']}")
    print(f"   Display Name: {test_user['display_name']}")
    print(f"   Email: {test_user['email']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=test_user,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\n📡 Response Status: {response.status_code}")
        print(f"📦 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: {data.get('message', 'Registration successful')}")
            print(f"🔗 Redirect URL: {data.get('redirect', 'N/A')}")
            return True, data
        else:
            try:
                data = response.json()
                print(f"❌ ERROR: {data.get('error', 'Unknown error')}")
            except:
                print(f"❌ ERROR: {response.text}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to Flask server. Is it running on port 5000?")
        return False, None
    except Exception as e:
        print(f"❌ EXCEPTION: {type(e).__name__}: {e}")
        return False, None


def test_speed_round():
    """Test the speed round functionality"""
    print("\n" + "="*60)
    print("⚡ TESTING SPEED ROUND FUNCTIONALITY")
    print("="*60)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Test configuration
    config = {
        "time_per_word": 10,
        "difficulty": "grade_3_4",
        "word_count": 5,
        "word_source": "auto"
    }
    
    print(f"\n🎯 Starting speed round with config:")
    print(f"   Time per word: {config['time_per_word']}s")
    print(f"   Difficulty: {config['difficulty']}")
    print(f"   Word count: {config['word_count']}")
    print(f"   Word source: {config['word_source']}")
    
    try:
        # Start speed round
        response = session.post(
            f"{BASE_URL}/api/speed-round/start",
            json=config,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\n📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Speed round started!")
            print(f"📊 Word count: {data.get('word_count', 'N/A')}")
            print(f"🔤 First word: {data.get('first_word', 'N/A')}")
            
            # Test getting next word
            print("\n🔄 Testing next word endpoint...")
            next_response = session.get(f"{BASE_URL}/api/speed-round/next")
            
            if next_response.status_code == 200:
                next_data = next_response.json()
                print(f"✅ Next word endpoint working!")
                print(f"   Complete: {next_data.get('complete', False)}")
                if not next_data.get('complete'):
                    print(f"   Definition: {next_data.get('definition', 'N/A')[:50]}...")
                return True, data
            else:
                print(f"❌ Next word endpoint failed: {next_response.status_code}")
                return False, None
        else:
            try:
                data = response.json()
                print(f"❌ ERROR: {data.get('message', 'Unknown error')}")
            except:
                print(f"❌ ERROR: {response.text}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to Flask server. Is it running on port 5000?")
        return False, None
    except Exception as e:
        print(f"❌ EXCEPTION: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_speed_round_answer():
    """Test submitting an answer in speed round"""
    print("\n" + "="*60)
    print("✍️ TESTING SPEED ROUND ANSWER SUBMISSION")
    print("="*60)
    
    session = requests.Session()
    
    # Start a round first
    config = {"time_per_word": 10, "difficulty": "grade_1_2", "word_count": 3, "word_source": "auto"}
    session.post(f"{BASE_URL}/api/speed-round/start", json=config)
    
    # Get first word
    next_resp = session.get(f"{BASE_URL}/api/speed-round/next")
    if next_resp.status_code != 200:
        print("❌ Failed to get word")
        return False, None
    
    word_data = next_resp.json()
    print(f"\n🔤 Testing with word from server")
    
    # Submit an answer
    answer = {
        "user_input": "test",  # Wrong answer on purpose
        "elapsed_ms": 3000,
        "skipped": False
    }
    
    try:
        response = session.post(
            f"{BASE_URL}/api/speed-round/answer",
            json=answer,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\n📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Answer submission working!")
            print(f"   Correct: {data.get('is_correct', False)}")
            print(f"   Correct spelling: {data.get('correct_spelling', 'N/A')}")
            print(f"   Points earned: {data.get('points_earned', 0)}")
            print(f"   Total points: {data.get('total_points', 0)}")
            return True, data
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(response.text)
            return False, None
            
    except Exception as e:
        print(f"❌ EXCEPTION: {type(e).__name__}: {e}")
        return False, None


def main():
    """Run all tests"""
    print("\n" + "🐝"*30)
    print("🎯 BeeSmart Registration & Speed Round Test Suite")
    print("🐝"*30)
    print(f"\n⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Testing server at: {BASE_URL}")
    
    results = []
    
    # Test 1: Registration
    reg_success, reg_data = test_registration()
    results.append(("Registration", reg_success))
    
    # Test 2: Speed Round Start
    speed_success, speed_data = test_speed_round()
    results.append(("Speed Round Start", speed_success))
    
    # Test 3: Speed Round Answer
    answer_success, answer_data = test_speed_round_answer()
    results.append(("Speed Round Answer", answer_success))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total_passed = sum(1 for _, success in results if success)
    total_tests = len(results)
    
    print(f"\n🎯 Overall: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    print("\n" + "🐝"*30)


if __name__ == "__main__":
    main()
