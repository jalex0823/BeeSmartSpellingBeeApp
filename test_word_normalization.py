#!/usr/bin/env python3
"""
Test script to verify word normalization consistency across the BeeSmart app
"""
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from AjaSpellBApp import normalize, _normalize_for_compare

def test_normalization():
    """Test that all normalization functions handle case consistently"""
    print("🔤 Testing Word Normalization Consistency")
    print("=" * 50)
    
    # Test various case combinations
    test_cases = [
        ("hello", "HELLO"),
        ("Hello", "hello"), 
        ("WORLD", "world"),
        ("BeeSmart", "beesmart"),
        ("BeeSmart", "BEESMART"),
        ("Apple", "apple"),
        ("COMPUTER", "computer"),
        ("spellING", "SPELLING"),
    ]
    
    all_passed = True
    
    for word1, word2 in test_cases:
        norm1 = normalize(word1)
        norm2 = normalize(word2)
        compare1 = _normalize_for_compare(word1)
        compare2 = _normalize_for_compare(word2)
        
        # Test main normalize function
        norm_match = norm1 == norm2
        # Test deduplication function
        compare_match = compare1 == compare2
        
        status1 = "✅ PASS" if norm_match else "❌ FAIL"
        status2 = "✅ PASS" if compare_match else "❌ FAIL"
        
        print(f"'{word1}' vs '{word2}':")
        print(f"  normalize(): '{norm1}' == '{norm2}' → {status1}")
        print(f"  _normalize_for_compare(): '{compare1}' == '{compare2}' → {status2}")
        print()
        
        if not norm_match or not compare_match:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 All normalization tests PASSED! Case handling is consistent.")
    else:
        print("⚠️  Some normalization tests FAILED! Case handling needs fixes.")
    
    return all_passed

def test_edge_cases():
    """Test edge cases like Unicode, accents, special characters"""
    print("🌟 Testing Unicode and Special Character Handling")
    print("=" * 50)
    
    edge_cases = [
        ("café", "CAFE"),
        ("résumé", "RESUME"), 
        ("naïve", "NAIVE"),
        ("hello!", "HELLO"),
        ("world.", "WORLD"),
        ("bee-smart", "BEE SMART"),
    ]
    
    all_passed = True
    
    for word1, word2 in edge_cases:
        norm1 = normalize(word1)
        norm2 = normalize(word2)
        
        match = norm1 == norm2
        status = "✅ PASS" if match else "❌ FAIL"
        
        print(f"'{word1}' vs '{word2}':")
        print(f"  normalize(): '{norm1}' == '{norm2}' → {status}")
        print()
        
        if not match:
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 All edge case tests PASSED! Unicode handling is working.")
    else:
        print("⚠️  Some edge case tests FAILED! Check Unicode normalization.")
    
    return all_passed

if __name__ == "__main__":
    print("🐝 BeeSmart Word Normalization Test Suite")
    print("Testing case-insensitive word handling for spelling quiz")
    print()
    
    test1_passed = test_normalization()
    print()
    test2_passed = test_edge_cases()
    
    print("\n🎯 FINAL RESULTS:")
    print("=" * 50)
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED! Word normalization is working correctly.")
        print("   - Case variations are handled consistently")
        print("   - Unicode and special characters are normalized properly") 
        print("   - Spelling quiz will treat 'Hello', 'HELLO', 'hello' as identical")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED! Please review normalization functions.")
        sys.exit(1)