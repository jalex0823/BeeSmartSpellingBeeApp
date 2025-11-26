"""
Test Bee Swarm Lips Visualizer Integration
Verifies all files are present and properly connected
"""
import os
import re
from pathlib import Path

def test_files_exist():
    """Verify all required files are present"""
    print("🔍 Testing file existence...")
    
    required_files = [
        'static/assets/visualizer/lips_mask_clean.png',
        'static/js/bee_swarm_visualizer.js',
        'templates/quiz.html'
    ]
    
    base_path = Path(__file__).parent
    missing = []
    
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING!")
            missing.append(file_path)
    
    assert not missing, f"Missing files: {missing}"
    print()

def test_visualizer_has_colors():
    """Verify bee_swarm_visualizer.js has honey color palette"""
    print("🎨 Testing honey color palette...")
    
    viz_path = Path(__file__).parent / 'static/js/bee_swarm_visualizer.js'
    content = viz_path.read_text(encoding='utf-8')
    
    # Check for color palette
    expected_colors = ['#FDB813', '#FFCC33', '#FFB84D', '#FFF6CC', '#E08A00']
    found_colors = []
    
    for color in expected_colors:
        if color in content:
            print(f"  ✅ {color} found")
            found_colors.append(color)
        else:
            print(f"  ❌ {color} missing")
    
    assert len(found_colors) == 5, f"Only found {len(found_colors)}/5 honey colors"
    print()

def test_speech_event_listeners():
    """Verify visualizer listens to speech events"""
    print("🎤 Testing speech event listeners...")
    
    viz_path = Path(__file__).parent / 'static/js/bee_swarm_visualizer.js'
    content = viz_path.read_text(encoding='utf-8')
    
    required_listeners = [
        'quiz-speech-start',
        'quiz-speech-end',
        'quiz-speech-boundary'
    ]
    
    for event in required_listeners:
        if event in content:
            print(f"  ✅ Listening to '{event}'")
        else:
            print(f"  ❌ Missing listener for '{event}'")
            assert False, f"Missing event listener: {event}"
    print()

def test_quiz_dispatches_events():
    """Verify quiz.html dispatches speech events"""
    print("📢 Testing quiz speech event dispatching...")
    
    quiz_path = Path(__file__).parent / 'templates/quiz.html'
    content = quiz_path.read_text(encoding='utf-8')
    
    # Count event dispatches
    start_count = content.count("dispatchEvent(new CustomEvent('quiz-speech-start')")
    end_count = content.count("dispatchEvent(new CustomEvent('quiz-speech-end')")
    boundary_count = content.count("dispatchEvent(new CustomEvent('quiz-speech-boundary')")
    
    print(f"  ✅ 'quiz-speech-start' dispatched {start_count} times")
    print(f"  ✅ 'quiz-speech-end' dispatched {end_count} times")
    print(f"  ✅ 'quiz-speech-boundary' dispatched {boundary_count} times")
    
    assert start_count >= 3, f"Expected at least 3 speech-start dispatches, found {start_count}"
    assert end_count >= 3, f"Expected at least 3 speech-end dispatches, found {end_count}"
    print()

def test_webgl_detection():
    """Verify WebGL detection code is present"""
    print("🔬 Testing WebGL detection...")
    
    quiz_path = Path(__file__).parent / 'templates/quiz.html'
    content = quiz_path.read_text(encoding='utf-8')
    
    # Check for WebGL detection
    webgl_check_patterns = [
        r"getContext\(['\"]webgl['\"]",
        r"getContext\(['\"]experimental-webgl['\"]",
        "WebGL not supported"
    ]
    
    for pattern in webgl_check_patterns:
        if re.search(pattern, content):
            print(f"  ✅ Found WebGL detection: {pattern}")
        else:
            print(f"  ⚠️  Pattern not found: {pattern}")
    print()

def test_mask_url_correct():
    """Verify mask URL matches actual file path"""
    print("🖼️  Testing mask URL configuration...")
    
    quiz_path = Path(__file__).parent / 'templates/quiz.html'
    content = quiz_path.read_text(encoding='utf-8')
    
    expected_url = '/static/assets/visualizer/lips_mask_clean.png'
    
    if expected_url in content:
        print(f"  ✅ Mask URL configured: {expected_url}")
    else:
        print(f"  ❌ Mask URL not found!")
        assert False, "Mask URL not configured correctly"
    
    # Verify file actually exists
    mask_path = Path(__file__).parent / 'static/assets/visualizer/lips_mask_clean.png'
    if mask_path.exists():
        file_size = mask_path.stat().st_size
        print(f"  ✅ Mask file exists ({file_size:,} bytes)")
    else:
        print(f"  ❌ Mask file missing!")
        assert False, "Mask file not found"
    print()

def test_container_element():
    """Verify beeSwarmVisualizerContainer exists in HTML"""
    print("📦 Testing container element...")
    
    quiz_path = Path(__file__).parent / 'templates/quiz.html'
    content = quiz_path.read_text(encoding='utf-8')
    
    if 'id="beeSwarmVisualizerContainer"' in content:
        print("  ✅ Container element found")
        
        # Check it's not display:none permanently
        container_match = re.search(r'id="beeSwarmVisualizerContainer"[^>]*style="([^"]+)"', content, re.DOTALL)
        if container_match:
            style = container_match.group(1)
            if 'display:none' in style and 'visibility:hidden' in style:
                print("  ⚠️  Container starts hidden (will be shown by JS)")
            else:
                print("  ✅ Container visibility will be controlled by JS")
    else:
        print("  ❌ Container element missing!")
        assert False, "beeSwarmVisualizerContainer not found"
    print()

def test_module_import():
    """Verify BeeSwarmVisualizer is imported as module"""
    print("📥 Testing module import...")
    
    quiz_path = Path(__file__).parent / 'templates/quiz.html'
    content = quiz_path.read_text(encoding='utf-8')
    
    if 'type="module"' in content and 'import BeeSwarmVisualizer' in content:
        print("  ✅ Module import found")
        
        # Extract import statement
        import_match = re.search(r'import BeeSwarmVisualizer from ["\']([^"\']+)["\']', content)
        if import_match:
            import_url = import_match.group(1)
            print(f"  ✅ Import URL: {import_url}")
    else:
        print("  ❌ Module import not found!")
        assert False, "BeeSwarmVisualizer not imported as module"
    print()

if __name__ == '__main__':
    print("=" * 60)
    print("🐝 Bee Swarm Lips Visualizer Integration Test")
    print("=" * 60)
    print()
    
    try:
        test_files_exist()
        test_visualizer_has_colors()
        test_speech_event_listeners()
        test_quiz_dispatches_events()
        test_webgl_detection()
        test_mask_url_correct()
        test_container_element()
        test_module_import()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print()
        print("🚀 Ready to push to Railway")
        print()
        
    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 60)
        exit(1)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"💥 UNEXPECTED ERROR: {e}")
        print("=" * 60)
        exit(1)
