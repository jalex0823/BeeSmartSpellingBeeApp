#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test to verify definition/sentence is properly returned for words with definitions.
Simplified test without emoji to avoid encoding issues.
"""

import sys
sys.path.insert(0, '/c/Users/jeff/Dropbox/BeeSmartSpellingBeeApp')

from AjaSpellBApp import app, get_wordbank, set_wordbank, init_quiz_state, WORD_STORAGE
import json

def test_definition_for_words():
    """Test that /api/next returns proper definitions/sentences for words"""
    
    print("\n" + "="*60)
    print("TEST: Definition/Sentence Verification")
    print("="*60)
    
    with app.test_client() as client:
        with app.test_request_context():
            # Create test word data with various combinations
            test_words = [
                {
                    "word": "apple",
                    "sentence": "A red fruit that grows on trees and is good for you.",
                    "hint": ""
                },
                {
                    "word": "bee",
                    "sentence": "An insect that makes honey and flies from flower to flower.",
                    "hint": ""
                },
                {
                    "word": "happy",
                    "sentence": "",  # No sentence provided
                    "hint": "A feeling when you smile"  # Will use hint instead
                },
                {
                    "word": "dance",
                    "sentence": "",
                    "hint": ""  # Will get definition from API/fallback
                }
            ]
            
            # Clear and upload test words
            print("\nStep 1: Uploading test words...")
            set_wordbank(test_words, is_user_upload=True)
            init_quiz_state()
            
            wb = get_wordbank()
            print(f"   Wordbank now has {len(wb)} words")
            
            # Test /api/next endpoint
            print("\nStep 2: Testing /api/next endpoint...")
            response = client.post('/api/next')
            print(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"\n   First word response:")
                print(f"   - Word: {data.get('word')}")
                print(f"   - Definition: {data.get('definition')[:80]}...")
                print(f"   - Has sentence: {data.get('wordMeta', {}).get('hasSentence')}")
                print(f"   - Has hint: {data.get('wordMeta', {}).get('hasHint')}")
                
                # Verify it's not a placeholder
                definition = data.get('definition', '')
                if 'placeholder' in definition.lower():
                    print(f"\n   ERROR: Still showing placeholder definition!")
                    print(f"   Full definition: {definition}")
                    return False
                else:
                    print(f"\n   SUCCESS: Proper definition returned!")
            else:
                print(f"   ERROR: Unexpected status code {response.status_code}")
                print(f"   Response: {response.get_data(as_text=True)}")
                return False
            
            # Move to next word to test hint field
            print("\nStep 3: Testing word with hint (no sentence)...")
            response = client.post('/api/next')
            if response.status_code == 200:
                data = response.get_json()
                print(f"   Word: {data.get('word')}")
                print(f"   Definition: {data.get('definition')[:80]}...")
                
                definition = data.get('definition', '')
                if definition and 'placeholder' not in definition.lower():
                    print(f"   SUCCESS: Hint/definition working!")
                else:
                    print(f"   ERROR: Invalid definition")
                    return False
            
            # Test word with no sentence or hint (should use fallback)
            print("\nStep 4: Testing word with API fallback...")
            response = client.post('/api/next')
            if response.status_code == 200:
                data = response.get_json()
                print(f"   Word: {data.get('word')}")
                definition = data.get('definition', '')
                print(f"   Definition: {definition[:80]}...")
                
                if definition and 'placeholder' not in definition.lower():
                    print(f"   SUCCESS: Fallback definition working!")
                else:
                    print(f"   ERROR: Invalid fallback")
                    return False
            
            print("\n" + "="*60)
            print("ALL TESTS PASSED!")
            print("="*60)
            return True

if __name__ == "__main__":
    try:
        success = test_definition_for_words()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nEXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
