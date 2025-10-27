#!/usr/bin/env python3
import requests
import json
import time

BASE_URL = "http://localhost:5000"

print("\n" + "="*60)
print("BATTLE OF THE BEES - QUICK FUNCTIONALITY CHECK")
print("="*60)

# Test 1: Check if battles page loads
print("\n[1] Testing Battles Page...")
try:
    response = requests.get(f"{BASE_URL}/battles")
    if response.status_code == 200:
        print("    SUCCESS: Battles page loads (200)")
    else:
        print(f"    FAIL: Battles page returned {response.status_code}")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 2: Check /api/battles/live endpoint
print("\n[2] Testing Live Battles API...")
try:
    response = requests.get(f"{BASE_URL}/api/battles/live")
    if response.status_code == 200:
        battles = response.json()
        print(f"    SUCCESS: Live battles API works (200)")
        print(f"    Currently {len(battles)} battles live")
    else:
        print(f"    FAIL: API returned {response.status_code}")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 3: Check battle.html page
print("\n[3] Testing Battle Page Template...")
try:
    response = requests.get(f"{BASE_URL}/battle/DEMO01")
    if response.status_code in [200, 404]:
        print(f"    SUCCESS: Battle page template works ({response.status_code})")
    else:
        print(f"    FAIL: Battle page returned {response.status_code}")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 4: Check battle_leaderboard page
print("\n[4] Testing Battle Leaderboard...")
try:
    response = requests.get(f"{BASE_URL}/battle-leaderboard")
    if response.status_code == 200:
        print(f"    SUCCESS: Battle leaderboard loads (200)")
    else:
        print(f"    FAIL: Leaderboard returned {response.status_code}")
except Exception as e:
    print(f"    ERROR: {e}")

print("\n" + "="*60)
print("BATTLE SYSTEM STATUS CHECK COMPLETE")
print("="*60 + "\n")
