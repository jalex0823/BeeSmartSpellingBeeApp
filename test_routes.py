#!/usr/bin/env python3
"""
Inspect all registered Flask routes
"""
import requests
from flask import Flask
import sys
sys.path.insert(0, '/cUsers/jeff/Dropbox/BeeSmartSpellingBeeApp')

# Try to get routing info from running app
print("\n" + "="*60)
print("CHECKING AVAILABLE ENDPOINTS")
print("="*60)

endpoints_to_test = [
    '/api/battles/live',
    '/api/battles/create', 
    '/api/battles/ABC123',
    '/api/battles/ABC123/join',
    '/api/battles/ABC123/leave',
    '/api/battles/my',
    '/battles',
]

for endpoint in endpoints_to_test:
    try:
        if endpoint.endswith('/my'):
            method = 'GET'
        elif endpoint.endswith('/create'):
            method = 'POST'
        elif endpoint.endswith('/join'):
            method = 'POST'
        elif endpoint.endswith('/leave'):
            method = 'POST'
        else:
            method = 'GET'
        
        url = f"http://localhost:5000{endpoint}"
        if method == 'GET':
            response = requests.get(url)
        else:
            response = requests.post(url, json={})
        
        print(f"\n{method} {endpoint}")
        print(f"  Status: {response.status_code}")
        if response.status_code in [200, 201]:
            print(f"  ✅ Working")
        elif response.status_code == 401:
            print(f"  ⚠️  Requires login")
        else:
            print(f"  ❌ Error: {response.text[:100]}")
            
    except Exception as e:
        print(f"\n{method} {endpoint}")
        print(f"  ❌ Connection error: {str(e)[:80]}")

print("\n" + "="*60)
