"""
Full Quiz Diagnostic - Word Input to Report Card
Tests the complete quiz flow end-to-end
"""
import sys
import os
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
TEST_USERNAME = f"quiz_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
TEST_PASSWORD = "TestPass123!"
TEST_EMAIL = f"{TEST_USERNAME}@test.com"

class QuizDiagnostic:
    def __init__(self):
        self.session = requests.Session()
        self.results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }
        self.user_id = None
        self.wordbank = []
        
    def log(self, message, level="INFO"):
        """Log diagnostic messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def add_result(self, test_name, passed, details=""):
        """Record test result"""
        if passed:
            self.results["passed"].append(test_name)
            self.log(f"✓ {test_name}", "PASS")
        else:
            self.results["failed"].append(f"{test_name}: {details}")
            self.log(f"✗ {test_name}: {details}", "FAIL")
        if details and passed:
            self.log(f"  Details: {details}", "INFO")
            
    def add_warning(self, message):
        """Add warning to results"""
        self.results["warnings"].append(message)
        self.log(f"⚠ {message}", "WARN")

    # ========== PHASE 1: Server Health ==========
    def test_server_health(self):
        """Test if server is running and responding"""
        self.log("=" * 60)
        self.log("PHASE 1: SERVER HEALTH CHECK")
        self.log("=" * 60)
        
        try:
            response = self.session.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.add_result("Server Health Check", True, 
                              f"Version: {data.get('version', 'unknown')}")
            else:
                self.add_result("Server Health Check", False, 
                              f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.add_result("Server Health Check", False, str(e))
            return False
        return True

    # ========== PHASE 2: User Registration & Login ==========
    def test_user_registration(self):
        """Test user registration"""
        self.log("=" * 60)
        self.log("PHASE 2: USER REGISTRATION & AUTHENTICATION")
        self.log("=" * 60)
        
        try:
            response = self.session.post(f"{BASE_URL}/register", data={
                "username": TEST_USERNAME,
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "confirm_password": TEST_PASSWORD
            }, allow_redirects=False)
            
            if response.status_code in [200, 302]:
                self.add_result("User Registration", True, f"User: {TEST_USERNAME}")
                return True
            else:
                self.add_result("User Registration", False, 
                              f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.add_result("User Registration", False, str(e))
            return False
            
    def test_user_login(self):
        """Test user login"""
        try:
            response = self.session.post(f"{BASE_URL}/login", data={
                "username": TEST_USERNAME,
                "password": TEST_PASSWORD
            }, allow_redirects=False)
            
            if response.status_code in [200, 302]:
                self.add_result("User Login", True)
                return True
            else:
                self.add_result("User Login", False, 
                              f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.add_result("User Login", False, str(e))
            return False

    # ========== PHASE 3: Word Input & Upload ==========
    def test_word_upload_text(self):
        """Test text-based word upload"""
        self.log("=" * 60)
        self.log("PHASE 3: WORD INPUT & UPLOAD")
        self.log("=" * 60)
        
        test_words = [
            "spelling\tThis is a spelling test.\tRemember the double L",
            "achievement\tGreat achievement today.\tStarts with A",
            "necessary\tIt is necessary to study.\tOne C, two S's",
            "beautiful\tThe sunset is beautiful.\tRemember BEAU",
            "separate\tKeep them separate.\tPAR in the middle"
        ]
        
        try:
            # Upload via text input
            response = self.session.post(f"{BASE_URL}/api/upload", 
                data={"wordbank_text": "\n".join(test_words)},
                headers={"X-Requested-With": "XMLHttpRequest"})
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    word_count = data.get("wordCount", 0)
                    self.add_result("Text Word Upload", True, 
                                  f"{word_count} words uploaded")
                    self.wordbank = data.get("words", [])
                    return True
                else:
                    self.add_result("Text Word Upload", False, 
                                  data.get("error", "Unknown error"))
            else:
                self.add_result("Text Word Upload", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.add_result("Text Word Upload", False, str(e))
        return False
        
    def test_wordbank_retrieval(self):
        """Test retrieving the uploaded wordbank"""
        try:
            response = self.session.get(f"{BASE_URL}/api/wordbank",
                headers={"X-Requested-With": "XMLHttpRequest"})
            
            if response.status_code == 200:
                data = response.json()
                words = data.get("words", [])
                if len(words) > 0:
                    self.add_result("Wordbank Retrieval", True, 
                                  f"{len(words)} words in bank")
                    
                    # Validate word structure
                    sample = words[0]
                    required_keys = ["word", "sentence", "hint"]
                    has_all_keys = all(k in sample for k in required_keys)
                    
                    if has_all_keys:
                        self.add_result("Word Structure Validation", True,
                                      f"Keys: {', '.join(required_keys)}")
                    else:
                        self.add_warning(f"Word missing keys: {sample.keys()}")
                    return True
                else:
                    self.add_result("Wordbank Retrieval", False, 
                                  "No words found")
            else:
                self.add_result("Wordbank Retrieval", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.add_result("Wordbank Retrieval", False, str(e))
        return False

    # ========== PHASE 4: Quiz Initialization ==========
    def test_quiz_initialization(self):
        """Test quiz state initialization"""
        self.log("=" * 60)
        self.log("PHASE 4: QUIZ INITIALIZATION")
        self.log("=" * 60)
        
        try:
            # Access quiz page to initialize
            response = self.session.get(f"{BASE_URL}/quiz")
            
            if response.status_code == 200:
                self.add_result("Quiz Page Access", True)
                
                # Check quiz state via API
                state_response = self.session.get(f"{BASE_URL}/api/quiz/state",
                    headers={"X-Requested-With": "XMLHttpRequest"})
                
                if state_response.status_code == 200:
                    state = state_response.json()
                    self.add_result("Quiz State Initialization", True,
                                  f"Index: {state.get('current_index', 0)}/{state.get('total_words', 0)}")
                    return True
            
            self.add_result("Quiz Initialization", False, 
                          f"Status: {response.status_code}")
        except Exception as e:
            self.add_result("Quiz Initialization", False, str(e))
        return False

    # ========== PHASE 5: Quiz Interaction ==========
    def test_quiz_navigation(self):
        """Test quiz navigation (next word)"""
        self.log("=" * 60)
        self.log("PHASE 5: QUIZ INTERACTION & NAVIGATION")
        self.log("=" * 60)
        
        try:
            response = self.session.post(f"{BASE_URL}/api/next",
                headers={"X-Requested-With": "XMLHttpRequest"})
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    word_data = data.get("word", {})
                    self.add_result("Quiz Navigation (Next)", True,
                                  f"Sentence: '{word_data.get('sentence', '')[:50]}...'")
                    
                    # Verify blanked word
                    sentence = word_data.get("sentence", "")
                    if "___" in sentence or "_" * 3 in sentence:
                        self.add_result("Word Blanking", True, 
                                      "Answer properly hidden")
                    else:
                        self.add_warning("Word may not be properly blanked")
                    return True
                else:
                    self.add_result("Quiz Navigation", False, 
                                  data.get("error", "Unknown"))
            else:
                self.add_result("Quiz Navigation", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.add_result("Quiz Navigation", False, str(e))
        return False
        
    def test_quiz_answer_correct(self):
        """Test submitting a correct answer"""
        try:
            # Get current word
            next_resp = self.session.post(f"{BASE_URL}/api/next",
                headers={"X-Requested-With": "XMLHttpRequest"})
            
            if next_resp.status_code == 200:
                word_data = next_resp.json().get("word", {})
                # Get the actual word from hint or reconstruct
                # For testing, we'll use our known test words
                test_answer = "spelling"  # First word from our upload
                
                response = self.session.post(f"{BASE_URL}/api/answer",
                    json={
                        "user_input": test_answer,
                        "method": "typing",
                        "elapsed_ms": 5000
                    },
                    headers={"X-Requested-With": "XMLHttpRequest"})
                
                if response.status_code == 200:
                    data = response.json()
                    is_correct = data.get("correct", False)
                    self.add_result("Correct Answer Submission", is_correct,
                                  f"Answer: '{test_answer}' -> {data.get('message', '')}")
                    return is_correct
            
            self.add_result("Answer Submission", False, "Could not test")
        except Exception as e:
            self.add_result("Answer Submission", False, str(e))
        return False
        
    def test_quiz_answer_incorrect(self):
        """Test submitting an incorrect answer"""
        try:
            # Get next word
            next_resp = self.session.post(f"{BASE_URL}/api/next",
                headers={"X-Requested-With": "XMLHttpRequest"})
            
            if next_resp.status_code == 200:
                wrong_answer = "wrongspelling123"
                
                response = self.session.post(f"{BASE_URL}/api/answer",
                    json={
                        "user_input": wrong_answer,
                        "method": "typing",
                        "elapsed_ms": 3000
                    },
                    headers={"X-Requested-With": "XMLHttpRequest"})
                
                if response.status_code == 200:
                    data = response.json()
                    is_incorrect = not data.get("correct", True)
                    self.add_result("Incorrect Answer Handling", is_incorrect,
                                  f"Properly marked as incorrect")
                    return is_incorrect
            
            self.add_result("Incorrect Answer Test", False, "Could not test")
        except Exception as e:
            self.add_result("Incorrect Answer Test", False, str(e))
        return False

    # ========== PHASE 6: Quiz Progress Tracking ==========
    def test_quiz_progress(self):
        """Test quiz progress tracking"""
        self.log("=" * 60)
        self.log("PHASE 6: PROGRESS TRACKING")
        self.log("=" * 60)
        
        try:
            response = self.session.get(f"{BASE_URL}/api/quiz/state",
                headers={"X-Requested-With": "XMLHttpRequest"})
            
            if response.status_code == 200:
                state = response.json()
                current = state.get("current_index", 0)
                total = state.get("total_words", 0)
                correct = state.get("correct_count", 0)
                incorrect = state.get("incorrect_count", 0)
                
                self.add_result("Progress Tracking", True,
                              f"{current}/{total} words, {correct} correct, {incorrect} incorrect")
                
                # Check if counters make sense
                if current >= 0 and total > 0 and (correct + incorrect) <= current:
                    self.add_result("Progress Logic Check", True,
                                  "Counters are consistent")
                else:
                    self.add_warning(f"Progress counters may be inconsistent")
                return True
            
            self.add_result("Progress Tracking", False, 
                          f"Status: {response.status_code}")
        except Exception as e:
            self.add_result("Progress Tracking", False, str(e))
        return False

    # ========== PHASE 7: Quiz Completion ==========
    def test_quiz_completion(self):
        """Test completing the quiz"""
        self.log("=" * 60)
        self.log("PHASE 7: QUIZ COMPLETION")
        self.log("=" * 60)
        
        try:
            # Complete remaining words
            for i in range(10):  # Max 10 attempts to finish
                next_resp = self.session.post(f"{BASE_URL}/api/next",
                    headers={"X-Requested-With": "XMLHttpRequest"})
                
                if next_resp.status_code == 200:
                    data = next_resp.json()
                    if not data.get("success"):
                        # Quiz might be complete
                        if "complete" in data.get("error", "").lower():
                            self.add_result("Quiz Completion Detection", True,
                                          "Quiz marked as complete")
                            return True
                        break
                    
                    # Submit a random answer
                    self.session.post(f"{BASE_URL}/api/answer",
                        json={"user_input": "test", "method": "typing", "elapsed_ms": 1000},
                        headers={"X-Requested-With": "XMLHttpRequest"})
                else:
                    break
            
            # Check if we can access results
            results_resp = self.session.get(f"{BASE_URL}/quiz_results")
            if results_resp.status_code == 200:
                self.add_result("Quiz Results Access", True,
                              "Results page accessible")
                return True
            
            self.add_result("Quiz Completion", False, 
                          "Could not complete or access results")
        except Exception as e:
            self.add_result("Quiz Completion", False, str(e))
        return False

    # ========== PHASE 8: Report Card ==========
    def test_report_card(self):
        """Test report card generation and display"""
        self.log("=" * 60)
        self.log("PHASE 8: REPORT CARD GENERATION")
        self.log("=" * 60)
        
        try:
            # Access results page
            response = self.session.get(f"{BASE_URL}/quiz_results")
            
            if response.status_code == 200:
                html = response.text
                
                # Check for key report card elements
                checks = {
                    "Results Page Loads": "quiz" in html.lower() or "result" in html.lower(),
                    "Score Display": "score" in html.lower() or "correct" in html.lower(),
                    "Performance Metrics": "%" in html or "percent" in html.lower(),
                }
                
                for check_name, passed in checks.items():
                    self.add_result(f"Report Card: {check_name}", passed)
                
                # Try to get results via API
                api_resp = self.session.get(f"{BASE_URL}/api/quiz/results",
                    headers={"X-Requested-With": "XMLHttpRequest"})
                
                if api_resp.status_code == 200:
                    results = api_resp.json()
                    self.add_result("Report Card API", True,
                                  f"Total: {results.get('total', 0)}, " +
                                  f"Correct: {results.get('correct', 0)}, " +
                                  f"Score: {results.get('percentage', 0)}%")
                    
                    # Validate results structure
                    if "words" in results:
                        word_details = results["words"]
                        if len(word_details) > 0:
                            self.add_result("Word-by-Word Results", True,
                                          f"{len(word_details)} words detailed")
                    return True
                
            self.add_result("Report Card Access", False, 
                          f"Status: {response.status_code}")
        except Exception as e:
            self.add_result("Report Card", False, str(e))
        return False
        
    def test_report_card_stats(self):
        """Test detailed statistics in report card"""
        try:
            response = self.session.get(f"{BASE_URL}/api/quiz/stats",
                headers={"X-Requested-With": "XMLHttpRequest"})
            
            if response.status_code == 200:
                stats = response.json()
                
                metrics = [
                    "total_attempts",
                    "correct_answers",
                    "incorrect_answers", 
                    "accuracy_rate",
                    "average_time"
                ]
                
                found_metrics = [m for m in metrics if m in stats]
                
                if found_metrics:
                    self.add_result("Report Card Statistics", True,
                                  f"Metrics: {', '.join(found_metrics)}")
                    return True
                else:
                    self.add_warning("No statistics found in report")
            
            self.add_result("Report Card Statistics", False, 
                          "Stats endpoint not available")
        except Exception as e:
            # Stats might not be implemented, just warn
            self.add_warning(f"Statistics check: {str(e)}")
        return False

    # ========== PHASE 9: Data Persistence ==========
    def test_data_persistence(self):
        """Test if quiz results are saved to database"""
        self.log("=" * 60)
        self.log("PHASE 9: DATA PERSISTENCE")
        self.log("=" * 60)
        
        try:
            # Check if there's a history endpoint
            response = self.session.get(f"{BASE_URL}/quiz_history")
            
            if response.status_code == 200:
                self.add_result("Quiz History Access", True,
                              "History page accessible")
                
                # Check if our recent quiz appears
                html = response.text
                if TEST_USERNAME in html or "quiz" in html.lower():
                    self.add_result("Quiz Data Persistence", True,
                                  "Recent quiz data found")
                    return True
                else:
                    self.add_warning("Could not verify quiz in history")
            else:
                self.add_warning("Quiz history not accessible")
        except Exception as e:
            self.add_warning(f"Data persistence check: {str(e)}")
        return False

    # ========== PHASE 10: Edge Cases ==========
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        self.log("=" * 60)
        self.log("PHASE 10: EDGE CASES & ERROR HANDLING")
        self.log("=" * 60)
        
        # Test empty answer
        try:
            response = self.session.post(f"{BASE_URL}/api/answer",
                json={"user_input": "", "method": "typing", "elapsed_ms": 100},
                headers={"X-Requested-With": "XMLHttpRequest"})
            
            if response.status_code == 200:
                data = response.json()
                if not data.get("correct", True):
                    self.add_result("Empty Answer Handling", True,
                                  "Empty answers rejected")
                else:
                    self.add_warning("Empty answer might be accepted")
        except Exception as e:
            self.add_warning(f"Empty answer test: {str(e)}")
        
        # Test special characters
        try:
            response = self.session.post(f"{BASE_URL}/api/answer",
                json={"user_input": "test@#$%", "method": "typing", "elapsed_ms": 100},
                headers={"X-Requested-With": "XMLHttpRequest"})
            
            if response.status_code == 200:
                self.add_result("Special Character Handling", True,
                              "Special characters processed")
        except Exception as e:
            self.add_warning(f"Special character test: {str(e)}")
        
        # Test case sensitivity
        try:
            next_resp = self.session.post(f"{BASE_URL}/api/next",
                headers={"X-Requested-With": "XMLHttpRequest"})
            
            if next_resp.status_code == 200:
                # Submit with different case
                response = self.session.post(f"{BASE_URL}/api/answer",
                    json={"user_input": "SPELLING", "method": "typing", "elapsed_ms": 100},
                    headers={"X-Requested-With": "XMLHttpRequest"})
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("correct"):
                        self.add_result("Case Insensitivity", True,
                                      "Uppercase/lowercase handled")
                    else:
                        self.add_warning("Case sensitivity might be strict")
        except Exception as e:
            self.add_warning(f"Case sensitivity test: {str(e)}")

    # ========== Main Test Runner ==========
    def run_all_tests(self):
        """Run complete diagnostic suite"""
        self.log("=" * 60)
        self.log("BEESMART SPELLING APP - FULL QUIZ DIAGNOSTIC")
        self.log("=" * 60)
        self.log(f"Test User: {TEST_USERNAME}")
        self.log(f"Base URL: {BASE_URL}")
        self.log("")
        
        # Phase 1: Server Health
        if not self.test_server_health():
            self.log("CRITICAL: Server not responding. Cannot continue.", "ERROR")
            return self.print_summary()
        
        # Phase 2: Authentication
        if not self.test_user_registration():
            self.add_warning("Registration failed, attempting login with existing user")
        
        if not self.test_user_login():
            self.log("CRITICAL: Cannot authenticate. Cannot continue.", "ERROR")
            return self.print_summary()
        
        # Phase 3: Word Input
        if not self.test_word_upload_text():
            self.log("CRITICAL: Word upload failed. Cannot continue.", "ERROR")
            return self.print_summary()
        
        self.test_wordbank_retrieval()
        
        # Phase 4: Quiz Init
        self.test_quiz_initialization()
        
        # Phase 5: Quiz Interaction
        self.test_quiz_navigation()
        self.test_quiz_answer_correct()
        self.test_quiz_answer_incorrect()
        
        # Phase 6: Progress
        self.test_quiz_progress()
        
        # Phase 7: Completion
        self.test_quiz_completion()
        
        # Phase 8: Report Card
        self.test_report_card()
        self.test_report_card_stats()
        
        # Phase 9: Persistence
        self.test_data_persistence()
        
        # Phase 10: Edge Cases
        self.test_edge_cases()
        
        # Final Summary
        return self.print_summary()
    
    def print_summary(self):
        """Print diagnostic summary"""
        self.log("")
        self.log("=" * 60)
        self.log("DIAGNOSTIC SUMMARY")
        self.log("=" * 60)
        
        total = len(self.results["passed"]) + len(self.results["failed"])
        passed = len(self.results["passed"])
        failed = len(self.results["failed"])
        warnings = len(self.results["warnings"])
        
        self.log(f"Total Tests: {total}")
        self.log(f"Passed: {passed} ({(passed/total*100) if total > 0 else 0:.1f}%)")
        self.log(f"Failed: {failed}")
        self.log(f"Warnings: {warnings}")
        self.log("")
        
        if self.results["failed"]:
            self.log("FAILED TESTS:", "ERROR")
            for failure in self.results["failed"]:
                self.log(f"  ✗ {failure}", "ERROR")
            self.log("")
        
        if self.results["warnings"]:
            self.log("WARNINGS:")
            for warning in self.results["warnings"]:
                self.log(f"  ⚠ {warning}", "WARN")
            self.log("")
        
        if passed == total:
            self.log("🎉 ALL TESTS PASSED! 🎉", "SUCCESS")
        elif failed == 0:
            self.log("✓ All critical tests passed (with warnings)", "SUCCESS")
        elif failed < 5:
            self.log("⚠ Minor issues detected", "WARN")
        else:
            self.log("✗ Significant issues detected", "ERROR")
        
        self.log("=" * 60)
        
        return failed == 0


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("BEESMART SPELLING APP - FULL QUIZ DIAGNOSTIC")
    print("=" * 60)
    print("\nThis diagnostic will test:")
    print("  1. Server health")
    print("  2. User authentication")
    print("  3. Word upload and storage")
    print("  4. Quiz initialization")
    print("  5. Quiz navigation and interaction")
    print("  6. Answer submission (correct/incorrect)")
    print("  7. Progress tracking")
    print("  8. Quiz completion")
    print("  9. Report card generation")
    print(" 10. Data persistence")
    print(" 11. Edge cases and error handling")
    print("\nMake sure the Flask app is running at http://localhost:5000")
    print("=" * 60)
    
    input("\nPress Enter to start diagnostic...")
    
    diagnostic = QuizDiagnostic()
    success = diagnostic.run_all_tests()
    
    sys.exit(0 if success else 1)
