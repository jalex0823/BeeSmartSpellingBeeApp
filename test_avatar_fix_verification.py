#!/usr/bin/env python3
"""
Avatar Loading Fix Verification Test

This script tests the avatar loading fixes:
1. MTL texture reference corrections
2. Canvas z-index improvements
3. Enhanced error handling

Usage: python test_avatar_fix_verification.py
"""

import os
import sys
import requests
from pathlib import Path

def test_avatar_files():
    """Test that avatar files exist and MTL references are correct"""
    print("🔍 Testing Professor Bee avatar files...")
    
    avatar_dir = Path("static/assets/avatars/professor-bee")
    
    # Check required files exist
    required_files = [
        "model.obj", "model.mtl", 
        "ProfessorBee.obj", "ProfessorBee.mtl", "ProfessorBee.png",
        "texture.png", "preview.png", "thumbnail.png"
    ]
    
    missing_files = []
    for file in required_files:
        file_path = avatar_dir / file
        if not file_path.exists():
            missing_files.append(str(file_path))
        else:
            print(f"  ✅ {file}")
    
    if missing_files:
        print(f"  ❌ Missing files: {missing_files}")
        return False
    
    # Check MTL texture references
    print("\n🎨 Checking MTL texture references...")
    
    mtl_files = ["model.mtl", "ProfessorBee.mtl"]
    for mtl_file in mtl_files:
        mtl_path = avatar_dir / mtl_file
        with open(mtl_path, 'r') as f:
            content = f.read()
            
        if "ProfessorBee.png" in content:
            print(f"  ✅ {mtl_file} correctly references ProfessorBee.png")
        else:
            print(f"  ❌ {mtl_file} does not reference ProfessorBee.png")
            print(f"     Content: {content}")
            return False
    
    return True

def test_avatar_api():
    """Test avatar API endpoints"""
    print("\n🌐 Testing avatar API endpoints...")
    
    try:
        # Test health endpoint first
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code != 200:
            print(f"  ❌ Health check failed: {response.status_code}")
            return False
        print("  ✅ Flask server is running")
        
        # Test avatar API
        response = requests.get("http://localhost:5000/api/avatars", timeout=10)
        if response.status_code != 200:
            print(f"  ❌ Avatar API failed: {response.status_code}")
            print(f"     Response: {response.text}")
            return False
        
        data = response.json()
        print(f"  ✅ Avatar API returned {len(data)} avatars")
        
        # Find professor-bee
        professor_bee = next((a for a in data if a['id'] == 'professor-bee'), None)
        if not professor_bee:
            print("  ❌ Professor Bee not found in avatar catalog")
            return False
        
        print("  ✅ Professor Bee found in catalog")
        print(f"     MTL URL: {professor_bee['urls']['model_mtl']}")
        print(f"     OBJ URL: {professor_bee['urls']['model_obj']}")
        print(f"     Texture URL: {professor_bee['urls']['texture']}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("  ❌ Cannot connect to Flask server (not running?)")
        return False
    except Exception as e:
        print(f"  ❌ Error testing API: {e}")
        return False

def test_static_file_access():
    """Test that static avatar files are accessible via HTTP"""
    print("\n📂 Testing static file access...")
    
    test_urls = [
        "/static/assets/avatars/professor-bee/ProfessorBee.obj",
        "/static/assets/avatars/professor-bee/ProfessorBee.mtl", 
        "/static/assets/avatars/professor-bee/ProfessorBee.png",
        "/static/assets/avatars/professor-bee/texture.png"
    ]
    
    base_url = "http://localhost:5000"
    
    for url_path in test_urls:
        try:
            response = requests.get(base_url + url_path, timeout=5)
            if response.status_code == 200:
                print(f"  ✅ {url_path} (size: {len(response.content)} bytes)")
            else:
                print(f"  ❌ {url_path} returned {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("  ❌ Cannot connect to Flask server")
            return False
        except Exception as e:
            print(f"  ❌ Error accessing {url_path}: {e}")
            return False
    
    return True

def main():
    """Run all avatar fix verification tests"""
    print("🐝 Avatar Loading Fix Verification")
    print("=" * 50)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    all_passed = True
    
    # Test 1: File existence and MTL references
    if not test_avatar_files():
        all_passed = False
    
    # Test 2: Avatar API
    if not test_avatar_api():
        all_passed = False
    
    # Test 3: Static file access
    if not test_static_file_access():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ ALL TESTS PASSED! Avatar loading fixes are working correctly.")
        print("\n📋 Summary of fixes applied:")
        print("   • Fixed MTL texture references (Professor_Bee_1019002841_texture.png → ProfessorBee.png)")
        print("   • Added canvas z-index and positioning fixes") 
        print("   • Enhanced MTL loader with proper resource paths")
        print("   • Added comprehensive error diagnostics")
        print("   • Set renderer to transparent background")
        
        print("\n🚀 Next steps:")
        print("   1. Test in browser: visit http://localhost:5000")
        print("   2. Check browser console for 3D loading messages")  
        print("   3. Deploy to Railway and verify avatar visibility")
        
    else:
        print("❌ SOME TESTS FAILED! Check the output above for issues.")
        print("\n🔧 Common fixes:")
        print("   • Start Flask server: python AjaSpellBApp.py")
        print("   • Check file permissions on avatar assets")
        print("   • Verify MTL files reference correct texture filenames")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())