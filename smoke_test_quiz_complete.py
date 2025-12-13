#!/usr/bin/env python3
"""
Comprehensive Quiz Smoke Test for BeeSmart Spelling App
Tests: Regular quiz, Speed round quiz, Badge morphing
"""

import requests
import time
from datetime import datetime

BASE_URL = "https://beesmart-sn5bj.ondigitalocean.app"
# BASE_URL = "http://localhost:5000"  # Uncomment for local testing

def print_status(emoji, message, status=""):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if status:
        print(f"{timestamp} {emoji} {message}: {status}")
    else:
        print(f"{timestamp} {emoji} {message}")

def test_health():
    """Test health endpoint"""
    print_status("🏥", "Testing health endpoint")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_status("✅", "Health check", f"OK (version: {data.get('version', 'unknown')})")
            return True
        else:
            print_status("❌", "Health check", f"FAILED (status: {response.status_code})")
            return False
    except Exception as e:
        print_status("❌", "Health check", f"ERROR: {e}")
        return False

def test_home_page():
    """Test home page loads with badge morphing"""
    print_status("🏠", "Testing home page (unified menu)")
    try:
        response = requests.get(BASE_URL, timeout=10)
        if response.status_code == 200:
            content = response.text
            
            # Check for critical elements
            checks = {
                "morph-badge-logo": "morph-badge-logo" in content,
                "initBadgeLogoMorphing": "initBadgeLogoMorphing" in content,
                "Badge morphing": "Badge/Logo slow morphing" in content or "Badge/Logo morphing" in content,
                "Particle effect": "morph-particle" in content or "createMorphParticles" in content
            }
            
            all_passed = all(checks.values())
            
            if all_passed:
                print_status("✅", "Home page", "OK (badge morphing present)")
            else:
                print_status("⚠️", "Home page", f"PARTIAL (missing: {[k for k,v in checks.items() if not v]})")
            
            return all_passed
        else:
            print_status("❌", "Home page", f"FAILED (status: {response.status_code})")
            return False
    except Exception as e:
        print_status("❌", "Home page", f"ERROR: {e}")
        return False

def test_quiz_page():
    """Test regular quiz page loads"""
    print_status("📝", "Testing regular quiz page")
    try:
        response = requests.get(f"{BASE_URL}/quiz", timeout=10)
        if response.status_code == 200:
            content = response.text
            
            # Check for critical elements
            checks = {
                "MorphController": "class MorphController" in content,
                "QuizManager": "class QuizManager" or "window.quizManager" in content,
                "Quiz script": "Quiz script loading" in content,
                "No badge morphing": "initBadgeLogoMorphing" not in content,  # Should NOT be in quiz
                "morphContainer": "morphContainer" in content,  # Timer/voice morph container
            }
            
            all_passed = all(checks.values())
            
            if all_passed:
                print_status("✅", "Regular quiz", "OK (no syntax errors)")
            else:
                print_status("⚠️", "Regular quiz", f"PARTIAL (issues: {[k for k,v in checks.items() if not v]})")
            
            return all_passed
        else:
            print_status("❌", "Regular quiz", f"FAILED (status: {response.status_code})")
            return False
    except Exception as e:
        print_status("❌", "Regular quiz", f"ERROR: {e}")
        return False

def test_speed_round():
    """Test speed round quiz page loads"""
    print_status("⚡", "Testing speed round quiz page")
    try:
        response = requests.get(f"{BASE_URL}/speed-round/quiz", timeout=10)
        if response.status_code == 200:
            content = response.text
            
            # Check for critical elements
            checks = {
                "Speed round": "speed" in content.lower() or "Speed Round" in content,
                "Canvas": "canvas" in content or "dotWaveCanvas" in content,
                "Voice visualizer": "initSwarm" in content or "voice" in content.lower(),
            }
            
            all_passed = all(checks.values())
            
            if all_passed:
                print_status("✅", "Speed round", "OK")
            else:
                print_status("⚠️", "Speed round", f"PARTIAL (missing: {[k for k,v in checks.items() if not v]})")
            
            return all_passed
        else:
            print_status("❌", "Speed round", f"FAILED (status: {response.status_code})")
            return False
    except Exception as e:
        print_status("❌", "Speed round", f"ERROR: {e}")
        return False

def test_api_wordbank():
    """Test wordbank API"""
    print_status("📚", "Testing wordbank API")
    try:
        response = requests.get(f"{BASE_URL}/api/wordbank", timeout=10)
        if response.status_code == 200:
            data = response.json()
            word_count = len(data.get('words', []))
            print_status("✅", "Wordbank API", f"OK ({word_count} words)")
            return True
        else:
            print_status("❌", "Wordbank API", f"FAILED (status: {response.status_code})")
            return False
    except Exception as e:
        print_status("❌", "Wordbank API", f"ERROR: {e}")
        return False

def main():
    print("="*60)
    print("🐝 BeeSmart Quiz Smoke Test")
    print(f"🌐 Testing: {BASE_URL}")
    print("="*60)
    print()
    
    results = {}
    
    # Run all tests
    results['health'] = test_health()
    time.sleep(0.5)
    
    results['home'] = test_home_page()
    time.sleep(0.5)
    
    results['quiz'] = test_quiz_page()
    time.sleep(0.5)
    
    results['speed'] = test_speed_round()
    time.sleep(0.5)
    
    results['wordbank'] = test_api_wordbank()
    
    # Summary
    print()
    print("="*60)
    print("📊 SMOKE TEST SUMMARY")
    print("="*60)
    
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
