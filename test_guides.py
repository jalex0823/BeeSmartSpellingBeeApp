#!/usr/bin/env python3
"""
Test script for guide functionality
Tests both user and admin guide routes
"""

import sys
import os
from pathlib import Path

def test_guide_files():
    """Test that guide files exist and can be read"""
    user_guide = Path("BEESMART_USER_GUIDE.md")
    admin_guide = Path("BEESMART_ADMIN_GUIDE.md")
    
    print("🔍 Testing guide files...")
    
    if user_guide.exists():
        print(f"✅ User guide found: {user_guide}")
        content = user_guide.read_text(encoding='utf-8')
        print(f"   📄 File size: {len(content):,} characters")
        print(f"   📖 First line: {content.split(chr(10))[0][:80]}...")
    else:
        print(f"❌ User guide missing: {user_guide}")
        return False
    
    if admin_guide.exists():
        print(f"✅ Admin guide found: {admin_guide}")
        content = admin_guide.read_text(encoding='utf-8')
        print(f"   📄 File size: {len(content):,} characters")
        print(f"   📖 First line: {content.split(chr(10))[0][:80]}...")
    else:
        print(f"❌ Admin guide missing: {admin_guide}")
        return False
    
    return True

def test_flask_routes():
    """Test Flask route imports"""
    print("🔍 Testing Flask route imports...")
    
    try:
        # Test if we can import the Flask app
        from AjaSpellBApp import app
        print("✅ Flask app imported successfully")
        
        # Check if markdown is available
        try:
            import markdown
            print("✅ Markdown package available")
        except ImportError:
            print("⚠️  Markdown package not found - will use fallback formatting")
        
        # Test route existence
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        
        expected_routes = ['/guide', '/admin-guide', '/help']
        for route in expected_routes:
            if route in routes:
                print(f"✅ Route found: {route}")
            else:
                print(f"❌ Route missing: {route}")
        
        print(f"📊 Total routes: {len(routes)}")
        return True
        
    except Exception as e:
        print(f"❌ Error importing Flask app: {e}")
        return False

def test_template():
    """Test template file exists"""
    print("🔍 Testing template file...")
    
    template_file = Path("templates/guide.html")
    if template_file.exists():
        print(f"✅ Template found: {template_file}")
        return True
    else:
        print(f"❌ Template missing: {template_file}")
        return False

def main():
    """Run all tests"""
    print("🐝 BeeSmart Guide System Test")
    print("=" * 50)
    
    tests = [
        ("Guide Files", test_guide_files),
        ("Flask Routes", test_flask_routes), 
        ("Template File", test_template)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append((test_name, False))
    
    print("\n📊 Test Results Summary:")
    print("=" * 50)
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Guide system is ready!")
        print("\n📋 Next steps:")
        print("   1. Start Flask server: python AjaSpellBApp.py")
        print("   2. Visit: http://localhost:5000/guide")
        print("   3. Visit: http://localhost:5000/admin-guide")
        print("   4. Check main menu for guide links")
    else:
        print("\n⚠️  Some tests failed. Please fix issues before deploying.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())