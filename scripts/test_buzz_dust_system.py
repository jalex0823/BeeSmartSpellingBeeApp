"""
Test Buzz Dust System
Quick validation script to ensure everything is working
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all modules can be imported"""
    print("=" * 60)
    print("Test 1: Module Imports")
    print("=" * 60)
    
    try:
        from buzz_dust_helpers import (
            get_bee_class,
            calculate_quiz_buzz_dust,
            get_rank_progress,
            get_all_bee_classes
        )
        print("✅ buzz_dust_helpers imports successful")
    except Exception as e:
        print(f"❌ Failed to import buzz_dust_helpers: {e}")
        return False
    
    try:
        import json
        with open('config/buzz_dust_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✅ Config file loads successfully")
        print(f"   - {len(config['bee_classes'])} Bee Classes defined")
        print(f"   - Multiplier: {config['buzz_dust']['multiplier']}")
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return False
    
    return True


def test_calculations():
    """Test Buzz Dust calculations"""
    print("\n" + "=" * 60)
    print("Test 2: Buzz Dust Calculations")
    print("=" * 60)
    
    from buzz_dust_helpers import calculate_quiz_buzz_dust
    
    # Test 1: Basic quiz (100 points, no bonuses)
    dust, breakdown = calculate_quiz_buzz_dust(points=100)
    print(f"\n📝 Basic Quiz (100 points, no bonuses)")
    print(f"   Buzz Dust: {dust}")
    print(f"   Breakdown: {breakdown}")
    assert dust == 10, "Expected 10 Buzz Dust (10% of 100)"
    print("   ✅ Correct!")
    
    # Test 2: Perfect round with no hints
    dust, breakdown = calculate_quiz_buzz_dust(
        points=100,
        perfect_round=True,
        no_hints=True
    )
    print(f"\n🌟 Perfect Quiz (100 points, perfect + no hints)")
    print(f"   Buzz Dust: {dust}")
    print(f"   Breakdown: {breakdown}")
    assert dust == 45, "Expected 45 (10 base + 25 perfect + 10 no hints)"
    print("   ✅ Correct!")
    
    # Test 3: With streak bonus
    dust, breakdown = calculate_quiz_buzz_dust(
        points=100,
        perfect_round=True,
        no_hints=True,
        streak_length=10
    )
    print(f"\n🔥 Streak Quiz (100 points, all bonuses, 10 streak)")
    print(f"   Buzz Dust: {dust}")
    print(f"   Breakdown: {breakdown}")
    print("   ✅ Calculation complete!")
    
    return True


def test_rankings():
    """Test ranking system"""
    print("\n" + "=" * 60)
    print("Test 3: Ranking System")
    print("=" * 60)
    
    from buzz_dust_helpers import get_bee_class, get_all_bee_classes
    
    all_classes = get_all_bee_classes()
    print(f"\n📊 Total Bee Classes: {len(all_classes)}")
    
    test_cases = [
        (0, "Novice Bee"),
        (500, "Apprentice Bee"),
        (2500, "Scholar Bee"),
        (10000, "Elite Bee"),
        (50000, "Magistrate Bee"),
        (100000, "Buzz Dust Master"),
        (250, "Novice Bee"),  # Still novice
        (75000, "Magistrate Bee")  # Not master yet
    ]
    
    print("\n🎯 Testing Rank Assignments:")
    for buzz_dust, expected_class in test_cases:
        bee_class = get_bee_class(buzz_dust)
        status = "✅" if bee_class['label'] == expected_class else "❌"
        print(f"   {status} {buzz_dust:>8} Buzz Dust → {bee_class['label']:<20} (expected: {expected_class})")
        if bee_class['label'] != expected_class:
            return False
    
    print("\n✅ All rank assignments correct!")
    return True


def test_progress():
    """Test rank progress calculation"""
    print("\n" + "=" * 60)
    print("Test 4: Rank Progress")
    print("=" * 60)
    
    from buzz_dust_helpers import get_rank_progress
    
    # Test at 1,000 Buzz Dust (Apprentice, halfway to Scholar)
    progress = get_rank_progress(1000)
    
    print(f"\n📈 Progress at 1,000 Buzz Dust:")
    print(f"   Current: {progress['current_class']['label']}")
    print(f"   Next: {progress['next_class']['label'] if progress['next_class'] else 'MAX RANK'}")
    print(f"   Progress: {progress['progress_percent']}%")
    print(f"   Needed: {progress['dust_needed']} more")
    
    # Verify calculations
    assert progress['current_class']['label'] == "Apprentice Bee"
    assert progress['next_class']['label'] == "Scholar Bee"
    assert progress['progress_percent'] == 25  # 500/2000 = 25%
    assert progress['dust_needed'] == 1500
    
    print("   ✅ Progress calculations correct!")
    
    # Test at max rank
    progress_max = get_rank_progress(150000)
    print(f"\n🏆 Progress at 150,000 Buzz Dust:")
    print(f"   Current: {progress_max['current_class']['label']}")
    print(f"   At Max Rank: {progress_max['at_max_rank']}")
    assert progress_max['at_max_rank'] == True
    print("   ✅ Max rank detection works!")
    
    return True


def main():
    """Run all tests"""
    print("\n🐝 BeeSmart Buzz Dust System - Validation Tests")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Calculations", test_calculations),
        ("Rankings", test_rankings),
        ("Progress", test_progress)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"\n❌ {name} test failed!")
        except Exception as e:
            failed += 1
            print(f"\n❌ {name} test crashed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 All tests passed! System is ready to use.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please review errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
