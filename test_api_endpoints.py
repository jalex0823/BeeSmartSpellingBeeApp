#!/usr/bin/env python3
"""
Quick Avatar API Test
Tests the fixed avatar endpoints
"""

import time
import subprocess
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def test_endpoints_with_retry():
    """Test avatar endpoints with retry logic"""
    print("🔧 Testing Avatar API Endpoints")
    print("=" * 40)
    
    # Setup requests session with retry
    session = requests.Session()
    retry_strategy = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    
    base_url = "http://localhost:5000"
    
    # Test 1: Avatar catalog endpoint
    try:
        print("🧪 Testing /api/avatars...")
        r = session.get(f"{base_url}/api/avatars", timeout=10)
        if r.status_code == 200:
            data = r.json()
            print(f"✅ /api/avatars: {data['status']} - {data['total']} avatars")
        else:
            print(f"❌ /api/avatars: HTTP {r.status_code}")
    except Exception as e:
        print(f"❌ /api/avatars: {str(e)}")
    
    # Test 2: Individual avatar endpoint  
    try:
        print("🧪 Testing /api/avatar/professor-bee...")
        r = session.get(f"{base_url}/api/avatar/professor-bee", timeout=10)
        if r.status_code == 200:
            data = r.json()
            print(f"✅ /api/avatar/professor-bee: {data['status']} - {data['avatar']['name']}")
        else:
            print(f"❌ /api/avatar/professor-bee: HTTP {r.status_code}")
    except Exception as e:
        print(f"❌ /api/avatar/professor-bee: {str(e)}")
    
    # Test 3: Invalid avatar (should return 404)
    try:
        print("🧪 Testing /api/avatar/invalid-bee...")
        r = session.get(f"{base_url}/api/avatar/invalid-bee", timeout=10)
        if r.status_code == 404:
            print(f"✅ /api/avatar/invalid-bee: Correctly returns 404")
        else:
            print(f"❌ /api/avatar/invalid-bee: Expected 404, got {r.status_code}")
    except Exception as e:
        print(f"❌ /api/avatar/invalid-bee: {str(e)}")
    
    print("\n🎯 API Endpoint Tests Complete!")

if __name__ == "__main__":
    test_endpoints_with_retry()