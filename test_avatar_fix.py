#!/usr/bin/env python3
"""
Test the avatar API endpoint to verify the thumbnail fix worked
"""
import requests
import json

def test_avatar_api():
    """Test the /api/avatars endpoint"""
    print("🧪 Testing /api/avatars endpoint...")
    
    try:
        response = requests.get('http://localhost:5000/api/avatars', timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)
            print(f"Total avatars: {total}")
            
            # Check a few specific avatars
            avatars = data.get('avatars', [])
            test_avatars = ['al-bee', 'anxious-bee', 'mascot-bee']
            
            print("\n📸 Thumbnail URLs:")
            for test_id in test_avatars:
                avatar = next((a for a in avatars if a['id'] == test_id), None)
                if avatar:
                    thumbnail = avatar['thumbnail']
                    print(f"✅ {test_id}: {thumbnail}")
                    
                    # Check if filename has spaces (should not)
                    filename = thumbnail.split('/')[-1]
                    if ' ' in filename:
                        print(f"   ⚠️ Filename still has spaces: {filename}")
                    else:
                        print(f"   ✅ Filename looks correct: {filename}")
                else:
                    print(f"❌ {test_id}: not found")
                    
            # Show all avatars briefly
            print(f"\n📋 All {total} avatars:")
            for avatar in avatars[:10]:  # Show first 10
                print(f"   {avatar['id']}: {avatar['thumbnail'].split('/')[-1]}")
            if total > 10:
                print(f"   ... and {total - 10} more")
                
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the Flask app is running on localhost:5000")
        print("   Start the app with: python AjaSpellBApp.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_avatar_api()