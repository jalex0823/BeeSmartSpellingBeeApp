#!/usr/bin/env python3
"""
Diagnostic script to check for disconnect between DigitalOcean database
and main menu stats display.

This script will:
1. Query the database directly for user stats
2. Compare with what the API endpoints return
3. Check for any stale data or caching issues
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from AjaSpellBApp import app, db
from models import User, QuizSession
from sqlalchemy import func

def check_user_stats_sync(username=None, user_id=None):
    """Check if user stats in database match what would be returned by API"""
    
    with app.app_context():
        # Find user
        if user_id:
            user = User.query.get(user_id)
        elif username:
            user = User.query.filter_by(username=username).first()
        else:
            print("❌ Please provide either username or user_id")
            return
        
        if not user:
            print(f"❌ User not found: {username or user_id}")
            return
        
        print(f"\n{'='*80}")
        print(f"📊 STATS SYNC CHECK for User: {user.username} (ID: {user.id})")
        print(f"{'='*80}\n")
        
        # 1. Check database values directly
        print("1️⃣ DIRECT DATABASE VALUES:")
        print(f"   total_lifetime_points: {user.total_lifetime_points or 0}")
        print(f"   total_quizzes_completed: {user.total_quizzes_completed or 0}")
        print(f"   cumulative_gpa: {user.cumulative_gpa or 0.0}")
        print(f"   average_accuracy: {user.average_accuracy or 0.0}")
        print(f"   best_streak: {user.best_streak or 0}")
        
        # 2. Calculate from QuizSessions
        print("\n2️⃣ CALCULATED FROM QUIZ SESSIONS:")
        completed_sessions = QuizSession.query.filter_by(
            user_id=user.id,
            completed=True
        ).all()
        
        total_points_from_sessions = 0
        for session in completed_sessions:
            if session.total_points:
                total_points_from_sessions += int(session.total_points)
            else:
                # Fallback: sum components
                total_points_from_sessions += int(session.points_earned or 0)
                total_points_from_sessions += int(session.badge_bonus_points or 0)
                total_points_from_sessions += int(session.extra_points or 0)
        
        quiz_count = len(completed_sessions)
        
        print(f"   Total points from sessions: {total_points_from_sessions}")
        print(f"   Quiz count from sessions: {quiz_count}")
        
        # 3. Check for discrepancies
        print("\n3️⃣ DISCREPANCIES:")
        points_match = (user.total_lifetime_points or 0) == total_points_from_sessions
        quizzes_match = (user.total_quizzes_completed or 0) == quiz_count
        
        if not points_match:
            diff = total_points_from_sessions - (user.total_lifetime_points or 0)
            print(f"   ⚠️ POINTS MISMATCH!")
            print(f"      DB value: {user.total_lifetime_points or 0}")
            print(f"      Calculated: {total_points_from_sessions}")
            print(f"      Difference: {diff}")
        else:
            print(f"   ✅ Points match")
        
        if not quizzes_match:
            diff = quiz_count - (user.total_quizzes_completed or 0)
            print(f"   ⚠️ QUIZ COUNT MISMATCH!")
            print(f"      DB value: {user.total_quizzes_completed or 0}")
            print(f"      Calculated: {quiz_count}")
            print(f"      Difference: {diff}")
        else:
            print(f"   ✅ Quiz count matches")
        
        # 4. Check incomplete sessions
        incomplete_sessions = QuizSession.query.filter_by(
            user_id=user.id,
            completed=False
        ).count()
        
        if incomplete_sessions > 0:
            print(f"\n   ⚠️ Found {incomplete_sessions} incomplete quiz sessions")
            print(f"      These may need to be completed or cleaned up")
        
        # 5. Recalculate stats
        print("\n4️⃣ RECALCULATING STATS:")
        try:
            old_points = user.total_lifetime_points or 0
            old_quizzes = user.total_quizzes_completed or 0
            
            # Force recalculation
            user.update_gpa_and_accuracy()
            
            # Update points and quiz count from sessions
            user.total_lifetime_points = total_points_from_sessions
            user.total_quizzes_completed = quiz_count
            
            db.session.commit()
            db.session.refresh(user)
            
            print(f"   ✅ Stats recalculated and saved")
            print(f"   Points: {old_points} → {user.total_lifetime_points}")
            print(f"   Quizzes: {old_quizzes} → {user.total_quizzes_completed}")
            print(f"   GPA: {user.cumulative_gpa}")
            print(f"   Accuracy: {user.average_accuracy}%")
            
        except Exception as e:
            print(f"   ❌ Error recalculating: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
        
        print(f"\n{'='*80}\n")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python check_db_stats_sync.py <username>")
        print("   or: python check_db_stats_sync.py --id <user_id>")
        sys.exit(1)
    
    if sys.argv[1] == '--id' and len(sys.argv) > 2:
        user_id = int(sys.argv[2])
        check_user_stats_sync(user_id=user_id)
    else:
        username = sys.argv[1]
        check_user_stats_sync(username=username)
