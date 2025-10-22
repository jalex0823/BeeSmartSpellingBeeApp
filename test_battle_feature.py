"""
Test script for Battle of the Bees feature
Tests the complete flow: create battle -> join battle -> check leaderboard
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_battle_flow():
    """Test the complete Battle of the Bees flow"""
    
    print("🐝 Testing Battle of the Bees Feature")
    print("=" * 60)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Step 1: Load some words first (needed for battle creation)
    print("\n📚 Step 1: Loading test words...")
    test_words = [
        {"word": "bee", "sentence": "A bee is an insect", "hint": "Buzzing insect"},
        {"word": "honey", "sentence": "Bees make honey", "hint": "Sweet golden liquid"},
        {"word": "hive", "sentence": "Bees live in a hive", "hint": "Bee home"},
        {"word": "queen", "sentence": "The queen bee leads", "hint": "Female ruler"},
        {"word": "worker", "sentence": "Worker bees collect pollen", "hint": "Busy employee"}
    ]
    
    # Upload words via manual entry API (simulating user upload)
    upload_response = session.post(
        f"{BASE_URL}/api/upload",
        files={'file': ('test.txt', '\n'.join([w['word'] for w in test_words]))},
        data={'source': 'text'}
    )
    
    if upload_response.status_code == 200:
        print("✅ Words loaded successfully")
    else:
        print(f"❌ Failed to load words: {upload_response.status_code}")
        print(upload_response.text)
        return
    
    # Step 2: Create a battle (Teacher's action)
    print("\n👩‍🏫 Step 2: Teacher creates a battle...")
    
    create_data = {
        "battle_name": "Mrs. Smith's Test Battle",
        "creator_name": "Mrs. Smith",
        "use_current_words": True
    }
    
    create_response = session.post(
        f"{BASE_URL}/api/battles/create",
        json=create_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if create_response.status_code == 200:
        battle_info = create_response.json()
        if battle_info.get('status') == 'success':
            battle_code = battle_info['battle_code']
            print(f"✅ Battle created successfully!")
            print(f"   Battle Code: {battle_code}")
            print(f"   Battle Name: {battle_info['battle_name']}")
            print(f"   Word Count: {battle_info['word_count']}")
        else:
            print(f"❌ Create battle failed: {battle_info.get('message')}")
            return
    else:
        print(f"❌ Create battle request failed: {create_response.status_code}")
        print(create_response.text)
        return
    
    # Step 3: Students join the battle
    print(f"\n🎯 Step 3: Students joining battle {battle_code}...")
    
    students = ["Alice", "Bob", "Charlie"]
    student_sessions = {}
    
    for student_name in students:
        # Each student needs their own session
        student_session = requests.Session()
        
        join_data = {
            "battle_code": battle_code,
            "player_name": student_name
        }
        
        join_response = student_session.post(
            f"{BASE_URL}/api/battles/join",
            json=join_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if join_response.status_code == 200:
            join_info = join_response.json()
            if join_info.get('status') == 'success':
                print(f"✅ {student_name} joined the battle!")
                print(f"   Player ID: {join_info['player_id']}")
                print(f"   Total Players: {join_info['player_count']}")
                student_sessions[student_name] = {
                    'session': student_session,
                    'player_id': join_info['player_id']
                }
            else:
                print(f"❌ {student_name} failed to join: {join_info.get('message')}")
        else:
            print(f"❌ {student_name} join request failed: {join_response.status_code}")
    
    # Step 4: Check leaderboard
    print(f"\n🏆 Step 4: Checking leaderboard for battle {battle_code}...")
    
    leaderboard_response = session.get(
        f"{BASE_URL}/api/battles/{battle_code}/leaderboard"
    )
    
    if leaderboard_response.status_code == 200:
        leaderboard = leaderboard_response.json()
        if leaderboard.get('status') == 'success':
            print("✅ Leaderboard retrieved successfully!")
            print(f"\nBattle: {leaderboard['battle_name']}")
            print(f"Players: {leaderboard['player_count']}")
            print(f"Words: {leaderboard['word_count']}")
            print("\n📊 Current Rankings:")
            print("-" * 60)
            
            for player in leaderboard['leaderboard']:
                print(f"#{player['rank']} {player['name']}")
                print(f"   Score: {player['score']} | Accuracy: {player['accuracy']}%")
                print(f"   Progress: {player['progress']} | Streak: {player['max_streak']}")
                print("-" * 60)
        else:
            print(f"❌ Get leaderboard failed: {leaderboard.get('message')}")
    else:
        print(f"❌ Leaderboard request failed: {leaderboard_response.status_code}")
    
    # Step 5: Simulate one student answering a word (optional progress test)
    print(f"\n📝 Step 5: Simulating Alice answering first word...")
    
    if "Alice" in student_sessions:
        alice_data = student_sessions["Alice"]
        
        progress_data = {
            "player_id": alice_data['player_id'],
            "word": "bee",
            "user_input": "bee",
            "correct": True,
            "time_ms": 3000  # 3 seconds
        }
        
        progress_response = alice_data['session'].post(
            f"{BASE_URL}/api/battles/{battle_code}/progress",
            json=progress_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if progress_response.status_code == 200:
            progress_info = progress_response.json()
            if progress_info.get('status') == 'success':
                player_data = progress_info['player_data']
                print("✅ Alice answered correctly!")
                print(f"   Score: {player_data['score']}")
                print(f"   Correct: {player_data['correct_count']}")
                print(f"   Streak: {player_data['streak']}")
            else:
                print(f"❌ Progress update failed: {progress_info.get('message')}")
        else:
            print(f"❌ Progress request failed: {progress_response.status_code}")
        
        # Check leaderboard again after Alice's answer
        print(f"\n🏆 Updated Leaderboard after Alice's answer:")
        leaderboard_response = session.get(
            f"{BASE_URL}/api/battles/{battle_code}/leaderboard"
        )
        
        if leaderboard_response.status_code == 200:
            leaderboard = leaderboard_response.json()
            if leaderboard.get('status') == 'success':
                for player in leaderboard['leaderboard']:
                    print(f"#{player['rank']} {player['name']} - Score: {player['score']}")
    
    print("\n" + "=" * 60)
    print("✅ Battle of the Bees test completed!")
    print(f"🎉 Battle Code for manual testing: {battle_code}")
    print("=" * 60)

if __name__ == "__main__":
    print("\n🚀 Make sure the Flask app is running on http://127.0.0.1:5000")
    print("   Run: python AjaSpellBApp.py")
    print()
    
    try:
        # Quick check if server is running
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running!")
            print()
            test_battle_flow()
        else:
            print("❌ Server responded but health check failed")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is the Flask app running?")
    except Exception as e:
        print(f"❌ Error: {e}")
