#!/usr/bin/env python
"""
Test script to verify GLB avatars are properly integrated and can be selected.
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_glb_avatars():
    print("=" * 70)
    print("🧪 Testing GLB Avatar Integration")
    print("=" * 70)
    
    # Step 1: Get all avatars from API
    print("\n1️⃣ Fetching all avatars from /api/avatars...")
    response = requests.get(f"{BASE_URL}/api/avatars")
    if response.status_code == 200:
        avatars = response.json()['avatars']
        print(f"   ✅ Retrieved {len(avatars)} avatars")
        
        # Separate OBJ and GLB avatars
        obj_avatars = [a for a in avatars if a['obj_file'] and a['obj_file'].endswith('.obj')]
        glb_avatars = [a for a in avatars if a['obj_file'] and a['obj_file'].endswith('.glb')]
        
        print(f"   📊 OBJ avatars: {len(obj_avatars)}")
        print(f"   📊 GLB avatars: {len(glb_avatars)}")
        
        # List some GLB avatars
        if glb_avatars:
            print(f"\n   🎮 GLB Avatars Available:")
            for avatar in glb_avatars[:5]:
                print(f"      • {avatar['name']} ({avatar['slug']})")
                print(f"        URL: {avatar['urls']['model_obj']}")
        
        # Step 2: Test selecting a GLB avatar
        if glb_avatars:
            test_avatar = glb_avatars[0]  # Try first GLB avatar
            print(f"\n2️⃣ Testing GLB avatar selection: {test_avatar['name']}")
            
            # Create a session
            session = requests.Session()
            
            # Test the /test/avatar-picker route to simulate picker interface
            print(f"   Testing avatar picker interface...")
            response = session.get(f"{BASE_URL}/test/avatar-picker")
            if response.status_code == 200:
                print(f"   ✅ Avatar picker page loaded")
                
                # Verify GLB file exists
                glb_url = f"{BASE_URL}{test_avatar['urls']['model_obj']}"
                print(f"\n3️⃣ Verifying GLB file exists: {glb_url}")
                response = session.head(glb_url)
                if response.status_code == 200:
                    print(f"   ✅ GLB file found (HTTP {response.status_code})")
                    print(f"   📦 File size: {response.headers.get('content-length', 'unknown')} bytes")
                else:
                    print(f"   ❌ GLB file not found (HTTP {response.status_code})")
                
                # Verify thumbnail exists
                thumbnail_url = f"{BASE_URL}{test_avatar['urls']['thumbnail']}"
                print(f"\n4️⃣ Verifying thumbnail exists: {thumbnail_url}")
                response = session.head(thumbnail_url)
                if response.status_code == 200:
                    print(f"   ✅ Thumbnail found (HTTP {response.status_code})")
                else:
                    print(f"   ⚠️ Thumbnail not found (HTTP {response.status_code})")
            else:
                print(f"   ❌ Avatar picker page not loaded (HTTP {response.status_code})")
        
        # Step 3: Verify Three.js loaders are loaded
        print(f"\n5️⃣ Checking Three.js script includes in unified_menu.html...")
        response = session.get(f"{BASE_URL}/")
        if response.status_code == 200:
            html = response.text
            loaders = {
                'OBJLoader': 'OBJLoader.js' in html,
                'MTLLoader': 'MTLLoader.js' in html,
                'GLTFLoader': 'GLTFLoader.js' in html,
            }
            
            all_loaded = all(loaders.values())
            for loader, loaded in loaders.items():
                status = "✅" if loaded else "❌"
                print(f"   {status} {loader}: {'Loaded' if loaded else 'NOT FOUND'}")
            
            if not all_loaded:
                print(f"\n   ⚠️  WARNING: Some loaders are missing!")
        
    else:
        print(f"   ❌ Failed to get avatars (HTTP {response.status_code})")
    
    print("\n" + "=" * 70)
    print("✅ GLB Avatar Integration Test Complete!")
    print("=" * 70)

if __name__ == "__main__":
    test_glb_avatars()
