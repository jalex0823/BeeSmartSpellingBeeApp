#!/usr/bin/env python3
"""
Test script for DigitalOcean database wordbank and Wiktionary integration.
Tests the complete flow: upload words → store in DB → retrieve → verify definitions.
"""

import sys
import os
import requests
import json
from datetime import datetime

# Test configuration
BASE_URL = "https://beesmartspelling.app"  # Production DigitalOcean
# BASE_URL = "http://localhost:5000"  # Uncomment for local testing

# Test word lists
TEST_WORDS_SMALL = ["apple", "book", "cat", "dog", "elephant"]
TEST_WORDS_MEDIUM = [
    "beautiful", "celebration", "dictionary", "education", "friendship",
    "happiness", "imagination", "knowledge", "language", "mathematics"
]

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def print_result(test_name, passed, details=""):
    """Print test result with formatting."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"      {details}")

def test_health_check():
    """Test that the server is responding."""
    print_section("1. Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        data = response.json()
        
        if response.status_code == 200 and data.get("status") == "ok":
            print_result("Server health check", True, f"Version: {data.get('version', 'unknown')}")
            return True
        else:
            print_result("Server health check", False, f"Status: {response.status_code}, Data: {data}")
            return False
    except Exception as e:
        print_result("Server health check", False, f"Error: {e}")
        return False

def test_clear_wordbank(session):
    """Clear existing wordbank before testing."""
    print_section("2. Clear Existing Wordbank")
    try:
        response = session.post(f"{BASE_URL}/api/clear", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_result("Clear wordbank", True, f"Message: {data.get('message', 'Cleared')}")
            return True
        else:
            print_result("Clear wordbank", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_result("Clear wordbank", False, f"Error: {e}")
        return False

def test_get_empty_wordbank(session):
    """Verify wordbank is empty after clearing."""
    print_section("3. Verify Empty Wordbank")
    try:
        response = session.get(f"{BASE_URL}/api/wordbank", timeout=10)
        data = response.json()
        
        if response.status_code == 200 and data.get("count", 0) == 0:
            print_result("Empty wordbank verification", True, "Count is 0 as expected")
            return True
        else:
            print_result("Empty wordbank verification", False, 
                        f"Status: {response.status_code}, Count: {data.get('count', 'unknown')}")
            return False
    except Exception as e:
        print_result("Empty wordbank verification", False, f"Error: {e}")
        return False

def test_upload_words_manual(session, words):
    """Test manual word upload to DigitalOcean database."""
    print_section(f"4. Upload {len(words)} Words to DigitalOcean DB")
    try:
        payload = {"words": words}
        response = session.post(
            f"{BASE_URL}/api/upload-manual-words",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            uploaded_count = data.get("count", 0)
            
            if uploaded_count == len(words):
                print_result("Manual word upload", True, 
                           f"Uploaded {uploaded_count}/{len(words)} words to database")
                return True, data
            else:
                print_result("Manual word upload", False, 
                           f"Expected {len(words)}, got {uploaded_count}")
                return False, data
        else:
            print_result("Manual word upload", False, f"Status: {response.status_code}")
            return False, {}
    except Exception as e:
        print_result("Manual word upload", False, f"Error: {e}")
        return False, {}

def test_retrieve_wordbank(session, expected_count):
    """Retrieve wordbank from DigitalOcean database and verify."""
    print_section("5. Retrieve Wordbank from Database")
    try:
        response = session.get(f"{BASE_URL}/api/wordbank", timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            actual_count = data.get("count", 0)
            words = data.get("words", [])
            
            if actual_count == expected_count and len(words) == expected_count:
                print_result("Retrieve wordbank", True, 
                           f"Retrieved {actual_count} words from database")
                
                # Show first 3 words as sample
                print("\n      Sample words retrieved:")
                for i, word_obj in enumerate(words[:3]):
                    word = word_obj.get("word", "unknown")
                    has_sentence = bool(word_obj.get("sentence"))
                    has_hint = bool(word_obj.get("hint"))
                    print(f"        {i+1}. {word} (sentence: {has_sentence}, hint: {has_hint})")
                
                return True, words
            else:
                print_result("Retrieve wordbank", False, 
                           f"Expected {expected_count}, got {actual_count} (array len: {len(words)})")
                return False, []
        else:
            print_result("Retrieve wordbank", False, f"Status: {response.status_code}")
            return False, []
    except Exception as e:
        print_result("Retrieve wordbank", False, f"Error: {e}")
        return False, []

def test_wiktionary_definitions(words):
    """Test Wiktionary integration for word definitions."""
    print_section("6. Test Wiktionary Definition Lookup")
    
    successful = 0
    failed = 0
    
    for word in words[:3]:  # Test first 3 words
        word_text = word.get("word") if isinstance(word, dict) else word
        sentence = word.get("sentence", "") if isinstance(word, dict) else ""
        hint = word.get("hint", "") if isinstance(word, dict) else ""
        
        has_definition = bool(sentence or hint)
        
        if has_definition:
            print_result(f"Definition for '{word_text}'", True, 
                       f"Sentence length: {len(sentence)}, Hint length: {len(hint)}")
            successful += 1
        else:
            print_result(f"Definition for '{word_text}'", False, "No sentence or hint found")
            failed += 1
    
    print(f"\n      Wiktionary Summary: {successful} success, {failed} failed")
    return successful > 0

def test_quiz_initialization(session):
    """Test that quiz can initialize with uploaded words."""
    print_section("7. Test Quiz State Initialization")
    try:
        response = session.get(f"{BASE_URL}/api/quiz/state", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            has_state = data.get("state") is not None or data.get("initialized") is True
            
            print_result("Quiz state check", has_state, 
                       f"State present: {has_state}")
            return has_state
        else:
            print_result("Quiz state check", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_result("Quiz state check", False, f"Error: {e}")
        return False

def test_database_persistence(session, original_words):
    """Test that wordbank persists across requests (simulating page reload)."""
    print_section("8. Test Database Persistence (Simulate Page Reload)")
    
    # Create new session to simulate page reload
    new_session = requests.Session()
    
    # Copy cookies from original session
    new_session.cookies.update(session.cookies)
    
    try:
        response = new_session.get(f"{BASE_URL}/api/wordbank", timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            count = data.get("count", 0)
            
            if count == len(original_words):
                print_result("Database persistence", True, 
                           f"Words persisted: {count}/{len(original_words)}")
                return True
            else:
                print_result("Database persistence", False, 
                           f"Expected {len(original_words)}, got {count}")
                return False
        else:
            print_result("Database persistence", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_result("Database persistence", False, f"Error: {e}")
        return False

def run_full_test_suite():
    """Run complete test suite."""
    print("\n" + "="*70)
    print("  BEESMART WORDBANK TEST SUITE")
    print(f"  Testing: {BASE_URL}")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Create session to maintain cookies
    session = requests.Session()
    
    # Track results
    results = []
    
    # Run tests in sequence
    results.append(("Health Check", test_health_check()))
    
    if not results[-1][1]:
        print("\n❌ Server not responding. Aborting tests.")
        return False
    
    results.append(("Clear Wordbank", test_clear_wordbank(session)))
    results.append(("Verify Empty", test_get_empty_wordbank(session)))
    
    # Upload test words
    upload_success, upload_data = test_upload_words_manual(session, TEST_WORDS_SMALL)
    results.append(("Upload Words", upload_success))
    
    if upload_success:
        # Retrieve and verify
        retrieve_success, words = test_retrieve_wordbank(session, len(TEST_WORDS_SMALL))
        results.append(("Retrieve Words", retrieve_success))
        
        if retrieve_success:
            # Test Wiktionary integration
            results.append(("Wiktionary Lookup", test_wiktionary_definitions(words)))
            
            # Test quiz initialization
            results.append(("Quiz Initialization", test_quiz_initialization(session)))
            
            # Test persistence
            results.append(("Database Persistence", test_database_persistence(session, words)))
    
    # Print summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n{'='*70}")
    print(f"  OVERALL: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    print(f"{'='*70}\n")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_full_test_suite()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
