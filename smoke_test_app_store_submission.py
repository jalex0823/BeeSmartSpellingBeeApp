#!/usr/bin/env python3
"""
Comprehensive Smoke Test for BeeSmart App Store Submission
Tests all critical functionality before iOS/Android submission
"""

import sys
import requests
import json
import time
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:5051"  # App running on 5051
TEST_RESULTS = []

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def log_test(category, test_name, passed, details=""):
    """Log test result"""
    status = f"{Colors.GREEN}✅ PASS{Colors.RESET}" if passed else f"{Colors.RED}❌ FAIL{Colors.RESET}"
    print(f"{status} [{category}] {test_name}")
    if details:
        print(f"   {details}")
    TEST_RESULTS.append({
        'category': category,
        'test': test_name,
        'passed': passed,
        'details': details,
        'timestamp': datetime.now().isoformat()
    })

def test_health_endpoints():
    """Test 1: Health and Version Endpoints"""
    print(f"\n{Colors.BLUE}=== Testing Health Endpoints ==={Colors.RESET}")
    
    try:
        # Test main health endpoint
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        data = r.json()
        passed = r.status_code == 200 and data.get('status') == 'ok' and data.get('version') == '1.7'
        log_test("Health", "Main health endpoint", passed, f"Version: {data.get('version')}")
    except Exception as e:
        log_test("Health", "Main health endpoint", False, str(e))
    
    try:
        # Test IAP health endpoint
        r = requests.get(f"{BASE_URL}/health/iap", timeout=5)
        data = r.json()
        passed = r.status_code == 200 and 'iap' in data
        log_test("Health", "IAP health endpoint", passed, f"Mock mode: {data.get('iap', {}).get('mock')}")
    except Exception as e:
        log_test("Health", "IAP health endpoint", False, str(e))

def test_core_pages():
    """Test 2: Core Page Loading"""
    print(f"\n{Colors.BLUE}=== Testing Core Pages ==={Colors.RESET}")
    
    pages = [
        ('/', 'Home page'),
        ('/quiz', 'Quiz page'),
        ('/privacy', 'Privacy policy'),
        ('/points-buzz-dust-explanation', 'Points explanation'),
    ]
    
    for path, name in pages:
        try:
            r = requests.get(f"{BASE_URL}{path}", timeout=5)
            passed = r.status_code == 200 and len(r.text) > 100
            log_test("Pages", name, passed, f"Status: {r.status_code}, Size: {len(r.text)} bytes")
        except Exception as e:
            log_test("Pages", name, False, str(e))

def test_wordbank_api():
    """Test 3: Wordbank API Endpoints"""
    print(f"\n{Colors.BLUE}=== Testing Wordbank API ==={Colors.RESET}")
    
    session = requests.Session()
    
    try:
        # Test wordbank count
        r = session.get(f"{BASE_URL}/api/wordbank/count", timeout=5)
        data = r.json()
        passed = r.status_code == 200 and 'count' in data
        log_test("Wordbank", "Get word count", passed, f"Count: {data.get('count', 0)}")
    except Exception as e:
        log_test("Wordbank", "Get word count", False, str(e))
    
    try:
        # Test wordbank POST with sample words
        test_words = [
            {"word": "test", "sentence": "This is a test", "hint": ""},
            {"word": "apple", "sentence": "Red fruit", "hint": ""},
        ]
        r = session.post(
            f"{BASE_URL}/api/wordbank",
            json={"words": test_words},
            timeout=5
        )
        data = r.json()
        passed = r.status_code == 200 and data.get('status') == 'ok'
        log_test("Wordbank", "Add words via API", passed, f"Added: {data.get('added', 0)} words")
    except Exception as e:
        log_test("Wordbank", "Add words via API", False, str(e))
    
    try:
        # Test wordbank clear
        r = session.post(f"{BASE_URL}/api/wordbank/clear", timeout=5)
        data = r.json()
        passed = r.status_code == 200 and data.get('status') == 'ok'
        log_test("Wordbank", "Clear wordbank", passed)
    except Exception as e:
        log_test("Wordbank", "Clear wordbank", False, str(e))

def test_avatar_api():
    """Test 4: Avatar API"""
    print(f"\n{Colors.BLUE}=== Testing Avatar API ==={Colors.RESET}")
    
    try:
        r = requests.get(f"{BASE_URL}/api/avatars", timeout=5)
        data = r.json()
        passed = r.status_code == 200 and len(data) > 0
        
        # Check for required avatar fields
        if passed and len(data) > 0:
            first_avatar = data[0]
            has_required_fields = all(k in first_avatar for k in ['id', 'name', 'slug'])
            passed = passed and has_required_fields
        
        log_test("Avatar", "Get avatar list", passed, f"Avatars: {len(data)}")
        
        # Check that avatar names end with "Avatar" (Apple requirement)
        if passed:
            non_compliant = [a['name'] for a in data if not a['name'].endswith(' Avatar')]
            if non_compliant:
                log_test("Avatar", "Apple naming compliance", False, f"Non-compliant: {non_compliant[:3]}")
            else:
                log_test("Avatar", "Apple naming compliance", True, "All avatars end with ' Avatar'")
    except Exception as e:
        log_test("Avatar", "Get avatar list", False, str(e))

def test_quiz_flow():
    """Test 5: Quiz Flow"""
    print(f"\n{Colors.BLUE}=== Testing Quiz Flow ==={Colors.RESET}")
    
    session = requests.Session()
    
    try:
        # Setup wordbank
        test_words = [
            {"word": "cat", "sentence": "A small pet", "hint": "Meow"},
            {"word": "dog", "sentence": "Man's best friend", "hint": "Woof"},
        ]
        r = session.post(
            f"{BASE_URL}/api/wordbank",
            json={"words": test_words},
            timeout=5
        )
        passed = r.status_code == 200
        log_test("Quiz", "Setup test wordbank", passed)
        
        if passed:
            # Get next word
            r = session.post(f"{BASE_URL}/api/next", timeout=5)
            data = r.json()
            passed = r.status_code == 200 and 'word' in data
            log_test("Quiz", "Get next word", passed, f"Word: {data.get('word', 'N/A')}")
            
            if passed:
                # Submit correct answer
                r = session.post(
                    f"{BASE_URL}/api/answer",
                    json={
                        "user_input": data['word'].lower(),
                        "method": "keyboard",
                        "elapsed_ms": 1000
                    },
                    timeout=5
                )
                answer_data = r.json()
                passed = r.status_code == 200 and answer_data.get('correct') == True
                log_test("Quiz", "Submit correct answer", passed, f"Result: {answer_data.get('message', 'N/A')}")
                
                # Test normalize function with invisible characters
                test_with_invisible = data['word'].lower() + '\u200b'  # Add zero-width space
                r = session.post(
                    f"{BASE_URL}/api/answer",
                    json={
                        "user_input": test_with_invisible,
                        "method": "keyboard",
                        "elapsed_ms": 1000
                    },
                    timeout=5
                )
                answer_data = r.json()
                passed = r.status_code == 200 and answer_data.get('correct') == True
                log_test("Quiz", "Normalize invisible chars (iOS/macOS)", passed, 
                        f"Input with \\u200b correctly normalized")
    except Exception as e:
        log_test("Quiz", "Quiz flow test", False, str(e))

def test_authentication():
    """Test 6: Authentication Endpoints"""
    print(f"\n{Colors.BLUE}=== Testing Authentication ==={Colors.RESET}")
    
    try:
        # Test registration page loads
        r = requests.get(f"{BASE_URL}/register", timeout=5)
        passed = r.status_code == 200
        log_test("Auth", "Registration page loads", passed)
    except Exception as e:
        log_test("Auth", "Registration page loads", False, str(e))
    
    try:
        # Test login page loads
        r = requests.get(f"{BASE_URL}/login", timeout=5)
        passed = r.status_code == 200
        log_test("Auth", "Login page loads", passed)
    except Exception as e:
        log_test("Auth", "Login page loads", False, str(e))
    
    try:
        # Test forgot password page loads
        r = requests.get(f"{BASE_URL}/forgot-password", timeout=5)
        passed = r.status_code == 200
        log_test("Auth", "Forgot password page loads", passed)
    except Exception as e:
        log_test("Auth", "Forgot password page loads", False, str(e))

def test_iap_endpoints():
    """Test 7: In-App Purchase Endpoints"""
    print(f"\n{Colors.BLUE}=== Testing IAP Endpoints ==={Colors.RESET}")
    
    session = requests.Session()
    
    try:
        # Test Apple IAP verification endpoint exists
        r = session.post(
            f"{BASE_URL}/api/iap/verify/apple",
            json={"receipt": "test_receipt", "product_id": "test.product"},
            timeout=5
        )
        # In mock mode, this should succeed; otherwise might return validation error
        passed = r.status_code in [200, 400]  # 400 is ok for invalid test receipt
        log_test("IAP", "Apple verification endpoint", passed, f"Status: {r.status_code}")
    except Exception as e:
        log_test("IAP", "Apple verification endpoint", False, str(e))
    
    try:
        # Test restore endpoint
        r = session.post(f"{BASE_URL}/api/iap/restore", json={}, timeout=5)
        passed = r.status_code in [200, 401]  # 401 is ok if not logged in
        log_test("IAP", "Restore purchases endpoint", passed, f"Status: {r.status_code}")
    except Exception as e:
        log_test("IAP", "Restore purchases endpoint", False, str(e))

def test_static_assets():
    """Test 8: Critical Static Assets"""
    print(f"\n{Colors.BLUE}=== Testing Static Assets ==={Colors.RESET}")
    
    assets = [
        ('/static/css/BeeSmart.css', 'Main CSS'),
        ('/static/js/avatar3d.js', 'Avatar 3D loader'),
        ('/service-worker.js', 'Service worker (PWA)'),
        ('/manifest.json', 'Web manifest (PWA)'),
    ]
    
    for path, name in assets:
        try:
            r = requests.get(f"{BASE_URL}{path}", timeout=5)
            passed = r.status_code == 200 and len(r.content) > 0
            log_test("Assets", name, passed, f"Size: {len(r.content)} bytes")
        except Exception as e:
            log_test("Assets", name, False, str(e))

def generate_report():
    """Generate test summary report"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}SMOKE TEST SUMMARY - App Store Submission{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    total = len(TEST_RESULTS)
    passed = sum(1 for t in TEST_RESULTS if t['passed'])
    failed = total - passed
    
    print(f"\nTotal Tests: {total}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {failed}{Colors.RESET}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    if failed > 0:
        print(f"\n{Colors.RED}Failed Tests:{Colors.RESET}")
        for t in TEST_RESULTS:
            if not t['passed']:
                print(f"  ❌ [{t['category']}] {t['test']}")
                if t['details']:
                    print(f"     {t['details']}")
    
    # Save detailed report
    report_file = f"smoke_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total': total,
                'passed': passed,
                'failed': failed,
                'success_rate': passed/total*100
            },
            'tests': TEST_RESULTS
        }, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    return failed == 0

def main():
    """Run all smoke tests"""
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}BeeSmart Spelling Bee - App Store Smoke Test{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"Target: {BASE_URL}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if server is running
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        if r.status_code != 200:
            print(f"\n{Colors.RED}ERROR: Server not responding at {BASE_URL}{Colors.RESET}")
            print("Please start the Flask app first: python AjaSpellBApp.py")
            sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}ERROR: Cannot connect to server at {BASE_URL}{Colors.RESET}")
        print(f"Error: {e}")
        print("\nPlease start the Flask app first: python AjaSpellBApp.py")
        sys.exit(1)
    
    print(f"{Colors.GREEN}✅ Server is running{Colors.RESET}\n")
    
    # Run all test suites
    test_health_endpoints()
    test_core_pages()
    test_wordbank_api()
    test_avatar_api()
    test_quiz_flow()
    test_authentication()
    test_iap_endpoints()
    test_static_assets()
    
    # Generate report
    all_passed = generate_report()
    
    if all_passed:
        print(f"\n{Colors.GREEN}✅ ALL TESTS PASSED - Ready for App Store submission!{Colors.RESET}\n")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}❌ SOME TESTS FAILED - Please fix before submission{Colors.RESET}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
