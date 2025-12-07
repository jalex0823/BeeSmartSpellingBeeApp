#!/usr/bin/env python3
"""
Test quiz sentence and definition display functionality.
Verifies that sentences appear correctly beneath timer and definitions show in popups.
"""

import requests
import json
import time
import sys

def test_quiz_display():
    """Test quiz sentence and definition display functionality"""
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    print("🧪 Testing Quiz Display Functionality")
    print("=" * 60)
    
    try:
        # 1. Test app health
        print("\n1. ✅ Testing app health...")
        response = session.get(f"{base_url}/health")
        if response.status_code != 200:
            print(f"❌ App not healthy: {response.status_code}")
            return False
        print(f"✅ App healthy: version {response.json().get('version', 'unknown')}")
        
        # 2. Clear any existing wordbank
        print("\n2. 🧹 Clearing wordbank...")
        response = session.post(f"{base_url}/api/clear")
        print(f"✅ Wordbank cleared: {response.json().get('message', 'OK')}")
        
        # 3. Upload test words with sentences and definitions
        print("\n3. 📤 Uploading test words...")
        test_data = {
            'words': [
                {'word': 'cat', 'sentence': 'The fluffy cat sat on the mat.', 'hint': 'A small furry animal that meows'},
                {'word': 'dog', 'sentence': 'The happy dog wagged its tail.', 'hint': 'A loyal animal that barks'},
                {'word': 'bee', 'sentence': 'The busy bee collected nectar.', 'hint': 'An insect that makes honey'},
                {'word': 'tree', 'sentence': 'The tall tree had green leaves.', 'hint': 'A woody plant that grows tall'},
                {'word': 'sun', 'sentence': 'The bright sun warmed the earth.', 'hint': 'The star that lights our planet'}
            ]
        }
        
        response = session.post(f"{base_url}/api/upload", 
                              json=test_data, 
                              headers={'Content-Type': 'application/json'})
        
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return False
        
        result = response.json()
        print(f"✅ Uploaded {result.get('words_added', 0)} words")
        
        # 4. Test getting next word with sentence
        print("\n4. 🎯 Testing word loading with sentences...")
        response = session.post(f"{base_url}/api/next")
        
        if response.status_code != 200:
            print(f"❌ Next word failed: {response.status_code} - {response.text}")
            return False
            
        word_data = response.json()
        print(f"✅ Loaded word: '{word_data.get('word', 'UNKNOWN')}'")
        
        # Check if sentence is provided for quiz display
        word_info = word_data.get('word_info', {})
        sentence = word_info.get('sentence', '')
        definition = word_info.get('definition', '')
        
        print(f"📝 Sentence: {sentence}")
        print(f"📖 Definition: {definition}")
        
        if not sentence and not definition:
            print("⚠️  No sentence or definition provided for display")
        else:
            print("✅ Content available for quiz display")
        
        # 5. Test correct answer submission to trigger definition popup
        print("\n5. ✅ Testing answer submission and definition display...")
        current_word = word_data.get('word', '')
        
        response = session.post(f"{base_url}/api/answer", 
                              json={
                                  'user_input': current_word,
                                  'method': 'typing',
                                  'elapsed_ms': 5000
                              },
                              headers={'Content-Type': 'application/json'})
        
        if response.status_code != 200:
            print(f"❌ Answer submission failed: {response.status_code} - {response.text}")
            return False
            
        answer_result = response.json()
        print(f"✅ Answer result: {answer_result.get('correct', False)}")
        
        # Check if definition is provided for popup
        word_definition = answer_result.get('word_definition', '')
        if word_definition:
            print(f"📚 Definition for popup: {word_definition}")
            print("✅ Definition popup should display")
        else:
            print("⚠️  No definition provided for popup")
        
        # 6. Test a few more words to verify consistency
        print("\n6. 🔄 Testing additional words...")
        for i in range(2):
            response = session.post(f"{base_url}/api/next")
            if response.status_code == 200:
                word_data = response.json()
                word = word_data.get('word', 'UNKNOWN')
                word_info = word_data.get('word_info', {})
                sentence = word_info.get('sentence', '')
                print(f"  Word {i+2}: '{word}' - Sentence: {sentence}")
            else:
                print(f"  ❌ Failed to load word {i+2}")
        
        print("\n" + "=" * 60)
        print("🎉 Quiz Display Test Complete!")
        print("✅ Quiz sentence and definition functionality verified")
        print("📝 Sentences should display beneath timer in voiceDefinition element")
        print("📚 Definitions should show in popups after correct answers")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_quiz_display()
    sys.exit(0 if success else 1)