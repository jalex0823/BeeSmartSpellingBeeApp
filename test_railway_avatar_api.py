#!/usr/bin/env python3
"""
Test Railway Avatar API - Check what the API is returning
"""
import requests
import json

BASE_URL = "https://beesmart.up.railway.app"

print("🔍 Testing Railway Avatar API...")
print(f"🌐 Base URL: {BASE_URL}\n")

try:
    response = requests.get(f"{BASE_URL}/api/avatars", timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get('status') == 'success':
            avatars = data.get('avatars', [])
            print(f"✅ API returned {len(avatars)} avatars\n")
            
            # Check the 15 previously broken avatars
            broken_slugs = ['astro-bee', 'biker-bee', 'cool-bee', 'seabea', 'superbee']
            
            for slug in broken_slugs:
                avatar = next((a for a in avatars if a['id'] == slug), None)
                if avatar:
                    print(f"📝 {avatar['name']} ({slug}):")
                    urls = avatar.get('urls', {})
                    print(f"   OBJ: {urls.get('model_obj', 'MISSING')}")
                    print(f"   MTL: {urls.get('model_mtl', 'MISSING')}")
                    print(f"   Texture: {urls.get('texture', 'MISSING')}")
                    print()
        else:
            print(f"❌ API returned error: {data}")
    else:
        print(f"❌ API request failed: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
        
except Exception as e:
    print(f"❌ Error: {e}")
