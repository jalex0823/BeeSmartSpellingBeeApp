"""
Quick diagnostic to check user stats in database
"""
from AjaSpellBApp import app, db
from models import User, QuizSession

with app.app_context():
    print("=" * 80)
    print("USER STATS DIAGNOSTIC")
    print("=" * 80)
    
    # Find the admin user
    admin = User.query.filter_by(username='admin').first()
    
    if not admin:
        print("\n❌ No 'admin' user found")
        print("\nAll users:")
        users = User.query.all()
        for user in users:
            print(f"  - {user.username} (role: {user.role})")
    else:
        print(f"\n✅ Found user: {admin.username}")
        print(f"   Role: {admin.role}")
        print(f"   Total Lifetime Points: {admin.total_lifetime_points}")
        print(f"   Total Quizzes Completed: {admin.total_quizzes_completed}")
        
        # Check quiz sessions
        print(f"\n📊 Quiz Sessions:")
        sessions = QuizSession.query.filter_by(user_id=admin.id).order_by(QuizSession.session_start.desc()).all()
        
        if not sessions:
            print("   ❌ No quiz sessions found!")
        else:
            print(f"   Found {len(sessions)} total sessions")
            print(f"\n   Recent sessions:")
            for i, s in enumerate(sessions[:5], 1):
                status = "✅ Completed" if s.completed else "⏸️  In Progress"
                print(f"   {i}. {status} - {s.correct_count}/{s.total_words} correct, {s.total_points} pts, Grade: {s.grade}")
                print(f"      Started: {s.session_start}, Completed: {s.session_end}")
        
        # Check if there are completed sessions
        completed_sessions = QuizSession.query.filter_by(user_id=admin.id, completed=True).all()
        print(f"\n   Completed sessions: {len(completed_sessions)}")
        
        if completed_sessions:
            total_pts_from_sessions = sum(s.total_points for s in completed_sessions)
            print(f"   Total points from completed sessions: {total_pts_from_sessions}")
            print(f"   User.total_lifetime_points: {admin.total_lifetime_points}")
            
            if total_pts_from_sessions != admin.total_lifetime_points:
                print(f"\n   ⚠️  MISMATCH! Session points ({total_pts_from_sessions}) != User points ({admin.total_lifetime_points})")
    
    print("\n" + "=" * 80)
