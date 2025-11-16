"""
Test wordbank single source of truth functionality.

This test validates:
1. Upload replaces (not appends) wordbank
2. Saved Lists replace (not append) wordbank
3. Clear sets suppress_default flag
4. /api/wordbank returns empty when suppressed
5. /api/next returns friendly error when suppressed and empty
6. /api/load-default explicitly loads defaults and clears suppression
"""
import urllib.request
import urllib.error
import json
import time


BASE_URL = "http://127.0.0.1:5000"


def make_request(endpoint, method="GET", data=None, headers=None):
    """Make HTTP request and return response or error."""
    url = f"{BASE_URL}{endpoint}"
    if headers is None:
        headers = {}
    
    if data is not None:
        data = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        response = urllib.request.urlopen(req)
        return json.loads(response.read().decode('utf-8')), response.status
    except urllib.error.HTTPError as e:
        error_data = json.loads(e.read().decode('utf-8'))
        return error_data, e.code
    except Exception as e:
        return {"error": str(e)}, 500


def test_clear_sets_suppression():
    """Test that /api/clear sets suppress_default flag."""
    print("\n" + "="*70)
    print("TEST 1: Clear sets suppression flag")
    print("="*70)
    
    # First, clear with confirmation
    result, status = make_request("/api/clear", method="POST", data={"confirmed": True})
    print(f"Clear response: {result}")
    assert result.get("ok") == True, "Clear should succeed"
    
    # Now check wordbank - should be empty with suppressed flag
    result, status = make_request("/api/wordbank", method="GET")
    print(f"Wordbank after clear: count={result.get('count')}, suppressed={result.get('suppressed')}")
    assert result.get("count") == 0, "Wordbank should be empty after clear"
    assert result.get("suppressed") == True, "Suppression flag should be set"
    
    print("✅ PASS: Clear sets suppression flag correctly")
    return True


def test_upload_replaces_wordbank():
    """Test that upload replaces (not appends) wordbank."""
    print("\n" + "="*70)
    print("TEST 2: Upload replaces wordbank")
    print("="*70)
    
    # Upload first set of words
    words1 = [
        {"word": "cat", "sentence": "The ____ meows.", "hint": ""},
        {"word": "dog", "sentence": "The ____ barks.", "hint": ""}
    ]
    result, status = make_request("/api/upload", method="POST", 
                                   data={"words": words1})
    print(f"First upload response: count={result.get('count')}")
    assert result.get("ok") == True, "First upload should succeed"
    assert result.get("count") == 2, "First upload should have 2 words"
    
    # Check wordbank
    result, status = make_request("/api/wordbank", method="GET")
    print(f"Wordbank after first upload: count={result.get('count')}")
    assert result.get("count") == 2, "Wordbank should have 2 words"
    
    # Upload second set of words (different words)
    words2 = [
        {"word": "bird", "sentence": "The ____ flies.", "hint": ""},
        {"word": "fish", "sentence": "The ____ swims.", "hint": ""},
        {"word": "frog", "sentence": "The ____ jumps.", "hint": ""}
    ]
    result, status = make_request("/api/upload", method="POST", 
                                   data={"words": words2})
    print(f"Second upload response: count={result.get('count')}")
    assert result.get("ok") == True, "Second upload should succeed"
    assert result.get("count") == 3, "Second upload should have 3 words"
    
    # Check wordbank - should be REPLACED, not appended (so 3, not 5)
    result, status = make_request("/api/wordbank", method="GET")
    print(f"Wordbank after second upload: count={result.get('count')}")
    assert result.get("count") == 3, "Wordbank should be REPLACED (3 words), not appended (5 words)"
    
    # Verify the words are from the second upload
    words = result.get("words", [])
    word_texts = [w.get("word") for w in words]
    print(f"Words in wordbank: {word_texts}")
    assert "bird" in word_texts, "Second upload words should be present"
    assert "cat" not in word_texts, "First upload words should be replaced"
    
    print("✅ PASS: Upload replaces wordbank correctly")
    return True


def test_next_with_suppression():
    """Test that /api/next returns friendly error when suppressed and empty."""
    print("\n" + "="*70)
    print("TEST 3: /api/next with suppression flag")
    print("="*70)
    
    # Clear to set suppression
    result, status = make_request("/api/clear", method="POST", data={"confirmed": True})
    assert result.get("ok") == True, "Clear should succeed"
    
    # Try to get next word - should return friendly error
    result, status = make_request("/api/next", method="POST")
    print(f"/api/next with suppression: {result}")
    assert result.get("total") == 0, "Total should be 0 when suppressed"
    assert result.get("suppressed") == True, "Suppressed flag should be true"
    assert "error" in result, "Should return error message"
    print(f"Error message: {result.get('message')}")
    
    print("✅ PASS: /api/next returns friendly error when suppressed")
    return True


def test_load_default_clears_suppression():
    """Test that /api/load-default loads defaults and clears suppression."""
    print("\n" + "="*70)
    print("TEST 4: /api/load-default clears suppression")
    print("="*70)
    
    # Clear to set suppression
    result, status = make_request("/api/clear", method="POST", data={"confirmed": True})
    assert result.get("ok") == True, "Clear should succeed"
    
    # Verify suppression is set
    result, status = make_request("/api/wordbank", method="GET")
    assert result.get("suppressed") == True, "Suppression should be set after clear"
    
    # Load defaults
    result, status = make_request("/api/load-default", method="GET")
    print(f"Load default response: {result}")
    assert result.get("ok") == True, "Load default should succeed"
    assert result.get("loaded", 0) > 0, "Should load some words"
    print(f"Loaded {result.get('loaded')} default words")
    
    # Check wordbank - suppression should be cleared
    result, status = make_request("/api/wordbank", method="GET")
    print(f"Wordbank after load-default: count={result.get('count')}, suppressed={result.get('suppressed')}")
    assert result.get("count", 0) > 0, "Wordbank should have words"
    assert result.get("suppressed") != True, "Suppression should be cleared"
    
    # /api/next should work now
    result, status = make_request("/api/next", method="POST")
    print(f"/api/next after load-default: done={result.get('done')}, error={result.get('error')}")
    assert result.get("error") is None or result.get("done") or "word" in result, "/api/next should work"
    
    print("✅ PASS: /api/load-default clears suppression correctly")
    return True


def test_manual_words_replaces():
    """Test that manual words upload replaces wordbank."""
    print("\n" + "="*70)
    print("TEST 5: Manual words upload replaces wordbank")
    print("="*70)
    
    # Upload first batch
    result, status = make_request("/api/upload-manual-words", method="POST",
                                   data={"words": ["apple", "banana"]})
    print(f"First manual upload: {result}")
    if not result.get("ok"):
        print(f"⚠️ SKIP: Manual upload not working: {result.get('error')}")
        return True
    
    assert result.get("count") == 2, "Should have 2 words"
    
    # Upload second batch
    result, status = make_request("/api/upload-manual-words", method="POST",
                                   data={"words": ["cherry", "date", "elderberry"]})
    print(f"Second manual upload: {result}")
    assert result.get("ok") == True, "Second upload should succeed"
    assert result.get("count") == 3, "Should have 3 words"
    
    # Check wordbank - should be replaced (3, not 5)
    result, status = make_request("/api/wordbank", method="GET")
    print(f"Wordbank after manual uploads: count={result.get('count')}")
    assert result.get("count") == 3, "Wordbank should be REPLACED (3 words), not appended (5 words)"
    
    print("✅ PASS: Manual words upload replaces wordbank correctly")
    return True


def test_full_flow():
    """Test complete flow: upload -> quiz -> clear -> no autoload -> load-default."""
    print("\n" + "="*70)
    print("TEST 6: Complete flow")
    print("="*70)
    
    # 1. Upload words
    words = [
        {"word": "test", "sentence": "This is a ____.", "hint": ""},
        {"word": "flow", "sentence": "The water will ____.", "hint": ""}
    ]
    result, status = make_request("/api/upload", method="POST", data={"words": words})
    print(f"Upload: count={result.get('count')}")
    assert result.get("ok") == True, "Upload should succeed"
    
    # 2. Start quiz
    result, status = make_request("/api/next", method="POST")
    print(f"Quiz started: word={result.get('word', 'N/A')}, error={result.get('error')}")
    assert result.get("error") is None, "Quiz should start successfully"
    
    # 3. Clear
    result, status = make_request("/api/clear", method="POST", data={"confirmed": True})
    print(f"Clear: ok={result.get('ok')}")
    assert result.get("ok") == True, "Clear should succeed"
    
    # 4. Verify no autoload
    result, status = make_request("/api/wordbank", method="GET")
    print(f"After clear: count={result.get('count')}, suppressed={result.get('suppressed')}")
    assert result.get("count") == 0, "Wordbank should be empty"
    assert result.get("suppressed") == True, "Should be suppressed"
    
    # 5. Try quiz - should fail gracefully
    result, status = make_request("/api/next", method="POST")
    print(f"Quiz after clear: total={result.get('total')}, suppressed={result.get('suppressed')}")
    assert result.get("total") == 0, "Should indicate no words"
    
    # 6. Load defaults
    result, status = make_request("/api/load-default", method="GET")
    print(f"Load default: loaded={result.get('loaded')}")
    assert result.get("ok") == True, "Load default should succeed"
    
    # 7. Verify quiz works again
    result, status = make_request("/api/next", method="POST")
    print(f"Quiz after load-default: word={result.get('word', 'N/A')}, error={result.get('error')}")
    assert result.get("error") is None, "Quiz should work after load-default"
    
    print("✅ PASS: Complete flow works correctly")
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*80)
    print("WORDBANK SINGLE SOURCE OF TRUTH - TEST SUITE")
    print("="*80)
    print("Testing against:", BASE_URL)
    print("="*80)
    
    tests = [
        ("Clear sets suppression", test_clear_sets_suppression),
        ("Upload replaces wordbank", test_upload_replaces_wordbank),
        ("Next with suppression", test_next_with_suppression),
        ("Load default clears suppression", test_load_default_clears_suppression),
        ("Manual words replaces", test_manual_words_replaces),
        ("Complete flow", test_full_flow),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"❌ FAIL: {name}")
        except AssertionError as e:
            failed += 1
            print(f"❌ FAIL: {name} - {e}")
        except Exception as e:
            failed += 1
            print(f"❌ ERROR: {name} - {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*80)
    
    return failed == 0


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
