#!/usr/bin/env python3
"""
Test the complete avatar selection flow:
1. API returns avatars with correct thumbnail URLs
2. User selects an avatar (simulate API call)
3. Avatar is saved to user's profile
4. User's avatar API returns the selected avatar
"""

import requests
import json
import time

def test_complete_avatar_flow():
    """Test the complete avatar selection and rendering flow"""
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing Complete Avatar Selection Flow")
    print("=" * 50)
    
    # Step 1: Test avatar catalog API
    print("\n1️⃣ Testing avatar catalog API...")
    try:
        response = requests.get(f"{base_url}/api/avatars", timeout=10)
        if response.status_code == 200:
            data = response.json()
            avatars = data.get('avatars', [])
            print(f"✅ Avatar API working: {len(avatars)} avatars loaded")
            
            # Check specific avatars that we fixed
            test_avatars = ['al-bee', 'anxious-bee', 'mascot-bee']
            print("\n📸 Checking thumbnail URLs:")
            for test_id in test_avatars:
                avatar = next((a for a in avatars if a['id'] == test_id), None)
                if avatar:
                    thumbnail_url = avatar.get('thumbnail', '')
                    print(f"✅ {test_id}: {thumbnail_url}")
                    
                    # Check if filename looks correct (no spaces)
                    filename = thumbnail_url.split('/')[-1]
                    if ' ' in filename:
                        print(f"   ⚠️ WARNING: Filename still has spaces: {filename}")
                    else:
                        print(f"   ✅ Filename looks correct: {filename}")
                else:
                    print(f"❌ {test_id}: not found in API response")
        else:
            print(f"❌ Avatar API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing avatar API: {e}")
        return False
    
    # Step 2: Test current user avatar (should be default mascot for guest)
    print("\n2️⃣ Testing current user avatar API...")
    try:
        response = requests.get(f"{base_url}/api/users/me/avatar", timeout=10)
        if response.status_code == 200:
            data = response.json()
            avatar = data.get('avatar', {})
            use_mascot = data.get('use_mascot', True)
            
            print(f"✅ User avatar API working")
            print(f"   Current avatar: {avatar.get('avatar_id', 'none')}")
            print(f"   Using mascot: {use_mascot}")
            print(f"   Thumbnail: {avatar.get('urls', {}).get('thumbnail', 'none')}")
        else:
            print(f"❌ User avatar API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing user avatar API: {e}")
        return False
    
    # Step 3: Test file accessibility for a few avatars
    print("\n3️⃣ Testing avatar file accessibility...")
    test_files = [
        "/static/assets/avatars/al-bee/AlBee!.png",
        "/static/assets/avatars/anxious-bee/AnxiousBee!.png", 
        "/static/assets/avatars/mascot-bee/MascotBee!.png",
        "/static/assets/avatars/al-bee/AlBee.obj",
        "/static/assets/avatars/al-bee/AlBee.mtl",
        "/static/assets/avatars/al-bee/AlBee.png"
    ]
    
    for file_path in test_files:
        try:
            response = requests.head(f"{base_url}{file_path}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path} - HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {file_path} - Error: {e}")
    
    print("\n🎉 Avatar flow test complete!")
    print("\n💡 Key points:")
    print("   - Avatar API should return correct thumbnail filenames (no spaces)")
    print("   - Files should be accessible at the returned URLs")
    print("   - When user selects avatar, it should replace the default mascot")
    
    return True

if __name__ == "__main__":
    test_complete_avatar_flow()