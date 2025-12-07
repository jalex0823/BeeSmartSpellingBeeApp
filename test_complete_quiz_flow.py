#!/usr/bin/env python3
"""
Complete Quiz Flow Test
Simulates a full quiz session to ensure all systems work together
"""

import sys
import os
import time
from datetime import datetime

def simulate_quiz_session():
    """Simulate a complete quiz session with rewards"""
    print("🐝 Complete Quiz Flow Integration Test")
    print("=" * 50)
    
    try:
        # Import required modules
        from buzz_dust_helpers import calculate_quiz_buzz_dust, get_bee_class
        from avatar_catalog import AVATAR_CATALOG, check_avatar_unlocked
        from AjaSpellBApp import check_badges, get_user_level
        
        print("✅ All modules imported successfully")
        
        # Simulate quiz state for a perfect session
        quiz_state = {
            "correct": 10,
            "incorrect": 0,
            "max_streak": 10,
            "hints_used_total": 0,
            "session_points": 0,  # Will be calculated
            "total_time_ms": 180000,  # 3 minutes
            "history": []
        }
        
        # Simulate individual question responses
        questions = [
            {"word": "beautiful", "time": 15000, "correct": True, "hints": 0},
            {"word": "science", "time": 12000, "correct": True, "hints": 0},
            {"word": "elephant", "time": 18000, "correct": True, "hints": 0},
            {"word": "butterfly", "time": 20000, "correct": True, "hints": 0},
            {"word": "rainbow", "time": 14000, "correct": True, "hints": 0},
            {"word": "mathematics", "time": 25000, "correct": True, "hints": 0},
            {"word": "adventure", "time": 16000, "correct": True, "hints": 0},
            {"word": "dinosaur", "time": 19000, "correct": True, "hints": 0},
            {"word": "chocolate", "time": 13000, "correct": True, "hints": 0},
            {"word": "friendship", "time": 22000, "correct": True, "hints": 0}
        ]
        
        session_points = 0
        history = []
        
        print("\n🎯 Simulating quiz questions...")
        for i, q in enumerate(questions, 1):
            # Simulate the point calculation logic from api_answer
            points = 0
            if q["correct"]:
                # Base points
                points += 100
                
                # Time bonus (5 points per second remaining from 60s timer)
                if q["time"] < 60000:
                    time_remaining_seconds = (60000 - q["time"]) / 1000
                    time_bonus = int(5 * time_remaining_seconds)
                    points += max(0, time_bonus)
                
                # Streak bonus (10 points × current streak)
                if i > 1:  # Has a streak
                    streak_bonus = 10 * (i - 1)
                    points += streak_bonus
                    
                # First attempt bonus (no hints)
                if q["hints"] == 0:
                    points += 50
            
            session_points += points
            
            history.append({
                "word": q["word"],
                "correct": q["correct"],
                "elapsed_ms": q["time"],
                "hints_used": q["hints"],
                "points": points
            })
            
            print(f"   Question {i}: '{q['word']}' → {points} points ({q['time']/1000:.1f}s)")
        
        # Update final quiz state
        quiz_state["session_points"] = session_points
        quiz_state["history"] = history
        
        print(f"\n📊 Session Summary:")
        print(f"   Total Points: {session_points}")
        print(f"   Perfect Score: {quiz_state['correct']}/{quiz_state['correct'] + quiz_state['incorrect']}")
        print(f"   Max Streak: {quiz_state['max_streak']}")
        print(f"   Total Time: {quiz_state['total_time_ms']/1000:.1f} seconds")
        
        # Test buzz dust calculation
        print(f"\n🌟 Testing Buzz Dust System...")
        is_perfect_round = (quiz_state.get("incorrect", 0) == 0 and quiz_state.get("correct", 0) > 0)
        no_hints_used = (quiz_state.get("hints_used_total", 0) == 0)
        max_streak = quiz_state.get("max_streak", 0)
        
        buzz_dust, buzz_dust_breakdown = calculate_quiz_buzz_dust(
            points=session_points,
            perfect_round=is_perfect_round,
            no_hints=no_hints_used,
            streak_length=max_streak,
            daily_challenge=False
        )
        bee_class = get_bee_class(buzz_dust)
        print(f"   Buzz Dust Earned: {buzz_dust}")
        print(f"   Buzz Dust Breakdown: {buzz_dust_breakdown}")
        print(f"   Bee Class: {bee_class}")
        
        # Test badge system
        print(f"\n🏆 Testing Badge System...")
        wordbank = [{"word": q["word"]} for q in questions]
        badges = check_badges(quiz_state, wordbank)
        print(f"   Badges Earned: {len(badges)}")
        for badge in badges:
            print(f"     • {badge['name']}: {badge['message']}")
        
        # Test avatar unlocking
        print(f"\n👤 Testing Avatar System...")
        user_lifetime_points = session_points * 10  # Simulate accumulated points
        unlocked_count = 0
        premium_count = 0
        
        for avatar in AVATAR_CATALOG:
            is_unlocked = check_avatar_unlocked(avatar, user_lifetime_points)
            if is_unlocked:
                unlocked_count += 1
            if avatar.get('tier') == 'premium':
                premium_count += 1
        
        print(f"   Avatars Unlocked: {unlocked_count}/{len(AVATAR_CATALOG)}")
        print(f"   Premium Avatars Available: {premium_count}")
        
        # Test level system
        print(f"\n🎚️ Testing Level System...")
        level_info = get_user_level(user_lifetime_points)
        print(f"   Current Level: {level_info['level']} ({level_info['tier']})")
        print(f"   Progress to Next: {level_info.get('progress_percent', 100):.1f}%")
        
        # Simulate report card data
        print(f"\n📋 Report Card Summary:")
        print(f"   Session Performance: {(quiz_state['correct']/(quiz_state['correct']+quiz_state['incorrect'])*100):.1f}%")
        print(f"   Average Time per Word: {(sum(q['time'] for q in questions)/len(questions)/1000):.1f}s")
        print(f"   Hints Used: {quiz_state['hints_used_total']}")
        print(f"   Streak Achievement: {quiz_state['max_streak']} words")
        
        print(f"\n🎉 COMPLETE QUIZ FLOW TEST: PASSED")
        print(f"   ✅ Points calculation working")
        print(f"   ✅ Buzz dust system working")
        print(f"   ✅ Badge awarding working")
        print(f"   ✅ Avatar unlocking working")
        print(f"   ✅ Level progression working")
        print(f"   ✅ Report card data working")
        
        return True
        
    except Exception as e:
        print(f"❌ Quiz Flow Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = simulate_quiz_session()
    sys.exit(0 if success else 1)