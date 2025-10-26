#!/usr/bin/env python3
"""
Quick Railway API test
"""

import requests
import time

def quick_railway_test():
    base_url = "https://beesmart.up.railway.app"
    
    print("🚂 Quick Railway API Test")
    print("=" * 40)
    
    # Test health endpoint
    print("🏥 Testing health...")
    try:
        start = time.time()
        health = requests.get(f"{base_url}/health", timeout=10)
        elapsed = time.time() - start
        print(f"✅ Health: {health.status_code} ({elapsed:.2f}s)")
    except Exception as e:
        print(f"❌ Health failed: {e}")
        return
    
    # Test avatars API
    print("🐝 Testing avatars API...")
    try:
        start = time.time()
        avatars = requests.get(f"{base_url}/api/avatars", timeout=20)
        elapsed = time.time() - start
        
        if avatars.status_code == 200:
            data = avatars.json()
            count = len(data.get('avatars', []))
            print(f"✅ Avatars: {avatars.status_code} ({elapsed:.2f}s)")
            print(f"📊 Found {count} avatars")
            
            # Quick test of a few avatars
            test_ids = ['al-bee', 'astro-bee', 'diva-bee']
            found_count = 0
            
            for avatar in data.get('avatars', []):
                if avatar.get('id') in test_ids:
                    found_count += 1
                    avatar_id = avatar.get('id')
                    folder = avatar.get('folder', 'N/A')
                    print(f"   ✅ {avatar_id} → {folder}")
            
            print(f"🎯 Test avatars found: {found_count}/{len(test_ids)}")
            
            if count >= 20 and found_count == len(test_ids):
                print("\n🎉 Railway avatar system is working!")
                return True
            else:
                print("\n⚠️ Some issues detected")
                return False
                
        else:
            print(f"❌ Avatars: {avatars.status_code} ({elapsed:.2f}s)")
            return False
            
    except Exception as e:
        print(f"❌ Avatars failed: {e}")
        return False

if __name__ == "__main__":
    quick_railway_test()