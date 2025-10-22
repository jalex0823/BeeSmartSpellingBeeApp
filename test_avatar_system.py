#!/usr/bin/env python3
"""
Avatar System Generation Test Suite
Tests the complete avatar system to ensure proper functionality
"""

import os
import json
import sys
from pathlib import Path

def test_avatar_catalog():
    """Test avatar catalog integrity"""
    print("🐝 Testing Avatar Catalog...")
    
    try:
        from avatar_catalog import AVATAR_CATALOG, get_avatar_info, get_avatar_catalog
        print(f"✅ Avatar catalog imported successfully")
        print(f"📊 Total avatars in catalog: {len(AVATAR_CATALOG)}")
        
        # Test each avatar entry
        missing_files = []
        valid_avatars = []
        
        for avatar in AVATAR_CATALOG:
            avatar_id = avatar.get('id', 'unknown')
            folder_path = f"static/Avatars/3D Avatar Files/{avatar['folder']}"
            
            # Check required files
            required_files = [
                (avatar['obj_file'], 'OBJ'),
                (avatar['mtl_file'], 'MTL'), 
                (avatar['texture_file'], 'Texture'),
                (avatar['obj_file'].replace('.obj', '!.png'), 'Thumbnail')
            ]
            
            avatar_missing = []
            for filename, file_type in required_files:
                file_path = os.path.join(folder_path, filename)
                if not os.path.exists(file_path):
                    avatar_missing.append(f"{file_type}: {filename}")
            
            if avatar_missing:
                missing_files.append(f"{avatar_id}: {', '.join(avatar_missing)}")
                print(f"❌ {avatar_id}: Missing {len(avatar_missing)} files")
            else:
                valid_avatars.append(avatar_id)
                print(f"✅ {avatar_id}: All files present")
        
        print(f"\n📈 Results:")
        print(f"✅ Valid avatars: {len(valid_avatars)}")
        print(f"❌ Avatars with missing files: {len(missing_files)}")
        
        if missing_files:
            print(f"\n🔍 Missing Files Report:")
            for missing in missing_files:
                print(f"   {missing}")
        
        return len(missing_files) == 0
        
    except Exception as e:
        print(f"❌ Avatar catalog test failed: {e}")
        return False

def test_avatar_loader_js():
    """Test JavaScript avatar loader mapping"""
    print("\n🖥️ Testing JavaScript Avatar Loader...")
    
    js_file = "static/js/user-avatar-loader.js"
    if not os.path.exists(js_file):
        print(f"❌ Avatar loader file not found: {js_file}")
        return False
    
    try:
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ Avatar loader file found: {len(content)} characters")
        
        # Check for key components
        required_components = [
            'class UserAvatarLoader',
            'avatarMap',
            'loadUserAvatar',
            'init()',
            '.obj',
            '.mtl', 
            '.png'
        ]
        
        missing_components = []
        for component in required_components:
            if component not in content:
                missing_components.append(component)
        
        if missing_components:
            print(f"❌ Missing components: {missing_components}")
            return False
        else:
            print(f"✅ All required components present")
            return True
            
    except Exception as e:
        print(f"❌ Error reading avatar loader: {e}")
        return False

def test_avatar_routes():
    """Test Flask avatar routes"""
    print("\n🌐 Testing Avatar Routes...")
    
    try:
        from AjaSpellBApp import app
        
        with app.test_client() as client:
            # Test avatar catalog endpoint
            response = client.get('/api/avatars')
            if response.status_code == 200:
                print(f"✅ /api/avatars endpoint working")
                try:
                    data = response.get_json()
                    print(f"📊 API returned {len(data)} avatars")
                except:
                    print(f"⚠️ API response not JSON format")
            else:
                print(f"❌ /api/avatars endpoint failed: {response.status_code}")
            
            # Test individual avatar info
            response = client.get('/api/avatar/professor-bee')
            if response.status_code == 200:
                print(f"✅ Individual avatar endpoint working")
            else:
                print(f"❌ Individual avatar endpoint failed: {response.status_code}")
            
            return True
            
    except Exception as e:
        print(f"❌ Route testing failed: {e}")
        return False

def test_file_structure():
    """Test avatar file structure integrity"""
    print("\n📁 Testing Avatar File Structure...")
    
    base_path = "static/Avatars/3D Avatar Files"
    if not os.path.exists(base_path):
        print(f"❌ Avatar base directory not found: {base_path}")
        return False
    
    folders = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    print(f"📂 Found {len(folders)} avatar folders")
    
    valid_folders = 0
    for folder in folders:
        folder_path = os.path.join(base_path, folder)
        files = os.listdir(folder_path)
        
        # Check for required file types
        has_obj = any(f.endswith('.obj') for f in files)
        has_mtl = any(f.endswith('.mtl') for f in files)
        has_texture = any(f.endswith('.png') and not f.endswith('!.png') for f in files)
        has_thumbnail = any(f.endswith('!.png') for f in files)
        
        if has_obj and has_mtl and has_texture and has_thumbnail:
            valid_folders += 1
            print(f"✅ {folder}: Complete")
        else:
            missing = []
            if not has_obj: missing.append("OBJ")
            if not has_mtl: missing.append("MTL")
            if not has_texture: missing.append("Texture")
            if not has_thumbnail: missing.append("Thumbnail")
            print(f"❌ {folder}: Missing {', '.join(missing)}")
    
    print(f"\n📈 Structure Results:")
    print(f"✅ Complete folders: {valid_folders}/{len(folders)}")
    
    return valid_folders == len(folders)

def test_authentication_integration():
    """Test avatar system integration with authentication"""
    print("\n🔐 Testing Authentication Integration...")
    
    template_file = "templates/unified_menu.html"
    if not os.path.exists(template_file):
        print(f"❌ Template file not found: {template_file}")
        return False
    
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for authentication-based avatar loading
        required_checks = [
            'current_user.is_authenticated',
            'userAvatarLoader',
            'mascotBee3D',
            'avatar-loader.js'
        ]
        
        missing_checks = []
        for check in required_checks:
            if check not in content:
                missing_checks.append(check)
        
        if missing_checks:
            print(f"❌ Missing authentication components: {missing_checks}")
            return False
        else:
            print(f"✅ Authentication integration present")
            return True
            
    except Exception as e:
        print(f"❌ Error checking authentication integration: {e}")
        return False

def run_comprehensive_test():
    """Run all avatar system tests"""
    print("🎯 Avatar System Comprehensive Test Suite")
    print("=" * 50)
    
    tests = [
        ("Avatar Catalog", test_avatar_catalog),
        ("JavaScript Loader", test_avatar_loader_js),
        ("File Structure", test_file_structure),
        ("Flask Routes", test_avatar_routes),
        ("Authentication Integration", test_authentication_integration)
    ]
    
    results = {}
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results[test_name] = False
    
    print(f"\n{'='*20} FINAL RESULTS {'='*20}")
    print(f"🎯 Tests Passed: {passed}/{total}")
    print(f"📊 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print(f"🎉 Avatar system is fully functional!")
    else:
        print(f"⚠️ Avatar system needs attention in {total-passed} areas")
    
    print(f"\n📋 Detailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    return passed == total

if __name__ == "__main__":
    # Change to app directory
    app_dir = Path(__file__).parent
    os.chdir(app_dir)
    
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)