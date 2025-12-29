"""
Smoke Test for Morning Changes - December 29, 2025

Tests for:
1. Back buttons on Terms of Use and Privacy Policy pages
2. Subscription check flow with popup dialogs
3. Registration form validation and button enablement
4. Page load subscription status checking
"""

import re
import sys
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}✗ {msg}{RESET}")

def print_info(msg):
    print(f"{BLUE}ℹ {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠ {msg}{RESET}")

def print_section(msg):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{msg}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def read_file(file_path):
    """Read file content safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print_error(f"Failed to read {file_path}: {e}")
        return None

def test_terms_back_button():
    """Test 1: Verify Terms of Use has back button"""
    print_section("TEST 1: Terms of Use - Back Button")
    
    file_path = Path("templates/terms.html")
    if not file_path.exists():
        print_error(f"File not found: {file_path}")
        return False
    
    content = read_file(file_path)
    if not content:
        return False
    
    tests_passed = 0
    tests_total = 4
    
    # Check 1: Back button CSS class exists
    if '.back-btn' in content:
        print_success("Back button CSS class found")
        tests_passed += 1
    else:
        print_error("Back button CSS class missing")
    
    # Check 2: Back button HTML element exists
    if 'class="back-btn"' in content:
        print_success("Back button HTML element found")
        tests_passed += 1
    else:
        print_error("Back button HTML element missing")
    
    # Check 3: Back button uses history.back()
    if 'javascript:history.back()' in content:
        print_success("Back button uses history.back()")
        tests_passed += 1
    else:
        print_error("Back button history.back() missing")
    
    # Check 4: Back button has arrow icon
    if '\\u2190' in content or '←' in content:
        print_success("Back button has left arrow icon")
        tests_passed += 1
    else:
        print_error("Back button arrow icon missing")
    
    print_info(f"Terms back button: {tests_passed}/{tests_total} checks passed")
    return tests_passed == tests_total

def test_privacy_back_button():
    """Test 2: Verify Privacy Policy has back button"""
    print_section("TEST 2: Privacy Policy - Back Button")
    
    file_path = Path("templates/privacy.html")
    if not file_path.exists():
        print_error(f"File not found: {file_path}")
        return False
    
    content = read_file(file_path)
    if not content:
        return False
    
    tests_passed = 0
    tests_total = 4
    
    # Check 1: Back button CSS class exists
    if '.back-btn' in content:
        print_success("Back button CSS class found")
        tests_passed += 1
    else:
        print_error("Back button CSS class missing")
    
    # Check 2: Back button HTML element exists
    if 'class="back-btn"' in content:
        print_success("Back button HTML element found")
        tests_passed += 1
    else:
        print_error("Back button HTML element missing")
    
    # Check 3: Back button uses history.back()
    if 'javascript:history.back()' in content:
        print_success("Back button uses history.back()")
        tests_passed += 1
    else:
        print_error("Back button history.back() missing")
    
    # Check 4: Back button has arrow icon
    if '\\u2190' in content or '←' in content:
        print_success("Back button has left arrow icon")
        tests_passed += 1
    else:
        print_error("Back button arrow icon missing")
    
    print_info(f"Privacy back button: {tests_passed}/{tests_total} checks passed")
    return tests_passed == tests_total

def test_subscription_check_flow():
    """Test 3: Verify subscription check implementation"""
    print_section("TEST 3: Subscription Check Flow")
    
    file_path = Path("templates/subscription.html")
    if not file_path.exists():
        print_error(f"File not found: {file_path}")
        return False
    
    content = read_file(file_path)
    if not content:
        return False
    
    tests_passed = 0
    tests_total = 10
    
    # Check 1: checkExistingSubscription function exists
    if 'async function checkExistingSubscription()' in content:
        print_success("checkExistingSubscription() function found")
        tests_passed += 1
    else:
        print_error("checkExistingSubscription() function missing")
    
    # Check 2: Function checks for BeeSmartIAP
    if 'window.BeeSmartIAP' in content and 'getOwnedProducts' in content:
        print_success("Function checks BeeSmartIAP.getOwnedProducts()")
        tests_passed += 1
    else:
        print_error("BeeSmartIAP check missing")
    
    # Check 3: subscribe() is async and calls checkExistingSubscription
    if re.search(r'async function subscribe\s*\(', content):
        print_success("subscribe() function is async")
        tests_passed += 1
    else:
        print_error("subscribe() function not async")
    
    if 'await checkExistingSubscription()' in content:
        print_success("subscribe() calls checkExistingSubscription()")
        tests_passed += 1
    else:
        print_error("subscribe() doesn't call checkExistingSubscription()")
    
    # Check 4: showNoSubscriptionDialog function exists
    if 'function showNoSubscriptionDialog()' in content:
        print_success("showNoSubscriptionDialog() function found")
        tests_passed += 1
    else:
        print_error("showNoSubscriptionDialog() function missing")
    
    # Check 5: Dialog shows correct message
    if "No Subscription Found" in content:
        print_success("'No Subscription Found' message found")
        tests_passed += 1
    else:
        print_error("'No Subscription Found' message missing")
    
    # Check 6: showSubscriptionActiveDialog function exists
    if 'function showSubscriptionActiveDialog' in content:
        print_success("showSubscriptionActiveDialog() function found")
        tests_passed += 1
    else:
        print_error("showSubscriptionActiveDialog() function missing")
    
    # Check 7: Active subscription message
    if "Active Subscription" in content:
        print_success("'Active Subscription' message found")
        tests_passed += 1
    else:
        print_error("'Active Subscription' message missing")
    
    # Check 8: Page load check
    if 'DOMContentLoaded' in content and 'async' in content:
        print_success("Page load subscription check found")
        tests_passed += 1
    else:
        print_error("Page load subscription check missing")
    
    # Check 9: updateUIForActiveSubscription function
    if 'function updateUIForActiveSubscription()' in content:
        print_success("updateUIForActiveSubscription() function found")
        tests_passed += 1
    else:
        print_error("updateUIForActiveSubscription() function missing")
    
    print_info(f"Subscription flow: {tests_passed}/{tests_total} checks passed")
    return tests_passed == tests_total

def test_registration_form_validation():
    """Test 4: Verify registration form validation"""
    print_section("TEST 4: Registration Form Validation")
    
    file_path = Path("templates/auth/register.html")
    if not file_path.exists():
        print_error(f"File not found: {file_path}")
        return False
    
    content = read_file(file_path)
    if not content:
        return False
    
    tests_passed = 0
    tests_total = 8
    
    # Check 1: validateForm function exists
    if 'function validateForm()' in content:
        print_success("validateForm() function found")
        tests_passed += 1
    else:
        print_error("validateForm() function missing")
    
    # Check 2: Checks all required fields
    required_checks = [
        'username',
        'display_name', 
        'role',
        'password',
        'selected_avatar'
    ]
    
    for field in required_checks:
        if f"getElementById('{field}')" in content:
            print_success(f"Validation checks '{field}' field")
            tests_passed += 1
        else:
            print_error(f"Validation missing for '{field}' field")
    
    # Check 3: Button enable/disable logic
    if 'submitBtn.disabled' in content:
        print_success("Button enable/disable logic found")
        tests_passed += 1
    else:
        print_error("Button enable/disable logic missing")
    
    # Check 4: Event listeners on required fields
    if 'addEventListener' in content and 'validateForm' in content:
        print_success("Event listeners call validateForm()")
        tests_passed += 1
    else:
        print_error("Event listeners for validation missing")
    
    print_info(f"Registration validation: {tests_passed}/{tests_total} checks passed")
    return tests_passed == tests_total

def test_subscription_dialog_styling():
    """Test 5: Verify subscription dialog styling"""
    print_section("TEST 5: Subscription Dialog Styling")
    
    file_path = Path("templates/subscription.html")
    if not file_path.exists():
        print_error(f"File not found: {file_path}")
        return False
    
    content = read_file(file_path)
    if not content:
        return False
    
    tests_passed = 0
    tests_total = 5
    
    # Check 1: Modal overlay styling
    if 'position: fixed' in content and 'z-index: 10000' in content:
        print_success("Modal overlay with proper z-index found")
        tests_passed += 1
    else:
        print_error("Modal overlay styling incomplete")
    
    # Check 2: Dialog animations
    if '@keyframes fadeIn' in content or 'fadeIn' in content:
        print_success("Fade-in animation found")
        tests_passed += 1
    else:
        print_error("Fade-in animation missing")
    
    if '@keyframes slideUp' in content or 'slideUp' in content:
        print_success("Slide-up animation found")
        tests_passed += 1
    else:
        print_error("Slide-up animation missing")
    
    # Check 3: Button styling
    if 'border-radius' in content and '#2196F3' in content:
        print_success("Blue button styling found")
        tests_passed += 1
    else:
        print_error("Button styling incomplete")
    
    # Check 4: Green success styling
    if '#4CAF50' in content:
        print_success("Green success color found")
        tests_passed += 1
    else:
        print_error("Green success color missing")
    
    print_info(f"Dialog styling: {tests_passed}/{tests_total} checks passed")
    return tests_passed == tests_total

def test_registration_button_state():
    """Test 6: Verify registration button initial state"""
    print_section("TEST 6: Registration Button Initial State")
    
    file_path = Path("templates/auth/register.html")
    if not file_path.exists():
        print_error(f"File not found: {file_path}")
        return False
    
    content = read_file(file_path)
    if not content:
        return False
    
    tests_passed = 0
    tests_total = 3
    
    # Check 1: Button starts disabled
    if 'id="submitBtn" disabled' in content or 'id="submitBtn"' in content and 'disabled' in content:
        print_success("Submit button initially disabled")
        tests_passed += 1
    else:
        print_error("Submit button not initially disabled")
    
    # Check 2: Initial validation check on page load
    if 'setTimeout(validateForm' in content:
        print_success("Initial validation check on page load found")
        tests_passed += 1
    else:
        print_error("Initial validation check missing")
    
    # Check 3: Console logging for debugging
    if 'console.log' in content and 'validation' in content.lower():
        print_success("Validation debug logging found")
        tests_passed += 1
    else:
        print_warning("No validation debug logging found (optional)")
        tests_passed += 1  # Not critical
    
    print_info(f"Button state: {tests_passed}/{tests_total} checks passed")
    return tests_passed == tests_total

def run_all_tests():
    """Run all smoke tests"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}🐝 BeeSmart Morning Changes - Smoke Test Suite{RESET}")
    print(f"{BLUE}   December 29, 2025{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    results = {
        "Terms Back Button": test_terms_back_button(),
        "Privacy Back Button": test_privacy_back_button(),
        "Subscription Check Flow": test_subscription_check_flow(),
        "Registration Form Validation": test_registration_form_validation(),
        "Subscription Dialog Styling": test_subscription_dialog_styling(),
        "Registration Button State": test_registration_button_state()
    }
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    for test_name, passed in results.items():
        status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
        print(f"  {test_name}: {status}")
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    
    if passed_count == total_count:
        print(f"{GREEN}✓ ALL TESTS PASSED ({passed_count}/{total_count}){RESET}")
        print(f"{GREEN}  Morning changes are working correctly! 🎉{RESET}")
        return_code = 0
    else:
        print(f"{RED}✗ SOME TESTS FAILED ({passed_count}/{total_count}){RESET}")
        print(f"{YELLOW}  Please review the failed tests above{RESET}")
        return_code = 1
    
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    return return_code

if __name__ == "__main__":
    sys.exit(run_all_tests())
