"""
Smoke Test: Avatar Picker Access for All User Roles
Tests that each user role gets correct avatar access
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from avatar_catalog import AVATAR_CATALOG

def test_unlock_logic():
    """Test the avatar unlock logic for different user profiles"""
    
    print("=" * 80)
    print("AVATAR PICKER SMOKE TEST - ALL USER ROLES")
    print("=" * 80)
    
    # Import the unlock function
    from AjaSpellBApp import _is_avatar_unlocked_for_user
    
    # Test scenarios
    scenarios = [
        {
            "name": "GUEST USER (Not Logged In)",
            "role": "guest",
            "user": None,
            "expected_unlocked": 0,  # Guest logic returns all locked; API layer shows mascot
            "description": "Guest users - unlock function returns all locked (API shows mascot only)"
        },
        {
            "name": "STUDENT (New, 0 points, no purchases)",
            "role": "student",
            "user": type('User', (), {
                'honey_points': 0,
                'purchased_avatars': [],
                'premium_member': False
            })(),
            "expected_unlocked": 6,  # 6 default_free avatars
            "description": "New students get 6 default free avatars"
        },
        {
            "name": "STUDENT (11,500 points, earned avatars)",
            "role": "student",
            "user": type('User', (), {
                'honey_points': 11500,
                'purchased_avatars': [],
                'premium_member': False
            })(),
            "expected_unlocked": 13,  # 6 default_free + 7 earned
            "description": "Students with 11,500 points unlock 13 avatars total"
        },
        {
            "name": "TEACHER (500 points, 1 purchase)",
            "role": "teacher",
            "user": type('User', (), {
                'honey_points': 500,
                'purchased_avatars': ['super-bee'],
                'premium_member': False
            })(),
            "expected_unlocked": 7,  # 6 default_free + 1 purchased
            "description": "Teachers can purchase premium avatars"
        },
        {
            "name": "PARENT (0 points, 0 purchases)",
            "role": "parent",
            "user": type('User', (), {
                'honey_points': 0,
                'purchased_avatars': [],
                'premium_member': False
            })(),
            "expected_unlocked": 6,  # 6 default_free
            "description": "Parents get same default 6 free avatars"
        },
        {
            "name": "ADMIN USER",
            "role": "admin",
            "user": type('User', (), {
                'honey_points': 0,
                'purchased_avatars': [],
                'premium_member': False
            })(),
            "expected_unlocked": 40,  # ALL avatars (40 total in catalog)
            "description": "Admins bypass all locks - full catalog access"
        }
    ]
    
    all_passed = True
    
    for scenario in scenarios:
        print(f"\n{'='*80}")
        print(f"TEST: {scenario['name']}")
        print(f"{'='*80}")
        print(f"Description: {scenario['description']}")
        print(f"Role: {scenario['role']}")
        
        if scenario['user']:
            print(f"Honey Points: {getattr(scenario['user'], 'honey_points', 0):,}")
            print(f"Purchased: {len(getattr(scenario['user'], 'purchased_avatars', []))}")
        
        # Count unlocked avatars
        unlocked = []
        locked = []
        
        for avatar in AVATAR_CATALOG:
            result = _is_avatar_unlocked_for_user(avatar, scenario['role'], scenario['user'])
            if result['unlocked']:
                unlocked.append(avatar['name'])
            else:
                locked.append(avatar['name'])
        
        actual_unlocked = len(unlocked)
        expected_unlocked = scenario['expected_unlocked']
        
        print(f"\nResults:")
        print(f"  Unlocked: {actual_unlocked}")
        print(f"  Locked: {len(locked)}")
        print(f"  Expected: {expected_unlocked}")
        
        # Verify expectation
        if actual_unlocked == expected_unlocked:
            print(f"  ✅ PASS - Correct number of unlocked avatars")
            
            # Show sample unlocked avatars
            if len(unlocked) <= 15:
                print(f"\n  Unlocked Avatars:")
                for name in unlocked:
                    print(f"    ✅ {name}")
            else:
                print(f"\n  Unlocked Avatars (showing first 10):")
                for name in unlocked[:10]:
                    print(f"    ✅ {name}")
                print(f"    ... and {len(unlocked) - 10} more")
        else:
            print(f"  ❌ FAIL - Expected {expected_unlocked}, got {actual_unlocked}")
            all_passed = False
            
            # Show difference
            diff = actual_unlocked - expected_unlocked
            if diff > 0:
                print(f"  ⚠️  {diff} extra avatars unlocked")
            else:
                print(f"  ⚠️  {abs(diff)} fewer avatars unlocked")
    
    # Final summary
    print(f"\n{'='*80}")
    print("SMOKE TEST SUMMARY")
    print(f"{'='*80}")
    
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("\nAvatar access is correctly configured for all user roles:")
        print("  ✅ Guest: All locked in unlock logic (API shows mascot only)")
        print("  ✅ Student: 6 free (1 mascot + 5 default) + earn via points")
        print("  ✅ Teacher: 6 free + earn/purchase")
        print("  ✅ Parent: 6 free + earn/purchase")
        print("  ✅ Admin: Full catalog (all 40 avatars)")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease review the unlock logic in _is_avatar_unlocked_for_user()")
        return 1

if __name__ == "__main__":
    sys.exit(test_unlock_logic())
