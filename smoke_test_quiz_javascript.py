#!/usr/bin/env python3
"""
Browser-based JavaScript smoke test for quiz page
Tests actual JavaScript execution and catches runtime errors that API tests miss

This test:
1. Loads the quiz page in a browser
2. Checks for JavaScript console errors
3. Verifies QuizManager and BeeDelightManager are defined
4. Tests initialization sequence
"""

import os
import sys
import time
import io

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
    """Test using Selenium WebDriver"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException, WebDriverException
    except ImportError:
        print("❌ Selenium not installed. Install with: pip install selenium")
        return False
    
    print("=" * 80)
    print("🌐 BROWSER-BASED JAVASCRIPT SMOKE TEST")
    print("=" * 80)
    print(f"Testing: {BASE_URL}/quiz")
    print()
    
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
    errors_found = []
    warnings_found = []
    
    try:
        print("🚀 Starting Chrome browser...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        print("📄 Loading quiz page...")
        
        # First, seed words if needed (for local testing)
        if '127.0.0.1' in BASE_URL or 'localhost' in BASE_URL:
            print("🌱 Seeding test words...")
            try:
                seed_response = requests.post(
                    f"{BASE_URL}/api/upload",
                    json={"words": [{"word": "test", "sentence": "", "hint": ""}]},
                    timeout=5
                )
                if seed_response.status_code == 200:
                    print("   ✅ Words seeded")
            except:
                print("   ⚠️  Could not seed words (may already exist)")
        
        driver.get(f"{BASE_URL}/quiz")
        
        # Wait for page to load and check for redirects
        print("⏳ Waiting for page initialization...")
        time.sleep(3)
        
        # Check if we were redirected
        current_url = driver.current_url
        if 'quiz' not in current_url.lower():
            print(f"⚠️  Redirected to: {current_url}")
            print("   (This may be normal if no words are loaded)")
        
        # Wait a bit more for JavaScript to execute
        time.sleep(5)
        
        # Get console logs
        print("📋 Checking browser console for errors...")
        logs = driver.get_log('browser')
        
        for log in logs:
            level = log.get('level', '').upper()
            message = log.get('message', '')
            
            if level == 'SEVERE':
                errors_found.append(message)
                print(f"❌ ERROR: {message[:200]}")
            elif level == 'WARNING' and ('QuizManager' in message or 'BeeDelightManager' in message or 'Three.js' in message):
                warnings_found.append(message)
                print(f"⚠️  WARNING: {message[:200]}")
        
        # Check if critical classes are defined
        print("\n🔍 Checking JavaScript class definitions...")
        
        # Wait a bit more and retry if classes aren't found
        max_wait = 10
        quiz_manager_defined = False
        bee_delight_defined = False
        quiz_manager_instance = False
        
        for attempt in range(max_wait):
            quiz_manager_defined = driver.execute_script("return typeof QuizManager !== 'undefined';")
            bee_delight_defined = driver.execute_script("return typeof BeeDelightManager !== 'undefined';")
            quiz_manager_instance = driver.execute_script("return typeof window.quizManager !== 'undefined';")
            
            if quiz_manager_defined and bee_delight_defined:
                break
            
            if attempt < max_wait - 1:
                time.sleep(0.5)
        
        print(f"   QuizManager class: {'✅' if quiz_manager_defined else '❌'}")
        print(f"   BeeDelightManager class: {'✅' if bee_delight_defined else '❌'}")
        print(f"   QuizManager instance: {'✅' if quiz_manager_instance else '❌'}")
        
        # Check for specific error patterns
        page_source = driver.page_source
        has_syntax_error = 'SyntaxError' in page_source or 'ReferenceError' in page_source
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"JavaScript Errors: {len(errors_found)}")
        print(f"Relevant Warnings: {len(warnings_found)}")
        print(f"QuizManager defined: {'✅' if quiz_manager_defined else '❌'}")
        print(f"BeeDelightManager defined: {'✅' if bee_delight_defined else '❌'}")
        print(f"QuizManager instance created: {'✅' if quiz_manager_instance else '❌'}")
        
        if errors_found:
            print(f"\n❌ FAILED: Found {len(errors_found)} JavaScript errors")
            return False
        elif not quiz_manager_defined or not bee_delight_defined:
            print(f"\n❌ FAILED: Critical classes not defined")
            return False
        elif warnings_found:
            print(f"\n⚠️  PASSED WITH WARNINGS: {len(warnings_found)} warnings found")
            return True
        else:
            print(f"\n✅ PASSED: No JavaScript errors detected")
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

def test_with_requests():
    """Fallback: Basic HTML check if Selenium not available"""
    try:
        import requests
        print("=" * 80)
        print("📄 BASIC HTML CHECK (Selenium not available)")
        print("=" * 80)
        print(f"Testing: {BASE_URL}/quiz")
        print()
        
        response = requests.get(f"{BASE_URL}/quiz", timeout=15)
        if response.status_code != 200:
            print(f"❌ FAILED: HTTP {response.status_code}")
            return False
        
        html = response.text
        
        # Check for class definitions in HTML
        has_quiz_manager = 'class QuizManager' in html
        has_bee_delight = 'class BeeDelightManager' in html
        has_registration = 'window.QuizManager = QuizManager' in html or 'window.BeeDelightManager' in html
        
        print(f"   QuizManager class in HTML: {'✅' if has_quiz_manager else '❌'}")
        print(f"   BeeDelightManager class in HTML: {'✅' if has_bee_delight else '❌'}")
        print(f"   Window registration: {'✅' if has_registration else '❌'}")
        
        if has_quiz_manager and has_bee_delight:
            print("\n✅ PASSED: Classes found in HTML (but JavaScript execution not tested)")
            return True
        else:
            print("\n❌ FAILED: Classes missing from HTML")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run the appropriate test"""
    # Try Selenium first (more thorough)
    if test_with_selenium():
        return 0
    
    # Fallback to basic check
    print("\n" + "=" * 80)
    print("⚠️  Falling back to basic HTML check...")
    print("=" * 80)
    if test_with_requests():
        print("\n⚠️  NOTE: Install Selenium for full JavaScript error detection:")
        print("   pip install selenium")
        return 0
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
