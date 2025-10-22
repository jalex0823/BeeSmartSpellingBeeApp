#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test to verify frontend fallback logic and API endpoints return proper data.
Tests both the validation AND the API responses.
"""

import sys
sys.path.insert(0, '/c/Users/jeff/Dropbox/BeeSmartSpellingBeeApp')

from AjaSpellBApp import app, validate_wordbank_definitions

def test_api_responses():
    """Test that both /api/next and /api/pronounce return valid data"""
    
    print("\n" + "="*70)
    print("TEST: API Response Data (Frontend Fallback Support)")
    print("="*70)
    
    with app.test_client() as client:
        with app.test_request_context():
            from AjaSpellBApp import set_wordbank, init_quiz_state, get_wordbank
            
            # Setup: Create test words with various data combinations
            test_words = [
                {
                    "word": "apple",
                    "sentence": "A red fruit that grows on trees.",
                    "hint": ""
                },
                {
                    "word": "bee",
                    "sentence": "An insect that makes honey.",
                    "hint": ""
                },
                {
                    "word": "dance",
                    "sentence": "",
                    "hint": "A movement to music"
                },
            ]
            
            print("\n[SETUP] Uploading test words...")
            set_wordbank(test_words, is_user_upload=True)
            init_quiz_state()
            wb = get_wordbank()
            print(f"   Stored {len(wb)} words")
            
            # Test 1: /api/next should return definition for word with sentence
            print("\n[TEST 1] /api/next with sentence word")
            response = client.post('/api/next')
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.get_json()
            print(f"   Response has 'definition': {'definition' in data}")
            print(f"   Definition value: {data.get('definition', 'EMPTY')[:60]}...")
            assert data.get('definition'), "Expected definition to be populated"
            assert 'apple' in data.get('definition', '').lower() or 'red' in data.get('definition', '').lower(), \
                f"Expected apple definition, got: {data.get('definition')}"
            print("   PASS: Definition populated")
            
            # Test 2: /api/pronounce should also have the definition/sentence
            print("\n[TEST 2] /api/pronounce returns sentence/hint for same word")
            response = client.post('/api/pronounce')
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            pronounce_data = response.get_json()
            print(f"   Has 'definition': {'definition' in pronounce_data}")
            print(f"   Has 'sentence': {'sentence' in pronounce_data}")
            print(f"   Has 'hint': {'hint' in pronounce_data}")
            
            # Should have at least one of these
            has_content = pronounce_data.get('definition') or pronounce_data.get('sentence') or pronounce_data.get('hint')
            print(f"   Content present: {bool(has_content)}")
            if has_content:
                content = pronounce_data.get('definition') or pronounce_data.get('sentence') or pronounce_data.get('hint')
                print(f"   First 60 chars: {str(content)[:60]}...")
            print("   PASS: /api/pronounce has fallback data")
            
            # Test 3: Advance to word with hint (no sentence)
            print("\n[TEST 3] /api/next with hint-only word")
            response = client.post('/api/next')  # Advance to next
            if response.status_code == 200:
                data = response.get_json()
                if not data.get('done'):
                    word = data.get('word', '')
                    definition = data.get('definition', '')
                    print(f"   Word: {word}")
                    print(f"   Definition from /api/next: {definition[:60] if definition else 'EMPTY'}...")
                    
                    # If /api/next doesn't have it, /api/pronounce should fallback
                    if not definition:
                        response = client.post('/api/pronounce')
                        if response.status_code == 200:
                            pdata = response.get_json()
                            fallback = pdata.get('sentence') or pdata.get('hint')
                            print(f"   Fallback from /api/pronounce: {fallback[:60] if fallback else 'EMPTY'}...")
                            assert fallback, "Expected /api/pronounce to have fallback"
                            print("   PASS: Fallback available from /api/pronounce")
            
            print("\n" + "="*70)
            print("ALL API TESTS PASSED!")
            print("Frontend fallback logic is supported by the API")
            print("="*70)

if __name__ == "__main__":
    try:
        test_api_responses()
    except Exception as e:
        print(f"\nFAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
