"""
BeeSmart Spelling Bee App - FULL Diagnostic Test
Tests routes, templates, url_for() calls, database, and all functionality
"""

import requests
import json
import time
from datetime import datetime
import os
import sys

# Test configuration
BASE_URL = "http://127.0.0.1:5000"
TEST_USERNAME = f"diagtest_{int(time.time())}"
TEST_EMAIL = f"{TEST_USERNAME}@test.com"
TEST_PASSWORD = "DiagTest123!"

# Color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}\n")

def print_section(text):
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}▶ {text}{Colors.RESET}")
    print(f"{Colors.MAGENTA}{'─'*80}{Colors.RESET}")

def print_test(test_name):
    print(f"{Colors.YELLOW}🔍 {test_name:<65}{Colors.RESET}", end=" ")

def print_success(message=""):
    print(f"{Colors.GREEN}✅ PASS{Colors.RESET}", message)

def print_fail(message=""):
    print(f"{Colors.RED}❌ FAIL{Colors.RESET}", message)

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")

# Session for maintaining cookies
session = requests.Session()

# Test results
results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "warnings": 0,
    "sections": {}
}

def test_route(name, url, method="GET", expected_status=200, data=None, json_data=None, check_content=None):
    """Test a route with optional content validation"""
    global results
    results["total"] += 1
    print_test(name)
    
    try:
        if method == "GET":
            response = session.get(url, timeout=10)
        elif method == "POST":
            if json_data:
                response = session.post(url, json=json_data, timeout=10)
            else:
                response = session.post(url, data=data, timeout=10)
        
        # Check status code
        if response.status_code != expected_status:
            results["failed"] += 1
            print_fail(f"(Expected: {expected_status}, Got: {response.status_code})")
            return False, response
        
        # Check content if specified
        if check_content:
            if check_content.lower() not in response.text.lower():
                results["failed"] += 1
                results["warnings"] += 1
                print_fail(f"(Missing content: '{check_content}')")
                return False, response
        
        results["passed"] += 1
        print_success(f"({response.status_code})")
        return True, response
        
    except requests.exceptions.Timeout:
        results["failed"] += 1
        print_fail("(Timeout)")
        return False, None
    except Exception as e:
        results["failed"] += 1
        print_fail(f"(Error: {str(e)[:30]})")
        return False, None

def run_full_diagnostic():
    """Run comprehensive diagnostic"""
    
    print_header("BeeSmart Spelling Bee - FULL DIAGNOSTIC TEST")
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Testing: {BASE_URL}\n")
    
    # ========== CONNECTIVITY ==========
    print_section("1. Server Connectivity")
    
    success, _ = test_route("Health Check", f"{BASE_URL}/health")
    if not success:
        print(f"\n{Colors.RED}❌ CRITICAL: Cannot connect to Flask server at {BASE_URL}{Colors.RESET}")
        print(f"{Colors.YELLOW}Please start Flask: python AjaSpellBApp.py{Colors.RESET}\n")
        return
    
    # ========== PUBLIC PAGES ==========
    print_section("2. Public Pages & Templates")
    
    test_route("Homepage (Unified Menu)", f"{BASE_URL}/", check_content="BeeSmart")
    test_route("Quiz Page", f"{BASE_URL}/quiz", check_content="quiz")
    test_route("Upload Page", f"{BASE_URL}/upload", check_content="upload")
    test_route("Login Page", f"{BASE_URL}/auth/login", check_content="login")
    test_route("Register Page", f"{BASE_URL}/auth/register", check_content="register")
    test_route("Speed Round Setup", f"{BASE_URL}/speed-round/setup", check_content="speed")
    
    # ========== STATIC FILES ==========
    print_section("3. Static Assets")
    
    test_route("Main CSS", f"{BASE_URL}/static/css/BeeSmart.css")
    test_route("3D Bee JavaScript", f"{BASE_URL}/static/js/smarty-bee-3d.js")
    test_route("Bee Swarm Animation", f"{BASE_URL}/static/js/bee-swarm-animation.js")
    test_route("Logo Image", f"{BASE_URL}/static/BeeSmartTitle.png")
    test_route("Avatar - CoolBee", f"{BASE_URL}/static/images/avatars/CoolBee.png")
    
    # ========== API ENDPOINTS - GET ==========
    print_section("4. API Endpoints (GET)")
    
    success, response = test_route("Get Wordbank", f"{BASE_URL}/api/wordbank")
    if success and response:
        try:
            data = response.json()
            word_count = len(data.get("words", []))
            print_info(f"Loaded {word_count} default words")
        except:
            pass
    
    test_route("Saved Lists", f"{BASE_URL}/api/saved-lists")
    test_route("Check Auth Status", f"{BASE_URL}/api/check-auth")
    
    # ========== API ENDPOINTS - POST ==========
    print_section("5. API Endpoints (POST)")
    
    # Clear wordbank first
    test_route("Clear Wordbank", f"{BASE_URL}/api/clear", method="POST")
    
    # Upload test word list
    print_test("Upload Word List (3 words)")
    try:
        files = {'file': ('test.txt', 'apple\nbanana\ncherry\n', 'text/plain')}
        response = session.post(f"{BASE_URL}/api/upload", files=files, timeout=10)
        if response.status_code == 200:
            results["passed"] += 1
            results["total"] += 1
            print_success("(Uploaded)")
        else:
            results["failed"] += 1
            results["total"] += 1
            print_fail(f"({response.status_code})")
    except Exception as e:
        results["failed"] += 1
        results["total"] += 1
        print_fail(f"({str(e)[:30]})")
    
    # ========== QUIZ FLOW ==========
    print_section("6. Quiz Flow & Game Logic")
    
    # Start quiz
    success, response = test_route("Start Quiz (api/next)", f"{BASE_URL}/api/next", method="POST")
    current_word = None
    if success and response:
        try:
            data = response.json()
            current_word = data.get("word")
            print_info(f"First word: '{current_word}'")
        except:
            pass
    
    # Submit answer
    if current_word:
        test_route("Submit Answer (correct)", 
                   f"{BASE_URL}/api/answer", 
                   method="POST",
                   json_data={"user_input": current_word, "method": "keyboard", "elapsed_ms": 5000})
    
    # Get hint
    test_route("Get Hint", f"{BASE_URL}/api/hint", method="POST")
    
    # Pronounce word
    test_route("Pronounce Word", f"{BASE_URL}/api/pronounce", method="POST")
    
    # Random words API
    test_route("Random Words (difficulty 1, count 5)", 
               f"{BASE_URL}/api/random-words", 
               method="POST",
               json_data={"difficulty": 1, "count": 5})
    
    # ========== AUTHENTICATION ==========
    print_section("7. Authentication System")
    
    # Register new user
    print_test("User Registration")
    try:
        register_data = {
            "username": TEST_USERNAME,
            "display_name": "Diagnostic Test User",
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "confirm_password": TEST_PASSWORD,
            "grade_level": "5",
            "profile_picture": "CoolBee.png"
        }
        response = session.post(f"{BASE_URL}/auth/register", data=register_data, timeout=10)
        if response.status_code == 200:
            results["passed"] += 1
            results["total"] += 1
            print_success(f"({TEST_USERNAME})")
        else:
            results["failed"] += 1
            results["total"] += 1
            print_fail(f"({response.status_code})")
    except Exception as e:
        results["failed"] += 1
        results["total"] += 1
        print_fail(f"({str(e)[:30]})")
    
    # Login
    print_test("User Login")
    try:
        login_data = {"username": TEST_USERNAME, "password": TEST_PASSWORD}
        response = session.post(f"{BASE_URL}/auth/login", data=login_data, timeout=10)
        if response.status_code == 200:
            results["passed"] += 1
            results["total"] += 1
            print_success("(Logged in)")
        else:
            results["failed"] += 1
            results["total"] += 1
            print_fail(f"({response.status_code})")
    except Exception as e:
        results["failed"] += 1
        results["total"] += 1
        print_fail(f"({str(e)[:30]})")
    
    # Access protected route
    test_route("Student Dashboard (Protected)", f"{BASE_URL}/auth/dashboard")
    
    # Logout
    test_route("User Logout", f"{BASE_URL}/auth/logout")
    
    # ========== DATABASE & MODELS ==========
    print_section("8. Database & Models")
    
    print_test("Import Database Models")
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from models import db, User, QuizSession, QuizResult, WordList
        results["passed"] += 1
        results["total"] += 1
        print_success("(All models)")
    except Exception as e:
        results["failed"] += 1
        results["total"] += 1
        print_fail(f"({str(e)[:30]})")
    
    # ========== FILE SYSTEM ==========
    print_section("9. Critical Files")
    
    critical_files = [
        ("Main App", "AjaSpellBApp.py"),
        ("Models", "models.py"),
        ("Config", "config.py"),
        ("Dictionary API", "dictionary_api.py"),
        ("Default Words", "50Words_kidfriendly.txt"),
        ("Dictionary Cache", "data/dictionary.json"),
        ("Quiz Template", "templates/quiz.html"),
        ("Unified Menu", "templates/unified_menu.html"),
        ("Login Template", "templates/auth/login.html"),
        ("Register Template", "templates/auth/register.html"),
        ("Speed Round Setup", "templates/speed_round_setup.html"),
        ("Speed Round Results", "templates/speed_round_results.html"),
        ("Main CSS", "static/css/BeeSmart.css"),
        ("3D Bee JS", "static/js/smarty-bee-3d.js"),
    ]
    
    for name, file_path in critical_files:
        print_test(name)
        results["total"] += 1
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            size_kb = size / 1024
            results["passed"] += 1
            print_success(f"({size_kb:.1f} KB)")
        else:
            results["failed"] += 1
            print_fail("(Not found)")
    
    # ========== SPEED ROUND SPECIFIC ==========
    print_section("10. Speed Round Feature")
    
    test_route("Speed Round Setup Page", f"{BASE_URL}/speed-round/setup", check_content="speed")
    test_route("Speed Round Words API", 
               f"{BASE_URL}/api/speed-round/words", 
               method="POST",
               json_data={"difficulty": 1, "count": 5})
    
    # ========== FINAL REPORT ==========
    print_header("DIAGNOSTIC REPORT")
    
    print(f"\n{Colors.BOLD}Test Summary:{Colors.RESET}")
    print(f"  📊 Total Tests:    {results['total']}")
    print(f"  {Colors.GREEN}✅ Passed:        {results['passed']}{Colors.RESET}")
    print(f"  {Colors.RED}❌ Failed:        {results['failed']}{Colors.RESET}")
    
    if results['warnings'] > 0:
        print(f"  {Colors.YELLOW}⚠️  Warnings:      {results['warnings']}{Colors.RESET}")
    
    # Calculate success rate
    success_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
    
    print(f"\n{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.RESET}")
    
    # Status message
    if success_rate >= 95:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 EXCELLENT! All systems operational!{Colors.RESET}")
    elif success_rate >= 85:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ GOOD! App is functional with minor issues{Colors.RESET}")
    elif success_rate >= 70:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  FAIR: Some issues detected, needs attention{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ CRITICAL: Multiple failures detected!{Colors.RESET}")
    
    print(f"\n🕐 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.CYAN}{'='*80}{Colors.RESET}\n")
    
    return success_rate

if __name__ == "__main__":
    print(f"{Colors.BOLD}BeeSmart Full Diagnostic Starting...{Colors.RESET}")
    print(f"{Colors.YELLOW}Ensure Flask is running on {BASE_URL}{Colors.RESET}\n")
    
    # Quick connectivity check
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=3)
        print(f"{Colors.GREEN}✅ Server is online!{Colors.RESET}\n")
    except:
        print(f"{Colors.RED}❌ ERROR: Cannot reach {BASE_URL}{Colors.RESET}")
        print(f"{Colors.YELLOW}Start Flask first: python AjaSpellBApp.py{Colors.RESET}\n")
        sys.exit(1)
    
    success_rate = run_full_diagnostic()
    sys.exit(0 if success_rate >= 85 else 1)
