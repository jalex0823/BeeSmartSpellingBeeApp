#!/usr/bin/env python3
"""
Test Battle of the Bees Functionality
Comprehensive test to verify battles system is working end-to-end
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_battles_page():
    """Test 1: Verify battles page loads"""
    print_section("TEST 1: Battles Page")
    try:
        response = requests.get(f"{BASE_URL}/battles")
        if response.status_code == 200:
            print("✅ Battles page loads successfully")
            return True
        else:
            print(f"❌ Battles page returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error loading battles page: {e}")
        return False

def test_create_battle():
    """Test 2: Create a new battle session"""
    print_section("TEST 2: Create Battle Session")
    try:
        battle_data = {
            "is_public": True,
            "allow_guests": True,
            "max_players": 4,
            "grade_range": "3-5",
            "mode": "standard",
            "wordset": "default"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/battles/create",
            json=battle_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            battle_code = data.get('code')
            battle_id = data.get('id')
            print(f"✅ Battle created successfully")
            print(f"   Battle Code: {battle_code}")
            print(f"   Battle ID: {battle_id}")
            print(f"   Status: {data.get('status')}")
            print(f"   Max Players: {data.get('max_players')}")
            print(f"   Mode: {data.get('mode')}")
            return battle_code, battle_id
        else:
            print(f"❌ Failed to create battle: {response.status_code}")
            print(f"   Response: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Error creating battle: {e}")
        return None, None

def test_list_battles():
    """Test 3: List active battles"""
    print_section("TEST 3: List Active Battles")
    try:
        response = requests.get(f"{BASE_URL}/api/battles")
        if response.status_code == 200:
            battles = response.json()
            print(f"✅ Retrieved {len(battles)} active battle(s)")
            for battle in battles:
                print(f"   • {battle.get('code')} - {battle.get('status')} - {battle.get('current_players')}/{battle.get('max_players')} players")
            return True
        else:
            print(f"❌ Failed to list battles: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error listing battles: {e}")
        return False

def test_join_battle(battle_code):
    """Test 4: Join a battle as a guest"""
    print_section("TEST 4: Join Battle as Guest")
    try:
        join_data = {
            "code": battle_code,
            "display_name": "TestBee"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/battles/join",
            json=join_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully joined battle {battle_code}")
            print(f"   Player Name: {data.get('player', {}).get('display_name')}")
            print(f"   Battle Status: {data.get('battle', {}).get('status')}")
            print(f"   Current Players: {data.get('battle', {}).get('current_players')}")
            return True
        else:
            print(f"❌ Failed to join battle: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error joining battle: {e}")
        return False

def test_get_battle_details(battle_code):
    """Test 5: Get battle details"""
    print_section("TEST 5: Get Battle Details")
    try:
        response = requests.get(f"{BASE_URL}/api/battles/{battle_code}")
        if response.status_code == 200:
            battle = response.json()
            print(f"✅ Battle details retrieved")
            print(f"   Code: {battle.get('code')}")
            print(f"   Status: {battle.get('status')}")
            print(f"   Players: {battle.get('current_players')}/{battle.get('max_players')}")
            print(f"   Mode: {battle.get('mode')}")
            print(f"   Grade Range: {battle.get('grade_range')}")
            print(f"   Public: {battle.get('is_public')}")
            print(f"   Allow Guests: {battle.get('allow_guests')}")
            return True
        else:
            print(f"❌ Failed to get battle details: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting battle details: {e}")
        return False

def test_start_battle(battle_code):
    """Test 6: Start the battle"""
    print_section("TEST 6: Start Battle")
    try:
        response = requests.post(
            f"{BASE_URL}/api/battles/{battle_code}/start",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Battle started successfully")
            print(f"   Status: {data.get('status')}")
            print(f"   Started At: {data.get('started_at')}")
            return True
        else:
            print(f"❌ Failed to start battle: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error starting battle: {e}")
        return False

def test_battle_api_endpoints():
    """Test 7: Check all battle API endpoints are registered"""
    print_section("TEST 7: Battle API Endpoints")
    endpoints = [
        "/api/battles",
        "/api/battles/create",
    ]
    
    all_working = True
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            # Accept 200, 405 (Method Not Allowed), or 400 as valid
            if response.status_code in [200, 405, 400]:
                print(f"✅ {endpoint} - Endpoint exists")
            else:
                print(f"⚠️  {endpoint} - Status {response.status_code}")
                all_working = False
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
            all_working = False
    
    return all_working

def run_all_tests():
    """Run all battle functionality tests"""
    print("\n" + "="*60)
    print("  🐝 BATTLE OF THE BEES - FUNCTIONALITY TEST")
    print("="*60)
    print(f"  Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    results = {}
    
    # Test 1: Battles page
    results['page'] = test_battles_page()
    
    # Test 2: Create battle
    battle_code, battle_id = test_create_battle()
    results['create'] = battle_code is not None
    
    # Test 3: List battles
    results['list'] = test_list_battles()
    
    # Test 4 & 5: Join and get details (only if battle created)
    if battle_code:
        results['join'] = test_join_battle(battle_code)
        results['details'] = test_get_battle_details(battle_code)
        
        # Test 6: Start battle (only if joined successfully)
        if results.get('join'):
            results['start'] = test_start_battle(battle_code)
        else:
            results['start'] = False
    else:
        results['join'] = False
        results['details'] = False
        results['start'] = False
    
    # Test 7: API endpoints
    results['endpoints'] = test_battle_api_endpoints()
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name.upper()}")
    
    print(f"\n  Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 ALL TESTS PASSED! Battle of the Bees is fully functional!")
        return True
    else:
        print(f"\n  ⚠️  {total - passed} test(s) failed. Check errors above.")
        return False

if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        exit(1)
