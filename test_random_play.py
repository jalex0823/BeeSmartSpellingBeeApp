"""
Test script for Random Play feature
Tests the /api/random-words endpoint with all difficulty levels
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_random_words(difficulty, count=10):
    """Test the random words API endpoint"""
    print(f"\n{'='*60}")
    print(f"🎲 Testing Random Play - Difficulty Level {difficulty}")
    print(f"{'='*60}")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # First, make a request to the homepage to get session cookie
    session.get(f"{BASE_URL}/")
    
    # Make API call
    response = session.post(
        f"{BASE_URL}/api/random-words",
        json={"difficulty": difficulty, "count": count}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {data.get('message', 'No message')}")
        print(f"📊 Generated {data.get('count', 0)} words")
        
        # Show a few sample words
        words = data.get('words', [])
        if words:
            print(f"\n📝 Sample words (first 3):")
            for i, word_data in enumerate(words[:3], 1):
                word = word_data.get('word', 'N/A')
                sentence = word_data.get('sentence', 'N/A')[:80] + "..."
                print(f"   {i}. {word.upper()}")
                print(f"      {sentence}")
        
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False

def test_all_difficulty_levels():
    """Test all 5 difficulty levels"""
    print("\n" + "="*60)
    print("🐝 BeeSmart Random Play Feature Test")
    print("="*60)
    
    results = []
    for level in range(1, 6):
        success = test_random_words(level, count=10)
        results.append((level, success))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Test Summary")
    print(f"{'='*60}")
    for level, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        level_name = ["Easy", "Medium", "Normal", "Hard", "Expert"][level-1]
        print(f"Level {level} ({level_name}): {status}")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    print(f"\nTotal: {passed}/{total} tests passed")

def test_word_difficulty_calculation():
    """Test the difficulty calculation for specific words"""
    print(f"\n{'='*60}")
    print("🔍 Testing Word Difficulty Calculation")
    print(f"{'='*60}")
    
    test_words = [
        ("cat", 1),      # Easy: 3 letters
        ("happy", 2),    # Medium-Easy: 5 letters
        ("elephant", 3), # Medium: 8 letters
        ("beautiful", 4), # Medium-Hard: 9 letters
        ("refrigerator", 5), # Hard: 12 letters
    ]
    
    from AjaSpellBApp import calculate_word_difficulty
    
    for word, expected_diff in test_words:
        actual_diff = calculate_word_difficulty(word)
        match = "✅" if abs(actual_diff - expected_diff) <= 1 else "❌"
        print(f"{match} '{word}': Expected ~{expected_diff}, Got {actual_diff}")

if __name__ == "__main__":
    # Test difficulty calculation locally
    test_word_difficulty_calculation()
    
    # Test API endpoints
    test_all_difficulty_levels()
    
    print("\n✨ All tests completed!")
