#!/usr/bin/env python3
"""
Speed Round Railway Test
Tests the Railway-optimized Speed Round functionality
"""

import requests
import time
import json
import sys
from datetime import datetime

def test_speed_round_railway():
    """
    Test Speed Round Railway functionality
    """
    
    print("🚂 SPEED ROUND RAILWAY TEST")
    print("=" * 60)
    
    # Test configuration
    base_url = "http://localhost:5000"
    test_config = {
        'time_per_word': 10,
        'difficulty': 'grade_3_4', 
        'word_count': 5,  # Small test
        'word_source': 'auto'
    }
    
    session = requests.Session()
    
    try:
        # Test 1: Health Check
        print("\n🏥 Testing Speed Round Health...")
        health_response = session.get(f"{base_url}/api/speed-round/health")
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Health Status: {health_data.get('speed_round_status', 'unknown')}")
            print(f"   Database: {health_data.get('database_status', 'unknown')}")
            print(f"   Environment: {health_data.get('environment', 'unknown')}")
            
            if health_data.get('speed_round_status') != 'operational':
                print(f"⚠️  Warning: Speed Round not fully operational")
                print(f"   Details: {json.dumps(health_data, indent=2)}")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
            print(f"   Response: {health_response.text}")
            return False
        
        # Test 2: Start Speed Round
        print(f"\n🎯 Starting Speed Round...")
        start_response = session.post(
            f"{base_url}/api/speed-round/start",
            json=test_config,
            headers={'Content-Type': 'application/json'}
        )
        
        if start_response.status_code == 200:
            start_data = start_response.json()
            print(f"✅ Speed Round Started!")
            print(f"   Word Count: {start_data.get('word_count', 0)}")
            print(f"   First Word: {start_data.get('first_word', 'N/A')}")
        else:
            print(f"❌ Start failed: {start_response.status_code}")
            print(f"   Response: {start_response.text}")
            return False
        
        # Test 3: Get Next Word
        print(f"\n📝 Getting next word...")
        next_response = session.get(f"{base_url}/api/speed-round/next")
        
        if next_response.status_code == 200:
            word_data = next_response.json()
            if not word_data.get('complete', False):
                current_word = word_data.get('word', '')
                definition = word_data.get('definition', '')
                print(f"✅ Got word: '{current_word}'")
                print(f"   Definition: {definition[:100]}...")
                print(f"   Progress: {word_data.get('current_index', 0)}/{word_data.get('total_words', 0)}")
            else:
                print(f"✅ Speed Round already complete")
        else:
            print(f"❌ Next word failed: {next_response.status_code}")
            print(f"   Response: {next_response.text}")
            return False
        
        # Test 4: Submit Answer (if we have a word)
        if not word_data.get('complete', False):
            print(f"\n✍️  Submitting test answer...")
            
            # Submit correct answer
            answer_data = {
                'user_input': current_word,  # Correct answer
                'elapsed_ms': 5000,  # 5 seconds
                'skipped': False
            }
            
            answer_response = session.post(
                f"{base_url}/api/speed-round/answer",
                json=answer_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if answer_response.status_code == 200:
                answer_result = answer_response.json()
                print(f"✅ Answer submitted!")
                print(f"   Correct: {answer_result.get('is_correct', False)}")
                print(f"   Points Earned: {answer_result.get('points_earned', 0)}")
                print(f"   Total Points: {answer_result.get('total_points', 0)}")
                print(f"   Current Streak: {answer_result.get('current_streak', 0)}")
                print(f"   Complete: {answer_result.get('complete', False)}")
            else:
                print(f"❌ Answer submission failed: {answer_response.status_code}")
                print(f"   Response: {answer_response.text}")
                return False
        
        # Test 5: Test a few more words quickly
        print(f"\n🏃 Quick test of remaining words...")
        
        for i in range(3):  # Test up to 3 more words
            # Get next word
            next_response = session.get(f"{base_url}/api/speed-round/next")
            
            if next_response.status_code != 200:
                print(f"❌ Failed to get word {i+2}")
                break
                
            word_data = next_response.json()
            
            if word_data.get('complete', False):
                print(f"✅ Speed Round completed at word {i+1}")
                break
            
            current_word = word_data.get('word', '')
            print(f"   Word {i+2}: '{current_word}'")
            
            # Submit answer (mix of correct and incorrect)
            test_answer = current_word if i % 2 == 0 else "wrong"
            
            answer_data = {
                'user_input': test_answer,
                'elapsed_ms': 3000 + (i * 1000),  # Varying response times
                'skipped': False
            }
            
            answer_response = session.post(
                f"{base_url}/api/speed-round/answer",
                json=answer_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if answer_response.status_code == 200:
                answer_result = answer_response.json()
                print(f"   Result: {'✅' if answer_result.get('is_correct') else '❌'} "
                      f"Points: {answer_result.get('points_earned', 0)} "
                      f"Total: {answer_result.get('total_points', 0)}")
                
                if answer_result.get('complete', False):
                    print(f"✅ Speed Round completed!")
                    break
            else:
                print(f"❌ Answer {i+2} failed: {answer_response.status_code}")
                break
        
        # Test 6: Health Check After Test
        print(f"\n🏥 Final Health Check...")
        final_health = session.get(f"{base_url}/api/speed-round/health")
        
        if final_health.status_code == 200:
            health_data = final_health.json()
            print(f"✅ Final Status: {health_data.get('speed_round_status', 'unknown')}")
            
            if health_data.get('error'):
                print(f"⚠️  Error detected: {health_data.get('error')}")
        
        print(f"\n✅ SPEED ROUND RAILWAY TEST COMPLETE")
        print(f"🚂 Railway optimizations appear to be working!")
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Is Flask app running on {base_url}?")
        return False
        
    except Exception as e:
        print(f"❌ Test Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_speed_round_stress():
    """
    Stress test Speed Round to check for Railway issues
    """
    print(f"\n🔥 SPEED ROUND STRESS TEST")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    successful_rounds = 0
    failed_rounds = 0
    
    for round_num in range(3):  # 3 quick rounds
        print(f"\n🎯 Stress Round {round_num + 1}/3...")
        
        session = requests.Session()
        
        try:
            # Start round
            start_response = session.post(
                f"{base_url}/api/speed-round/start",
                json={
                    'time_per_word': 5,  # Fast rounds
                    'difficulty': 'grade_3_4',
                    'word_count': 3,  # Small rounds
                    'word_source': 'auto'
                }
            )
            
            if start_response.status_code != 200:
                print(f"❌ Round {round_num + 1} start failed")
                failed_rounds += 1
                continue
            
            # Complete the round quickly
            for word_num in range(3):
                # Get word
                next_resp = session.get(f"{base_url}/api/speed-round/next")
                if next_resp.status_code != 200:
                    break
                    
                word_data = next_resp.json()
                if word_data.get('complete'):
                    break
                
                # Submit answer
                answer_resp = session.post(
                    f"{base_url}/api/speed-round/answer",
                    json={
                        'user_input': word_data.get('word', ''),
                        'elapsed_ms': 2000,
                        'skipped': False
                    }
                )
                
                if answer_resp.status_code != 200:
                    break
            
            print(f"✅ Round {round_num + 1} completed")
            successful_rounds += 1
            
        except Exception as e:
            print(f"❌ Round {round_num + 1} failed: {e}")
            failed_rounds += 1
        
        time.sleep(0.5)  # Brief pause between rounds
    
    print(f"\n📊 STRESS TEST RESULTS:")
    print(f"   Successful: {successful_rounds}/3")
    print(f"   Failed: {failed_rounds}/3")
    
    return successful_rounds >= 2  # At least 2/3 should succeed

if __name__ == "__main__":
    print("🚂 SPEED ROUND RAILWAY TEST SUITE")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run basic functionality test
    basic_success = test_speed_round_railway()
    
    if basic_success:
        # Run stress test
        stress_success = test_speed_round_stress()
        
        print(f"\n🎯 FINAL RESULTS:")
        print(f"   Basic Test: {'✅ PASS' if basic_success else '❌ FAIL'}")
        print(f"   Stress Test: {'✅ PASS' if stress_success else '❌ FAIL'}")
        
        if basic_success and stress_success:
            print(f"\n🚀 SPEED ROUND RAILWAY FIXES WORKING!")
            print(f"   Ready for Railway deployment")
            sys.exit(0)
        else:
            print(f"\n⚠️  SOME TESTS FAILED - CHECK LOGS")
            sys.exit(1)
    else:
        print(f"\n❌ BASIC TEST FAILED - FIXES NEED REVIEW")
        sys.exit(1)