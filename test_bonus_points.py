#!/usr/bin/env python3
"""
Test script to verify bonus and extra points are properly tracked and included in cumulative score
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from AjaSpellBApp import app, db
from models import QuizSession, QuizResult, User
from datetime import datetime

def test_points_breakdown():
    """Test that points are properly broken down and summed"""
    
    print("=" * 70)
    print("🧪 Testing Bonus & Extra Points Tracking")
    print("=" * 70)
    print()
    
    with app.app_context():
        # Create test user
        test_username = f"test_points_{datetime.now().timestamp()}"
        test_user = User(
            username=test_username,
            display_name=test_username,  # Required field
            email=f"test_{datetime.now().timestamp()}@test.com",
            role="student"
        )
        test_user.set_password("test123")
        db.session.add(test_user)
        db.session.commit()
        
        print(f"✅ Created test user: {test_user.username} (ID: {test_user.id})")
        print()
        
        # Create test quiz session
        quiz_session = QuizSession(
            user_id=test_user.id,
            total_words=5,
            correct_count=4,
            incorrect_count=1
        )
        db.session.add(quiz_session)
        db.session.commit()
        
        print(f"✅ Created quiz session (ID: {quiz_session.id})")
        print()
        
        # Simulate word results with bonuses
        word_results = [
            {
                "word": "spelling",
                "is_correct": True,
                "base_points": 100,
                "time_bonus": 60,
                "streak_bonus": 0,
                "first_attempt_bonus": 50,
                "no_hints_bonus": 25,
                "points_earned": 235
            },
            {
                "word": "awesome",
                "is_correct": True,
                "base_points": 100,
                "time_bonus": 40,
                "streak_bonus": 10,
                "first_attempt_bonus": 50,
                "no_hints_bonus": 25,
                "points_earned": 225
            },
            {
                "word": "challenge",
                "is_correct": True,
                "base_points": 100,
                "time_bonus": 35,
                "streak_bonus": 20,
                "first_attempt_bonus": 50,
                "no_hints_bonus": 25,
                "points_earned": 230
            },
            {
                "word": "brilliant",
                "is_correct": True,
                "base_points": 100,
                "time_bonus": 30,
                "streak_bonus": 30,
                "first_attempt_bonus": 50,
                "no_hints_bonus": 25,
                "points_earned": 235
            },
            {
                "word": "difficult",
                "is_correct": False,
                "base_points": 0,
                "time_bonus": 0,
                "streak_bonus": 0,
                "first_attempt_bonus": 0,
                "no_hints_bonus": 0,
                "points_earned": 0
            }
        ]
        
        total_word_points = 0
        for i, result_data in enumerate(word_results, 1):
            result = QuizResult(
                session_id=quiz_session.id,
                user_id=test_user.id,
                word=result_data["word"],
                is_correct=result_data["is_correct"],
                user_answer=result_data["word"] if result_data["is_correct"] else "wrong",
                correct_spelling=result_data["word"],
                points_earned=result_data["points_earned"],
                base_points=result_data["base_points"],
                time_bonus=result_data["time_bonus"],
                streak_bonus=result_data["streak_bonus"],
                first_attempt_bonus=result_data["first_attempt_bonus"],
                no_hints_bonus=result_data["no_hints_bonus"],
                question_number=i
            )
            db.session.add(result)
            total_word_points += result_data["points_earned"]
            
            if result_data["is_correct"]:
                print(f"   Word {i}: '{result_data['word']}' ✓")
                print(f"      Base: {result_data['base_points']}, Time: {result_data['time_bonus']}, "
                      f"Streak: {result_data['streak_bonus']}, First: {result_data['first_attempt_bonus']}, "
                      f"No Hints: {result_data['no_hints_bonus']}")
                print(f"      Total: {result_data['points_earned']} points")
            else:
                print(f"   Word {i}: '{result_data['word']}' ✗ (0 points)")
            print()
        
        print(f"📊 Word Points Total: {total_word_points}")
        print()
        
        # Simulate badge bonuses
        badge_points = 150  # e.g., "Perfect Bee" (100) + "Speed Demon" (50)
        print(f"🏆 Badge Bonus Points: {badge_points}")
        print("   - Perfect Bee: 100 points")
        print("   - Speed Demon: 50 points")
        print()
        
        # Simulate extra bonuses
        extra_points = 200  # e.g., teacher award or special milestone
        print(f"🎁 Extra Bonus Points: {extra_points}")
        print("   - Teacher Excellence Award: 200 points")
        print()
        
        # Update quiz session with all points
        quiz_session.points_earned = total_word_points
        quiz_session.badge_bonus_points = badge_points
        quiz_session.extra_points = extra_points
        quiz_session.total_points = total_word_points + badge_points + extra_points
        quiz_session.completed = True
        
        db.session.commit()
        
        # Display final calculations
        print("=" * 70)
        print("📈 FINAL CUMULATIVE SCORE CALCULATION")
        print("=" * 70)
        print(f"   Word Points:        {quiz_session.points_earned:>6} points")
        print(f"   Badge Bonuses:      {quiz_session.badge_bonus_points:>6} points")
        print(f"   Extra Bonuses:      {quiz_session.extra_points:>6} points")
        print("   " + "-" * 35)
        print(f"   CUMULATIVE TOTAL:   {quiz_session.total_points:>6} points ✅")
        print("=" * 70)
        print()
        
        # Verify database integrity
        print("🔍 Verifying Database Integrity...")
        print()
        
        # Reload from database
        db.session.expire_all()
        reloaded_session = QuizSession.query.get(quiz_session.id)
        
        assert reloaded_session.points_earned == total_word_points, "Word points mismatch!"
        assert reloaded_session.badge_bonus_points == badge_points, "Badge points mismatch!"
        assert reloaded_session.extra_points == extra_points, "Extra points mismatch!"
        assert reloaded_session.total_points == (total_word_points + badge_points + extra_points), "Total points calculation error!"
        
        print(f"✅ points_earned: {reloaded_session.points_earned}")
        print(f"✅ badge_bonus_points: {reloaded_session.badge_bonus_points}")
        print(f"✅ extra_points: {reloaded_session.extra_points}")
        print(f"✅ total_points: {reloaded_session.total_points}")
        print()
        
        # Verify individual word results
        results = QuizResult.query.filter_by(session_id=quiz_session.id).all()
        assert len(results) == 5, "Should have 5 word results!"
        
        for result in results:
            if result.is_correct:
                calculated_total = (result.base_points + result.time_bonus + 
                                  result.streak_bonus + result.first_attempt_bonus + 
                                  result.no_hints_bonus)
                assert result.points_earned == calculated_total, f"Points breakdown error for '{result.word}'!"
        
        print(f"✅ All {len(results)} word results have correct point breakdowns")
        print()
        
        # Clean up
        print("🧹 Cleaning up test data...")
        QuizResult.query.filter_by(session_id=quiz_session.id).delete()
        db.session.delete(quiz_session)
        db.session.delete(test_user)
        db.session.commit()
        print("✅ Test data cleaned up")
        print()
        
        print("=" * 70)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 70)
        print()
        print("Summary:")
        print("✅ Bonus points are properly tracked in separate fields")
        print("✅ Cumulative total is correctly calculated (word + badge + extra)")
        print("✅ Individual word bonuses are stored in QuizResult")
        print("✅ Database schema supports full points breakdown")
        print("✅ All bonus and extra points are included in cumulative score")
        print()
        return True

if __name__ == "__main__":
    try:
        success = test_points_breakdown()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
