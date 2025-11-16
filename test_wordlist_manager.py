#!/usr/bin/env python3
"""
Test Word List Manager functionality
Verifies that the word list manager correctly initializes and manages word lists
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_quiz_template_includes_wordlist_manager():
    """Verify that quiz.html includes the word list manager script and data anchor"""
    print("🧪 Testing quiz template includes word list manager...")
    
    with open('templates/quiz.html', 'r') as f:
        content = f.read()
    
    # Check for data anchor
    assert 'id="quiz-root"' in content, "❌ Missing quiz-root data anchor"
    assert 'data-selected-list-id' in content, "❌ Missing data-selected-list-id attribute"
    assert 'data-selected-list-name' in content, "❌ Missing data-selected-list-name attribute"
    assert 'data-words-url' in content, "❌ Missing data-words-url attribute"
    
    # Check for refresh button
    assert 'id="refreshWordListBtn"' in content, "❌ Missing refresh button"
    
    # Check for script include
    assert 'quiz-wordlist.js' in content, "❌ Missing quiz-wordlist.js script include"
    
    # Check for initialization code
    assert 'wordListManager.ensureUsingSelectedList' in content, "❌ Missing initialization code"
    
    print("✅ Quiz template correctly includes word list manager")
    return True

def test_wordlist_js_exists():
    """Verify that the quiz-wordlist.js file exists and has expected content"""
    print("🧪 Testing quiz-wordlist.js exists and has expected content...")
    
    filepath = 'static/js/quiz-wordlist.js'
    assert os.path.exists(filepath), f"❌ File {filepath} does not exist"
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check for key classes and functions
    assert 'class WordListManager' in content, "❌ Missing WordListManager class"
    assert 'getCurrentWordList' in content, "❌ Missing getCurrentWordList function"
    assert 'clearActiveWordList' in content, "❌ Missing clearActiveWordList function"
    assert 'ensureUsingSelectedList' in content, "❌ Missing ensureUsingSelectedList method"
    assert 'wordlist:changed' in content, "❌ Missing wordlist:changed event dispatch"
    
    # Check for backward-compatible globals
    assert 'window.QUIZ_WORDS' in content, "❌ Missing QUIZ_WORDS global update"
    assert 'window.QUIZ_CURRENT_INDEX' in content, "❌ Missing QUIZ_CURRENT_INDEX global update"
    assert 'window.QUIZ_ACTIVE_LIST_ID' in content, "❌ Missing QUIZ_ACTIVE_LIST_ID global update"
    
    # Check for localStorage persistence
    assert 'localStorage.setItem' in content, "❌ Missing localStorage persistence"
    assert 'localStorage.getItem' in content, "❌ Missing localStorage retrieval"
    
    print("✅ quiz-wordlist.js has all expected content")
    return True

def test_flask_route_passes_selected_list():
    """Verify that the Flask quiz route passes selected_list to template"""
    print("🧪 Testing Flask route passes selected_list...")
    
    with open('AjaSpellBApp.py', 'r') as f:
        content = f.read()
    
    # Find the quiz_page function
    assert 'def quiz_page():' in content, "❌ Missing quiz_page function"
    
    # Check that selected_list is created and passed to template
    assert 'selected_list = {' in content, "❌ Missing selected_list creation"
    assert 'selected_list=selected_list' in content, "❌ Missing selected_list in render_template"
    
    # Check for active_list_id and active_list_name in session
    assert 'active_list_id' in content, "❌ Missing active_list_id handling"
    assert 'active_list_name' in content, "❌ Missing active_list_name handling"
    
    print("✅ Flask route correctly passes selected_list")
    return True

def test_saved_lists_load_sets_active_list():
    """Verify that loading a saved list sets active_list_id and active_list_name"""
    print("🧪 Testing saved lists load sets active list metadata...")
    
    with open('AjaSpellBApp.py', 'r') as f:
        content = f.read()
    
    # Find the load_saved_wordlist function
    assert 'def load_saved_wordlist():' in content, "❌ Missing load_saved_wordlist function"
    
    # Check that it sets active_list_id and active_list_name
    assert 'session["active_list_id"]' in content, "❌ Missing active_list_id setting in load"
    assert 'session["active_list_name"]' in content, "❌ Missing active_list_name setting in load"
    
    print("✅ Saved lists load correctly sets active list metadata")
    return True

def test_clear_api_clears_active_list():
    """Verify that /api/clear clears active list metadata"""
    print("🧪 Testing /api/clear clears active list metadata...")
    
    with open('AjaSpellBApp.py', 'r') as f:
        content = f.read()
    
    # Find the api_clear function
    assert 'def api_clear():' in content, "❌ Missing api_clear function"
    
    # Check that it pops active_list_id and active_list_name
    assert 'session.pop("active_list_id"' in content, "❌ Missing active_list_id pop in clear"
    assert 'session.pop("active_list_name"' in content, "❌ Missing active_list_name pop in clear"
    
    print("✅ /api/clear correctly clears active list metadata")
    return True

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 Running Word List Manager Tests")
    print("="*60 + "\n")
    
    tests = [
        test_quiz_template_includes_wordlist_manager,
        test_wordlist_js_exists,
        test_flask_route_passes_selected_list,
        test_saved_lists_load_sets_active_list,
        test_clear_api_clears_active_list,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"❌ Test failed: {test.__name__}")
            print(f"   Error: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"❌ Test error: {test.__name__}")
            print(f"   Error: {str(e)}")
            failed += 1
        print()
    
    print("="*60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
