#!/usr/bin/env python3
"""
Test BeeDiva Avatar Integration
Simple script to test if BeeDiva appears in the avatar API
"""

import requests
import json
import time

def test_avatar_api():
    """Test the avatar API endpoints"""
    
    base_url = "http://localhost:5000"
    
    # Give the server a moment to fully start
    print("🔄 Waiting for server to be ready...")
    time.sleep(2)
    
    try:
        # Test health endpoint first
        print("🩺 Testing health endpoint...")
        health_response = requests.get(f"{base_url}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Server is healthy")
        else:
            print(f"⚠️ Health check returned {health_response.status_code}")
    
        # Test avatars endpoint
        print("\n🐝 Testing avatars API...")
        avatars_response = requests.get(f"{base_url}/api/avatars", timeout=10)
        
        if avatars_response.status_code == 200:
            avatars = avatars_response.json()
            print(f"✅ Avatar API successful - {len(avatars)} avatars found")
            
            # Look for BeeDiva
            bee_diva = None
            for avatar in avatars:
                if avatar.get('id') == 'bee-diva':
                    bee_diva = avatar
                    break
            
            if bee_diva:
                print("\n🎉 BeeDiva found in avatar list!")
                print(f"   ✅ ID: {bee_diva.get('id')}")
                print(f"   ✅ Name: {bee_diva.get('name')}")
                print(f"   ✅ Category: {bee_diva.get('category')}")
                print(f"   ✅ Folder: {bee_diva.get('folder')}")
                print(f"   ✅ Thumbnail: {bee_diva.get('thumbnail_file')}")
                
                # Test direct avatar info endpoint
                print(f"\n🔍 Testing individual avatar info...")
                avatar_info_response = requests.get(f"{base_url}/api/avatar/bee-diva", timeout=5)
                if avatar_info_response.status_code == 200:
                    avatar_info = avatar_info_response.json()
                    print("✅ Individual avatar info successful")
                    print(f"   📝 Description: {avatar_info.get('description', 'N/A')}")
                else:
                    print(f"⚠️ Individual avatar info failed: {avatar_info_response.status_code}")
            else:
                print("❌ BeeDiva NOT found in avatar list")
                print("\n📋 Available avatars:")
                for avatar in avatars:
                    print(f"   - {avatar.get('id')}: {avatar.get('name')}")
        else:
            print(f"❌ Avatar API failed: {avatars_response.status_code}")
            print(f"   Response: {avatars_response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        print("   Make sure the Flask server is running on port 5000")

if __name__ == '__main__':
    print("🐝 BeeDiva Avatar Integration Test")
    print("=" * 50)
    test_avatar_api()
    print("=" * 50)