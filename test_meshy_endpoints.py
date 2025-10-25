#!/usr/bin/env python3
"""
Quick test of Meshy API endpoints to find the correct one
"""

import requests

def test_meshy_endpoints():
    api_key = "msy_t9FYfPHBWK1c8VBfX0pLxnEZMdWbg0DEc2qz"
    headers = {'Authorization': f'Bearer {api_key}'}
    
    endpoints_to_test = [
        '/v2/user',
        '/v1/user', 
        '/v2/account',
        '/v1/account',
        '/v2/credits',
        '/v1/credits',
        '/v2/me',
        '/v1/me',
        '/v2/user/profile',
        '/v1/user/profile'
    ]
    
    print("🔍 Testing Meshy API endpoints...")
    print("=" * 50)
    
    for endpoint in endpoints_to_test:
        try:
            url = f"https://api.meshy.ai{endpoint}"
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {endpoint}: {response.status_code} - SUCCESS")
                try:
                    data = response.json()
                    print(f"   Response: {data}")
                except:
                    print(f"   Response: {response.text[:100]}")
            elif response.status_code == 401:
                print(f"🔑 {endpoint}: {response.status_code} - UNAUTHORIZED (API key issue)")
            elif response.status_code == 404:
                print(f"❌ {endpoint}: {response.status_code} - NOT FOUND")
            else:
                print(f"⚠️ {endpoint}: {response.status_code} - {response.text[:50]}")
                
        except requests.exceptions.RequestException as e:
            print(f"💥 {endpoint}: ERROR - {str(e)}")
    
    print("\n🌐 Testing basic connectivity...")
    try:
        response = requests.get('https://httpbin.org/status/200', timeout=5)
        print(f"✅ Internet connectivity: OK ({response.status_code})")
    except Exception as e:
        print(f"❌ Internet connectivity: FAILED - {e}")

if __name__ == "__main__":
    test_meshy_endpoints()