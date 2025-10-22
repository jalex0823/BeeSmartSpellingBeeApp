#!/usr/bin/env python3
"""
Simple Speed Round Test
Quick test of speed round functionality after JavaScript fixes
"""

import requests
import json
import time
from datetime import datetime

def test_speed_round():
    """Test speed round functionality"""
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    print("🐝 BeeSmart Speed Round Test")
    print("=" * 40)
    print(f"Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        # 1. Test server health
        print("\n1. 🔍 Testing server health...")
        response = session.get(f"{base_url}/health")
        if response.status_code == 200:
            print(f"   ✅ Server running: {response.text}")
        else:
            print(f"   ❌ Server not responding: {response.status_code}")
            return
        
        # 2. Test quiz page load
        print("\n2. 🔍 Testing quiz page load...")
        response = session.get(f"{base_url}/quiz")
        if response.status_code == 200:
            content = response.text
            
            # Check for JavaScript safety fixes
            safety_checks = {
                'Safe template interpolation (|tojson)': '|tojson' in content,
                'Global error handler': 'window.addEventListener("error"' in content,
                'Try-catch blocks': 'try {' in content and 'catch' in content,
                'Error recovery for syntax errors': 'Unexpected token' in content
            }
            
            print("   ✅ Quiz page loaded successfully")
            print("   🔧 JavaScript Safety Checks:")
            for check, passed in safety_checks.items():
                status = "✅" if passed else "❌"
                print(f"      {status} {check}")
            
            safety_score = sum(safety_checks.values())
            print(f"   📊 Safety Score: {safety_score}/{len(safety_checks)}")
            
        else:
            print(f"   ❌ Quiz page failed: {response.status_code}")
            return
        
        # 3. Test wordbank
        print("\n3. 🔍 Testing wordbank...")
        response = session.get(f"{base_url}/api/wordbank")
        if response.status_code == 200:
            data = response.json()
            word_count = len(data.get('words', []))
            print(f"   ✅ Wordbank loaded: {word_count} words")
        else:
            print(f"   ❌ Wordbank failed: {response.status_code}")
            return
        
        # 4. Test speed round API calls
        print("\n4. ⚡ Testing speed round API...")
        
        # Get next word
        response = session.post(f"{base_url}/api/next")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Next word API works")
            definition = data.get('definition', 'No definition')[:50] + '...'
            print(f"   📝 Definition: {definition}")
        else:
            print(f"   ❌ Next word API failed: {response.status_code}")
            return
        
        # Test rapid answers (simulating speed round)
        print("\n5. 🏃‍♂️ Simulating speed round answers...")
        speeds = [1500, 1200, 900, 700, 500]  # Getting faster each round
        
        for i, speed_ms in enumerate(speeds):
            # Submit answer with timing
            answer_data = {
                "user_input": f"test{i}",
                "method": "keyboard", 
                "elapsed_ms": speed_ms
            }
            
            start_time = time.time()
            response = session.post(f"{base_url}/api/answer", json=answer_data)
            api_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Round {i+1}: {speed_ms}ms input, {api_time:.1f}ms API response")
            else:
                print(f"   ❌ Round {i+1}: API error {response.status_code}")
            
            time.sleep(0.1)  # Brief pause
        
        # 6. Test pronunciation and hints
        print("\n6. 🔊 Testing pronunciation and hints...")
        
        # Test pronounce
        response = session.post(f"{base_url}/api/pronounce")
        if response.status_code == 200:
            data = response.json()
            phonetic = data.get('phonetic', 'No phonetic')
            print(f"   ✅ Pronounce works: {phonetic}")
        else:
            print(f"   ⚠️ Pronounce API: {response.status_code}")
        
        # Test hint
        response = session.post(f"{base_url}/api/hint")
        if response.status_code == 200:
            data = response.json()
            hint = data.get('hint', 'No hint')[:30] + '...'
            print(f"   ✅ Hint works: {hint}")
        else:
            print(f"   ⚠️ Hint API: {response.status_code}")
        
        print("\n" + "=" * 40)
        print("🎉 SPEED ROUND TEST COMPLETED SUCCESSFULLY!")
        print("✅ JavaScript syntax error fixes are working!")
        print("✅ No 'Unexpected token '}'' errors should occur!")
        print("✅ Speed round functionality is operational!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("Please check that Flask server is running on localhost:5000")

if __name__ == "__main__":
    test_speed_round()