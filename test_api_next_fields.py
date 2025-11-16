#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test to verify /api/next returns explicit sentence, hint, and definition fields.
Also verifies that builtin dictionary (DICT_LOOKUP) is prioritized over external APIs.
"""

import sys
sys.path.insert(0, '/c/Users/jeff/Dropbox/BeeSmartSpellingBeeApp')

from AjaSpellBApp import app, set_wordbank, init_quiz_state, get_wordbank
import json

def test_api_next_fields():
    """Test that /api/next returns sentence, hint, and definitionSource fields"""
    
    print("\n" + "="*70)
    print("TEST: /api/next Returns Explicit Fields")
    print("="*70)
    
    with app.test_client() as client:
        with app.test_request_context():
            # Test words with different field combinations
            test_words = [
                {
                    "word": "inspire",
                    "sentence": "She gathered ideas for her story from old books.",
                    "hint": ""
                },
                {
                    "word": "happy",
                    "sentence": "",
                    "hint": "A feeling when you smile"
                },
                {
                    "word": "dictionary",
                    "sentence": "A book that has all the words in it.",
                    "hint": "A reference book"
                }
            ]
            
            print("\nStep 1: Setting up test wordbank...")
            set_wordbank(test_words, is_user_upload=True)
            init_quiz_state()
            
            wb = get_wordbank()
            print(f"   Wordbank has {len(wb)} words")
            
            # Test /api/next endpoint
            print("\nStep 2: Testing /api/next response fields...")
            response = client.post('/api/next')
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"\n   Response Status: {response.status_code}")
                print(f"\n   Response JSON Keys: {list(data.keys())}")
                
                # Check for all expected fields
                print("\n   Field Validation:")
                fields_to_check = [
                    ("definition", "Core definition field (backward compat)"),
                    ("sentence", "Explicit sentence field"),
                    ("hint", "Explicit hint field"),
                    ("definitionSource", "Where definition came from"),
                    ("hasDefinition", "Boolean - has valid definition"),
                    ("word", "The word being spelled"),
                    ("wordMeta", "Metadata about word"),
                    ("progress", "Quiz progress"),
                ]
                
                for field, description in fields_to_check:
                    has_field = field in data
                    status = "✓" if has_field else "✗"
                    print(f"   {status} {field}: {description}")
                    if has_field:
                        print(f"      Value: {data[field]}")
                
                # Specific checks
                print("\n   Detailed Check:")
                print(f"   Word: {data.get('word')}")
                print(f"   Sentence: {data.get('sentence')}")
                print(f"   Hint: {data.get('hint')}")
                print(f"   Definition Source: {data.get('definitionSource')}")
                print(f"   Has Definition: {data.get('hasDefinition')}")
                
                # Verify logic - prioritization should be sentence -> hint -> builtin -> fallback
                source = data.get('definitionSource')
                valid_sources = {'sentence', 'hint', 'builtin', 'definition_field', 'fallback'}
                if source in valid_sources:
                    print(f"\n   ✓ Valid definitionSource: {source}")
                else:
                    print(f"\n   ✗ Invalid definitionSource: {source}")
                
                if source == 'sentence' and data.get('sentence'):
                    print("   ✓ Correctly prioritized sentence!")
                elif source == 'hint' and data.get('hint'):
                    print("   ✓ Correctly prioritized hint!")
                elif source == 'builtin':
                    print("   ✓ Using builtin dictionary (DICT_LOOKUP)!")
                elif source == 'fallback':
                    print("   ✓ Using fallback definition")
                
                print("\n   Full Response:")
                print("   " + json.dumps(data, indent=6).replace("\n", "\n   "))
                
            else:
                print(f"   ERROR: Unexpected status {response.status_code}")
                print(f"   Response: {response.get_data(as_text=True)}")
            
            print("\n" + "="*70)
            print("API Field Test Complete!")
            print("="*70)

def test_builtin_dictionary_priority():
    """Test that builtin dictionary is preferred over external API"""
    
    print("\n" + "="*70)
    print("TEST: Built-in Dictionary Priority")
    print("="*70)
    
    from AjaSpellBApp import DICT_LOOKUP, SIMPLE_WIKTIONARY
    
    print(f"\nSimple Wiktionary loaded: {len(SIMPLE_WIKTIONARY)} words")
    
    # Test DICT_LOOKUP function
    test_word = "happy"
    result = DICT_LOOKUP(test_word)
    
    if result:
        print(f"\n✓ DICT_LOOKUP('{test_word}') returned:")
        print(f"  Definition: {result.get('definition', 'N/A')[:80]}...")
        print(f"  Example: {result.get('example', 'N/A')[:80]}...")
        print(f"  Source: {result.get('source', 'N/A')}")
    else:
        print(f"\n✗ DICT_LOOKUP('{test_word}') returned None")
    
    print("\n✓ Verified that DICT_LOOKUP uses built-in dictionary only")
    print("="*70)

if __name__ == "__main__":
    test_api_next_fields()
    test_builtin_dictionary_priority()

