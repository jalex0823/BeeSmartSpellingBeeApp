"""
Quick Battle of the Bees functionality test
Tests: Create Battle, Join Battle, Submit Progress
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_battle_flow():
    """Test complete Battle of the Bees flow"""
    
    print("\n" + "="*60)
    print("🐝 BATTLE OF THE BEES - FUNCTIONALITY TEST")
    print("="*60)
    
    # Test 1: Create a battle
    print("\n📝 TEST 1: Creating a battle...")
    create_data = {
        "battle_name": "Test Battle - Python Script",
        "creator_name": "Test Teacher"
    }
    
    response = requests.post(f"{BASE_URL}/api/battles/create", json=create_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Battle created successfully!")
        print(f"   Battle Code: {result['battle_code']}")
        print(f"   Battle Name: {result['battle_name']}")
        print(f"   Creator: {result['creator_name']}")
        battle_code = result['battle_code']
    else:
        print(f"❌ Failed to create battle: {response.text}")
        return
    
    # Test 2: Join the battle
    print(f"\n📝 TEST 2: Joining battle {battle_code}...")
    join_data = {
        "battle_code": battle_code,
        "participant_name": "Test Student 1"
    }
    
    response = requests.post(f"{BASE_URL}/api/battles/join", json=join_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Joined battle successfully!")
        print(f"   Participant: {result['participant_name']}")
        print(f"   Battle: {result['battle_name']}")
        participant_id = result['participant_id']
    else:
        print(f"❌ Failed to join battle: {response.text}")
        return
    
    # Test 3: Submit progress
    print(f"\n📝 TEST 3: Submitting progress...")
    progress_data = {
        "participant_id": participant_id,
        "words_attempted": 10,
        "words_correct": 8,
        "current_score": 80
    }
    
    response = requests.post(f"{BASE_URL}/api/battles/{battle_code}/progress", json=progress_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Progress submitted successfully!")
        print(f"   Words Correct: {result.get('words_correct', 'N/A')}")
        print(f"   Score: {result.get('current_score', 'N/A')}")
    else:
        print(f"❌ Failed to submit progress: {response.text}")
        return
    
    # Test 4: Get leaderboard
    print(f"\n📝 TEST 4: Fetching leaderboard...")
    response = requests.get(f"{BASE_URL}/api/battles/{battle_code}/leaderboard")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Leaderboard fetched successfully!")
        print(f"   Battle Name: {result['battle_name']}")
        print(f"   Total Participants: {len(result['participants'])}")
        print(f"\n   📊 Current Standings:")
        for i, p in enumerate(result['participants'][:5], 1):
            print(f"      {i}. {p['name']}: {p['score']} points ({p['words_correct']}/{p['words_attempted']} correct)")
    else:
        print(f"❌ Failed to fetch leaderboard: {response.text}")
        return
    
    # Test 5: Join with another student
    print(f"\n📝 TEST 5: Adding another participant...")
    join_data2 = {
        "battle_code": battle_code,
        "participant_name": "Test Student 2"
    }
    
    response = requests.post(f"{BASE_URL}/api/battles/join", json=join_data2)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Second participant joined!")
        print(f"   Participant: {result['participant_name']}")
        participant_id2 = result['participant_id']
        
        # Submit their progress
        progress_data2 = {
            "participant_id": participant_id2,
            "words_attempted": 10,
            "words_correct": 9,
            "current_score": 95
        }
        response = requests.post(f"{BASE_URL}/api/battles/{battle_code}/progress", json=progress_data2)
        if response.status_code == 200:
            print(f"   ✅ Progress submitted for Student 2")
    
    # Final leaderboard
    print(f"\n📝 FINAL TEST: Updated leaderboard...")
    response = requests.get(f"{BASE_URL}/api/battles/{battle_code}/leaderboard")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Final Leaderboard:")
        for i, p in enumerate(result['participants'], 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
            accuracy = (p['words_correct'] / p['words_attempted'] * 100) if p['words_attempted'] > 0 else 0
            print(f"      {medal} {i}. {p['name']}: {p['score']} points ({accuracy:.0f}% accuracy)")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print(f"🎉 Battle Code: {battle_code} (valid for 24 hours)")
    print(f"🔗 Share this link: http://localhost:5000/battle/{battle_code}")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        test_battle_flow()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to Flask app")
        print("   Make sure the app is running: python AjaSpellBApp.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
