#!/usr/bin/env python3
"""
Simple test to verify retry choice flow HTML/CSS elements are present
"""

import requests
from bs4 import BeautifulSoup

BASE_URL = "http://localhost:5000"

def test_retry_ui_elements():
    """Check if all retry choice UI elements are present in the HTML"""
    
    print("\n" + "="*70)
    print("🧪 TESTING RETRY CHOICE UI ELEMENTS")
    print("="*70)
    
    try:
        # Get the quiz page
        response = requests.get(f"{BASE_URL}/quiz", timeout=5)
        if response.status_code != 200:
            print(f"❌ Failed to fetch /quiz: {response.status_code}")
            return False
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for retry choice buttons
        print("\n📋 Checking for retry choice UI elements...")
        
        elements_to_check = [
            ('retryChoiceYes', 'Retry button'),
            ('retryChoiceNo', 'Show Answer button'),
            ('retryChoiceTimer', 'Retry choice timer container'),
            ('retryChoiceSeconds', 'Retry choice seconds display'),
        ]
        
        all_found = True
        for element_id, description in elements_to_check:
            element = soup.find(id=element_id)
            if element:
                print(f"✅ Found {description} (#{element_id})")
            else:
                print(f"❌ Missing {description} (#{element_id})")
                all_found = False
        
        # Check for CSS classes in style tags
        print("\n📋 Checking for retry choice CSS classes...")
        
        css_classes = [
            'retry-choice-container',
            'retry-choice-btn',
            'retry-choice-timer',
        ]
        
        style_tags = soup.find_all('style')
        full_css = ' '.join(tag.string for tag in style_tags if tag.string)
        
        for css_class in css_classes:
            if f'.{css_class}' in full_css:
                print(f"✅ Found CSS class .{css_class}")
            else:
                print(f"❌ Missing CSS class .{css_class}")
                all_found = False
        
        # Check for JavaScript functions
        print("\n📋 Checking for JavaScript functions...")
        
        js_functions = [
            'startRetryChoiceCountdown',
            'handleRetryChoiceYes',
            'handleRetryChoiceNo',
            'startRetryInputWindow',
            'showRetryInputExpired',
        ]
        
        scripts = soup.find_all('script')
        full_js = ' '.join(tag.string for tag in scripts if tag.string)
        
        for func in js_functions:
            if func in full_js:
                print(f"✅ Found JavaScript function {func}()")
            else:
                print(f"❌ Missing JavaScript function {func}()")
                all_found = False
        
        print("\n" + "="*70)
        if all_found:
            print("✅ ALL RETRY CHOICE UI ELEMENTS FOUND!")
            print("="*70)
            return True
        else:
            print("❌ SOME ELEMENTS MISSING - Check the output above")
            print("="*70)
            return False
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to {BASE_URL}")
        print("   Make sure the Flask app is running on port 5000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_retry_ui_elements()
    exit(0 if success else 1)
