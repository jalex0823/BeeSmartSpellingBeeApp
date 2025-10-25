#!/usr/bin/env python3
"""
Extended test of Meshy API endpoints based on common API patterns
"""

import requests

def test_more_endpoints():
    api_key = "msy_t9FYfPHBWK1c8VBfX0pLxnEZMdWbg0DEc2qz"
    headers = {'Authorization': f'Bearer {api_key}'}
    
    # Try more endpoints based on typical API patterns
    endpoints_to_test = [
        # Version endpoints
        '/v1',
        '/v2', 
        '/api/v1',
        '/api/v2',
        
        # Task/job endpoints (common for AI services)
        '/v1/tasks',
        '/v2/tasks',
        '/v1/jobs',
        '/v2/jobs',
        
        # Upload endpoints
        '/v1/upload',
        '/v2/upload',
        '/v1/file-upload',
        '/v2/file-upload',
        
        # Model endpoints
        '/v1/models',
        '/v2/models',
        '/v1/text-to-3d',
        '/v2/text-to-3d',
        
        # Status/health endpoints
        '/status',
        '/health',
        '/ping',
        '/v1/status',
        '/v2/status',
        
        # Root endpoint
        '/',
        ''
    ]
    
    print("🔍 Testing extended Meshy API endpoints...")
    print("=" * 60)
    
    for endpoint in endpoints_to_test:
        try:
            url = f"https://api.meshy.ai{endpoint}"
            response = requests.get(url, headers=headers, timeout=5)
            
            status_emoji = "✅" if response.status_code == 200 else "⚠️" if response.status_code < 400 else "❌"
            
            print(f"{status_emoji} {endpoint or 'ROOT'}: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   📄 Response: {str(data)[:150]}...")
                except:
                    print(f"   📄 Response: {response.text[:100]}")
            elif response.status_code != 404:
                print(f"   📄 Response: {response.text[:100]}")
                
        except requests.exceptions.RequestException as e:
            print(f"💥 {endpoint or 'ROOT'}: ERROR - {str(e)}")
    
    print("\n🔑 Testing API key validation...")
    # Test with wrong API key format
    wrong_headers = {'Authorization': 'Bearer invalid_key'}
    try:
        response = requests.get('https://api.meshy.ai/v1/models', headers=wrong_headers, timeout=5)
        print(f"Wrong API key test: {response.status_code} - {response.text[:50]}")
    except Exception as e:
        print(f"Wrong API key test failed: {e}")

if __name__ == "__main__":
    test_more_endpoints()