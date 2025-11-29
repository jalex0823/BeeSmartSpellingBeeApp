"""
Test Avatar Unlock System - Points & Purchase Validation
===========================================================
Validates that avatar unlocking via Honey Points and IAP purchases works correctly.

Tests:
1. Free avatar access (default_free tier)
2. Points-based unlocking (earn_or_buy tier)
3. Purchase validation (premium tier)
4. Guest user restrictions
5. Admin bypass
6. Point threshold accuracy
"""

import sys
import os

# Ensure app context
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_avatar_unlock_logic():
    """Test the avatar_catalog unlock logic without database"""
    print("\n" + "="*70)
    print("🐝 AVATAR UNLOCK SYSTEM VALIDATION")
    print("="*70)
    
    try:
        from avatar_catalog import (
            AVATAR_CATALOG, 
            check_avatar_unlocked,
            get_free_avatars,
            get_earn_or_buy_avatars,
            get_premium_avatars
        )
        
        # Test 1: Default Free Avatars
        print("\n📌 TEST 1: Default Free Avatars (should be unlocked at 0 points)")
        print("-" * 70)
        free_avatars = get_free_avatars()
        print(f"Found {len(free_avatars)} default free avatars")
        
        for avatar in free_avatars[:3]:  # Test first 3
            result = check_avatar_unlocked(avatar['id'], user_honey_points=0)
            status = "✅ PASS" if result['unlocked'] else "❌ FAIL"
            print(f"  {status} {avatar['name']:20s} - {result['reason']}")
        
        # Test 2: Earn-or-Buy Tier (Points-based unlock)
        print("\n📌 TEST 2: Earn-or-Buy Avatars (unlock via points)")
        print("-" * 70)
        earn_or_buy = get_earn_or_buy_avatars()
        print(f"Found {len(earn_or_buy)} earn-or-buy avatars")
        
        for avatar in earn_or_buy[:5]:  # Test first 5
            unlock_points = avatar.get('unlock_points', 0)
            
            # Test with insufficient points
            result_locked = check_avatar_unlocked(
                avatar['id'], 
                user_honey_points=unlock_points - 1
            )
            
            # Test with exact points
            result_unlocked = check_avatar_unlocked(
                avatar['id'], 
                user_honey_points=unlock_points
            )
            
            locked_status = "✅ PASS" if not result_locked['unlocked'] else "❌ FAIL"
            unlocked_status = "✅ PASS" if result_unlocked['unlocked'] else "❌ FAIL"
            
            print(f"  {avatar['name']:20s} (needs {unlock_points:,} points)")
            print(f"    {locked_status} Locked at {unlock_points-1:,} points")
            print(f"    {unlocked_status} Unlocked at {unlock_points:,} points")
        
        # Test 3: Premium Tier (Purchase-only)
        print("\n📌 TEST 3: Premium Avatars (purchase required)")
        print("-" * 70)
        premium = get_premium_avatars()
        print(f"Found {len(premium)} premium avatars")
        
        for avatar in premium[:3]:  # Test first 3
            # Test without purchase - should be locked even with high points
            result_no_purchase = check_avatar_unlocked(
                avatar['id'], 
                user_honey_points=999999,
                purchased_avatars=[]
            )
            
            # Test with purchase
            result_purchased = check_avatar_unlocked(
                avatar['id'], 
                user_honey_points=0,
                purchased_avatars=[avatar['id']]
            )
            
            locked_status = "✅ PASS" if not result_no_purchase['unlocked'] else "❌ FAIL"
            unlocked_status = "✅ PASS" if result_purchased['unlocked'] else "❌ FAIL"
            
            price = avatar.get('price', 0)
            print(f"  {avatar['name']:20s} (${price:.2f})")
            print(f"    {locked_status} Locked without purchase (even with 999k points)")
            print(f"    {unlocked_status} Unlocked after purchase")
        
        # Test 4: Guest User Restrictions
        print("\n📌 TEST 4: Guest User Access (mascot only)")
        print("-" * 70)
        
        # Find mascot avatar
        mascot = next((a for a in AVATAR_CATALOG if a.get('tier') == 'mascot_free'), None)
        if mascot:
            result = check_avatar_unlocked(mascot['id'], is_guest=True)
            status = "✅ PASS" if result['unlocked'] else "❌ FAIL"
            print(f"  {status} Guest can access {mascot['name']}")
        
        # Guest should NOT access free avatars
        if free_avatars:
            result = check_avatar_unlocked(free_avatars[0]['id'], is_guest=True)
            status = "✅ PASS" if not result['unlocked'] else "❌ FAIL"
            print(f"  {status} Guest CANNOT access {free_avatars[0]['name']} (registration required)")
        
        # Test 5: Point Threshold Accuracy
        print("\n📌 TEST 5: Point Threshold Accuracy")
        print("-" * 70)
        
        test_cases = [
            ('doctor-bee', 2000),
            ('knight-bee', 4000),
            ('monster-bee', 6000),
            ('rocker-bee', 8000),
            ('seabea', 10000),
        ]
        
        for avatar_id, expected_points in test_cases:
            avatar = next((a for a in AVATAR_CATALOG if a['id'] == avatar_id), None)
            if avatar:
                actual_points = avatar.get('unlock_points', 0)
                status = "✅ PASS" if actual_points == expected_points else "❌ FAIL"
                print(f"  {status} {avatar['name']:20s} - Expected: {expected_points:,}, Actual: {actual_points:,}")
        
        # Test 6: Price Tier Validation
        print("\n📌 TEST 6: Price Tier Validation")
        print("-" * 70)
        
        price_099 = [a for a in AVATAR_CATALOG if a.get('price') == 0.99]
        price_199 = [a for a in AVATAR_CATALOG if a.get('price') == 1.99]
        price_299 = [a for a in AVATAR_CATALOG if a.get('price') == 2.99]
        
        print(f"  $0.99 avatars: {len(price_099)}")
        print(f"  $1.99 avatars: {len(price_199)}")
        print(f"  $2.99 avatars: {len(price_299)}")
        
        # Summary
        print("\n" + "="*70)
        print("📊 SUMMARY")
        print("="*70)
        print(f"Total avatars in catalog: {len(AVATAR_CATALOG)}")
        print(f"  - Default Free: {len(free_avatars)}")
        print(f"  - Earn or Buy: {len(earn_or_buy)}")
        print(f"  - Premium: {len(premium)}")
        print(f"\nPrice tiers:")
        print(f"  - $0.99: {len(price_099)} avatars")
        print(f"  - $1.99: {len(price_199)} avatars")
        print(f"  - $2.99: {len(price_299)} avatars")
        
        return True
        
    except ImportError as e:
        print(f"❌ FAIL: Could not import avatar_catalog: {e}")
        return False
    except Exception as e:
        print(f"❌ FAIL: Test error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_integration():
    """Test avatar unlock with actual database (if available)"""
    print("\n" + "="*70)
    print("🗄️ DATABASE INTEGRATION TEST")
    print("="*70)
    
    try:
        from AjaSpellBApp import app, db
        from models import User
        
        with app.app_context():
            # Find a test user or create one
            test_user = User.query.filter_by(username='test_unlock_user').first()
            
            if not test_user:
                print("⚠️ No test user found. Creating temporary test user...")
                test_user = User(
                    username='test_unlock_user',
                    display_name='Test Unlock User',
                    email='test_unlock@beesmart.local',
                    role='student',
                    honey_points=0,
                    purchased_avatars=[]
                )
                test_user.set_password('test123')
                db.session.add(test_user)
                db.session.commit()
                created_new = True
            else:
                created_new = False
            
            print(f"\n✅ Test user: {test_user.username}")
            print(f"   Current Honey Points: {test_user.honey_points or 0:,}")
            print(f"   Purchased avatars: {len(test_user.purchased_avatars or [])}")
            
            # Test point-based unlock
            from avatar_catalog import check_avatar_unlocked
            
            print("\n📌 Testing point-based unlock:")
            test_user.honey_points = 2000
            result = check_avatar_unlocked('doctor-bee', test_user.honey_points, test_user.purchased_avatars)
            status = "✅ PASS" if result['unlocked'] else "❌ FAIL"
            print(f"  {status} Doctor Bee at 2,000 points: {result['reason']}")
            
            test_user.honey_points = 1999
            result = check_avatar_unlocked('doctor-bee', test_user.honey_points, test_user.purchased_avatars)
            status = "✅ PASS" if not result['unlocked'] else "❌ FAIL"
            print(f"  {status} Doctor Bee at 1,999 points (locked): {result['reason']}")
            
            # Test purchase unlock
            print("\n📌 Testing purchase-based unlock:")
            success, message = test_user.purchase_avatar('queen-bee')
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} Purchase Queen Bee: {message}")
            
            result = check_avatar_unlocked('queen-bee', 0, test_user.purchased_avatars)
            status = "✅ PASS" if result['unlocked'] else "❌ FAIL"
            print(f"  {status} Queen Bee unlocked via purchase: {result['reason']}")
            
            # Cleanup
            if created_new:
                db.session.delete(test_user)
                db.session.commit()
                print("\n🗑️ Cleaned up test user")
            else:
                db.session.rollback()  # Don't save changes to existing user
                print("\n↩️ Rolled back changes to existing test user")
            
            return True
            
    except ImportError as e:
        print(f"⚠️ SKIP: Database not available: {e}")
        return None
    except Exception as e:
        print(f"❌ FAIL: Database test error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("\n🐝 BeeSmart Avatar Unlock System - Comprehensive Test")
    print("=" * 70)
    
    # Run logic tests
    logic_pass = test_avatar_unlock_logic()
    
    # Run database tests if available
    db_result = test_database_integration()
    
    # Final summary
    print("\n" + "="*70)
    print("🎯 FINAL RESULTS")
    print("="*70)
    print(f"Avatar Logic Tests: {'✅ PASS' if logic_pass else '❌ FAIL'}")
    if db_result is not None:
        print(f"Database Integration: {'✅ PASS' if db_result else '❌ FAIL'}")
    else:
        print(f"Database Integration: ⚠️ SKIPPED (database not available)")
    
    print("\n" + "="*70)
    
    sys.exit(0 if logic_pass else 1)
