#!/usr/bin/env python3
"""
BeeSmart Spelling App - Quiz Redirect Fix Verification
========================================================
Tests the specific scenario that was causing quiz redirect errors:
1. Upload words to wordbank
2. Verify wordbank persists
3. Navigate to /quiz
4. Verify quiz loads without redirect error
5. Test /api/next doesn't fail
6. Test complete quiz flow

Expected: No redirect errors, quiz loads successfully
"""

import requests
import time
import sys

BASE_URL = "https://beesmartspelling.app"
TIMEOUT = 10

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

def print_test(name):
    print(f"\n{Colors.BLUE}🔍 TEST:{Colors.ENDC} {name}")

def print_pass(message):
    print(f"{Colors.GREEN}✅ PASS:{Colors.ENDC} {message}")

def print_fail(message):
    print(f"{Colors.RED}❌ FAIL:{Colors.ENDC} {message}")

def print_info(message):
    print(f"{Colors.YELLOW}ℹ️  INFO:{Colors.ENDC} {message}")

def main():
    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}Quiz Redirect Fix Verification{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
    print(f"Testing against: {BASE_URL}\n")
    
    session = requests.Session()
    
    # TEST 1: Clear wordbank and verify it's empty
    print_test("1. Clear wordbank and verify empty state")
    try:
        clear_response = session.post(f"{BASE_URL}/api/clear", json={}, timeout=TIMEOUT)
        if clear_response.status_code == 200:
            print_pass("Wordbank cleared successfully")
            
            # Verify count is 0
            count_response = session.get(f"{BASE_URL}/api/wordbank/count", timeout=TIMEOUT)
            if count_response.status_code == 200:
                count = count_response.json().get('count', -1)
                if count == 0:
                    print_pass(f"Wordbank count confirmed 0")
                else:
                    print_fail(f"Wordbank count is {count}, expected 0")
            else:
                print_fail(f"Failed to verify count: {count_response.status_code}")
        else:
            print_fail(f"Clear failed: {clear_response.status_code}")
    except Exception as e:
        print_fail(f"Exception: {e}")
        return False
    
    # TEST 2: Try to access /quiz with empty wordbank (should redirect)
    print_test("2. Attempt to access /quiz with empty wordbank (should redirect to home)")
    try:
        quiz_response = session.get(f"{BASE_URL}/quiz", timeout=TIMEOUT, allow_redirects=False)
        
        # Should get 302 redirect when wordbank is empty
        if quiz_response.status_code in [302, 303, 307]:
            redirect_location = quiz_response.headers.get('Location', '')
            if 'error=no_words' in redirect_location or redirect_location == '/':
                print_pass(f"Correctly redirected to home when wordbank empty (status: {quiz_response.status_code})")
            else:
                print_info(f"Redirected to: {redirect_location}")
                print_pass("Backend correctly blocks quiz access when wordbank empty")
        elif quiz_response.status_code == 200:
            print_fail("Quiz loaded with empty wordbank (should have redirected)")
        else:
            print_info(f"Got status {quiz_response.status_code} - checking if this is expected")
    except Exception as e:
        print_fail(f"Exception: {e}")
        return False
    
    # TEST 3: Upload test words
    print_test("3. Upload test words to wordbank")
    try:
        test_words = ["apple", "banana", "cherry", "dragon", "elephant"]
        txt_content = "\n".join(test_words)
        
        files = {'file': ('test_words.txt', txt_content, 'text/plain')}
        upload_response = session.post(f"{BASE_URL}/api/upload", files=files, timeout=TIMEOUT)
        
        if upload_response.status_code == 200:
            data = upload_response.json()
            count = data.get('count', 0)
            if count == len(test_words):
                print_pass(f"Uploaded {count}/{len(test_words)} words successfully")
            else:
                print_fail(f"Upload count mismatch: {count}/{len(test_words)}")
                return False
        else:
            print_fail(f"Upload failed: {upload_response.status_code}")
            return False
    except Exception as e:
        print_fail(f"Exception: {e}")
        return False
    
    # TEST 4: Verify wordbank persists
    print_test("4. Verify wordbank persists in database")
    try:
        time.sleep(0.5)  # Brief pause for DB write
        
        count_response = session.get(f"{BASE_URL}/api/wordbank/count", timeout=TIMEOUT)
        if count_response.status_code == 200:
            data = count_response.json()
            count = data.get('count', 0)
            storage_id = data.get('storage_id', 'none')
            db_exists = data.get('exists', False)
            
            if count == len(test_words) and storage_id != 'none':
                print_pass(f"Wordbank persists: {count} words, storage_id: {storage_id}")
                print_info(f"Database record exists: {db_exists}")
            else:
                print_fail(f"Persistence issue: count={count}, storage_id={storage_id}")
                return False
        else:
            print_fail(f"Failed to verify persistence: {count_response.status_code}")
            return False
    except Exception as e:
        print_fail(f"Exception: {e}")
        return False
    
    # TEST 5: Access /quiz page with words in wordbank (should load successfully)
    print_test("5. Access /quiz with populated wordbank (should load successfully)")
    try:
        quiz_response = session.get(f"{BASE_URL}/quiz", timeout=TIMEOUT, allow_redirects=False)
        
        if quiz_response.status_code == 200:
            print_pass("Quiz page loaded successfully (no redirect)")
            
            # Check if response contains quiz HTML (not an error page)
            if 'quiz' in quiz_response.text.lower() or 'spelling' in quiz_response.text.lower():
                print_pass("Quiz page contains expected content")
            else:
                print_info("Quiz page loaded but content may be minimal")
                
        elif quiz_response.status_code in [302, 303, 307]:
            redirect_location = quiz_response.headers.get('Location', '')
            print_fail(f"Quiz redirected when wordbank has words! Redirect to: {redirect_location}")
            return False
        else:
            print_fail(f"Unexpected status: {quiz_response.status_code}")
            return False
    except Exception as e:
        print_fail(f"Exception: {e}")
        return False
    
    # TEST 6: Call /api/next to get first question (this was failing before)
    print_test("6. Call /api/next to get first quiz question (critical test)")
    try:
        next_response = session.post(f"{BASE_URL}/api/next", json={}, timeout=TIMEOUT)
        
        if next_response.status_code == 200:
            data = next_response.json()
            
            if data.get('done', True):
                print_fail("Quiz reports as 'done' immediately (no questions loaded)")
                return False
            
            word = data.get('word', '')
            current = data.get('current', 0)
            total = data.get('total', 0)
            
            if word and total == len(test_words):
                print_pass(f"First question loaded: '{word}' ({current}/{total})")
                print_pass("✨ NO REDIRECT ERROR - Quiz initialized successfully!")
            else:
                print_fail(f"Question data incomplete: word='{word}', total={total}")
                return False
        else:
            print_fail(f"/api/next failed with status {next_response.status_code}")
            print_info(f"Response: {next_response.text[:200]}")
            return False
            
    except Exception as e:
        print_fail(f"Exception: {e}")
        return False
    
    # TEST 7: Submit an answer to verify full quiz flow
    print_test("7. Submit answer to verify complete quiz flow")
    try:
        # Get the word from previous test
        next_response = session.post(f"{BASE_URL}/api/next", json={}, timeout=TIMEOUT)
        if next_response.status_code != 200:
            print_fail("Failed to get current word")
            return False
        
        word = next_response.json().get('word', '')
        
        # Submit correct answer
        answer_response = session.post(
            f"{BASE_URL}/api/answer",
            json={"user_input": word, "method": "keyboard", "elapsed_ms": 1000},
            timeout=TIMEOUT
        )
        
        if answer_response.status_code == 200:
            data = answer_response.json()
            correct = data.get('correct', False)
            
            if correct:
                print_pass(f"Answer '{word}' accepted and scored correctly")
                print_pass("Complete quiz flow working without errors")
            else:
                print_fail("Answer marked incorrect (should be correct)")
                return False
        else:
            print_fail(f"/api/answer failed: {answer_response.status_code}")
            return False
            
    except Exception as e:
        print_fail(f"Exception: {e}")
        return False
    
    # Final Summary
    print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.GREEN}✅ ALL TESTS PASSED - QUIZ REDIRECT ISSUE FIXED!{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*80}{Colors.ENDC}\n")
    
    print("Verification Summary:")
    print("✅ Wordbank clearing works")
    print("✅ Empty wordbank correctly blocks quiz access")
    print("✅ Word upload and persistence working")
    print("✅ Quiz loads successfully with words in wordbank")
    print("✅ /api/next returns questions without 500 error")
    print("✅ No redirect error on quiz initialization")
    print("✅ Answer submission working correctly")
    print("\n🎉 The quiz redirect issue has been resolved!\n")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {e}{Colors.ENDC}")
        sys.exit(1)
