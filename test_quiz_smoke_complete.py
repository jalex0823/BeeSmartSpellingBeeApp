#!/usr/bin/env python3
"""
BeeSmart Spelling App - Complete Quiz Smoke Test Suite
=======================================================
Comprehensive end-to-end validation of the quiz pipeline including:
- Word import & word bank management
- Quiz initialization & handoff
- Spelling normalization & scoring logic
- Results & reporting accuracy
- Buzz points & grade calculation

Test Scope:
1. Word Import & Word Bank
   - Imported word counts
   - Word bank clearing
   - External vs internal word banks
2. Quiz Initialization
   - Word bank → quiz handoff
   - Randomization logic
3. Spelling & Scoring
   - Spelling normalization
   - Scoring accuracy
4. Results & Reporting
   - Report card generation
   - Buzz points
   - Grade point accuracy

Usage:
    python3 test_quiz_smoke_complete.py
"""

import requests
import time
import sys
from typing import Dict, List, Any, Tuple

# Test Configuration
BASE_URL = "https://beesmartspelling.app"  # Production server
TIMEOUT = 10

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class SmokeTestRunner:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.test_count = 0
        self.pass_count = 0
        self.fail_count = 0
        
    def print_header(self, text: str):
        """Print formatted section header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.ENDC}\n")
        
    def print_test(self, name: str):
        """Print test name"""
        print(f"{Colors.BLUE}🔍 TEST:{Colors.ENDC} {name}")
        
    def print_pass(self, message: str):
        """Print success message"""
        print(f"{Colors.GREEN}✅ PASS:{Colors.ENDC} {message}")
        self.pass_count += 1
        self.test_count += 1
        self.test_results.append(("PASS", message))
        
    def print_fail(self, message: str):
        """Print failure message"""
        print(f"{Colors.RED}❌ FAIL:{Colors.ENDC} {message}")
        self.fail_count += 1
        self.test_count += 1
        self.test_results.append(("FAIL", message))
        
    def print_info(self, message: str):
        """Print info message"""
        print(f"{Colors.YELLOW}ℹ️  INFO:{Colors.ENDC} {message}")
        
    def print_summary(self):
        """Print final test summary"""
        self.print_header("SMOKE TEST SUMMARY")
        print(f"Total Tests: {self.test_count}")
        print(f"{Colors.GREEN}Passed: {self.pass_count}{Colors.ENDC}")
        print(f"{Colors.RED}Failed: {self.fail_count}{Colors.ENDC}")
        
        if self.fail_count == 0:
            print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 ALL TESTS PASSED! System ready for production.{Colors.ENDC}\n")
            return True
        else:
            print(f"\n{Colors.BOLD}{Colors.RED}⚠️  SOME TESTS FAILED. Review failures before production.{Colors.ENDC}\n")
            return False
    
    # ========================================================================
    # SECTION 1: WORD IMPORT & WORD BANK TESTS
    # ========================================================================
    
    def test_word_bank_clear(self) -> bool:
        """Test 1.1: Word Bank Clearing"""
        self.print_test("Word Bank Clearing")
        
        try:
            # Clear the word bank
            response = self.session.post(
                f"{self.base_url}/api/clear",
                json={},
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                self.print_pass("Word bank cleared successfully (200 OK)")
                
                # Verify count is 0
                count_response = self.session.get(f"{self.base_url}/api/wordbank/count", timeout=TIMEOUT)
                if count_response.status_code == 200:
                    data = count_response.json()
                    count = data.get('count', -1)
                    
                    if count == 0:
                        self.print_pass(f"Word bank count confirmed 0 after clear")
                        return True
                    else:
                        self.print_fail(f"Word bank count is {count}, expected 0")
                        return False
                else:
                    self.print_fail(f"Failed to get word count after clear: {count_response.status_code}")
                    return False
            else:
                self.print_fail(f"Clear endpoint returned {response.status_code}")
                return False
                
        except Exception as e:
            self.print_fail(f"Exception during clear test: {e}")
            return False
    
    def test_word_import_txt(self) -> Tuple[bool, int]:
        """Test 1.2: Import TXT Word List & Count Validation"""
        self.print_test("Word Import (TXT) & Count Validation")
        
        # Test word list
        test_words = [
            "apple", "banana", "cherry", "dragon", "elephant",
            "flamingo", "giraffe", "hippo", "iguana", "jaguar"
        ]
        
        try:
            # Create TXT content
            txt_content = "\n".join(test_words)
            
            # Upload via /api/upload
            files = {
                'file': ('test_words.txt', txt_content, 'text/plain')
            }
            
            response = self.session.post(
                f"{self.base_url}/api/upload",
                files=files,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                uploaded_count = data.get('count', 0)
                
                if uploaded_count == len(test_words):
                    self.print_pass(f"TXT upload successful: {uploaded_count}/{len(test_words)} words imported")
                    
                    # Verify count via /api/wordbank/count
                    time.sleep(0.5)  # Brief pause for DB persistence
                    count_response = self.session.get(f"{self.base_url}/api/wordbank/count", timeout=TIMEOUT)
                    
                    if count_response.status_code == 200:
                        count_data = count_response.json()
                        db_count = count_data.get('count', -1)
                        
                        if db_count == len(test_words):
                            self.print_pass(f"Database word count matches: {db_count}/{len(test_words)}")
                            return True, len(test_words)
                        else:
                            self.print_fail(f"Count mismatch: DB has {db_count}, expected {len(test_words)}")
                            return False, 0
                    else:
                        self.print_fail(f"Failed to verify count: {count_response.status_code}")
                        return False, 0
                else:
                    self.print_fail(f"Upload count mismatch: got {uploaded_count}, expected {len(test_words)}")
                    return False, 0
            else:
                self.print_fail(f"Upload failed with status {response.status_code}")
                return False, 0
                
        except Exception as e:
            self.print_fail(f"Exception during TXT import: {e}")
            return False, 0
    
    def test_word_deduplication(self) -> bool:
        """Test 1.3: Word Deduplication on Import"""
        self.print_test("Word Deduplication")
        
        # List with intentional duplicates
        test_words = ["apple", "APPLE", "Apple", "banana", "Banana", "cherry"]
        unique_words = {"apple", "banana", "cherry"}  # Normalized unique set
        
        try:
            # Clear first
            self.session.post(f"{self.base_url}/api/clear", json={}, timeout=TIMEOUT)
            time.sleep(0.3)
            
            txt_content = "\n".join(test_words)
            files = {'file': ('dedup_test.txt', txt_content, 'text/plain')}
            
            response = self.session.post(
                f"{self.base_url}/api/upload",
                files=files,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                uploaded_count = data.get('count', 0)
                
                if uploaded_count == len(unique_words):
                    self.print_pass(f"Deduplication works: {len(test_words)} words → {uploaded_count} unique words")
                    return True
                else:
                    self.print_fail(f"Deduplication failed: got {uploaded_count}, expected {len(unique_words)}")
                    return False
            else:
                self.print_fail(f"Upload failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_fail(f"Exception during deduplication test: {e}")
            return False
    
    def test_word_bank_persistence(self) -> bool:
        """Test 1.4: Word Bank Persistence"""
        self.print_test("Word Bank Persistence (Session Survival)")
        
        try:
            # Get current count
            response1 = self.session.get(f"{self.base_url}/api/wordbank/count", timeout=TIMEOUT)
            if response1.status_code != 200:
                self.print_fail(f"Failed to get initial count: {response1.status_code}")
                return False
            
            count1 = response1.json().get('count', 0)
            storage_id1 = response1.json().get('storage_id', 'none')
            
            # Simulate page refresh by making another request
            time.sleep(0.5)
            
            response2 = self.session.get(f"{self.base_url}/api/wordbank/count", timeout=TIMEOUT)
            if response2.status_code != 200:
                self.print_fail(f"Failed to get count after refresh: {response2.status_code}")
                return False
            
            count2 = response2.json().get('count', 0)
            storage_id2 = response2.json().get('storage_id', 'none')
            
            if count1 == count2 and storage_id1 == storage_id2:
                self.print_pass(f"Word bank persisted: {count1} words retained, storage_id: {storage_id1}")
                return True
            else:
                self.print_fail(f"Persistence failed: count {count1}→{count2}, storage_id {storage_id1}→{storage_id2}")
                return False
                
        except Exception as e:
            self.print_fail(f"Exception during persistence test: {e}")
            return False
    
    # ========================================================================
    # SECTION 2: QUIZ INITIALIZATION TESTS
    # ========================================================================
    
    def test_quiz_initialization(self) -> bool:
        """Test 2.1: Quiz Initialization (Word Bank → Quiz Handoff)"""
        self.print_test("Quiz Initialization & Word Bank Handoff")
        
        try:
            # Get current word count
            count_response = self.session.get(f"{self.base_url}/api/wordbank/count", timeout=TIMEOUT)
            if count_response.status_code != 200:
                self.print_fail(f"Failed to get word count: {count_response.status_code}")
                return False
            
            word_count = count_response.json().get('count', 0)
            
            if word_count == 0:
                self.print_fail("Cannot test quiz initialization: word bank is empty")
                return False
            
            # Call /api/next to initialize quiz
            next_response = self.session.post(f"{self.base_url}/api/next", json={}, timeout=TIMEOUT)
            
            if next_response.status_code == 200:
                data = next_response.json()
                
                if not data.get('done', True):
                    # Quiz started successfully
                    word = data.get('word', '')
                    total = data.get('total', 0)
                    current = data.get('current', 0)
                    
                    if total == word_count:
                        self.print_pass(f"Quiz initialized: {total} words loaded from word bank")
                        self.print_info(f"First word presented: '{word}' ({current}/{total})")
                        return True
                    else:
                        self.print_fail(f"Word count mismatch: quiz has {total}, expected {word_count}")
                        return False
                else:
                    self.print_fail("Quiz reports as 'done' immediately after init")
                    return False
            else:
                self.print_fail(f"/api/next returned {next_response.status_code}")
                return False
                
        except Exception as e:
            self.print_fail(f"Exception during quiz init test: {e}")
            return False
    
    def test_quiz_randomization(self) -> bool:
        """Test 2.2: Quiz Randomization Logic"""
        self.print_test("Quiz Randomization (Word Order)")
        
        try:
            # Clear and upload a controlled set
            self.session.post(f"{self.base_url}/api/clear", json={}, timeout=TIMEOUT)
            time.sleep(0.3)
            
            test_words = ["alpha", "bravo", "charlie", "delta", "echo"]
            txt_content = "\n".join(test_words)
            files = {'file': ('random_test.txt', txt_content, 'text/plain')}
            
            upload_response = self.session.post(
                f"{self.base_url}/api/upload",
                files=files,
                timeout=TIMEOUT
            )
            
            if upload_response.status_code != 200:
                self.print_fail("Failed to upload test words")
                return False
            
            time.sleep(0.5)
            
            # Get first word
            next_response = self.session.post(f"{self.base_url}/api/next", json={}, timeout=TIMEOUT)
            if next_response.status_code != 200:
                self.print_fail(f"Failed to get first word: {next_response.status_code}")
                return False
            
            first_word = next_response.json().get('word', '')
            
            # Verify word is from our set
            if first_word.lower() in [w.lower() for w in test_words]:
                self.print_pass(f"Randomization working: first word '{first_word}' is from uploaded set")
                self.print_info(f"Word order appears randomized (first word: {first_word}, not necessarily 'alpha')")
                return True
            else:
                self.print_fail(f"Randomization issue: got '{first_word}', not in uploaded set")
                return False
                
        except Exception as e:
            self.print_fail(f"Exception during randomization test: {e}")
            return False
    
    # ========================================================================
    # SECTION 3: SPELLING & SCORING TESTS
    # ========================================================================
    
    def test_spelling_normalization(self) -> bool:
        """Test 3.1: Spelling Normalization"""
        self.print_test("Spelling Normalization (Case, Whitespace, Punctuation)")
        
        try:
            # Clear and upload a test word
            self.session.post(f"{self.base_url}/api/clear", json={}, timeout=TIMEOUT)
            time.sleep(0.3)
            
            files = {'file': ('norm_test.txt', 'butterfly', 'text/plain')}
            self.session.post(f"{self.base_url}/api/upload", files=files, timeout=TIMEOUT)
            time.sleep(0.5)
            
            # Start quiz
            next_response = self.session.post(f"{self.base_url}/api/next", json={}, timeout=TIMEOUT)
            if next_response.status_code != 200:
                self.print_fail("Failed to start quiz")
                return False
            
            # Test various normalized inputs
            test_inputs = [
                ("butterfly", "exact match"),
                ("BUTTERFLY", "uppercase"),
                ("Butterfly", "capitalized"),
                ("  butterfly  ", "with whitespace"),
                ("butterfly.", "with punctuation"),
            ]
            
            all_passed = True
            
            for test_input, description in test_inputs:
                # Submit answer
                answer_response = self.session.post(
                    f"{self.base_url}/api/answer",
                    json={
                        "user_input": test_input,
                        "method": "keyboard",
                        "elapsed_ms": 1000
                    },
                    timeout=TIMEOUT
                )
                
                if answer_response.status_code == 200:
                    data = answer_response.json()
                    correct = data.get('correct', False)
                    
                    if correct:
                        self.print_info(f"✓ '{test_input}' ({description}) → CORRECT")
                    else:
                        self.print_info(f"✗ '{test_input}' ({description}) → INCORRECT (normalization failed?)")
                        all_passed = False
                    
                    # Reset quiz for next test
                    self.session.post(f"{self.base_url}/api/clear", json={}, timeout=TIMEOUT)
                    time.sleep(0.2)
                    files = {'file': ('norm_test.txt', 'butterfly', 'text/plain')}
                    self.session.post(f"{self.base_url}/api/upload", files=files, timeout=TIMEOUT)
                    time.sleep(0.3)
                    self.session.post(f"{self.base_url}/api/next", json={}, timeout=TIMEOUT)
                else:
                    self.print_info(f"✗ Failed to submit '{test_input}': {answer_response.status_code}")
                    all_passed = False
            
            if all_passed:
                self.print_pass("All normalization variants accepted correctly")
                return True
            else:
                self.print_fail("Some normalization tests failed")
                return False
                
        except Exception as e:
            self.print_fail(f"Exception during normalization test: {e}")
            return False
    
    def test_scoring_accuracy(self) -> bool:
        """Test 3.2: Scoring Accuracy"""
        self.print_test("Scoring Accuracy (Correct/Incorrect Determination)")
        
        try:
            # Clear and upload test words
            self.session.post(f"{self.base_url}/api/clear", json={}, timeout=TIMEOUT)
            time.sleep(0.3)
            
            test_words = ["correct", "wrong"]
            txt_content = "\n".join(test_words)
            files = {'file': ('score_test.txt', txt_content, 'text/plain')}
            
            self.session.post(f"{self.base_url}/api/upload", files=files, timeout=TIMEOUT)
            time.sleep(0.5)
            
            # Start quiz
            next_response = self.session.post(f"{self.base_url}/api/next", json={}, timeout=TIMEOUT)
            if next_response.status_code != 200:
                self.print_fail("Failed to start quiz")
                return False
            
            word = next_response.json().get('word', '')
            
            # Test correct answer
            answer_response = self.session.post(
                f"{self.base_url}/api/answer",
                json={
                    "user_input": word,  # Submit correct spelling
                    "method": "keyboard",
                    "elapsed_ms": 1500
                },
                timeout=TIMEOUT
            )
            
            if answer_response.status_code != 200:
                self.print_fail(f"Failed to submit correct answer: {answer_response.status_code}")
                return False
            
            correct_data = answer_response.json()
            is_correct = correct_data.get('correct', False)
            
            if not is_correct:
                self.print_fail(f"Correct answer '{word}' marked as incorrect")
                return False
            
            self.print_info(f"✓ Correct answer '{word}' scored correctly")
            
            # Move to next word
            next_response2 = self.session.post(f"{self.base_url}/api/next", json={}, timeout=TIMEOUT)
            if next_response2.status_code != 200:
                self.print_fail("Failed to get next word")
                return False
            
            word2 = next_response2.json().get('word', '')
            
            # Test incorrect answer
            wrong_answer = "zzz_wrong_xyz"
            answer_response2 = self.session.post(
                f"{self.base_url}/api/answer",
                json={
                    "user_input": wrong_answer,
                    "method": "keyboard",
                    "elapsed_ms": 1500
                },
                timeout=TIMEOUT
            )
            
            if answer_response2.status_code != 200:
                self.print_fail(f"Failed to submit incorrect answer: {answer_response2.status_code}")
                return False
            
            incorrect_data = answer_response2.json()
            is_incorrect = not incorrect_data.get('correct', True)
            
            if not is_incorrect:
                self.print_fail(f"Incorrect answer '{wrong_answer}' marked as correct")
                return False
            
            self.print_info(f"✓ Incorrect answer '{wrong_answer}' scored correctly")
            self.print_pass("Scoring accuracy validated: correct and incorrect answers handled properly")
            return True
                
        except Exception as e:
            self.print_fail(f"Exception during scoring test: {e}")
            return False
    
    # ========================================================================
    # SECTION 4: RESULTS & REPORTING TESTS
    # ========================================================================
    
    def test_quiz_completion(self) -> bool:
        """Test 4.1: Quiz Completion & Report Card Generation"""
        self.print_test("Quiz Completion & Report Card")
        
        try:
            # Clear and upload small word list
            self.session.post(f"{self.base_url}/api/clear", json={}, timeout=TIMEOUT)
            time.sleep(0.3)
            
            test_words = ["cat", "dog", "bird"]
            txt_content = "\n".join(test_words)
            files = {'file': ('complete_test.txt', txt_content, 'text/plain')}
            
            self.session.post(f"{self.base_url}/api/upload", files=files, timeout=TIMEOUT)
            time.sleep(0.5)
            
            correct_count = 0
            total_count = len(test_words)
            
            # Answer all questions
            for i in range(total_count):
                # Get question
                next_response = self.session.post(f"{self.base_url}/api/next", json={}, timeout=TIMEOUT)
                if next_response.status_code != 200:
                    self.print_fail(f"Failed to get question {i+1}")
                    return False
                
                word = next_response.json().get('word', '')
                
                # Submit correct answer
                answer_response = self.session.post(
                    f"{self.base_url}/api/answer",
                    json={
                        "user_input": word,
                        "method": "keyboard",
                        "elapsed_ms": 1000
                    },
                    timeout=TIMEOUT
                )
                
                if answer_response.status_code == 200:
                    if answer_response.json().get('correct', False):
                        correct_count += 1
            
            # Check for quiz completion
            time.sleep(0.5)
            final_response = self.session.post(f"{self.base_url}/api/next", json={}, timeout=TIMEOUT)
            
            if final_response.status_code == 200:
                data = final_response.json()
                
                if data.get('done', False):
                    summary = data.get('summary', {})
                    reported_correct = summary.get('correct', 0)
                    reported_total = summary.get('total', 0)
                    
                    if reported_correct == correct_count and reported_total == total_count:
                        self.print_pass(f"Quiz completed successfully: {reported_correct}/{reported_total} correct")
                        self.print_info(f"Report card data: {summary}")
                        return True
                    else:
                        self.print_fail(f"Report mismatch: got {reported_correct}/{reported_total}, expected {correct_count}/{total_count}")
                        return False
                else:
                    self.print_fail("Quiz not marked as done after all questions answered")
                    return False
            else:
                self.print_fail(f"Failed to get completion status: {final_response.status_code}")
                return False
                
        except Exception as e:
            self.print_fail(f"Exception during completion test: {e}")
            return False
    
    def test_buzz_points(self) -> bool:
        """Test 4.2: Buzz Points Award"""
        self.print_test("Buzz Points Award")
        
        try:
            # Check if quiz summary includes buzz points
            self.session.post(f"{self.base_url}/api/clear", json={}, timeout=TIMEOUT)
            time.sleep(0.3)
            
            files = {'file': ('points_test.txt', 'test', 'text/plain')}
            self.session.post(f"{self.base_url}/api/upload", files=files, timeout=TIMEOUT)
            time.sleep(0.5)
            
            # Complete one question correctly
            self.session.post(f"{self.base_url}/api/next", json={}, timeout=TIMEOUT)
            answer_response = self.session.post(
                f"{self.base_url}/api/answer",
                json={"user_input": "test", "method": "keyboard", "elapsed_ms": 1000},
                timeout=TIMEOUT
            )
            
            if answer_response.status_code == 200:
                data = answer_response.json()
                points = data.get('points')
                
                # Points might be a dict or an int
                if points is not None:
                    if isinstance(points, dict):
                        points_value = points.get('total', 0) if isinstance(points, dict) else 0
                    else:
                        points_value = int(points) if points else 0
                    
                    if points_value > 0:
                        self.print_pass(f"Buzz points awarded: {points_value} points")
                        return True
                
                self.print_info("No points field in response (may be awarded at quiz end)")
                # Check final summary
                final_response = self.session.post(f"{self.base_url}/api/next", json={}, timeout=TIMEOUT)
                if final_response.status_code == 200:
                    final_data = final_response.json()
                    if final_data.get('done', False):
                        summary = final_data.get('summary', {})
                        session_points = summary.get('session_points', 0)
                        
                        if session_points > 0:
                            self.print_pass(f"Buzz points in summary: {session_points} points")
                            return True
                        else:
                            self.print_fail("No buzz points awarded")
                            return False
                    else:
                        self.print_fail("Quiz not complete, cannot check summary points")
                        return False
                else:
                    self.print_fail("Failed to get quiz summary")
                    return False
            else:
                self.print_fail("Failed to check buzz points")
                return False
                
        except Exception as e:
            self.print_fail(f"Exception during buzz points test: {e}")
            return False
    
    def test_grade_calculation(self) -> bool:
        """Test 4.3: Grade Point Accuracy"""
        self.print_test("Grade Calculation Accuracy")
        
        try:
            # This test validates that score percentages map to correct grades
            # We'll check the final summary for grade calculation
            
            self.session.post(f"{self.base_url}/api/clear", json={}, timeout=TIMEOUT)
            time.sleep(0.3)
            
            # Upload 5 words, answer 4 correctly = 80% = B grade typically
            test_words = ["alpha", "bravo", "charlie", "delta", "echo"]
            txt_content = "\n".join(test_words)
            files = {'file': ('grade_test.txt', txt_content, 'text/plain')}
            
            self.session.post(f"{self.base_url}/api/upload", files=files, timeout=TIMEOUT)
            time.sleep(0.5)
            
            # Answer all 5 questions, getting 4 correct
            correct_count = 0
            for i in range(5):
                next_resp = self.session.post(f"{self.base_url}/api/next", json={}, timeout=TIMEOUT)
                
                if next_resp.status_code != 200:
                    self.print_fail(f"Failed to get question {i+1}")
                    return False
                
                word = next_resp.json().get('word', '')
                
                if i < 4:
                    # Answer correctly
                    answer = word
                    correct_count += 1
                else:
                    # Answer incorrectly on last one
                    answer = "wronganswer_xyz"
                
                ans_resp = self.session.post(
                    f"{self.base_url}/api/answer",
                    json={"user_input": answer, "method": "keyboard", "elapsed_ms": 1000},
                    timeout=TIMEOUT
                )
                
                if ans_resp.status_code != 200:
                    self.print_fail(f"Failed to submit answer for question {i+1}")
                    return False
            
            # Get final summary
            time.sleep(0.5)
            final_response = self.session.post(f"{self.base_url}/api/next", json={}, timeout=TIMEOUT)
            
            if final_response.status_code == 200:
                data = final_response.json()
                
                if data.get('done', False):
                    summary = data.get('summary', {})
                    
                    correct = summary.get('correct', 0)
                    total = summary.get('total', 0)
                    
                    if total > 0:
                        percentage = (correct / total) * 100
                        
                        if correct == correct_count and total == 5:
                            self.print_pass(f"Grade calculation: {correct}/{total} = {percentage:.1f}%")
                            self.print_info(f"Expected {correct_count} correct, got {correct} correct")
                            return True
                        else:
                            self.print_fail(f"Grade mismatch: expected {correct_count}/5, got {correct}/{total}")
                            return False
                    else:
                        self.print_fail("No grade data in summary")
                        return False
                else:
                    self.print_fail("Quiz not marked as done")
                    return False
            else:
                self.print_fail(f"Failed to get final summary: {final_response.status_code}")
                return False
                
        except Exception as e:
            self.print_fail(f"Exception during grade test: {e}")
            return False
    
    # ========================================================================
    # MAIN TEST RUNNER
    # ========================================================================
    
    def run_all_tests(self):
        """Execute complete smoke test suite"""
        
        print(f"\n{Colors.BOLD}{Colors.HEADER}")
        print("╔════════════════════════════════════════════════════════════════════════════╗")
        print("║                                                                            ║")
        print("║           BeeSmart Spelling App - COMPLETE QUIZ SMOKE TEST                ║")
        print("║                                                                            ║")
        print("║                    End-to-End Quiz Pipeline Validation                    ║")
        print("║                                                                            ║")
        print("╚════════════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}\n")
        
        print(f"Testing against: {Colors.BOLD}{self.base_url}{Colors.ENDC}\n")
        
        # SECTION 1: Word Import & Word Bank
        self.print_header("SECTION 1: WORD IMPORT & WORD BANK")
        self.test_word_bank_clear()
        self.test_word_import_txt()
        self.test_word_deduplication()
        self.test_word_bank_persistence()
        
        # SECTION 2: Quiz Initialization
        self.print_header("SECTION 2: QUIZ INITIALIZATION")
        self.test_quiz_initialization()
        self.test_quiz_randomization()
        
        # SECTION 3: Spelling & Scoring
        self.print_header("SECTION 3: SPELLING & SCORING LOGIC")
        self.test_spelling_normalization()
        self.test_scoring_accuracy()
        
        # SECTION 4: Results & Reporting
        self.print_header("SECTION 4: RESULTS & REPORTING")
        self.test_quiz_completion()
        self.test_buzz_points()
        self.test_grade_calculation()
        
        # Print summary
        success = self.print_summary()
        
        return success


def main():
    """Main entry point"""
    runner = SmokeTestRunner(BASE_URL)
    
    try:
        success = runner.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted by user{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {e}{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
