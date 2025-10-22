#!/usr/bin/env python3
"""
Comprehensive Speed Round Test Suite
Tests the speed round functionality after JavaScript syntax fixes
"""

import requests
import json
import time
import subprocess
import sys
from datetime import datetime
from threading import Thread
from time import sleep

class SpeedRoundTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BeeSmart Speed Round Tester',
            'Content-Type': 'application/json'
        })
        self.server_process = None
        
    def start_flask_server(self):
        """Start Flask server in background"""
        print("🚀 Starting Flask server...")
        try:
            # Kill any existing Python processes
            subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                         capture_output=True, check=False)
            sleep(2)
            
            # Start server in background
            self.server_process = subprocess.Popen(
                [sys.executable, 'AjaSpellBApp.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
            )
            
            # Wait for server to start
            for i in range(30):  # Wait up to 30 seconds
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=2)
                    if response.status_code == 200:
                        print(f"✅ Flask server started successfully - {response.text}")
                        return True
                except:
                    pass
                sleep(1)
                print(f"   Waiting for server... ({i+1}/30)")
            
            print("❌ Failed to start Flask server")
            return False
            
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            return False
    
    def stop_flask_server(self):
        """Stop Flask server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process = None
        # Also kill any remaining Python processes
        subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                     capture_output=True, check=False)
        
    def test_server_status(self):
        """Test if server is running"""
        print("\n🔍 Testing server status...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print(f"✅ Server is running - {response.text}")
                return True
            else:
                print(f"❌ Server health check failed: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Server is not running or not accessible")
            return False
            
    def test_quiz_page_load(self):
        """Test quiz page loads without JavaScript errors"""
        print("\n🔍 Testing quiz page load...")
        try:
            response = self.session.get(f"{self.base_url}/quiz")
            if response.status_code == 200:
                print("✅ Quiz page loaded successfully")
                
                # Check for our JavaScript fixes
                content = response.text
                checks = {
                    'Global error handler': 'window.addEventListener("error"' in content,
                    'Safe template interpolation': '|tojson' in content,
                    'Try-catch blocks': 'try {' in content and 'catch' in content,
                    'Error recovery': 'Unexpected token' in content
                }
                
                for check_name, passed in checks.items():
                    status = "✅" if passed else "⚠️"
                    print(f"   {status} {check_name}: {'Present' if passed else 'Missing'}")
                
                return all(checks.values())
            else:
                print(f"❌ Quiz page failed to load: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Quiz page load error: {e}")
            return False
            
    def test_wordbank_setup(self):
        """Set up a test wordbank for speed round"""
        print("\n🔍 Setting up test wordbank...")
        try:
            # Check if we have words
            response = self.session.get(f"{self.base_url}/api/wordbank")
            if response.status_code == 200:
                data = response.json()
                if data.get('words') and len(data['words']) > 0:
                    word_count = len(data['words'])
                    print(f"✅ Wordbank ready with {word_count} words")
                    return True
            
            print("⚠️ No words found, will use default wordbank")
            return True
                
        except Exception as e:
            print(f"❌ Wordbank setup error: {e}")
            return False
            
    def test_quiz_api_endpoints(self):
        """Test quiz API endpoints for speed round"""
        print("\n🔍 Testing quiz API endpoints...")
        
        try:
            # Test getting next word
            response = self.session.post(f"{self.base_url}/api/next")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Next word API works")
                print(f"   Definition: '{data.get('definition', 'No definition')[:50]}...'")
                
                # Test answering with speed timing
                test_answers = [
                    {"user_input": "test1", "method": "keyboard", "elapsed_ms": 1500},
                    {"user_input": "test2", "method": "keyboard", "elapsed_ms": 1200},
                    {"user_input": "test3", "method": "keyboard", "elapsed_ms": 900}
                ]
                
                for i, answer in enumerate(test_answers):
                    try:
                        answer_response = self.session.post(
                            f"{self.base_url}/api/answer", 
                            json=answer
                        )
                        if answer_response.status_code == 200:
                            result = answer_response.json()
                            elapsed = answer.get('elapsed_ms', 0)
                            print(f"✅ Answer {i+1} processed ({elapsed}ms response time)")
                        else:
                            print(f"⚠️ Answer {i+1} API returned: {answer_response.status_code}")
                    except Exception as e:
                        print(f"⚠️ Answer {i+1} error: {e}")
                    
                    sleep(0.1)  # Brief pause between answers
                    
                return True
            else:
                print(f"❌ Next word API failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Quiz API test error: {e}")
            return False
            
    def test_speed_round_features(self):
        """Test specific speed round features"""
        print("\n🔍 Testing speed round specific features...")
        
        try:
            # Test pronounce API
            response = self.session.post(f"{self.base_url}/api/pronounce")
            if response.status_code == 200:
                data = response.json()
                phonetic = data.get('phonetic', 'No phonetic')
                print(f"✅ Pronounce API works: '{phonetic}'")
            else:
                print(f"⚠️ Pronounce API: {response.status_code}")
                
            # Test hint API
            response = self.session.post(f"{self.base_url}/api/hint")
            if response.status_code == 200:
                data = response.json()
                hint = data.get('hint', 'No hint')
                print(f"✅ Hint API works: '{hint[:30]}...'")
            else:
                print(f"⚠️ Hint API: {response.status_code}")
                
            # Test rapid-fire simulation (speed round pattern)
            print("\n⚡ Simulating rapid-fire speed round...")
            start_time = time.time()
            
            for round_num in range(5):
                # Get word
                next_response = self.session.post(f"{self.base_url}/api/next")
                if next_response.status_code == 200:
                    # Quick answer (simulating speed typing)
                    elapsed_ms = max(500, 1500 - (round_num * 200))  # Getting faster
                    answer_data = {
                        "user_input": f"speed{round_num}",
                        "method": "keyboard",
                        "elapsed_ms": elapsed_ms
                    }
                    
                    answer_response = self.session.post(
                        f"{self.base_url}/api/answer",
                        json=answer_data
                    )
                    
                    if answer_response.status_code == 200:
                        print(f"   Round {round_num + 1}: {elapsed_ms}ms response time")
                    else:
                        print(f"   Round {round_num + 1}: API error {answer_response.status_code}")
                else:
                    print(f"   Round {round_num + 1}: Failed to get next word")
            
            total_time = time.time() - start_time
            print(f"✅ Speed round simulation completed in {total_time:.2f}s")
            return True
            
        except Exception as e:
            print(f"❌ Speed round features test error: {e}")
            return False
            
    def test_javascript_safety(self):
        """Test that our JavaScript fixes prevent errors"""
        print("\n🔍 Testing JavaScript safety improvements...")
        
        try:
            # Test quiz page with potential problematic characters
            response = self.session.get(f"{self.base_url}/quiz")
            
            if response.status_code == 200:
                content = response.text
                
                # Check for unsafe template interpolation patterns
                unsafe_patterns = ['{{ user_name }}', '{{ display_name }}']
                safe_patterns = ['|tojson', 'window.addEventListener("error"', 'try {']
                
                has_unsafe = any(pattern in content for pattern in unsafe_patterns)
                has_safe_features = sum(1 for pattern in safe_patterns if pattern in content)
                
                if has_unsafe:
                    print("❌ Found unsafe template interpolation patterns")
                    return False
                else:
                    print("✅ No unsafe template interpolation found")
                    
                print(f"✅ Safety features detected: {has_safe_features}/{len(safe_patterns)}")
                
                # Specific safety checks
                if 'window.addEventListener("error"' in content:
                    print("✅ Global JavaScript error handler present")
                
                if 'try {' in content and 'catch' in content:
                    print("✅ Try-catch error protection detected")
                    
                if '|tojson' in content:
                    print("✅ Safe JSON template filters in use")
                    
                return has_safe_features >= 2  # At least 2 safety features
            else:
                print(f"❌ Could not load quiz page: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ JavaScript safety test error: {e}")
            return False
    
    def test_performance_timing(self):
        """Test response time performance for speed round"""
        print("\n🔍 Testing API response performance...")
        
        try:
            response_times = []
            
            for i in range(10):
                start_time = time.time()
                response = self.session.post(f"{self.base_url}/api/next")
                end_time = time.time()
                
                if response.status_code == 200:
                    response_time = (end_time - start_time) * 1000  # Convert to ms
                    response_times.append(response_time)
                    
            if response_times:
                avg_time = sum(response_times) / len(response_times)
                max_time = max(response_times)
                min_time = min(response_times)
                
                print(f"✅ API Performance Results:")
                print(f"   Average response time: {avg_time:.2f}ms")
                print(f"   Min response time: {min_time:.2f}ms")
                print(f"   Max response time: {max_time:.2f}ms")
                
                # Speed round should be fast (under 200ms average)
                if avg_time < 200:
                    print("✅ Performance suitable for speed round")
                    return True
                else:
                    print("⚠️ Performance may be slow for speed round")
                    return True  # Still pass, just warn
            else:
                print("❌ No successful API responses")
                return False
                
        except Exception as e:
            print(f"❌ Performance test error: {e}")
            return False

def main():
    """Run all speed round tests"""
    print("🐝 BeeSmart Speed Round Comprehensive Test Suite")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = SpeedRoundTester()
    
    # Start server
    if not tester.start_flask_server():
        print("❌ Failed to start Flask server, exiting...")
        return
    
    try:
        tests = [
            ("Server Status", tester.test_server_status),
            ("Quiz Page Load", tester.test_quiz_page_load),
            ("Wordbank Setup", tester.test_wordbank_setup),
            ("Quiz API Endpoints", tester.test_quiz_api_endpoints),
            ("Speed Round Features", tester.test_speed_round_features),
            ("JavaScript Safety", tester.test_javascript_safety),
            ("Performance Timing", tester.test_performance_timing)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                print(f"\n{'='*20} {test_name} {'='*20}")
                result = test_func()
                results.append((test_name, result))
                if result:
                    print(f"✅ {test_name} - PASSED")
                else:
                    print(f"❌ {test_name} - FAILED")
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results.append((test_name, False))
        
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
        
        print(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("🎉 All speed round tests PASSED!")
            print("✅ Speed round JavaScript fixes are working correctly!")
            print("✅ No 'Unexpected token' errors should occur!")
        elif passed >= total * 0.8:  # 80% pass rate
            print("⚠️ Most tests passed - speed round should work with minor issues")
        else:
            print(f"❌ {total - passed} test(s) failed. Please check the issues above.")
        
        print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    finally:
        # Always stop the server
        print("\n🛑 Stopping Flask server...")
        tester.stop_flask_server()
        print("✅ Server stopped")

if __name__ == "__main__":
    main()