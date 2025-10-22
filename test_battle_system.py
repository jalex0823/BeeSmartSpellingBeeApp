"""
Battle of the Bees - Comprehensive Testing Script
Tests the complete battle system including name tracking and grading
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_battle_creation():
    """Test creating a new battle"""
    print("\n=== TEST 1: Create Battle ===")
    
    payload = {
        "battle_name": "Spelling Champions",
        "creator_name": "Mrs. Johnson",
        "use_current_words": False,
        "word_list": [
            {"word": "apple", "sentence": "The apple is red.", "hint": "A fruit"},
            {"word": "book", "sentence": "I read a book.", "hint": "For reading"},
            {"word": "cat", "sentence": "The cat meows.", "hint": "An animal"},
            {"word": "dog", "sentence": "The dog barks.", "hint": "Pet"},
            {"word": "egg", "sentence": "I ate an egg.", "hint": "From chickens"}
        ]
    }
    
    response = requests.post(f"{BASE_URL}/api/battles/create", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Battle created successfully!")
        print(f"   Battle Code: {data['battle_code']}")
        print(f"   Battle Name: {data['battle_name']}")
        print(f"   Word Count: {data['word_count']}")
        return data['battle_code']
    else:
        print(f"❌ Failed to create battle: {response.text}")
        return None

def test_student_join(battle_code, student_name):
    """Test student joining a battle"""
    print(f"\n=== TEST 2: Student '{student_name}' Joins Battle ===")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    payload = {
        "battle_code": battle_code,
        "player_name": student_name
    }
    
    response = session.post(f"{BASE_URL}/api/battles/join", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {student_name} joined successfully!")
        print(f"   Battle Name: {data['battle_name']}")
        print(f"   Word Count: {data['word_count']}")
        print(f"   Session has wordbank: {data.get('wordbank_loaded', False)}")
        return session
    else:
        print(f"❌ {student_name} failed to join: {response.text}")
        return None

def test_duplicate_name_prevention(battle_code):
    """Test that duplicate names are prevented"""
    print(f"\n=== TEST 3: Duplicate Name Prevention ===")
    
    payload = {
        "battle_code": battle_code,
        "player_name": "Alice"  # Try to join again with same name
    }
    
    response = requests.post(f"{BASE_URL}/api/battles/join", json=payload)
    
    if response.status_code == 400:
        print(f"✅ Duplicate name correctly rejected!")
        print(f"   Error: {response.json().get('error', 'Unknown')}")
    else:
        print(f"❌ Duplicate name should have been rejected!")

def test_progress_update(battle_code, player_name, score, correct, total):
    """Test updating player progress"""
    print(f"\n=== TEST 4: Update Progress for {player_name} ===")
    
    # First, get the player_id from the leaderboard
    leaderboard_response = requests.get(f"{BASE_URL}/api/battles/{battle_code}/leaderboard")
    if leaderboard_response.status_code != 200:
        print(f"❌ Failed to get leaderboard to find player_id")
        return
    
    leaderboard_data = leaderboard_response.json()
    player_id = None
    for player in leaderboard_data['leaderboard']:
        if player['name'] == player_name:
            player_id = player['player_id']
            break
    
    if not player_id:
        print(f"❌ Player {player_name} not found in leaderboard")
        return
    
    payload = {
        "player_id": player_id,
        "word": "test",
        "user_input": "test",
        "correct": correct > 0,
        "time_ms": 3000
    }
    
    # Update progress multiple times to simulate answering words
    for i in range(correct):
        response = requests.post(f"{BASE_URL}/api/battles/{battle_code}/progress", json=payload)
        if response.status_code != 200:
            print(f"❌ Failed to update progress: {response.text}")
            return
    
    print(f"✅ Progress updated for {player_name}")
    print(f"   Correct answers: {correct}")

def test_leaderboard(battle_code):
    """Test fetching the leaderboard"""
    print(f"\n=== TEST 5: Fetch Leaderboard ===")
    
    response = requests.get(f"{BASE_URL}/api/battles/{battle_code}/leaderboard")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Leaderboard fetched successfully!")
        print(f"\n   📊 BATTLE: {data['battle_name']}")
        print(f"   Total Players: {len(data['leaderboard'])}")
        print("\n   Rankings:")
        
        for player in data['leaderboard']:
            medal = "🥇" if player['rank'] == 1 else "🥈" if player['rank'] == 2 else "🥉" if player['rank'] == 3 else f"  {player['rank']}."
            print(f"   {medal} {player['name']}: {player['score']} pts | "
                  f"{player['correct_count']}/{player['correct_count'] + player['incorrect_count']} ({player['accuracy']:.1f}%) | "
                  f"Progress: {player['progress']}")
    else:
        print(f"❌ Failed to fetch leaderboard: {response.text}")

def test_csv_export(battle_code):
    """Test CSV export for teacher grading"""
    print(f"\n=== TEST 6: CSV Export for Grading ===")
    
    response = requests.get(f"{BASE_URL}/api/battles/{battle_code}/export")
    
    if response.status_code == 200:
        print(f"✅ CSV export successful!")
        print(f"\n   CSV Content Preview:")
        lines = response.text.split('\n')[:6]  # Show first 6 lines
        for line in lines:
            print(f"   {line}")
        print(f"   ... (showing first 6 lines)")
    else:
        print(f"❌ Failed to export CSV: {response.text}")

def test_leaderboard_page(battle_code):
    """Test that the leaderboard page loads"""
    print(f"\n=== TEST 7: Leaderboard Page Access ===")
    
    response = requests.get(f"{BASE_URL}/battle/{battle_code}")
    
    if response.status_code == 200:
        print(f"✅ Leaderboard page loads successfully!")
        print(f"   URL: {BASE_URL}/battle/{battle_code}")
        print(f"   Status: {response.status_code}")
        print(f"   Page size: {len(response.text)} bytes")
    else:
        print(f"❌ Failed to load leaderboard page: {response.status_code}")

def run_complete_test():
    """Run the complete test suite"""
    print("\n" + "="*60)
    print("🐝 BATTLE OF THE BEES - COMPREHENSIVE TEST SUITE 🐝")
    print("="*60)
    
    # Test 1: Create Battle
    battle_code = test_battle_creation()
    if not battle_code:
        print("\n❌ Cannot continue - battle creation failed")
        return
    
    time.sleep(1)
    
    # Test 2: Students Join
    alice_session = test_student_join(battle_code, "Alice")
    time.sleep(0.5)
    bob_session = test_student_join(battle_code, "Bob")
    time.sleep(0.5)
    charlie_session = test_student_join(battle_code, "Charlie")
    
    time.sleep(1)
    
    # Test 3: Duplicate Name Prevention
    test_duplicate_name_prevention(battle_code)
    
    time.sleep(1)
    
    # Test 4: Simulate Progress Updates
    test_progress_update(battle_code, "Alice", 95, 19, 20)
    time.sleep(0.5)
    test_progress_update(battle_code, "Bob", 88, 22, 25)
    time.sleep(0.5)
    test_progress_update(battle_code, "Charlie", 75, 15, 20)
    
    time.sleep(1)
    
    # Test 5: Fetch Leaderboard
    test_leaderboard(battle_code)
    
    time.sleep(1)
    
    # Test 6: CSV Export
    test_csv_export(battle_code)
    
    time.sleep(1)
    
    # Test 7: Leaderboard Page
    test_leaderboard_page(battle_code)
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED!")
    print("="*60)
    print(f"\n📝 Teacher Instructions:")
    print(f"   1. Share battle code with students: {battle_code}")
    print(f"   2. Monitor progress at: {BASE_URL}/battle/{battle_code}")
    print(f"   3. Export grades: {BASE_URL}/api/battles/{battle_code}/export")
    print("\n")

if __name__ == "__main__":
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print("✅ Server is running!")
            run_complete_test()
        else:
            print("❌ Server returned unexpected status")
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to Flask server")
        print("Please start the server first:")
        print("   python AjaSpellBApp.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
