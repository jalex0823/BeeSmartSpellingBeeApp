#!/usr/bin/env python3
"""
Quick API test script for BeeSmart enhanced features
"""
import requests
import json
import time

API_BASE = "http://localhost:5000"

def test_word_of_day():
    """Test the word of the day API endpoint"""
    print("🌟 Testing Word of the Day API...")
    try:
        response = requests.get(f"{API_BASE}/api/word-of-day", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Word of the Day: {data}")
            return True
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_health_endpoint():
    """Test the health check endpoint"""
    print("🏥 Testing Health Endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data}")
            return True
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_main_page():
    """Test the main page loads"""
    print("🏠 Testing Main Page...")
    try:
        response = requests.get(API_BASE, timeout=5)
        if response.status_code == 200:
            print(f"✅ Main page loads (Content length: {len(response.text)} chars)")
            return True
        else:
            print(f"❌ HTTP {response.status_code}: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def main():
    """Run all tests"""
    print("🐝 BeeSmart Enhanced Features API Testing")
    print("=" * 50)
    
    tests = [
        test_health_endpoint,
        test_main_page,
        test_word_of_day
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
            print()
            time.sleep(0.5)  # Brief pause between tests
        except Exception as e:
            print(f"❌ Test '{test_func.__name__}' failed with error: {e}")
            results.append(False)
            print()
    
    print("=" * 50)
    print(f"📊 Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("🎉 All tests passed! The BeeSmart enhanced features are working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()