#!/usr/bin/env python
"""
Quick test to verify avatar setup for OBJ and GLB formats.
"""
import requests
import json

BASE_URL = "http://localhost:5000"

print("=" * 70)
print("🧪 QUICK AVATAR TEST - OBJ & GLB Preview Setup")
print("=" * 70)

# 1. Test API endpoint
print("\n1️⃣ Testing /api/avatars endpoint...")
response = requests.get(f"{BASE_URL}/api/avatars")
if response.status_code == 200:
    data = response.json()
    avatars = data.get('avatars', [])
    print(f"   ✅ API working - {len(avatars)} avatars returned")
    
    # Count by format
    obj_avatars = [a for a in avatars if a.get('obj_file', '').endswith('.obj')]
    glb_avatars = [a for a in avatars if a.get('obj_file', '').endswith('.glb')]
    
    print(f"\n   📊 Avatar Breakdown:")
    print(f"      • OBJ avatars: {len(obj_avatars)}")
    print(f"      • GLB avatars: {len(glb_avatars)}")
    print(f"      • Total: {len(avatars)}")
    
    # Show sample from each
    if obj_avatars:
        obj_sample = obj_avatars[0]
        print(f"\n   🎭 Sample OBJ Avatar: {obj_sample['name']}")
        print(f"      slug: {obj_sample['slug']}")
        print(f"      model_obj URL: {obj_sample['urls']['model_obj']}")
        print(f"      thumbnail URL: {obj_sample['urls']['thumbnail']}")
    
    if glb_avatars:
        glb_sample = glb_avatars[0]
        print(f"\n   🎭 Sample GLB Avatar: {glb_sample['name']}")
        print(f"      slug: {glb_sample['slug']}")
        print(f"      model_obj URL: {glb_sample['urls']['model_obj']}")
        print(f"      thumbnail URL: {glb_sample['urls']['thumbnail']}")
else:
    print(f"   ❌ API failed - HTTP {response.status_code}")
    print(response.text)

# 2. Test file existence
print("\n2️⃣ Testing file existence...")
session = requests.Session()

if obj_avatars:
    obj_file_url = f"{BASE_URL}{obj_avatars[0]['urls']['model_obj']}"
    response = session.head(obj_file_url)
    status = "✅" if response.status_code == 200 else "❌"
    print(f"   {status} OBJ file: HTTP {response.status_code}")

if glb_avatars:
    glb_file_url = f"{BASE_URL}{glb_avatars[0]['urls']['model_obj']}"
    response = session.head(glb_file_url)
    status = "✅" if response.status_code == 200 else "❌"
    print(f"   {status} GLB file: HTTP {response.status_code}")

# 3. Test Three.js loaders in page
print("\n3️⃣ Checking Three.js loaders on home page...")
response = session.get(f"{BASE_URL}/")
html = response.text
loaders = {
    'Three.js': 'three' in html.lower() and 'three.min.js' in html.lower(),
    'OBJLoader': 'OBJLoader.js' in html,
    'MTLLoader': 'MTLLoader.js' in html,
    'GLTFLoader': 'GLTFLoader.js' in html,
}

for loader, found in loaders.items():
    status = "✅" if found else "❌"
    print(f"   {status} {loader}: {'Found' if found else 'MISSING'}")

print("\n" + "=" * 70)
print("✅ Test Complete - Check results above")
print("=" * 70)
