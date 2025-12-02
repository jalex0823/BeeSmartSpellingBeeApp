"""
Test wordbank replacement behavior and suppression flag functionality.

This test verifies that:
1. Loading a Saved List or uploading words REPLACES the session wordbank (no append)
2. Clearing the wordbank sets suppression flag and prevents default autoload
3. /api/load-default endpoint loads defaults and clears suppression
4. /api/next returns appropriate error when suppressed and empty
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from AjaSpellBApp import app
import json

def test_wordbank_replacement():
    """Test that uploads and saved list loads REPLACE the wordbank instead of appending."""
    print("\n" + "="*70)
    print("TEST: Wordbank Replacement Behavior")
    print("="*70)
    
    with app.test_client() as client:
        # Start with a fresh session
        with client.session_transaction() as sess:
            sess.clear()
        
        # Upload first list (List A)
        print("\n1. Upload List A (3 words)")
        response = client.post('/api/upload', 
            json={
                'words': [
                    {'word': 'apple', 'sentence': 'An _____ a day.', 'hint': ''},
                    {'word': 'banana', 'sentence': 'Yellow fruit _____.', 'hint': ''},
                    {'word': 'cherry', 'sentence': 'Red _____.', 'hint': ''}
                ]
            },
            content_type='application/json'
        )
        assert response.status_code == 200, f"Upload failed: {response.data}"
        data = response.get_json()
        assert data['ok'] == True
        assert data['count'] == 3
        print(f"✅ List A uploaded: {data['count']} words")
        
        # Check wordbank
        response = client.get('/api/wordbank')
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] == 3
        words_a = [w['word'] for w in data['words']]
        print(f"✅ Wordbank contains: {words_a}")
        
        # Upload second list (List B) - should REPLACE, not append
        print("\n2. Upload List B (2 words) - should REPLACE List A")
        response = client.post('/api/upload',
            json={
                'words': [
                    {'word': 'dog', 'sentence': 'A _____ barks.', 'hint': ''},
                    {'word': 'cat', 'sentence': 'A _____ meows.', 'hint': ''}
                ]
            },
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] == 2
        print(f"✅ List B uploaded: {data['count']} words")
        
        # Verify wordbank was REPLACED (not appended)
        response = client.get('/api/wordbank')
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] == 2, f"Expected 2 words, got {data['count']}"
        words_b = [w['word'] for w in data['words']]
        print(f"✅ Wordbank now contains: {words_b}")
        
        # Verify List A words are gone
        assert 'apple' not in words_b
        assert 'banana' not in words_b
        assert 'cherry' not in words_b
        assert 'dog' in words_b
        assert 'cat' in words_b
        print("✅ List A completely replaced by List B")
        
        print("\n" + "="*70)
        print("✅ PASS: Wordbank Replacement Test")
        print("="*70)


def test_suppression_flag():
    """Test that clearing wordbank sets suppression flag and prevents default autoload."""
    print("\n" + "="*70)
    print("TEST: Suppression Flag Behavior")
    print("="*70)
    
    with app.test_client() as client:
        # Start with a fresh session
        with client.session_transaction() as sess:
            sess.clear()
        
        # Upload some words
        print("\n1. Upload initial wordbank")
        response = client.post('/api/upload',
            json={
                'words': [
                    {'word': 'test', 'sentence': 'A _____.', 'hint': ''}
                ]
            },
            content_type='application/json'
        )
        assert response.status_code == 200
        print("✅ Words uploaded")
        
        # Clear the wordbank
        print("\n2. Clear wordbank with confirmed flag")
        response = client.post('/api/clear',
            json={'confirmed': True},
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['ok'] == True
        print("✅ Wordbank cleared")
        
        # Check that wordbank is empty and suppressed
        print("\n3. Check wordbank is empty with suppression flag")
        response = client.get('/api/wordbank')
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] == 0, f"Expected 0 words, got {data['count']}"
        assert data.get('suppressed') == True, "Expected suppressed flag to be True"
        print(f"✅ Wordbank empty with suppressed={data.get('suppressed')}")
        
        # Try to call /api/next - should return error without loading defaults
        print("\n4. Call /api/next - should return error (no autoload)")
        response = client.post('/api/next')
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.get_json()
        assert 'error' in data
        assert data['total'] == 0
        print(f"✅ /api/next returned error: {data['error']}")
        
        # Verify no default words were loaded
        response = client.get('/api/wordbank')
        data = response.get_json()
        assert data['count'] == 0, "Default words should NOT have been loaded"
        print("✅ Default words NOT auto-loaded (suppression working)")
        
        print("\n" + "="*70)
        print("✅ PASS: Suppression Flag Test")
        print("="*70)


def test_load_default_endpoint():
    """Test that /api/load-default explicitly loads defaults and clears suppression."""
    print("\n" + "="*70)
    print("TEST: /api/load-default Endpoint")
    print("="*70)
    
    with app.test_client() as client:
        # Start with a fresh session and set suppression
        with client.session_transaction() as sess:
            sess.clear()
            sess['suppress_default'] = True
        
        print("\n1. Session has suppression flag set")
        
        # Call /api/load-default
        print("\n2. Call /api/load-default")
        response = client.get('/api/load-default')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.data}"
        data = response.get_json()
        assert data['ok'] == True
        assert data['count'] > 0, "Should have loaded default words"
        assert data['source'] == 'default'
        print(f"✅ Loaded {data['count']} default words")
        
        # Verify wordbank now has words and suppression is cleared
        print("\n3. Verify wordbank and suppression cleared")
        response = client.get('/api/wordbank')
        assert response.status_code == 200
        data = response.get_json()
        assert data['count'] > 0
        assert data.get('suppressed') == False or 'suppressed' not in data
        print(f"✅ Wordbank has {data['count']} words, suppressed={data.get('suppressed', False)}")
        
        # Verify can now call /api/next
        print("\n4. Verify /api/next works")
        response = client.post('/api/next')
        assert response.status_code == 200
        data = response.get_json()
        assert 'word' in data or 'done' in data
        print("✅ /api/next returned successfully")
        
        print("\n" + "="*70)
        print("✅ PASS: /api/load-default Test")
        print("="*70)


def test_source_tracking():
    """Test that word source is properly tracked in session."""
    print("\n" + "="*70)
    print("TEST: Word Source Tracking")
    print("="*70)
    
    with app.test_client() as client:
        # Test uploaded source
        print("\n1. Upload words - should track as 'uploaded'")
        with client.session_transaction() as sess:
            sess.clear()
        
        response = client.post('/api/upload',
            json={
                'words': [
                    {'word': 'test', 'sentence': 'A _____.', 'hint': ''}
                ]
            },
            content_type='application/json'
        )
        assert response.status_code == 200
        
        with client.session_transaction() as sess:
            assert sess.get('word_source') == 'uploaded', f"Expected 'uploaded', got {sess.get('word_source')}"
        print("✅ Upload tracked as 'uploaded'")
        
        # Test load-default source
        print("\n2. Load default - should track as 'default'")
        response = client.get('/api/load-default')
        assert response.status_code == 200
        
        with client.session_transaction() as sess:
            assert sess.get('word_source') == 'default', f"Expected 'default', got {sess.get('word_source')}"
        print("✅ Default load tracked as 'default'")
        
        print("\n" + "="*70)
        print("✅ PASS: Source Tracking Test")
        print("="*70)


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🐝 BeeSmart Wordbank Replacement Test Suite")
    print("="*70)
    
    try:
        test_wordbank_replacement()
        test_suppression_flag()
        test_load_default_endpoint()
        test_source_tracking()
        
        print("\n" + "="*70)
        print("🎉 ALL TESTS PASSED!")
        print("="*70 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
