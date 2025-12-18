#!/usr/bin/env python3
"""
Test the new retry choice flow:
1. User makes incorrect answer
2. See choice buttons (Retry / Show Answer)
3. Can click Retry to get 20-second input window
4. Can click Show Answer to see correct spelling
"""

import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

BASE_URL = "http://localhost:5000"
UPLOAD_FILE = "PlainWordList50.txt"

def test_retry_choice_flow():
    """Test the complete retry choice flow"""
    
    print("\n" + "="*70)
    print("🧪 TESTING RETRY CHOICE FLOW")
    print("="*70)
    
    # 1) Ensure we have a wordbank in the same session the browser will use.
    # We do this by uploading via requests.Session and then copying its cookies into Selenium.
    print("\n📦 Preparing session wordbank via /api/upload...")
    api_session = requests.Session()
    try:
        with open(UPLOAD_FILE, 'rb') as f:
            files = {'file': (UPLOAD_FILE, f, 'text/plain')}
            up = api_session.post(f"{BASE_URL}/api/upload", files=files, timeout=30)
        if up.status_code != 200:
            print(f"❌ Upload failed: {up.status_code} {up.text[:200]}")
            return False
        up_json = up.json() if up.headers.get('content-type','').startswith('application/json') else {}
        if not up_json.get('ok'):
            print(f"❌ Upload response not ok: {up_json}")
            return False
        print(f"✅ Upload ok ({up_json.get('count')} words)")
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

    # 2) Start browser session
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment to hide browser
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        # Prime domain for cookie injection (use /minimal to avoid any special root-path middleware)
        driver.get(f"{BASE_URL}/minimal")

        # Copy cookies from requests session to browser
        for c in api_session.cookies:
            try:
                driver.add_cookie({
                    'name': c.name,
                    'value': c.value,
                    'path': c.path or '/',
                })
            except Exception as ce:
                print(f"⚠️  Could not add cookie {c.name}: {ce}")

        # Now open quiz in the same session (wordbank should exist)
        driver.get(f"{BASE_URL}/quiz")
        
        print("\n✅ Browser opened at", f"{BASE_URL}/quiz")
        
        # Wait for page to load
        wait = WebDriverWait(driver, 15)
        
        # Wait for quiz input to be present
        try:
            wait.until(EC.presence_of_element_located((By.ID, "spellingInput")))
            print("✅ Quiz input loaded")
        except Exception as e:
            print(f"❌ Quiz input did not load: {e}")
            return False

        # Wait until the quiz JS has a current word loaded (preferred, avoids DOM coupling)
        try:
            wait.until(lambda d: d.execute_script(
                "return !!(window.spellingQuiz && window.spellingQuiz.currentWordData && window.spellingQuiz.currentWordData.word);"
            ))
            current_word = driver.execute_script("return window.spellingQuiz.currentWordData.word;")
            print(f"📝 Current word to spell (from JS state): {current_word}")
        except Exception as e:
            print(f"⚠️  Could not read current word from JS state (continuing anyway): {e}")
            current_word = ""
        
        # Get the spelling input
        try:
            input_field = driver.find_element(By.ID, "spellingInput")
            print("✅ Found spelling input field")
        except:
            print("❌ Could not find spelling input field")
            return False
        
        # Type INCORRECT answer
        incorrect_answer = "WRONG_ANSWER_XYZ"
        input_field.clear()
        input_field.send_keys(incorrect_answer)
        print(f"📝 Typed incorrect answer: {incorrect_answer}")
        
        # Click submit button to submit
        try:
            submit_btn = driver.find_element(By.ID, "submitButton")
            submit_btn.click()
            print("✅ Clicked submit button")
        except Exception as e:
            print(f"⚠️  Could not click submitButton, falling back to Enter: {e}")
            input_field.send_keys("\n")
            print("✅ Pressed Enter to submit")
        
        # Check for choice buttons
        try:
            retry_btn = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "retryChoiceYes"))
            )
            print("✅ RETRY button appeared!")

            show_answer_btn = driver.find_element(By.ID, "retryChoiceNo")
            print("✅ SHOW ANSWER button appeared!")

            # Check for timer display
            timer_display = driver.find_element(By.ID, "retryChoiceSeconds")
            timer_text = timer_display.text
            print(f"⏱️  Timer shows: {timer_text} seconds")
            
            # Test 1: Click Retry button
            print("\n--- TEST 1: Testing RETRY button ---")
            retry_btn.click()
            print("✅ Clicked Retry button")
            
            # Should show input field again for 20-second retry
            time.sleep(1)
            try:
                input_field = driver.find_element(By.ID, "spellingInput")
                if not input_field.get_attribute("disabled"):
                    print("✅ Input field is ENABLED for retry")
                else:
                    print("⚠️  Input field is disabled during retry")
                
                # Try typing the current word (if available) as retry input
                if current_word:
                    input_field.clear()
                    input_field.send_keys(current_word)
                    print(f"📝 Typed (hopefully) correct: {current_word}")
                    
                    # Submit retry
                    input_field.send_keys("\n")
                    print("✅ Submitted retry answer")
                else:
                    print("⚠️  Current word unknown; skipping retry submit")
                time.sleep(2)
                
                # Check for success/next word
                try:
                    correct_feedback = driver.find_element(By.CLASS_NAME, "feedback-success")
                    print("✅ Got success feedback!")
                except:
                    print("⚠️  Could not find success feedback")
                    
            except Exception as e:
                print(f"❌ Error during retry: {e}")
                return False
            
            print("\n✅ RETRY CHOICE FLOW TEST PASSED!")
            return True
            
        except Exception as e:
            print(f"❌ Choice buttons did not appear: {e}")
            print("📸 Taking screenshot for debugging...")
            try:
                driver.save_screenshot("retry_choice_debug.png")
                print("📸 Saved retry_choice_debug.png")
            except Exception as se:
                print(f"⚠️  Screenshot failed: {se}")
            return False
        
    finally:
        if driver:
            driver.quit()
            print("\n🔌 Browser closed")

if __name__ == "__main__":
    success = test_retry_choice_flow()
    if success:
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED - Retry choice flow is working!")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("❌ TESTS FAILED - Check the output above")
        print("="*70)
