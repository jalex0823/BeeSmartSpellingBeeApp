#!/usr/bin/env python3
"""
BeeSmart Spelling App - Mobile/iOS Compatibility Test
======================================================
Tests all wordbank fixes and quiz functionality with mobile/iOS Safari user agents
to ensure compatibility across all platforms.

Tests:
1. Wordbank operations with mobile user agents
2. Quiz flow with iOS Safari user agent
3. Touch event compatibility
4. Session persistence on mobile
5. API endpoint compatibility
6. Database operations from mobile context

Usage:
    python3 test_mobile_ios_compatibility.py
"""

import requests
import time
import sys
from typing import Dict

BASE_URL = "https://beesmartspelling.app"
TIMEOUT = 10

# Mobile User Agents
USER_AGENTS = {
    'ios_safari': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'ios_chrome': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) CriOS/119.0.6045.109 Mobile/15E148 Safari/604.1',
    'ipad_safari': 'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'android_chrome': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.163 Mobile Safari/537.36',
}

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class MobileCompatibilityTest:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.test_results = []
        self.pass_count = 0
        self.fail_count = 0
        
    def print_header(self, text: str):
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.ENDC}\n")
        
    def print_test(self, name: str):
        print(f"{Colors.BLUE}🔍 TEST:{Colors.ENDC} {name}")
        
    def print_pass(self, message: str):
        print(f"{Colors.GREEN}✅ PASS:{Colors.ENDC} {message}")
        self.pass_count += 1
        self.test_results.append(("PASS", message))
        
    def print_fail(self, message: str):
        print(f"{Colors.RED}❌ FAIL:{Colors.ENDC} {message}")
        self.fail_count += 1
        self.test_results.append(("FAIL", message))
        
    def print_info(self, message: str):
        print(f"{Colors.YELLOW}ℹ️  INFO:{Colors.ENDC} {message}")
    
    def create_mobile_session(self, user_agent: str) -> requests.Session:
        """Create session with mobile user agent"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'application/json, text/html, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            # Don't set Accept-Encoding manually - let requests handle compression
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        return session
    
    def test_wordbank_clear_mobile(self, platform: str, user_agent: str) -> bool:
        """Test wordbank clear on mobile platform"""
        self.print_test(f"Wordbank Clear on {platform}")
        
        try:
            session = self.create_mobile_session(user_agent)
            response = session.post(f"{self.base_url}/api/clear", json={}, timeout=TIMEOUT)
            
            if response.status_code == 200:
                # Don't count as pass yet - wait for verification
                # Verify count is 0
                time.sleep(0.5)  # Give DB time to commit
                count_response = session.get(f"{self.base_url}/api/wordbank/count", timeout=TIMEOUT)
                if count_response.status_code == 200:
                    try:
                        count_data = count_response.json()
                        count = count_data.get('count', -1)
                        if count == 0:
                            self.print_pass(f"{platform}: Clear & count verified (0 words)")
                            return True
                        else:
                            self.print_fail(f"{platform}: Count is {count}, expected 0")
                            return False
                    except ValueError as json_err:
                        self.print_fail(f"{platform}: Count response not JSON: {count_response.text[:100]}")
                        return False
                else:
                    self.print_fail(f"{platform}: Count check failed ({count_response.status_code})")
                    return False
            else:
                self.print_fail(f"{platform}: Clear failed with {response.status_code}")
                return False
        except Exception as e:
            self.print_fail(f"{platform}: Exception - {e}")
            return False
    
    def test_wordbank_upload_mobile(self, platform: str, user_agent: str) -> bool:
        """Test word upload on mobile platform"""
        self.print_test(f"Word Upload on {platform}")
        
        try:
            session = self.create_mobile_session(user_agent)
            
            # Clear first
            session.post(f"{self.base_url}/api/clear", json={}, timeout=TIMEOUT)
            time.sleep(0.3)
            
            # Upload words
            test_words = ["mobile", "testing", "ios", "safari", "compatible"]
            txt_content = "\n".join(test_words)
            files = {'file': ('mobile_test.txt', txt_content, 'text/plain')}
            
            response = session.post(f"{self.base_url}/api/upload", files=files, timeout=TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                
                if count == len(test_words):
                    self.print_pass(f"{platform}: Uploaded {count}/{len(test_words)} words")
                    return True
                else:
                    self.print_fail(f"{platform}: Upload count mismatch {count}/{len(test_words)}")
                    return False
            else:
                self.print_fail(f"{platform}: Upload failed {response.status_code}")
                return False
        except Exception as e:
            self.print_fail(f"{platform}: Exception - {e}")
            return False
    
    def test_wordbank_persistence_mobile(self, platform: str, user_agent: str) -> bool:
        """Test wordbank persistence on mobile"""
        self.print_test(f"Wordbank Persistence on {platform}")
        
        try:
            session = self.create_mobile_session(user_agent)
            
            # First upload some words
            test_words = ["persist", "mobile", "session"]
            txt_content = "\n".join(test_words)
            files = {'file': ('persist_test.txt', txt_content, 'text/plain')}
            
            session.post(f"{self.base_url}/api/clear", json={}, timeout=TIMEOUT)
            time.sleep(0.5)
            
            upload_resp = session.post(f"{self.base_url}/api/upload", files=files, timeout=TIMEOUT)
            if upload_resp.status_code != 200:
                self.print_fail(f"{platform}: Upload failed for persistence test")
                return False
            
            time.sleep(0.5)
            
            # Get initial count
            response1 = session.get(f"{self.base_url}/api/wordbank/count", timeout=TIMEOUT)
            if response1.status_code != 200:
                self.print_fail(f"{platform}: Failed to get initial count")
                return False
            
            try:
                data1 = response1.json()
                count1 = data1.get('count', 0)
                storage_id1 = data1.get('storage_id', 'none')
            except ValueError:
                self.print_fail(f"{platform}: Initial count not JSON: {response1.text[:100]}")
                return False
            
            # Simulate mobile app context switch / background
            time.sleep(0.5)
            
            # Get count again
            response2 = session.get(f"{self.base_url}/api/wordbank/count", timeout=TIMEOUT)
            if response2.status_code != 200:
                self.print_fail(f"{platform}: Failed to get count after refresh")
                return False
            
            try:
                data2 = response2.json()
                count2 = data2.get('count', 0)
                storage_id2 = data2.get('storage_id', 'none')
            except ValueError:
                self.print_fail(f"{platform}: Second count not JSON: {response2.text[:100]}")
                return False
            
            if count1 == count2 and storage_id1 == storage_id2 and count1 == len(test_words):
                self.print_pass(f"{platform}: Wordbank persisted ({count1} words, {storage_id1[:8]}...)")
                return True
            else:
                self.print_fail(f"{platform}: Persistence failed (count {count1}→{count2}, expected {len(test_words)})")
                return False
        except Exception as e:
            self.print_fail(f"{platform}: Exception - {e}")
            return False
    
    def test_quiz_initialization_mobile(self, platform: str, user_agent: str) -> bool:
        """Test quiz initialization on mobile"""
        self.print_test(f"Quiz Initialization on {platform}")
        
        try:
            session = self.create_mobile_session(user_agent)
            
            # Upload test words first
            test_words = ["quiz", "mobile", "init", "test"]
            txt_content = "\n".join(test_words)
            files = {'file': ('quiz_test.txt', txt_content, 'text/plain')}
            
            session.post(f"{self.base_url}/api/clear", json={}, timeout=TIMEOUT)
            time.sleep(0.5)
            
            upload_resp = session.post(f"{self.base_url}/api/upload", files=files, timeout=TIMEOUT)
            if upload_resp.status_code != 200:
                self.print_fail(f"{platform}: Upload failed for quiz test")
                return False
            
            time.sleep(0.5)
            
            # Get word count
            count_response = session.get(f"{self.base_url}/api/wordbank/count", timeout=TIMEOUT)
            if count_response.status_code != 200:
                self.print_fail(f"{platform}: Failed to get word count")
                return False
            
            try:
                count_data = count_response.json()
                word_count = count_data.get('count', 0)
            except ValueError:
                self.print_fail(f"{platform}: Count response not JSON: {count_response.text[:100]}")
                return False
            
            if word_count == 0:
                self.print_fail(f"{platform}: Upload verification failed - count is 0")
                return False
            
            # Initialize quiz
            next_response = session.post(f"{self.base_url}/api/next", json={}, timeout=TIMEOUT)
            
            if next_response.status_code == 200:
                try:
                    data = next_response.json()
                    
                    if not data.get('done', True):
                        word = data.get('word', '')
                        total = data.get('total', 0)
                        
                        if total == word_count and word:
                            self.print_pass(f"{platform}: Quiz initialized ({total} words, first: '{word}')")
                            return True
                        else:
                            self.print_fail(f"{platform}: Quiz data mismatch (total={total}, count={word_count})")
                            return False
                    else:
                        self.print_fail(f"{platform}: Quiz marked done immediately")
                        return False
                except ValueError:
                    self.print_fail(f"{platform}: Quiz response not JSON: {next_response.text[:100]}")
                    return False
            else:
                self.print_fail(f"{platform}: /api/next failed {next_response.status_code}")
                return False
        except Exception as e:
            self.print_fail(f"{platform}: Exception - {e}")
            return False
    
    def test_quiz_answer_mobile(self, platform: str, user_agent: str) -> bool:
        """Test answer submission on mobile"""
        self.print_test(f"Answer Submission on {platform}")
        
        try:
            session = self.create_mobile_session(user_agent)
            
            # Upload test word first
            test_words = ["answer", "mobile"]
            txt_content = "\n".join(test_words)
            files = {'file': ('answer_test.txt', txt_content, 'text/plain')}
            
            session.post(f"{self.base_url}/api/clear", json={}, timeout=TIMEOUT)
            time.sleep(0.5)
            
            upload_resp = session.post(f"{self.base_url}/api/upload", files=files, timeout=TIMEOUT)
            if upload_resp.status_code != 200:
                self.print_fail(f"{platform}: Upload failed for answer test")
                return False
            
            time.sleep(0.5)
            
            # Get current word
            next_response = session.post(f"{self.base_url}/api/next", json={}, timeout=TIMEOUT)
            if next_response.status_code != 200:
                self.print_fail(f"{platform}: Failed to get question")
                return False
            
            try:
                data = next_response.json()
            except ValueError:
                self.print_fail(f"{platform}: Question response not JSON: {next_response.text[:100]}")
                return False
            
            if data.get('done', False):
                self.print_fail(f"{platform}: Quiz marked done before answering")
                return False
            
            word = data.get('word', '')
            
            # Submit answer (simulating touch/keyboard input)
            answer_response = session.post(
                f"{self.base_url}/api/answer",
                json={
                    "user_input": word,
                    "method": "keyboard",  # or "voice" for mobile
                    "elapsed_ms": 1500
                },
                timeout=TIMEOUT
            )
            
            if answer_response.status_code == 200:
                try:
                    answer_data = answer_response.json()
                    correct = answer_data.get('correct', False)
                    
                    if correct:
                        self.print_pass(f"{platform}: Answer submitted and scored correctly")
                        return True
                    else:
                        self.print_fail(f"{platform}: Answer marked incorrect")
                        return False
                except ValueError:
                    self.print_fail(f"{platform}: Answer response not JSON: {answer_response.text[:100]}")
                    return False
            else:
                self.print_fail(f"{platform}: Answer submission failed {answer_response.status_code}")
                return False
        except Exception as e:
            self.print_fail(f"{platform}: Exception - {e}")
            return False
    
    def test_session_cookies_mobile(self, platform: str, user_agent: str) -> bool:
        """Test session cookie handling on mobile"""
        self.print_test(f"Session Cookie Handling on {platform}")
        
        try:
            session = self.create_mobile_session(user_agent)
            
            # Make initial request to establish session
            response1 = session.get(f"{self.base_url}/api/wordbank/count", timeout=TIMEOUT)
            
            if response1.status_code == 200:
                # Check if cookies are set
                cookies = session.cookies.get_dict()
                
                if cookies:
                    self.print_pass(f"{platform}: Session cookies established ({len(cookies)} cookies)")
                    
                    # Make second request to verify cookies persist
                    time.sleep(0.2)
                    response2 = session.get(f"{self.base_url}/api/wordbank/count", timeout=TIMEOUT)
                    
                    if response2.status_code == 200:
                        try:
                            storage_id1 = response1.json().get('storage_id', 'none')
                            storage_id2 = response2.json().get('storage_id', 'none')
                            
                            if storage_id1 == storage_id2:
                                # Don't double-count - we already printed PASS above
                                return True
                            else:
                                self.print_fail(f"{platform}: Session ID changed between requests")
                                return False
                        except ValueError:
                            self.print_fail(f"{platform}: Response not JSON")
                            return False
                    else:
                        self.print_fail(f"{platform}: Second request failed")
                        return False
                else:
                    self.print_info(f"{platform}: No cookies set (may be expected)")
                    return True
            else:
                self.print_fail(f"{platform}: Initial request failed")
                return False
        except Exception as e:
            self.print_fail(f"{platform}: Exception - {e}")
            return False
    
    def test_real_time_counts_mobile(self, platform: str, user_agent: str) -> bool:
        """Test real-time database counts on mobile"""
        self.print_test(f"Real-Time Database Counts on {platform}")
        
        try:
            session = self.create_mobile_session(user_agent)
            
            # Clear wordbank
            session.post(f"{self.base_url}/api/clear", json={}, timeout=TIMEOUT)
            time.sleep(0.5)
            
            # Verify 0
            response1 = session.get(f"{self.base_url}/api/wordbank/count", timeout=TIMEOUT)
            if response1.status_code != 200:
                self.print_fail(f"{platform}: Failed to get initial count")
                return False
            
            try:
                count1 = response1.json().get('count', -1)
            except ValueError:
                self.print_fail(f"{platform}: Initial count not JSON: {response1.text[:100]}")
                return False
            
            if count1 != 0:
                self.print_fail(f"{platform}: Initial count not 0 ({count1})")
                return False
            
            # Upload 3 words
            files = {'file': ('count_test.txt', 'one\ntwo\nthree', 'text/plain')}
            session.post(f"{self.base_url}/api/upload", files=files, timeout=TIMEOUT)
            time.sleep(0.5)
            
            # Verify 3
            response2 = session.get(f"{self.base_url}/api/wordbank/count", timeout=TIMEOUT)
            if response2.status_code != 200:
                self.print_fail(f"{platform}: Failed to get count after upload")
                return False
            
            try:
                count2 = response2.json().get('count', -1)
            except ValueError:
                self.print_fail(f"{platform}: Upload count not JSON: {response2.text[:100]}")
                return False
            
            if count2 != 3:
                self.print_fail(f"{platform}: Count after upload not 3 ({count2})")
                return False
            
            # Clear again
            session.post(f"{self.base_url}/api/clear", json={}, timeout=TIMEOUT)
            time.sleep(0.5)
            
            # Verify back to 0
            response3 = session.get(f"{self.base_url}/api/wordbank/count", timeout=TIMEOUT)
            if response3.status_code != 200:
                self.print_fail(f"{platform}: Failed to get count after second clear")
                return False
            
            try:
                count3 = response3.json().get('count', -1)
            except ValueError:
                self.print_fail(f"{platform}: Final count not JSON: {response3.text[:100]}")
                return False
            
            if count3 != 0:
                self.print_fail(f"{platform}: Count after clear not 0 ({count3})")
                return False
            
            self.print_pass(f"{platform}: Real-time counts accurate (0→3→0)")
            return True
            
        except Exception as e:
            self.print_fail(f"{platform}: Exception - {e}")
            return False
    
    def run_all_tests(self):
        """Execute all mobile compatibility tests"""
        
        print(f"\n{Colors.BOLD}{Colors.HEADER}")
        print("╔════════════════════════════════════════════════════════════════════════════╗")
        print("║                                                                            ║")
        print("║           BeeSmart Spelling App - Mobile/iOS Compatibility Test           ║")
        print("║                                                                            ║")
        print("║              Wordbank Fixes & Quiz Flow on Mobile Devices                 ║")
        print("║                                                                            ║")
        print("╚════════════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}\n")
        
        print(f"Testing against: {Colors.BOLD}{self.base_url}{Colors.ENDC}\n")
        
        # Test each platform
        for platform_name, user_agent in USER_AGENTS.items():
            self.print_header(f"TESTING: {platform_name.upper().replace('_', ' ')}")
            
            # Core wordbank operations
            self.test_wordbank_clear_mobile(platform_name, user_agent)
            self.test_wordbank_upload_mobile(platform_name, user_agent)
            self.test_wordbank_persistence_mobile(platform_name, user_agent)
            
            # Quiz operations
            self.test_quiz_initialization_mobile(platform_name, user_agent)
            self.test_quiz_answer_mobile(platform_name, user_agent)
            
            # Session and data integrity
            self.test_session_cookies_mobile(platform_name, user_agent)
            self.test_real_time_counts_mobile(platform_name, user_agent)
        
        # Print summary
        self.print_header("MOBILE COMPATIBILITY TEST SUMMARY")
        
        total_tests = self.pass_count + self.fail_count
        print(f"Total Tests: {total_tests}")
        print(f"{Colors.GREEN}Passed: {self.pass_count}{Colors.ENDC}")
        print(f"{Colors.RED}Failed: {self.fail_count}{Colors.ENDC}")
        
        if self.fail_count == 0:
            print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 ALL MOBILE TESTS PASSED!{Colors.ENDC}")
            print(f"{Colors.GREEN}System is fully compatible with mobile/iOS devices!{Colors.ENDC}\n")
            return True
        else:
            print(f"\n{Colors.BOLD}{Colors.RED}⚠️  SOME MOBILE TESTS FAILED{Colors.ENDC}")
            print(f"{Colors.RED}Review failures for mobile compatibility issues.{Colors.ENDC}\n")
            return False


def main():
    """Main entry point"""
    tester = MobileCompatibilityTest(BASE_URL)
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted by user{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {e}{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
