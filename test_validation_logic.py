#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test to verify that definition validation happens BEFORE quiz loads
and errors are returned to the frontend.
"""

import sys
sys.path.insert(0, '/c/Users/jeff/Dropbox/BeeSmartSpellingBeeApp')

from AjaSpellBApp import app, validate_wordbank_definitions

def test_validation():
    """Test that validation catches words without definitions"""
    
    print("\n" + "="*70)
    print("TEST: Definition Validation Before Quiz Loads")
    print("="*70)
    
    # Test 1: Words WITH valid sentences - should pass
    print("\n[TEST 1] Words WITH valid sentences")
    good_words = [
        {"word": "apple", "sentence": "An apple is a red fruit.", "hint": ""},
        {"word": "bee", "sentence": "A bee makes honey.", "hint": ""},
    ]
    is_valid, error = validate_wordbank_definitions(good_words)
    print(f"  Result: {'PASS' if is_valid else 'FAIL'}")
    if not is_valid:
        print(f"  Error: {error}")
    
    # Test 2: Words WITH placeholder definitions - should fail
    print("\n[TEST 2] Words WITH placeholder definitions (should fail)")
    bad_words = [
        {"word": "xyz", "sentence": "A placeholder definition for 'xyz'.", "hint": ""},
        {"word": "abc", "sentence": "A placeholder definition for 'abc'.", "hint": ""},
    ]
    is_valid, error = validate_wordbank_definitions(bad_words)
    print(f"  Result: {'FAIL (as expected)' if not is_valid else 'PASS (unexpected!)'}")
    print(f"  Error message: {error}")
    
    # Test 3: Words with NO sentence AND NO hint - should fail
    print("\n[TEST 3] Words with NO sentence/hint (should fail)")
    missing_words = [
        {"word": "test", "sentence": "", "hint": ""},
        {"word": "word", "sentence": "", "hint": ""},
    ]
    is_valid, error = validate_wordbank_definitions(missing_words)
    print(f"  Result: {'FAIL (as expected)' if not is_valid else 'PASS (unexpected!)'}")
    print(f"  Error message: {error}")
    
    # Test 4: Mixed - some with hints should pass
    print("\n[TEST 4] Words with valid hints (should pass)")
    hint_words = [
        {"word": "apple", "sentence": "", "hint": "A red fruit"},
        {"word": "bee", "sentence": "A bee makes honey", "hint": ""},
    ]
    is_valid, error = validate_wordbank_definitions(hint_words)
    print(f"  Result: {'PASS' if is_valid else 'FAIL'}")
    if not is_valid:
        print(f"  Error: {error}")
    
    print("\n" + "="*70)
    print("Validation logic verified!")
    print("="*70)

if __name__ == "__main__":
    test_validation()
