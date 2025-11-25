"""
Voice Visualization Fix Verification
Tests that the particle swarm voice visualization has proper fallback
"""
import re
from pathlib import Path

def test_mask_url_fix():
    """Verify mask URL is corrected in quiz.html"""
    quiz_file = Path('templates/quiz.html')
    content = quiz_file.read_text(encoding='utf-8')
    
    # Check for correct mask URL
    assert 'lips_mask_clean.png' in content, "❌ Correct mask URL not found"
    
    # Check old incorrect URL is gone
    assert content.count("maskUrl: '/static/assets/visualizer/lips_mask.png'") == 0, \
        "❌ Old incorrect mask URL still present"
    
    print("✅ Mask URL correctly updated to lips_mask_clean.png")
    return True

def test_css_fallback_present():
    """Verify CSS fallback voice waves are present"""
    quiz_file = Path('templates/quiz.html')
    content = quiz_file.read_text(encoding='utf-8')
    
    # Check for fallback HTML structure
    assert 'voice-wave-fallback' in content, "❌ CSS fallback structure missing"
    assert 'voice-wave-bar' in content, "❌ Voice wave bars missing"
    
    # Check for fallback CSS animations
    assert 'voiceWavePulse' in content, "❌ Voice wave pulse animation missing"
    assert '@keyframes voiceWavePulse' in content, "❌ Voice wave keyframes missing"
    
    print("✅ CSS fallback voice waves present")
    return True

def test_fallback_activation_logic():
    """Verify fallback activation logic in catch block"""
    quiz_file = Path('templates/quiz.html')
    content = quiz_file.read_text(encoding='utf-8')
    
    # Check for fallback activation in error handler
    assert 'Activating CSS fallback voice visualization' in content, \
        "❌ Fallback activation message missing"
    assert 'usingFallbackViz' in content, "❌ Fallback flag not set"
    assert "fallbackWaves.classList.add('speaking')" in content, \
        "❌ Fallback speech event handler missing"
    
    print("✅ Fallback activation logic present")
    return True

def test_speech_event_listeners():
    """Verify speech event listeners for both THREE.js and CSS fallback"""
    quiz_file = Path('templates/quiz.html')
    content = quiz_file.read_text(encoding='utf-8')
    
    # Check for quiz-speech-start event listeners
    assert "window.addEventListener('quiz-speech-start'" in content, \
        "❌ Speech start listener missing"
    assert "window.addEventListener('quiz-speech-end'" in content, \
        "❌ Speech end listener missing"
    
    print("✅ Speech event listeners configured")
    return True

def test_mask_file_exists():
    """Verify the correct mask file actually exists"""
    mask_path = Path('static/assets/visualizer/lips_mask_clean.png')
    
    assert mask_path.exists(), \
        f"❌ Mask file not found at {mask_path}"
    
    print(f"✅ Mask file exists at {mask_path}")
    return True

def main():
    """Run all voice visualization fix tests"""
    print("🎤 Voice Visualization Fix Verification")
    print("=" * 50)
    
    tests = [
        ("Mask URL Fix", test_mask_url_fix),
        ("CSS Fallback Structure", test_css_fallback_present),
        ("Fallback Activation Logic", test_fallback_activation_logic),
        ("Speech Event Listeners", test_speech_event_listeners),
        ("Mask File Exists", test_mask_file_exists),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Testing: {test_name}")
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"   {e}")
            failed += 1
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ ALL TESTS PASSED - Voice visualization fix verified!")
        print("\n📝 Summary of fixes:")
        print("   1. Corrected mask URL to lips_mask_clean.png")
        print("   2. Added CSS fallback voice wave bars")
        print("   3. Added fallback activation on THREE.js failure")
        print("   4. Integrated speech event listeners for both modes")
        print("   5. Verified mask file exists in correct location")
    else:
        print(f"❌ {failed} test(s) failed - review errors above")
    
    return failed == 0

if __name__ == '__main__':
    import sys
    sys.exit(0 if main() else 1)
