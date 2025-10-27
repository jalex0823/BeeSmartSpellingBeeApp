#!/usr/bin/env python3
"""
Quick test to debug the Meshy API connection issue
"""

import requests
import sys

def test_api_key(api_key):
    """Test the API key with all known endpoints"""
    print(f"🔑 Testing API Key: {api_key[:8]}...{api_key[-4:]}")
    print("=" * 60)
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Test the exact endpoints the GUI is using
    endpoints_to_test = [
        'https://api.meshy.ai/openapi/v1/image-to-3d',  # Main endpoint for your projects
        'https://api.meshy.ai/openapi/v2/text-to-3d',   # Secondary endpoint
        'https://api.meshy.ai/v1/user',                  # Account info
        'https://api.meshy.ai/v1/account',               # Account info
    ]
    
    for endpoint in endpoints_to_test:
        try:
            print(f"📡 Testing: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"   ✅ SUCCESS: Found {len(data)} items")
                    if len(data) > 0:
                        print(f"   📋 Sample item keys: {list(data[0].keys())[:5]}")
                elif isinstance(data, dict):
                    print(f"   ✅ SUCCESS: Dict with keys: {list(data.keys())}")
                    # Check for common project container keys
                    for key in ['result', 'data', 'tasks', 'projects']:
                        if key in data:
                            items = data[key]
                            if isinstance(items, list):
                                print(f"   📋 Found {len(items)} items in '{key}' field")
                else:
                    print(f"   ⚠️ Unexpected response type: {type(data)}")
            elif response.status_code == 401:
                print(f"   ❌ UNAUTHORIZED - API key invalid")
            elif response.status_code == 404:
                print(f"   ❌ NOT FOUND - endpoint doesn't exist")
            else:
                print(f"   ❌ ERROR: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {str(e)}")
        
        print()

def main():
    # Test with your current API key
    api_key = "msy_6iDQC1PM3YYIrZkautmQrKMsiLSB1Nyerw0F"
    test_api_key(api_key)
    
    print("\n" + "=" * 60)
    print("🔍 DIAGNOSIS:")
    print("=" * 60)
    print("1. If you see 'Found 0 items' for all endpoints = API key works but wrong account")
    print("2. If you see 'UNAUTHORIZED' = API key is invalid")
    print("3. If you see 'Found X items' where X > 0 = SUCCESS! Found your projects")
    print("4. If you see 'NOT FOUND' = Wrong endpoint (shouldn't happen)")

if __name__ == "__main__":
    main()