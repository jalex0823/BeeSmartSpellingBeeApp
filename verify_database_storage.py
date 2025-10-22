"""
Verify Database Storage - Check all quiz data is being saved
This script verifies that all quiz scores, grades, achievements, badges, and datetime data
are properly stored in the PostgreSQL database on Railway.
"""

import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import func

# Import Flask app and database
from AjaSpellBApp import app, db
from models import (
    User, QuizSession, QuizResult, WordMastery, Achievement, 
    SpeedRoundScore, SessionLog, TeacherStudent
)


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def verify_database_connection():
    """Verify we're connected to the right database"""
    print_section("DATABASE CONNECTION")
    
    database_url = os.getenv('DATABASE_URL', 'Not set')
    if database_url.startswith('postgresql'):
        print("✅ Connected to PostgreSQL (Railway)")
        print(f"   URL: {database_url[:50]}...")
    else:
        print("⚠️  Using SQLite (local development)")
        print(f"   URL: {database_url}")
    
    return database_url.startswith('postgresql')


def verify_quiz_sessions():
    """Check QuizSession records"""
    print_section("QUIZ SESSIONS")
    
    total = QuizSession.query.count()
    completed = QuizSession.query.filter_by(completed=True).count()
    recent = QuizSession.query.filter(
        QuizSession.session_start >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    print(f"Total Quiz Sessions: {total}")
    print(f"Completed Sessions: {completed}")
    print(f"Sessions (Last 7 days): {recent}")
    
    # Show recent sessions with grades
    print("\n📊 Recent Quiz Sessions (Last 5):")
    recent_sessions = QuizSession.query.order_by(
        QuizSession.session_start.desc()
    ).limit(5).all()
    
    for session in recent_sessions:
        user = User.query.get(session.user_id)
        username = user.username if user else "Unknown"
        status = "✅ Complete" if session.completed else "⏳ In Progress"
        grade = session.grade or "N/A"
        accuracy = session.accuracy_percentage or 0
        print(f"  • ID {session.id} | User: {username} | Grade: {grade} | "
              f"Accuracy: {accuracy}% | {status}")
        print(f"    Started: {session.session_start} | Points: {session.total_points}")
    
    return total > 0


def verify_quiz_results():
    """Check QuizResult records (individual word attempts)"""
    print_section("QUIZ RESULTS (Individual Words)")
    
    total = QuizResult.query.count()
    correct = QuizResult.query.filter_by(is_correct=True).count()
    incorrect = QuizResult.query.filter_by(is_correct=False).count()
    recent = QuizResult.query.filter(
        QuizResult.timestamp >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    print(f"Total Word Attempts: {total}")
    print(f"Correct Answers: {correct}")
    print(f"Incorrect Answers: {incorrect}")
    print(f"Attempts (Last 7 days): {recent}")
    
    if total > 0:
        accuracy = (correct / total * 100) if total > 0 else 0
        print(f"Overall Accuracy: {accuracy:.1f}%")
    
    # Show recent results
    print("\n📝 Recent Word Attempts (Last 5):")
    recent_results = QuizResult.query.order_by(
        QuizResult.timestamp.desc()
    ).limit(5).all()
    
    for result in recent_results:
        status = "✅" if result.is_correct else "❌"
        user = User.query.get(result.user_id)
        username = user.username if user else "Unknown"
        print(f"  {status} {result.word} | User: {username} | "
              f"Answer: {result.user_answer} | Points: {result.points_earned}")
        print(f"    Time: {result.timestamp} | Method: {result.input_method}")
    
    return total > 0


def verify_achievements():
    """Check Achievement records (badges)"""
    print_section("ACHIEVEMENTS & BADGES")
    
    total = Achievement.query.count()
    recent = Achievement.query.filter(
        Achievement.earned_date >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    print(f"Total Achievements Earned: {total}")
    print(f"Achievements (Last 7 days): {recent}")
    
    # Count by type
    achievement_types = db.session.query(
        Achievement.achievement_type,
        func.count(Achievement.id)
    ).group_by(Achievement.achievement_type).all()
    
    if achievement_types:
        print("\n🏆 Achievements by Type:")
        for ach_type, count in achievement_types:
            print(f"  • {ach_type}: {count}")
    
    # Show recent achievements
    print("\n🎖️ Recent Achievements (Last 5):")
    recent_achievements = Achievement.query.order_by(
        Achievement.earned_date.desc()
    ).limit(5).all()
    
    for achievement in recent_achievements:
        user = User.query.get(achievement.user_id)
        username = user.username if user else "Unknown"
        print(f"  🏆 {achievement.achievement_name}")
        print(f"    User: {username} | Points: {achievement.points_bonus} | "
              f"Earned: {achievement.earned_date}")
    
    return total > 0


def verify_word_mastery():
    """Check WordMastery records (individual word tracking)"""
    print_section("WORD MASTERY TRACKING")
    
    total = WordMastery.query.count()
    mastered = WordMastery.query.filter_by(mastery_level='mastered').count()
    
    print(f"Total Words Tracked: {total}")
    print(f"Mastered Words: {mastered}")
    
    if total > 0:
        mastery_rate = (mastered / total * 100) if total > 0 else 0
        print(f"Mastery Rate: {mastery_rate:.1f}%")
    
    # Show top mastered words
    print("\n📚 Most Practiced Words (Top 5):")
    top_words = WordMastery.query.order_by(
        WordMastery.times_seen.desc()
    ).limit(5).all()
    
    for wm in top_words:
        user = User.query.get(wm.user_id)
        username = user.username if user else "Unknown"
        status = f"✅ {wm.mastery_level.title()}"
        accuracy = float(wm.success_rate) if wm.success_rate else 0
        print(f"  • {wm.word} | User: {username}")
        print(f"    Attempts: {wm.times_seen} | Correct: {wm.times_correct} | "
              f"Accuracy: {accuracy:.1f}% | {status}")
    
    return total > 0


def verify_speed_rounds():
    """Check SpeedRoundScore records"""
    print_section("SPEED ROUND SCORES")
    
    total = SpeedRoundScore.query.count()
    recent = SpeedRoundScore.query.filter(
        SpeedRoundScore.completed_at >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    print(f"Total Speed Rounds: {total}")
    print(f"Speed Rounds (Last 7 days): {recent}")
    
    if total > 0:
        # Get average stats
        avg_stats = db.session.query(
            func.avg(SpeedRoundScore.words_correct),
            func.avg(SpeedRoundScore.honey_points_earned),
            func.max(SpeedRoundScore.longest_streak)
        ).first()
        
        print(f"Average Words Correct: {avg_stats[0]:.1f}" if avg_stats[0] else "N/A")
        print(f"Average Points: {avg_stats[1]:.0f}" if avg_stats[1] else "N/A")
        print(f"Best Streak: {avg_stats[2]}" if avg_stats[2] else "N/A")
    
    # Show recent speed rounds
    print("\n⚡ Recent Speed Rounds (Last 5):")
    recent_scores = SpeedRoundScore.query.order_by(
        SpeedRoundScore.completed_at.desc()
    ).limit(5).all()
    
    for score in recent_scores:
        user = User.query.get(score.user_id)
        username = user.username if user else "Unknown"
        print(f"  • User: {username} | Score: {score.honey_points_earned} pts")
        print(f"    Correct: {score.words_correct}/{score.words_attempted} | "
              f"Accuracy: {score.accuracy_percentage}% | Streak: {score.longest_streak}")
        print(f"    Completed: {score.completed_at}")
    
    return total > 0


def verify_session_logs():
    """Check SessionLog records (audit trail)"""
    print_section("SESSION LOGS (Audit Trail)")
    
    total = SessionLog.query.count()
    recent = SessionLog.query.filter(
        SessionLog.timestamp >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    print(f"Total Session Logs: {total}")
    print(f"Logs (Last 7 days): {recent}")
    
    # Count by action type
    action_counts = db.session.query(
        SessionLog.action,
        func.count(SessionLog.id)
    ).group_by(SessionLog.action).all()
    
    if action_counts:
        print("\n📋 Actions Logged:")
        for action, count in action_counts:
            print(f"  • {action}: {count}")
    
    return total > 0


def verify_users():
    """Check User records"""
    print_section("USER ACCOUNTS")
    
    total = User.query.count()
    students = User.query.filter_by(role='student').count()
    teachers = User.query.filter_by(role='teacher').count()
    parents = User.query.filter_by(role='parent').count()
    admins = User.query.filter_by(role='admin').count()
    
    print(f"Total Users: {total}")
    print(f"Students: {students}")
    print(f"Teachers: {teachers}")
    print(f"Parents: {parents}")
    print(f"Admins: {admins}")
    
    # Show users with most activity
    print("\n👥 Most Active Users (by quiz count):")
    active_users = User.query.order_by(
        User.total_quizzes_completed.desc().nullslast()
    ).limit(5).all()
    
    for user in active_users:
        quizzes = user.total_quizzes_completed or 0
        points = user.total_lifetime_points or 0
        streak = user.best_streak or 0
        print(f"  • {user.username} ({user.role})")
        print(f"    Quizzes: {quizzes} | Points: {points} | Best Streak: {streak}")
        if user.teacher_key:
            print(f"    Teacher Key: {user.teacher_key}")
    
    return total > 0


def verify_teacher_student_links():
    """Check TeacherStudent relationships"""
    print_section("TEACHER-STUDENT LINKS")
    
    total = TeacherStudent.query.count()
    print(f"Total Teacher-Student Links: {total}")
    
    if total > 0:
        print("\n👨‍🏫 Recent Links:")
        links = TeacherStudent.query.order_by(
            TeacherStudent.linked_at.desc()
        ).limit(5).all()
        
        for link in links:
            teacher = User.query.get(link.teacher_user_id)
            student = User.query.get(link.student_id)
            teacher_name = teacher.username if teacher else "Unknown"
            student_name = student.username if student else "Unknown"
            print(f"  • Teacher: {teacher_name} (Key: {link.teacher_key})")
            print(f"    Student: {student_name}")
            print(f"    Linked: {link.linked_at}")
    
    return total > 0


def run_verification():
    """Run all verification checks"""
    print("\n" + "="*70)
    print("  🐝 BeeSmart Spelling Bee - Database Verification")
    print("="*70)
    print(f"  Running at: {datetime.utcnow()} UTC")
    print("="*70)
    
    with app.app_context():
        results = {
            "database_connection": verify_database_connection(),
            "users": verify_users(),
            "quiz_sessions": verify_quiz_sessions(),
            "quiz_results": verify_quiz_results(),
            "achievements": verify_achievements(),
            "word_mastery": verify_word_mastery(),
            "speed_rounds": verify_speed_rounds(),
            "session_logs": verify_session_logs(),
            "teacher_student_links": verify_teacher_student_links()
        }
        
        # Summary
        print_section("VERIFICATION SUMMARY")
        
        all_good = all(results.values())
        
        for check, passed in results.items():
            status = "✅" if passed else "⚠️ "
            print(f"{status} {check.replace('_', ' ').title()}: {'PASS' if passed else 'NO DATA'}")
        
        print("\n" + "="*70)
        if all_good:
            print("  ✅ ALL SYSTEMS OPERATIONAL - Data is being stored!")
        else:
            print("  ⚠️  Some tables have no data yet (expected for new deployments)")
        print("="*70 + "\n")
        
        return all_good


if __name__ == "__main__":
    try:
        run_verification()
    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
