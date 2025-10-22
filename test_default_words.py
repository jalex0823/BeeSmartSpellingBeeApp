#!/usr/bin/env python3
"""
Test script to verify default word loading functionality
"""

import requests
import json

def test_default_words():
    print("🧪 Testing default word loading functionality...")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    try:
        # First, access the main menu to establish session
        print("📝 Accessing main menu...")
        response = session.get("http://localhost:5000/")
        if response.status_code != 200:
            print(f"❌ Failed to access main menu: {response.status_code}")
            return False
        print("✅ Main menu accessed successfully")
        
        # Now try to access quiz page to trigger word loading
        print("📝 Accessing quiz page...")
        response = session.get("http://localhost:5000/quiz")
        if response.status_code != 200:
            print(f"❌ Failed to access quiz page: {response.status_code}")
            return False
        print("✅ Quiz page accessed successfully")
        
        # Check if we can get the next word (this will trigger default word loading)
        print("📝 Testing API next word endpoint...")
        response = session.post("http://localhost:5000/api/next")
        if response.status_code != 200:
            print(f"❌ Failed to get next word: {response.status_code}")
            return False
        
        data = response.json()
        print(f"📊 API Next Response: {json.dumps(data, indent=2)}")
        
        if data.get("total", 0) > 0:
            print(f"✅ Quiz initialized with {data['total']} words!")
            
            # Now get the word details via pronounce endpoint
            print("📝 Testing API pronounce endpoint...")
            response = session.post("http://localhost:5000/api/pronounce")
            if response.status_code != 200:
                print(f"❌ Failed to get word details: {response.status_code}")
                return False
            
            word_data = response.json()
            print(f"📊 API Pronounce Response: {json.dumps(word_data, indent=2)}")
            
            if word_data.get("word"):
                print(f"✅ SUCCESS! Default words loaded. First word: '{word_data['word']}'")
                print(f"📖 Definition: {word_data.get('definition', 'N/A')}")
                return True
            else:
                print("❌ No word returned from pronounce API")
                return False
        else:
            print("❌ No words loaded in quiz")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_default_words()
    if success:
        print("\n🎉 Default word loading is working correctly!")
    else:
        print("\n💥 Default word loading test failed!")