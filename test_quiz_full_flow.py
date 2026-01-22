#!/usr/bin/env python3
"""
Comprehensive End-to-End Quiz Test
Tests the full flow with actual browser to catch JavaScript errors
"""

import os
import sys
import time
import io
import requests

# Ensure Windows console can handle Unicode
if sys.platform == "win32":
    try:
        if getattr(sys.stdout, "buffer", None) is not None and not getattr(sys.stdout, "closed", False):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        if getattr(sys.stderr, "buffer", None) is not None and not getattr(sys.stderr, "closed", False):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:5051").rstrip("/")

def test_with_selenium():
    """Test using Selenium WebDriver - actually loads page and checks for errors"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException, WebDriverException
    except ImportError:
        print("❌ Selenium not installed. Install with: pip install selenium")
        return False
    
    print("=" * 80)
    print("🌐 COMPREHENSIVE QUIZ FLOW TEST - BROWSER-BASED")
    print("=" * 80)
    print(f"Testing: {BASE_URL}")
    print()
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # Capture console logs
    chrome_options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    
    driver = None
    errors = []
    warnings = []
    
    try:
        print("🚀 Starting Chrome browser...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        # Step 1: Seed words via API and verify
        print("\n📝 Step 1: Seeding test words...")
        session = requests.Session()
        words = [
            {"word": "test", "sentence": "This is a test.", "hint": "A trial"},
            {"word": "quiz", "sentence": "Take the quiz.", "hint": "A test"},
            {"word": "spell", "sentence": "Spell the word.", "hint": "Write letters"}
        ]
        
        words_seeded = False
        try:
            resp = session.post(
                f"{BASE_URL}/api/upload",
                json={"words": words},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get('ok') and data.get('count', 0) > 0:
                    print(f"   ✅ Words seeded successfully ({data.get('count')} words)")
                    words_seeded = True
                else:
                    print(f"   ⚠️  Word seed response: {data}")
            else:
                print(f"   ⚠️  Word seed returned {resp.status_code}")
        except Exception as e:
            print(f"   ⚠️  Could not seed words: {e}")
        
        # Verify wordbank exists
        print("\n🔍 Step 1b: Verifying wordbank...")
        try:
            wb_resp = session.get(f"{BASE_URL}/api/wordbank", timeout=10)
            if wb_resp.status_code == 200:
                wb_data = wb_resp.json()
                wb_words = wb_data.get('words', [])
                if len(wb_words) > 0:
                    print(f"   ✅ Wordbank verified ({len(wb_words)} words)")
                    words_seeded = True
                else:
                    print("   ⚠️  Wordbank is empty")
            else:
                print(f"   ⚠️  Wordbank check returned {wb_resp.status_code}")
        except Exception as e:
            print(f"   ⚠️  Could not verify wordbank: {e}")
        
        if not words_seeded:
            print("   ❌ Cannot proceed - no words available")
            return False
        
        # Step 2: Load quiz page with proper session handling
        print("\n📄 Step 2: Loading quiz page...")
        
        # First visit to establish session
        driver.get(f"{BASE_URL}/")
        time.sleep(1)
        
        # Transfer cookies from requests session to selenium
        for cookie in session.cookies:
            try:
                # Selenium needs domain without protocol
                cookie_dict = {
                    'name': cookie.name,
                    'value': cookie.value,
                    'domain': cookie.domain if cookie.domain else '127.0.0.1',
                    'path': cookie.path if cookie.path else '/'
                }
                driver.add_cookie(cookie_dict)
            except Exception as e:
                print(f"   ⚠️  Could not add cookie {cookie.name}: {e}")
        
        # Now load quiz page
        driver.get(f"{BASE_URL}/quiz")
        time.sleep(3)  # Wait for initial load
        
        # Check for redirects
        current_url = driver.current_url
        if 'quiz' not in current_url.lower():
            print(f"   ⚠️  Redirected to: {current_url}")
            # Check if it's a wordbank issue
            if 'no_words' in current_url or 'error' in current_url:
                print("   ❌ Quiz redirected due to wordbank issue")
                print("   ⚠️  This may be a session/cookie problem")
                # Still continue to check for JavaScript errors on the page we're on
                print("   ⚠️  Continuing to check for JavaScript errors on current page...")
        
        # Step 3: Wait for JavaScript to execute
        print("\n⏳ Step 3: Waiting for JavaScript initialization...")
        time.sleep(5)
        
        # Step 4: Check console for errors
        print("\n📋 Step 4: Checking browser console...")
        logs = driver.get_log('browser')
        
        for log in logs:
            level = log.get('level', '').upper()
            message = log.get('message', '')
            
            # Filter out non-critical warnings and expected errors
            if level == 'SEVERE':
                # Filter out expected 401 errors for upload/image (not a real error)
                if '401' in message and 'upload/image' in message:
                    continue  # Skip this - it's expected
                errors.append(message)
                print(f"   ❌ ERROR: {message[:150]}")
            elif level == 'WARNING':
                # Only report critical warnings
                if any(keyword in message for keyword in ['QuizManager', 'BeeDelightManager', 'SyntaxError', 'ReferenceError', 'TypeError', 'Three.js']):
                    warnings.append(message)
                    print(f"   ⚠️  WARNING: {message[:150]}")
        
        # Step 5: Check JavaScript class definitions
        print("\n🔍 Step 5: Verifying JavaScript classes...")
        
        # Wait and retry for classes to be defined
        max_attempts = 20
        quiz_manager_defined = False
        bee_delight_defined = False
        quiz_manager_instance = False
        
        for attempt in range(max_attempts):
            try:
                quiz_manager_defined = driver.execute_script("return typeof QuizManager !== 'undefined';")
                bee_delight_defined = driver.execute_script("return typeof BeeDelightManager !== 'undefined';")
                quiz_manager_instance = driver.execute_script("return typeof window.quizManager !== 'undefined';")
                
                if quiz_manager_defined and bee_delight_defined:
                    break
            except Exception as e:
                print(f"   ⚠️  Error checking classes (attempt {attempt + 1}): {e}")
            
            if attempt < max_attempts - 1:
                time.sleep(0.5)
        
        print(f"   QuizManager class: {'✅' if quiz_manager_defined else '❌'}")
        print(f"   BeeDelightManager class: {'✅' if bee_delight_defined else '❌'}")
        print(f"   QuizManager instance: {'✅' if quiz_manager_instance else '❌'}")
        
        # Step 6: Check for syntax errors in page source
        print("\n🔎 Step 6: Checking for syntax errors...")
        page_source = driver.page_source.lower()
        syntax_indicators = ['syntaxerror', 'referenceerror', 'typeerror', 'uncaught']
        found_syntax_errors = [ind for ind in syntax_indicators if ind in page_source]
        
        if found_syntax_errors:
            print(f"   ⚠️  Found syntax error indicators: {found_syntax_errors}")
        
        # Step 7: Try to interact with quiz (if loaded)
        print("\n🎮 Step 7: Testing quiz interaction...")
        try:
            # Check if quiz elements exist
            spelling_input = driver.find_elements(By.ID, "spellingInput")
            if spelling_input:
                print("   ✅ Quiz input field found")
            else:
                print("   ⚠️  Quiz input field not found")
        except Exception as e:
            print(f"   ⚠️  Could not check quiz elements: {e}")
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"JavaScript Errors: {len(errors)}")
        print(f"Critical Warnings: {len(warnings)}")
        print(f"QuizManager defined: {'✅' if quiz_manager_defined else '❌'}")
        print(f"BeeDelightManager defined: {'✅' if bee_delight_defined else '❌'}")
        print(f"QuizManager instance: {'✅' if quiz_manager_instance else '❌'}")
        
        if errors:
            print("\n❌ ERRORS FOUND:")
            for i, error in enumerate(errors[:5], 1):  # Show first 5 errors
                print(f"   {i}. {error[:200]}")
        
        if warnings:
            print("\n⚠️  WARNINGS FOUND:")
            for i, warning in enumerate(warnings[:5], 1):  # Show first 5 warnings
                print(f"   {i}. {warning[:200]}")
        
        # Determine result
        if errors:
            print("\n❌ FAILED: JavaScript errors detected")
            return False
        elif not quiz_manager_defined or not bee_delight_defined:
            print("\n❌ FAILED: Critical classes not defined")
            return False
        elif warnings:
            print("\n⚠️  PASSED WITH WARNINGS")
            return True
        else:
            print("\n✅ PASSED: No errors detected")
            return True
            
    except WebDriverException as e:
        print(f"❌ Browser error: {e}")
        print("   Make sure ChromeDriver is installed and in PATH")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if driver:
            driver.quit()
            print("\n🔒 Browser closed")

def main():
    """Run the comprehensive test"""
    success = test_with_selenium()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
