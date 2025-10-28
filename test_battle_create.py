#!/usr/bin/env python3
"""
Test Battle Creation - Debug Error
"""
import requests
import json

BASE_URL = "http://localhost:5000"

print("\n" + "="*60)
print("TESTING BATTLE CREATION")
print("="*60)

# Test creating a battle without authentication
print("\n[1] Attempting to create battle (without auth)...")
try:
    battle_data = {
        "wordset_name": "Test Battle",
        "is_public": True,
        "allow_guests": True,
        "max_players": 4,
        "mode": "standard"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/battles/create",
        json=battle_data
    )
    
    print(f"    Status Code: {response.status_code}")
    print(f"    Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"    SUCCESS: {data}")
    elif response.status_code == 401:
        print("    ERROR: Requires login (@login_required)")
    else:
        print(f"    ERROR: {response.text}")
        
except Exception as e:
    print(f"    EXCEPTION: {e}")

print("\n" + "="*60)
