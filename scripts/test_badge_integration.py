"""
Test Badge Integration
Verify that badge images are properly integrated into the Buzz Dust system
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_badge_files():
    """Test that all badge files exist"""
    print("=" * 60)
    print("Test 1: Badge Files")
    print("=" * 60)
    
    badge_dir = os.path.join('static', 'assets', 'badges')
    
    if not os.path.exists(badge_dir):
        print(f"❌ Badge directory not found: {badge_dir}")
        return False
    
    expected_badges = [
        'Novice.png',
        'Apprentice.png',
        'Scholar.png',
        'Elete.png',
        'Magistrate.png',
        'BuzzDustMaster.png'
    ]
    
    print(f"\n📁 Checking badge directory: {badge_dir}")
    
    all_found = True
    for badge_file in expected_badges:
        badge_path = os.path.join(badge_dir, badge_file)
        if os.path.exists(badge_path):
            size = os.path.getsize(badge_path)
            size_mb = size / (1024 * 1024)
            print(f"   ✅ {badge_file:<25} ({size_mb:.2f} MB)")
        else:
            print(f"   ❌ {badge_file:<25} NOT FOUND")
            all_found = False
    
    return all_found


def test_config_integration():
    """Test that config file references badge images"""
    print("\n" + "=" * 60)
    print("Test 2: Configuration Integration")
    print("=" * 60)
    
    config_path = os.path.join('config', 'buzz_dust_config.json')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"\n📝 Checking bee_classes in config...")
        
        all_have_badges = True
        for bee_class in config['bee_classes']:
            badge_img = bee_class.get('badge_image')
            if badge_img:
                print(f"   ✅ {bee_class['label']:<25} → {badge_img}")
            else:
                print(f"   ❌ {bee_class['label']:<25} → NO BADGE IMAGE")
                all_have_badges = False
        
        return all_have_badges
        
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return False


def test_helper_functions():
    """Test that helper functions return badge_image field"""
    print("\n" + "=" * 60)
    print("Test 3: Helper Functions")
    print("=" * 60)
    
    try:
        from buzz_dust_helpers import get_bee_class, get_all_bee_classes
        
        # Test get_bee_class
        novice = get_bee_class(100)
        print(f"\n🐝 Novice Bee (100 Buzz Dust):")
        print(f"   Label: {novice.get('label')}")
        print(f"   Badge Image: {novice.get('badge_image')}")
        
        if not novice.get('badge_image'):
            print("   ❌ No badge_image field!")
            return False
        
        # Test get_all_bee_classes
        all_classes = get_all_bee_classes()
        print(f"\n📊 All Bee Classes ({len(all_classes)} total):")
        
        all_valid = True
        for bee_class in all_classes:
            has_badge = 'badge_image' in bee_class
            status = "✅" if has_badge else "❌"
            badge_name = bee_class.get('badge_image', 'MISSING')
            print(f"   {status} {bee_class['label']:<25} → {badge_name}")
            if not has_badge:
                all_valid = False
        
        return all_valid
        
    except Exception as e:
        print(f"❌ Helper function test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_template_syntax():
    """Check that templates reference badge images correctly"""
    print("\n" + "=" * 60)
    print("Test 4: Template Integration")
    print("=" * 60)
    
    templates_to_check = [
        ('templates/points_buzz_dust_explanation.html', 'badge_image'),
        ('templates/components/rank_progress_bar.html', 'badge_image'),
    ]
    
    all_valid = True
    for template_path, keyword in templates_to_check:
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if keyword in content:
                print(f"   ✅ {template_path:<50} references '{keyword}'")
            else:
                print(f"   ❌ {template_path:<50} missing '{keyword}'")
                all_valid = False
        else:
            print(f"   ⚠️  {template_path:<50} not found")
    
    return all_valid


def main():
    """Run all badge integration tests"""
    print("\n🎨 BeeSmart Badge Integration - Validation Tests")
    print("=" * 60)
    
    tests = [
        ("Badge Files", test_badge_files),
        ("Config Integration", test_config_integration),
        ("Helper Functions", test_helper_functions),
        ("Template Integration", test_template_syntax)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"\n❌ {name} test failed!")
        except Exception as e:
            failed += 1
            print(f"\n❌ {name} test crashed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Badge Integration Test Summary")
    print("=" * 60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 All badge integration tests passed!")
        print("✨ Your beautiful badges are ready to use!")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please review errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
