#!/usr/bin/env python3
"""
Sync avatar names in Railway database with catalog names (Apple Store compliance).
Run this AFTER deploying to Railway to update DB avatar names.
"""

import requests
import sys

# Railway URL
BASE_URL = "https://beesmartspellingbee.up.railway.app"

def sync_avatar_names(username, password):
    """Login and trigger avatar name sync"""
    
    session = requests.Session()
    
    # 1. Login as admin
    print(f"🔐 Logging in as {username}...")
    login_response = session.post(
        f"{BASE_URL}/login",
        data={
            "username": username,
            "password": password
        },
        allow_redirects=False
    )
    
    if login_response.status_code not in [200, 302]:
        print(f"❌ Login failed: {login_response.status_code}")
        return False
    
    print("✅ Logged in successfully")
    
    # 2. Call sync endpoint
    print("\n🔄 Syncing avatar names with catalog...")
    sync_response = session.post(f"{BASE_URL}/admin/sync-avatar-names")
    
    if sync_response.status_code != 200:
        print(f"❌ Sync failed: {sync_response.status_code}")
        print(sync_response.text)
        return False
    
    result = sync_response.json()
    
    if result['status'] == 'success':
        print(f"\n✅ Sync completed!")
        print(f"   Updated {result['updated_count']} avatars\n")
        
        if result['updated_avatars']:
            print("📝 Changes:")
            for update in result['updated_avatars']:
                print(f"   {update['slug']:20} | {update['old_name']:30} → {update['new_name']}")
        else:
            print("   (No changes needed - all names already match catalog)")
        
        return True
    else:
        print(f"❌ Sync failed: {result.get('message', 'Unknown error')}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 sync_railway_avatars.py <admin_username> <admin_password>")
        print("\nExample:")
        print("  python3 sync_railway_avatars.py bigdaddy your_password")
        print("\n⚠️  Remember to update BASE_URL in this script with your Railway URL!")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    success = sync_avatar_names(username, password)
    sys.exit(0 if success else 1)
