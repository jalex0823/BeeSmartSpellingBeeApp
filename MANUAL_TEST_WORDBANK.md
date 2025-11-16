# Manual Testing Guide - Wordbank Single Source of Truth

This guide demonstrates the wordbank single source of truth functionality.

## Setup
1. Start the Flask server: `python3 AjaSpellBApp.py`
2. Server will be running at http://127.0.0.1:5000

## Test Scenarios

### Scenario 1: Upload Replaces Wordbank

**Goal**: Verify that uploading a second set of words REPLACES (not appends to) the first set.

**Steps**:
1. Open a new browser session
2. Upload first set of words:
   ```bash
   curl -X POST http://127.0.0.1:5000/api/upload \
     -H "Content-Type: application/json" \
     -d '{"words": [{"word": "cat", "sentence": "The ____ meows.", "hint": ""}]}' \
     -c cookies.txt
   ```
   Expected: `{"ok": true, "count": 1}`

3. Check wordbank:
   ```bash
   curl http://127.0.0.1:5000/api/wordbank -b cookies.txt
   ```
   Expected: 1 word in wordbank

4. Upload second set:
   ```bash
   curl -X POST http://127.0.0.1:5000/api/upload \
     -H "Content-Type: application/json" \
     -d '{"words": [{"word": "dog", "sentence": "The ____ barks.", "hint": ""}, {"word": "bird", "sentence": "The ____ flies.", "hint": ""}]}' \
     -b cookies.txt -c cookies.txt
   ```
   Expected: `{"ok": true, "count": 2}`

5. Check wordbank again:
   ```bash
   curl http://127.0.0.1:5000/api/wordbank -b cookies.txt
   ```
   **Expected**: 2 words (dog, bird) - NOT 3 words
   **Verifies**: Wordbank was REPLACED, not appended

### Scenario 2: Clear Suppresses Default Autoload

**Goal**: Verify that after clearing, the app doesn't automatically load default words.

**Steps**:
1. Clear the wordbank:
   ```bash
   curl -X POST http://127.0.0.1:5000/api/clear \
     -H "Content-Type: application/json" \
     -d '{"confirmed": true}' \
     -b cookies.txt -c cookies.txt
   ```
   Expected: `{"ok": true, "cleared": {...}}`

2. Check wordbank:
   ```bash
   curl http://127.0.0.1:5000/api/wordbank -b cookies.txt
   ```
   **Expected**: `{"words": [], "count": 0, "suppressed": true}`
   **Verifies**: Wordbank is empty and suppression flag is set

3. Try to start quiz:
   ```bash
   curl -X POST http://127.0.0.1:5000/api/next -b cookies.txt
   ```
   **Expected**: `{"error": "No words loaded", "total": 0, "suppressed": true, ...}`
   **Verifies**: Quiz doesn't start with auto-loaded defaults

### Scenario 3: Load Default Clears Suppression

**Goal**: Verify that explicitly loading defaults re-enables the quiz.

**Steps**:
1. Load defaults (continuing from Scenario 2):
   ```bash
   curl http://127.0.0.1:5000/api/load-default -b cookies.txt -c cookies.txt
   ```
   **Expected**: `{"ok": true, "loaded": 50, "source": "default"}`

2. Check wordbank:
   ```bash
   curl http://127.0.0.1:5000/api/wordbank -b cookies.txt
   ```
   **Expected**: `{"words": [...], "count": 50}` (no suppressed flag)

3. Start quiz:
   ```bash
   curl -X POST http://127.0.0.1:5000/api/next -b cookies.txt
   ```
   **Expected**: Returns a word from the default list
   **Verifies**: Quiz works after explicit load-default

### Scenario 4: Saved List Replaces Wordbank

**Goal**: Verify that loading a saved list replaces the current wordbank.

**Note**: This requires being logged in. For guest users, skip this test.

**Steps**:
1. Upload some words (creates first wordbank)
2. Load a saved list via `/api/saved-lists/load`
3. Check wordbank
   **Expected**: Only words from the saved list are present

## Automated Testing

Run the comprehensive test suite:
```bash
python3 test_wordbank_single_source.py
```

Expected output:
```
================================================================================
RESULTS: 6 passed, 0 failed
================================================================================
```

All tests should pass:
- ✅ TEST 1: Clear sets suppression flag
- ✅ TEST 2: Upload replaces wordbank
- ✅ TEST 3: /api/next with suppression flag
- ✅ TEST 4: /api/load-default clears suppression
- ✅ TEST 5: Manual words upload replaces wordbank
- ✅ TEST 6: Complete flow

## Backward Compatibility

Verify existing functionality still works:

1. New session (without any uploads):
   ```bash
   curl http://127.0.0.1:5000/api/wordbank
   ```
   **Expected**: Auto-loads 50 default words (backward compatible behavior)

2. Existing tests:
   ```bash
   python3 test_clear_api.py
   python3 test_default_words.py
   ```
   **Expected**: All tests pass

## Summary

This implementation ensures:
- ✅ Wordbank always uses REPLACE semantics (never appends)
- ✅ Clear action suppresses default autoload
- ✅ Explicit load-default endpoint for users who want defaults after clear
- ✅ Friendly error messages when trying to quiz with no words
- ✅ Backward compatibility with existing flows
