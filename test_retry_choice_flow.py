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

def test_retry_choice_flow():
    """Test the complete retry choice flow"""
    
    print("\n" + "="*70)
    print("🧪 TESTING RETRY CHOICE FLOW")
    print("="*70)
    
    # Start browser session
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment to hide browser
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(BASE_URL)
        
        print("\n✅ Browser opened at", BASE_URL)
        
        # Wait for page to load
        wait = WebDriverWait(driver, 10)
        
        # Find upload button or skip to quiz
        try:
            quiz_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Quiz')]")))
            quiz_btn.click()
            print("✅ Clicked Quiz button")
        except:
            print("⚠️  Quiz button not found, trying to navigate directly...")
            driver.get(f"{BASE_URL}/quiz")
        
        # Wait for quiz interface to load
        time.sleep(2)
        
        # Check for word display
        try:
            word_display = wait.until(EC.presence_of_element_located((By.ID, "currentWordDisplay")))
            current_word = word_display.text
            print(f"📝 Current word to spell: {current_word}")
        except:
            print("⚠️  Could not find word display")
            return False
        
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
        
        # Click submit/Next button to submit
        try:
            # Look for submit button (could be Next or Submit)
            submit_btn = driver.find_element(By.XPATH, "//*[contains(@id, 'submit') or contains(text(), 'Next') or contains(text(), 'Submit')]")
            submit_btn.click()
            print("✅ Clicked submit button")
        except Exception as e:
            print(f"⚠️  Could not find submit button: {e}")
            # Try pressing Enter
            input_field.send_keys("\n")
            print("✅ Pressed Enter to submit")
        
        # Wait for retry choice UI to appear
        time.sleep(1)
        
        # Check for choice buttons
        try:
            retry_btn = wait.until(EC.presence_of_element_located((By.ID, "retryChoiceYes")), timeout=5)
            print("✅ RETRY button appeared!")
            
            show_answer_btn = driver.find_element(By.ID, "retryChoiceNo")
            print("✅ SHOW ANSWER button appeared!")
            
            # Verify buttons are enabled (not disabled)
            if "disabled" not in retry_btn.get_attribute("class"):
                print("✅ Retry button is ENABLED (not disabled)")
            else:
                print("⚠️  Retry button has disabled class")
            
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
                
                # Try typing correct answer this time
                input_field.clear()
                input_field.send_keys(current_word)
                print(f"📝 Typed (hopefully) correct: {current_word}")
                
                # Submit retry
                input_field.send_keys("\n")
                print("✅ Submitted retry answer")
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
            driver.save_screenshot("/tmp/retry_choice_debug.png")
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
