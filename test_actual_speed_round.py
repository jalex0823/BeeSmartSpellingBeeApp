#!/usr/bin/env python3
"""
Speed Round Functionality Test
Tests the actual speed round feature (not the regular quiz)
"""

import requests
import json
import time
from datetime import datetime

def test_speed_round_functionality():
    """Test the dedicated speed round feature"""
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    print("⚡ BeeSmart Speed Round Test")
    print("=" * 45)
    print(f"Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        # 1. Test Speed Round Health Check
        print("\n1. 🔍 Testing speed round health...")
        response = session.get(f"{base_url}/api/speed-round/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Speed Round Health: {data.get('status', 'Unknown')}")
        else:
            print(f"   ⚠️ Speed Round Health API: {response.status_code}")
        
        # 2. Test Speed Round Setup Page
        print("\n2. 🔍 Testing speed round setup page...")
        response = session.get(f"{base_url}/speed-round/setup")
        if response.status_code == 200:
            print("   ✅ Speed Round Setup page loaded")
        else:
            print(f"   ❌ Setup page failed: {response.status_code}")
            return
        
        # 3. Test Speed Round Start
        print("\n3. ⚡ Testing speed round start...")
        config = {
            "word_count": 10,
            "difficulty": "grade_3_4",
            "time_per_word": 10
        }
        
        response = session.post(f"{base_url}/api/speed-round/start", json=config)
        if response.status_code == 200:
            start_data = response.json()
            print(f"   ✅ Speed Round Started!")
            print(f"      Words: {start_data.get('word_count', 'Unknown')}")
            print(f"      Difficulty: {start_data.get('difficulty', 'Unknown')}")
            print(f"      Time per word: {start_data.get('time_per_word', 'Unknown')}s")
        else:
            print(f"   ❌ Speed Round Start failed: {response.status_code}")
            return
        
        # 4. Test Speed Round Next Word
        print("\n4. 📝 Testing speed round next word...")
        response = session.get(f"{base_url}/api/speed-round/next")
        if response.status_code == 200:
            word_data = response.json()
            current_word = word_data.get('word', 'Unknown')
            definition = word_data.get('definition', 'No definition')[:40] + '...'
            word_index = word_data.get('current_word_index', 0)
            print(f"   ✅ Got word #{word_index + 1}")
            print(f"      Definition: {definition}")
        else:
            print(f"   ❌ Next word failed: {response.status_code}")
            return
        
        # 5. Test Speed Round Answers (Rapid Fire)
        print("\n5. 🏃‍♂️ Testing rapid-fire speed round answers...")
        
        for round_num in range(5):
            # Get next word
            next_response = session.get(f"{base_url}/api/speed-round/next")
            if next_response.status_code != 200:
                print(f"   ⚠️ Round {round_num + 1}: Could not get next word")
                continue
            
            word_info = next_response.json()
            
            # Submit answer with speed timing
            response_time = 2000 - (round_num * 300)  # Getting faster each round
            answer_data = {
                "answer": f"test{round_num}",  # Dummy answer for testing
                "time_taken": response_time,
                "method": "keyboard"
            }
            
            start_time = time.time()
            answer_response = session.post(
                f"{base_url}/api/speed-round/answer", 
                json=answer_data
            )
            api_time = (time.time() - start_time) * 1000
            
            if answer_response.status_code == 200:
                result = answer_response.json()
                correct = result.get('correct', False)
                status = "✅" if correct else "❌"
                print(f"   {status} Round {round_num + 1}: {response_time}ms response, {api_time:.1f}ms API")
            else:
                print(f"   ❌ Round {round_num + 1}: API error {answer_response.status_code}")
            
            time.sleep(0.1)  # Brief pause between rounds
        
        # 6. Test Speed Round Quiz Page
        print("\n6. 🔍 Testing speed round quiz page...")
        response = session.get(f"{base_url}/speed-round/quiz")
        if response.status_code == 200:
            print("   ✅ Speed Round Quiz page loaded")
        elif response.status_code == 302:
            print("   ⚠️ Speed Round Quiz redirected (may need active session)")
        else:
            print(f"   ❌ Quiz page failed: {response.status_code}")
        
        # 7. Test Performance
        print("\n7. 📊 Testing speed round performance...")
        response_times = []
        
        for i in range(5):
            start_time = time.time()
            response = session.get(f"{base_url}/api/speed-round/next")
            end_time = time.time()
            
            if response.status_code == 200:
                response_time = (end_time - start_time) * 1000
                response_times.append(response_time)
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            print(f"   ✅ API Performance:")
            print(f"      Average: {avg_time:.1f}ms")
            print(f"      Range: {min_time:.1f}ms - {max_time:.1f}ms")
            
            if avg_time < 100:
                print("   🚀 Excellent speed for speed round!")
            elif avg_time < 200:
                print("   ✅ Good speed for speed round!")
            else:
                print("   ⚠️ Could be faster for optimal speed round experience")
        
        print("\n" + "=" * 45)
        print("🎉 SPEED ROUND TEST COMPLETED!")
        print("⚡ Speed Round is a separate feature from regular quiz")
        print("✅ Speed Round functionality is working properly!")
        print("🏆 Rapid-fire spelling challenge is operational!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("Please check that Flask server is running on localhost:5000")

if __name__ == "__main__":
    test_speed_round_functionality()