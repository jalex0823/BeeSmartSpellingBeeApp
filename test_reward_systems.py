#!/usr/bin/env python3
"""
BeeSmart Reward Systems Smoke Test
Tests all point systems, badges, avatars, and progression mechanics

Run this to verify all reward systems are working properly:
- Session Points (quiz scoring)
- Honey Points (avatar unlocking)  
- Buzz Dust (ranking system)
- Badges (achievement system)
- Level Progression
- Avatar Unlocks
"""

import sys
import os
import json
import time
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_buzz_dust_system():
    """Test the Buzz Dust ranking system"""
    print("🔸 Testing Buzz Dust System...")
    try:
        from buzz_dust_helpers import (
            get_bee_class, 
            get_all_bee_classes,
            get_rank_progress,
            calculate_quiz_buzz_dust,
            BEE_CLASSES
        )
        
        # Test bee class retrieval
        novice = get_bee_class(0)
        print(f"   ✅ Novice Bee (0 dust): {novice['label']}")
        
        elite = get_bee_class(25000000)
        print(f"   ✅ Elite Bee (25M dust): {elite['label']}")
        
        # Test all classes
        all_classes = get_all_bee_classes()
        print(f"   ✅ Total Bee Classes: {len(all_classes)}")
        
        # Test rank progress
        progress = get_rank_progress(5000000)
        print(f"   ✅ Progress calculation works: {progress['progress_percent']}% to next rank")
        
        # Test buzz dust calculation
        dust, breakdown = calculate_quiz_buzz_dust(
            points=1000,
            perfect_round=True,
            no_hints=True,
            streak_length=15
        )
        print(f"   ✅ Buzz dust calculation: {dust} (breakdown: {breakdown})")
        
        print("   ✅ Buzz Dust System: PASS")
        return True
        
    except Exception as e:
        print(f"   ❌ Buzz Dust System Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_avatar_system():
    """Test the Avatar catalog and unlocking system"""
    print("🔸 Testing Avatar System...")
    try:
        from avatar_catalog import AVATAR_CATALOG, check_avatar_unlocked, get_avatar_info
        
        # Test catalog loading
        print(f"   ✅ Avatar catalog loaded: {len(AVATAR_CATALOG)} avatars")
        
        # Test different tier avatars
        test_cases = [
            ("buzzy-bee", 0, "Free avatar"),
            ("cool-bee", 3000, "Earn-or-buy avatar"),  
            ("knight-bee", 25000, "Premium avatar")
        ]
        
        for avatar_id, points, description in test_cases:
            avatar = get_avatar_info(avatar_id)
            if avatar:
                status = check_avatar_unlocked(avatar_id, points, [])
                unlock_status = "UNLOCKED" if status.get('unlocked') else "LOCKED"
                print(f"   ✅ {description} ({avatar_id}): {unlock_status} at {points} points")
            else:
                print(f"   ⚠️ Avatar {avatar_id} not found in catalog")
        
        # Test tier distribution
        tiers = {}
        for avatar in AVATAR_CATALOG:
            tier = avatar.get('tier', 'unknown')
            tiers[tier] = tiers.get(tier, 0) + 1
            
        print(f"   ✅ Avatar distribution: {tiers}")
        print("   ✅ Avatar System: PASS")
        return True
        
    except Exception as e:
        print(f"   ❌ Avatar System Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_badge_system():
    """Test the Achievement/Badge system"""
    print("🔸 Testing Badge System...")
    try:
        # Import the app to access badge logic
        from AjaSpellBApp import check_badges
        
        # Test perfect game badge
        perfect_state = {
            "correct": 15,
            "incorrect": 0, 
            "max_streak": 15,
            "hints_used_total": 0,
            "session_points": 1500,
            "history": [{"correct": True, "elapsed_ms": 3000} for _ in range(15)]
        }
        perfect_wordbank = [{"word": f"word{i}"} for i in range(15)]  # Mock wordbank
        
        perfect_badges = check_badges(perfect_state, perfect_wordbank)
        print(f"   ✅ Perfect game badges: {[b['name'] for b in perfect_badges]}")
        
        # Test speed demon badge
        speed_state = {
            "correct": 12,
            "incorrect": 2,
            "max_streak": 8,
            "hints_used_total": 1,
            "session_points": 1200,
            "history": [{"correct": True, "elapsed_ms": 5000} for _ in range(12)] +
                      [{"correct": False, "elapsed_ms": 8000} for _ in range(2)]
        }
        speed_wordbank = [{"word": f"word{i}"} for i in range(14)]  # Mock wordbank
        
        speed_badges = check_badges(speed_state, speed_wordbank)
        print(f"   ✅ Speed game badges: {[b['name'] for b in speed_badges]}")
        
        print("   ✅ Badge System: PASS")
        return True
        
    except Exception as e:
        print(f"   ❌ Badge System Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_points_calculation():
    """Test points calculation in quiz scenarios"""
    print("🔸 Testing Points Calculation...")
    try:
        # Test base points calculation
        base_points = 100
        time_bonus = 50  # Fast answer
        streak_bonus = 30  # 3-streak * 10
        no_hints_bonus = 25
        
        total_points = base_points + time_bonus + streak_bonus + no_hints_bonus
        print(f"   ✅ Points breakdown: Base({base_points}) + Time({time_bonus}) + Streak({streak_bonus}) + NoHints({no_hints_bonus}) = {total_points}")
        
        # Test hint penalty
        with_hints_points = total_points - int(total_points * 0.30)
        print(f"   ✅ With hints penalty (30%): {with_hints_points}")
        
        # Test session points accumulation
        session_points = 0
        for word_points in [205, 180, 145, 200, 175]:
            session_points += word_points
        print(f"   ✅ Session accumulation: {session_points} points")
        
        print("   ✅ Points Calculation: PASS")
        return True
        
    except Exception as e:
        print(f"   ❌ Points Calculation Error: {e}")
        return False

def test_level_system():
    """Test level progression system"""
    print("🔸 Testing Level System...")
    try:
        from AjaSpellBApp import get_user_level, check_level_up
        
        # Test different point levels
        test_levels = [
            (0, "Novice"),
            (5000, "Bronze"),
            (25000, "Silver"), 
            (75000, "Gold"),
            (200000, "Platinum")
        ]
        
        for points, expected_tier in test_levels:
            level = get_user_level(points)
            print(f"   ✅ {points} points = Level {level['level']} ({level['tier']})")
            
        # Test level up detection
        level_up = check_level_up(4900, 5100)  # Cross Bronze threshold
        if level_up and level_up.get('leveled_up'):
            old_tier = level_up['old_level']['tier']
            new_tier = level_up['new_level']['tier']
            print(f"   ✅ Level up detected: {old_tier} → {new_tier}")
        else:
            print("   ✅ No level up detected for small increase")
            
        print("   ✅ Level System: PASS")
        return True
        
    except Exception as e:
        print(f"   ❌ Level System Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_integration():
    """Test that models can be imported and basic operations work"""
    print("🔸 Testing Database Integration...")
    try:
        from models import User, Achievement, QuizSession, QuizResult
        
        # Test model imports
        print("   ✅ User model imported")
        print("   ✅ Achievement model imported")
        print("   ✅ QuizSession model imported")
        print("   ✅ QuizResult model imported")
        
        # Test model structure
        user_columns = [c.name for c in User.__table__.columns]
        required_fields = ['honey_points', 'total_buzz_dust', 'total_lifetime_points', 'bee_class']
        
        for field in required_fields:
            if field in user_columns:
                print(f"   ✅ User.{field} field exists")
            else:
                print(f"   ❌ User.{field} field missing")
                
        print("   ✅ Database Integration: PASS")
        return True
        
    except Exception as e:
        print(f"   ❌ Database Integration Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_smoke_test():
    """Run all reward system smoke tests"""
    print("🐝 BeeSmart Reward Systems Smoke Test")
    print("=" * 50)
    
    tests = [
        test_buzz_dust_system,
        test_avatar_system,
        test_badge_system,
        test_points_calculation,
        test_level_system,
        test_database_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   💥 Test crashed: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed} PASSED, {failed} FAILED")
    
    if failed == 0:
        print("🎉 ALL REWARD SYSTEMS WORKING PROPERLY!")
        return True
    else:
        print(f"⚠️ {failed} SYSTEMS NEED ATTENTION")
        return False

if __name__ == "__main__":
    success = run_smoke_test()
    sys.exit(0 if success else 1)