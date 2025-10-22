"""
BeeSmart Spelling Bee App - Comprehensive Diagnostic Test
Tests all routes, database operations, and core functionality
"""

import requests
import json
import time
from datetime import datetime
import os

# Test configuration
BASE_URL = "http://127.0.0.1:5000"
TEST_USERNAME = f"test_user_{int(time.time())}"
TEST_EMAIL = f"{TEST_USERNAME}@test.com"
TEST_PASSWORD = "TestPass123!"

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_test(test_name):
    print(f"{Colors.YELLOW}🔍 Testing:{Colors.RESET} {test_name}...", end=" ")

def print_success(message=""):
    print(f"{Colors.GREEN}✅ PASS{Colors.RESET}", message)

def print_fail(message=""):
    print(f"{Colors.RED}❌ FAIL{Colors.RESET}", message)

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  WARNING:{Colors.RESET} {message}")

# Create session for maintaining cookies
session = requests.Session()

# Test results tracking
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "warnings": 0
}

def test_route(name, url, method="GET", expected_status=200, data=None, json_data=None):
    """Generic route testing function"""
    global test_results
    test_results["total"] += 1
    print_test(name)
    
    try:
        if method == "GET":
            response = session.get(url, timeout=5)
        elif method == "POST":
            if json_data:
                response = session.post(url, json=json_data, timeout=5)
            else:
                response = session.post(url, data=data, timeout=5)
        
        if response.status_code == expected_status:
            test_results["passed"] += 1
            print_success(f"(Status: {response.status_code})")
            return True, response
        else:
            test_results["failed"] += 1
            print_fail(f"(Expected: {expected_status}, Got: {response.status_code})")
            return False, response
    except Exception as e:
        test_results["failed"] += 1
        print_fail(f"(Exception: {str(e)[:50]})")
        return False, None

def run_diagnostics():
    """Run comprehensive app diagnostics"""
    
    print_header("BeeSmart Spelling Bee App - Full Diagnostic Test")
    print(f"🕐 Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Testing URL: {BASE_URL}")
    
    # ========== SECTION 1: PUBLIC ROUTES ==========
    print_header("SECTION 1: Public Routes & Static Files")
    
    # Homepage
    test_route("Homepage (/)", f"{BASE_URL}/")
    
    # Authentication pages
    test_route("Login Page", f"{BASE_URL}/auth/login")
    test_route("Register Page", f"{BASE_URL}/auth/register")
    
    # Main app pages
    test_route("Quiz Page", f"{BASE_URL}/quiz")
    test_route("Upload Page", f"{BASE_URL}/upload")
    test_route("Unified Menu", f"{BASE_URL}/unified_menu")
    
    # Health check
    test_route("Health Check", f"{BASE_URL}/health")
    
    # Static files
    test_route("CSS File", f"{BASE_URL}/static/css/BeeSmart.css")
    test_route("JavaScript File", f"{BASE_URL}/static/js/smarty-bee-3d.js")
    test_route("Logo Image", f"{BASE_URL}/static/BeeSmartTitle.png")
    
    # ========== SECTION 2: API ENDPOINTS (Wordbank) ==========
    print_header("SECTION 2: Wordbank API Endpoints")
    
    # Get wordbank (should load default words)
    success, response = test_route("Get Wordbank", f"{BASE_URL}/api/wordbank")
    if success and response:
        try:
            data = response.json()
            word_count = len(data.get("words", []))
            print(f"   📝 Default word count: {word_count}")
        except:
            pass
    
    # Clear wordbank
    test_route("Clear Wordbank", f"{BASE_URL}/api/clear", method="POST")
    
    # Upload wordlist (test with sample data)
    print_test("Upload Word List")
    try:
        files = {'file': ('test.txt', 'apple\nbanana\ncherry\n', 'text/plain')}
        response = session.post(f"{BASE_URL}/api/upload", files=files, timeout=10)
        if response.status_code == 200:
            test_results["passed"] += 1
            test_results["total"] += 1
            print_success(f"(Uploaded 3 words)")
        else:
            test_results["failed"] += 1
            test_results["total"] += 1
            print_fail(f"(Status: {response.status_code})")
    except Exception as e:
        test_results["failed"] += 1
        test_results["total"] += 1
        print_fail(f"(Exception: {str(e)[:50]})")
    
    # ========== SECTION 3: QUIZ API ENDPOINTS ==========
    print_header("SECTION 3: Quiz Flow API Endpoints")
    
    # Start quiz (get next word)
    success, response = test_route("Start Quiz (/api/next)", f"{BASE_URL}/api/next", method="POST")
    current_word = None
    if success and response:
        try:
            data = response.json()
            current_word = data.get("word")
            print(f"   📝 Current word: {current_word}")
        except:
            pass
    
    # Submit answer
    if current_word:
        test_route("Submit Answer (/api/answer)", 
                   f"{BASE_URL}/api/answer", 
                   method="POST",
                   json_data={"user_input": current_word, "method": "keyboard", "elapsed_ms": 5000})
    
    # Get hint
    test_route("Get Hint (/api/hint)", f"{BASE_URL}/api/hint", method="POST")
    
    # Pronounce word
    test_route("Pronounce Word (/api/pronounce)", f"{BASE_URL}/api/pronounce", method="POST")
    
    # ========== SECTION 4: AUTHENTICATION FLOW ==========
    print_header("SECTION 4: Authentication System")
    
    # Register new user
    print_test("User Registration")
    try:
        register_data = {
            "username": TEST_USERNAME,
            "display_name": "Test User",
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "confirm_password": TEST_PASSWORD,
            "grade_level": "5",
            "profile_picture": "CoolBee.png"
        }
        response = session.post(f"{BASE_URL}/auth/register", data=register_data, timeout=5)
        if response.status_code == 200 and "success" in response.text.lower():
            test_results["passed"] += 1
            test_results["total"] += 1
            print_success(f"(User: {TEST_USERNAME})")
        else:
            test_results["failed"] += 1
            test_results["total"] += 1
            print_fail(f"(Status: {response.status_code})")
    except Exception as e:
        test_results["failed"] += 1
        test_results["total"] += 1
        print_fail(f"(Exception: {str(e)[:50]})")
    
    # Login
    print_test("User Login")
    try:
        login_data = {
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        }
        response = session.post(f"{BASE_URL}/auth/login", data=login_data, timeout=5)
        if response.status_code == 200:
            test_results["passed"] += 1
            test_results["total"] += 1
            print_success(f"(Logged in as {TEST_USERNAME})")
        else:
            test_results["failed"] += 1
            test_results["total"] += 1
            print_fail(f"(Status: {response.status_code})")
    except Exception as e:
        test_results["failed"] += 1
        test_results["total"] += 1
        print_fail(f"(Exception: {str(e)[:50]})")
    
    # Access protected dashboard
    test_route("Student Dashboard (Protected)", f"{BASE_URL}/auth/dashboard")
    
    # Logout
    test_route("User Logout", f"{BASE_URL}/auth/logout")
    
    # ========== SECTION 5: SPECIAL FEATURES ==========
    print_header("SECTION 5: Special Features")
    
    # Random words generator
    test_route("Random Words API", 
               f"{BASE_URL}/api/random-words", 
               method="POST",
               json_data={"difficulty": 1, "count": 10})
    
    # Saved lists
    test_route("Get Saved Lists", f"{BASE_URL}/api/saved-lists")
    
    # Dictionary lookup (if word exists)
    if current_word:
        test_route("Dictionary Lookup", 
                   f"{BASE_URL}/api/dictionary", 
                   method="POST",
                   json_data={"word": current_word})
    
    # ========== SECTION 6: DATABASE OPERATIONS ==========
    print_header("SECTION 6: Database Connectivity")
    
    print_test("Database Models Import")
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from models import db, User, QuizSession, QuizResult, WordList
        test_results["passed"] += 1
        test_results["total"] += 1
        print_success("(All models imported)")
    except Exception as e:
        test_results["failed"] += 1
        test_results["total"] += 1
        print_fail(f"(Exception: {str(e)[:50]})")
    
    # ========== SECTION 7: FILE SYSTEM CHECKS ==========
    print_header("SECTION 7: File System & Configuration")
    
    # Check critical files
    critical_files = [
        "AjaSpellBApp.py",
        "models.py",
        "config.py",
        "dictionary_api.py",
        "50Words_kidfriendly.txt",
        "data/dictionary.json",
        "templates/quiz.html",
        "templates/unified_menu.html",
        "templates/auth/login.html",
        "templates/auth/register.html",
        "static/css/BeeSmart.css",
        "static/js/smarty-bee-3d.js"
    ]
    
    for file_path in critical_files:
        print_test(f"File: {file_path}")
        test_results["total"] += 1
        if os.path.exists(file_path):
            test_results["passed"] += 1
            print_success(f"(Size: {os.path.getsize(file_path)} bytes)")
        else:
            test_results["failed"] += 1
            print_fail("(File not found)")
    
    # ========== FINAL REPORT ==========
    print_header("DIAGNOSTIC REPORT")
    
    print(f"📊 Total Tests: {test_results['total']}")
    print(f"{Colors.GREEN}✅ Passed: {test_results['passed']}{Colors.RESET}")
    print(f"{Colors.RED}❌ Failed: {test_results['failed']}{Colors.RESET}")
    
    if test_results['warnings'] > 0:
        print(f"{Colors.YELLOW}⚠️  Warnings: {test_results['warnings']}{Colors.RESET}")
    
    # Calculate success rate
    success_rate = (test_results['passed'] / test_results['total'] * 100) if test_results['total'] > 0 else 0
    print(f"\n📈 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 EXCELLENT! App is functioning properly!{Colors.RESET}")
    elif success_rate >= 75:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  GOOD, but some issues detected{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️  CRITICAL: Multiple failures detected!{Colors.RESET}")
    
    print(f"\n🕐 Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}\n")

if __name__ == "__main__":
    print(f"{Colors.BOLD}Starting BeeSmart App Diagnostics...{Colors.RESET}")
    print(f"{Colors.YELLOW}Make sure the Flask app is running on {BASE_URL}{Colors.RESET}\n")
    
    try:
        # Quick connectivity check
        response = requests.get(f"{BASE_URL}/health", timeout=3)
        print(f"{Colors.GREEN}✅ Server is reachable!{Colors.RESET}\n")
    except:
        print(f"{Colors.RED}❌ ERROR: Cannot connect to {BASE_URL}{Colors.RESET}")
        print(f"{Colors.YELLOW}Please start the Flask app first: python AjaSpellBApp.py{Colors.RESET}\n")
        exit(1)
    
    run_diagnostics()
