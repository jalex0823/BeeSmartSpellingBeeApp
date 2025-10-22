"""
Production Smoke Test - BeeSmart Spelling Bee App
Tests critical user flows on live Railway deployment
"""

import requests
import time
import json
from io import BytesIO

BASE_URL = "https://beesmartspellingbee.up.railway.app"
TEST_USER = "BigDaddy2"
TEST_PASSWORD = "Aja123!!"

def print_test(name):
    """Print test header"""
    print(f"\n{'='*70}")
    print(f"🧪 TEST: {name}")
    print('='*70)

def print_result(success, message):
    """Print test result"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")
    return success

class SmokeTest:
    def __init__(self):
        self.session = requests.Session()
        self.results = []
    
    def test_health(self):
        """Test 1: Health endpoint"""
        print_test("Health Check")
        try:
            r = self.session.get(f"{BASE_URL}/health", timeout=10)
            data = r.json()
            
            success = (
                r.status_code == 200 and
                data.get('status') == 'ok' and
                data.get('version') == '1.6'
            )
            
            msg = f"Health: {r.status_code}, Status: {data.get('status')}, Version: {data.get('version')}"
            self.results.append(print_result(success, msg))
            return success
        except Exception as e:
            self.results.append(print_result(False, f"Health check failed: {e}"))
            return False
    
    def test_homepage(self):
        """Test 2: Homepage loads"""
        print_test("Homepage Access")
        try:
            r = self.session.get(BASE_URL, timeout=10)
            success = r.status_code == 200 and 'BeeSmart' in r.text
            
            msg = f"Homepage loaded: {r.status_code}, Contains 'BeeSmart': {success}"
            self.results.append(print_result(success, msg))
            return success
        except Exception as e:
            self.results.append(print_result(False, f"Homepage failed: {e}"))
            return False
    
    def test_login(self):
        """Test 3: Login with BigDaddy2"""
        print_test("User Login")
        try:
            # Get login page first to establish session
            r = self.session.get(f"{BASE_URL}/auth/login", timeout=10)
            
            # Attempt login
            r = self.session.post(
                f"{BASE_URL}/auth/login",
                data={
                    'username': TEST_USER,
                    'password': TEST_PASSWORD
                },
                timeout=10,
                allow_redirects=False
            )
            
            # Check for redirect (successful login)
            success = r.status_code in [302, 303] or 'dashboard' in r.text.lower()
            
            msg = f"Login attempt: {r.status_code}, Redirect: {r.status_code in [302, 303]}"
            self.results.append(print_result(success, msg))
            return success
        except Exception as e:
            self.results.append(print_result(False, f"Login failed: {e}"))
            return False
    
    def test_dashboard(self):
        """Test 4: Dashboard access (requires auth)"""
        print_test("Dashboard Access")
        try:
            r = self.session.get(f"{BASE_URL}/dashboard", timeout=10)
            success = r.status_code == 200 and 'dashboard' in r.text.lower()
            
            msg = f"Dashboard: {r.status_code}, Contains dashboard content: {success}"
            self.results.append(print_result(success, msg))
            return success
        except Exception as e:
            self.results.append(print_result(False, f"Dashboard failed: {e}"))
            return False
    
    def test_word_upload(self):
        """Test 5: Word list upload"""
        print_test("Word List Upload")
        try:
            # Create a simple test word list
            test_words = "bee\nspell\nhoney\nhive\nqueen\n"
            
            files = {
                'file': ('test_words.txt', BytesIO(test_words.encode()), 'text/plain')
            }
            
            r = self.session.post(
                f"{BASE_URL}/api/upload",
                files=files,
                timeout=15
            )
            
            data = r.json() if r.status_code == 200 else {}
            success = r.status_code == 200 and data.get('success') == True
            
            word_count = data.get('word_count', 0)
            msg = f"Upload: {r.status_code}, Success: {success}, Words: {word_count}"
            self.results.append(print_result(success, msg))
            return success
        except Exception as e:
            self.results.append(print_result(False, f"Upload failed: {e}"))
            return False
    
    def test_wordbank(self):
        """Test 6: Wordbank API"""
        print_test("Wordbank Retrieval")
        try:
            r = self.session.get(f"{BASE_URL}/api/wordbank", timeout=10)
            
            data = r.json() if r.status_code == 200 else {}
            success = r.status_code == 200 and len(data) > 0
            
            word_count = len(data)
            msg = f"Wordbank: {r.status_code}, Words loaded: {word_count}"
            self.results.append(print_result(success, msg))
            return success
        except Exception as e:
            self.results.append(print_result(False, f"Wordbank failed: {e}"))
            return False
    
    def test_quiz_next(self):
        """Test 7: Quiz next word"""
        print_test("Quiz Next Word")
        try:
            r = self.session.post(f"{BASE_URL}/api/next", timeout=10)
            
            data = r.json() if r.status_code == 200 else {}
            success = r.status_code == 200 and 'definition' in data
            
            has_def = 'definition' in data
            has_hint = 'hint' in data
            msg = f"Next word: {r.status_code}, Has definition: {has_def}, Has hint: {has_hint}"
            self.results.append(print_result(success, msg))
            return success
        except Exception as e:
            self.results.append(print_result(False, f"Quiz next failed: {e}"))
            return False
    
    def test_dictionary_fallback(self):
        """Test 8: Dictionary fallback system"""
        print_test("Dictionary Fallback")
        try:
            # Test with a word that should have a definition
            r = self.session.get(f"{BASE_URL}/api/test-dictionary", timeout=15)
            
            data = r.json() if r.status_code == 200 else {}
            
            # Check if we got a result (from API, cache, or fallback)
            has_result = 'result' in data or 'message' in data
            success = r.status_code == 200 and has_result
            
            msg = f"Dictionary: {r.status_code}, Has result: {has_result}"
            if 'result' in data:
                msg += f", Definition available: {bool(data['result'])}"
            
            self.results.append(print_result(success, msg))
            return success
        except Exception as e:
            self.results.append(print_result(False, f"Dictionary test failed: {e}"))
            return False
    
    def test_quiz_page(self):
        """Test 9: Quiz page loads"""
        print_test("Quiz Page")
        try:
            r = self.session.get(f"{BASE_URL}/quiz", timeout=10)
            success = r.status_code == 200 and 'quiz' in r.text.lower()
            
            msg = f"Quiz page: {r.status_code}, Page loaded: {success}"
            self.results.append(print_result(success, msg))
            return success
        except Exception as e:
            self.results.append(print_result(False, f"Quiz page failed: {e}"))
            return False
    
    def run_all(self):
        """Run all smoke tests"""
        print("\n" + "="*70)
        print("🐝 BeeSmart Production Smoke Test")
        print(f"🌐 Target: {BASE_URL}")
        print("="*70)
        
        tests = [
            self.test_health,
            self.test_homepage,
            self.test_login,
            self.test_dashboard,
            self.test_word_upload,
            self.test_wordbank,
            self.test_quiz_next,
            self.test_dictionary_fallback,
            self.test_quiz_page,
        ]
        
        for test in tests:
            try:
                test()
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                print(f"❌ Test crashed: {e}")
                self.results.append(False)
        
        # Summary
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        
        passed = sum(self.results)
        total = len(self.results)
        percentage = (passed / total * 100) if total > 0 else 0
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        print(f"📈 Success Rate: {percentage:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! Deployment is healthy!")
        elif passed >= total * 0.8:
            print("\n⚠️  MOSTLY PASSING - Check failed tests")
        else:
            print("\n❌ CRITICAL ISSUES - Multiple failures detected")
        
        print("="*70)
        
        return passed == total

if __name__ == "__main__":
    tester = SmokeTest()
    success = tester.run_all()
    exit(0 if success else 1)
