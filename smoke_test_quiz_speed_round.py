#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smoke Test for Quiz and Speed Round Pages
Tests for errors and validates key functionality
"""

import requests
import time
import re
import sys
import io
from datetime import datetime

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://localhost:5051"

def print_status(emoji, message, status=""):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if status:
        print(f"{timestamp} {emoji} {message}: {status}")
    else:
        print(f"{timestamp} {emoji} {message}")

def check_html_structure(content, page_name):
    """Check HTML structure (DOCTYPE, lang, title, meta tags)"""
    issues = []
    
    # Check DOCTYPE
    if not re.search(r'<!DOCTYPE\s+html', content, re.IGNORECASE):
        issues.append("Missing DOCTYPE")
    
    # Check lang attribute
    if not re.search(r'<html[^>]*lang\s*=', content, re.IGNORECASE):
        issues.append("Missing lang attribute on <html>")
    
    # Check title
    if not re.search(r'<title[^>]*>', content, re.IGNORECASE):
        issues.append("Missing <title> element")
    
    # Check viewport meta
    if not re.search(r'<meta[^>]*viewport', content, re.IGNORECASE):
        issues.append("Missing viewport meta tag")
    
    # Check charset
    if not re.search(r'<meta[^>]*charset', content, re.IGNORECASE):
        issues.append("Missing charset meta tag")
    
    return issues

def check_javascript_errors(content, page_name):
    """Check for JavaScript errors and issues"""
    issues = []
    
    # Check for url_for('home') - should be fixed
    if "url_for('home')" in content and page_name == "speed_round_setup":
        issues.append("Found url_for('home') - should use '/' or endpoint='home'")
    
    # Check for THREE.js loading
    three_js_patterns = [
        r'src=["\']https://cdnjs\.cloudflare\.com/ajax/libs/three\.js',
        r'src=["\']/static/js/vendor/three\.min\.js',
    ]
    has_three_js = any(re.search(pattern, content) for pattern in three_js_patterns)
    
    # Check for GLTFLoader
    gltf_loader_patterns = [
        r'src=["\'].*GLTFLoader\.js',
        r'GLTFLoader\.js',
    ]
    has_gltf_loader = any(re.search(pattern, content) for pattern in gltf_loader_patterns)
    
    # Check script loading order - GLTFLoader should come after Three.js
    three_js_index = content.find('three.min.js') if has_three_js else -1
    gltf_loader_index = content.find('GLTFLoader.js') if has_gltf_loader else -1
    
    if has_three_js and has_gltf_loader and three_js_index > gltf_loader_index:
        issues.append("GLTFLoader.js loads before three.min.js - wrong order")
    
    # Check for common JavaScript errors
    if "Uncaught ReferenceError" in content:
        issues.append("Potential JavaScript ReferenceError found")
    
    # Check for duplicate class declarations
    if content.count('class SmartyBee3D') > 1:
        issues.append("Duplicate SmartyBee3D class declaration")
    
    if content.count('class Badge3DRenderer') > 1:
        issues.append("Duplicate Badge3DRenderer class declaration")
    
    return issues

def test_quiz_page():
    """Test regular quiz page"""
    print_status("📝", "Testing regular quiz page")
    try:
        response = requests.get(f"{BASE_URL}/quiz", timeout=15)
        
        if response.status_code != 200:
            print_status("❌", "Quiz page", f"FAILED (status: {response.status_code})")
            return False
        
        content = response.text
        
        # Check HTML structure
        html_issues = check_html_structure(content, "quiz")
        if html_issues:
            print_status("⚠️", "Quiz HTML structure", f"Issues: {', '.join(html_issues)}")
        else:
            print_status("✅", "Quiz HTML structure", "OK")
        
        # Check JavaScript errors
        js_issues = check_javascript_errors(content, "quiz")
        if js_issues:
            print_status("⚠️", "Quiz JavaScript", f"Issues: {', '.join(js_issues)}")
        else:
            print_status("✅", "Quiz JavaScript", "OK")
        
        # Check for critical elements
        checks = {
            "Three.js": "three.min.js" in content or "three.js" in content,
            "GLTFLoader": "GLTFLoader.js" in content,
            "SmartyBee3D": "smarty-bee-3d.js" in content,
            "Quiz container": 'id="quiz-container"' in content or 'class="quiz-container"' in content,
        }
        
        missing = [k for k, v in checks.items() if not v]
        if missing:
            print_status("⚠️", "Quiz elements", f"Missing: {', '.join(missing)}")
        else:
            print_status("✅", "Quiz elements", "All present")
        
        # Quiz page is OK if HTML structure and JS are OK, even if some elements are missing
        all_ok = len(html_issues) == 0 and len(js_issues) == 0
        return all_ok
        
    except Exception as e:
        print_status("❌", "Quiz page", f"ERROR: {e}")
        return False

def test_speed_round_setup():
    """Test speed round setup page"""
    print_status("⚡", "Testing speed round setup page")
    try:
        response = requests.get(f"{BASE_URL}/speed-round/setup", timeout=15)
        
        if response.status_code != 200:
            print_status("❌", "Speed round setup", f"FAILED (status: {response.status_code})")
            if response.status_code == 500:
                print_status("⚠️", "Speed round setup", "Server error - check Flask logs")
            return False
        
        content = response.text
        
        # Check for error page (should not be the error page)
        if "Error Loading Speed Round Setup" in content:
            print_status("❌", "Speed round setup", "ERROR PAGE RETURNED")
            return False
        
        # Check HTML structure
        html_issues = check_html_structure(content, "speed_round_setup")
        if html_issues:
            print_status("⚠️", "Speed round setup HTML", f"Issues: {', '.join(html_issues)}")
        else:
            print_status("✅", "Speed round setup HTML", "OK")
        
        # Check JavaScript errors (especially url_for issues)
        js_issues = check_javascript_errors(content, "speed_round_setup")
        if js_issues:
            print_status("⚠️", "Speed round setup JavaScript", f"Issues: {', '.join(js_issues)}")
        else:
            print_status("✅", "Speed round setup JavaScript", "OK")
        
        # Check for critical elements
        checks = {
            "Speed Round Setup": "Speed Round Setup" in content or "speed-round" in content.lower(),
            "Back to Menu": "Back to Menu" in content or "Back to" in content,
            "Form": '<form' in content or 'id="speedRoundForm"' in content,
        }
        
        missing = [k for k, v in checks.items() if not v]
        if missing:
            print_status("⚠️", "Speed round setup elements", f"Missing: {', '.join(missing)}")
        else:
            print_status("✅", "Speed round setup elements", "All present")
        
        all_ok = len(html_issues) == 0 and len(js_issues) == 0 and len(missing) == 0
        return all_ok
        
    except Exception as e:
        print_status("❌", "Speed round setup", f"ERROR: {e}")
        return False

def test_speed_round_quiz():
    """Test speed round quiz page (may require setup first)"""
    print_status("⚡", "Testing speed round quiz page")
    try:
        response = requests.get(f"{BASE_URL}/speed-round/quiz", timeout=15)
        
        # Speed round quiz may redirect if not set up, which is OK
        if response.status_code in [200, 302, 307]:
            if response.status_code == 200:
                content = response.text
                
                # Check HTML structure
                html_issues = check_html_structure(content, "speed_round_quiz")
                if html_issues:
                    print_status("⚠️", "Speed round quiz HTML", f"Issues: {', '.join(html_issues)}")
                else:
                    print_status("✅", "Speed round quiz HTML", "OK")
                
                # Check JavaScript
                js_issues = check_javascript_errors(content, "speed_round_quiz")
                if js_issues:
                    print_status("⚠️", "Speed round quiz JavaScript", f"Issues: {', '.join(js_issues)}")
                else:
                    print_status("✅", "Speed round quiz JavaScript", "OK")
                
                all_ok = len(html_issues) == 0 and len(js_issues) == 0
                print_status("✅", "Speed round quiz", "OK (page loaded)" if all_ok else "PARTIAL")
                return all_ok
            else:
                print_status("✅", "Speed round quiz", f"OK (redirects to setup - status {response.status_code})")
                return True
        else:
            print_status("❌", "Speed round quiz", f"FAILED (status: {response.status_code})")
            return False
        
    except Exception as e:
        print_status("❌", "Speed round quiz", f"ERROR: {e}")
        return False

def test_health():
    """Test health endpoint"""
    print_status("🏥", "Testing health endpoint")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print_status("✅", "Health check", "OK")
            return True
        else:
            print_status("❌", "Health check", f"FAILED (status: {response.status_code})")
            return False
    except Exception as e:
        print_status("❌", "Health check", f"ERROR: {e}")
        return False

def main():
    print("="*70)
    print("🐝 BeeSmart Quiz & Speed Round Smoke Test")
    print(f"🌐 Testing: {BASE_URL}")
    print("="*70)
    print()
    
    results = {}
    
    # Run all tests
    results['health'] = test_health()
    time.sleep(0.5)
    
    results['quiz'] = test_quiz_page()
    time.sleep(0.5)
    
    results['speed_setup'] = test_speed_round_setup()
    time.sleep(0.5)
    
    results['speed_quiz'] = test_speed_round_quiz()
    
    # Summary
    print()
    print("="*70)
    print("📊 SMOKE TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} - {test_name.upper()}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED!")
        return 0
    else:
        print(f"⚠️ {total - passed} TEST(S) FAILED")
        return 1

if __name__ == "__main__":
    exit(main())
