"""
Verify GPA tracking data is being stored in the database.
"""
from AjaSpellBApp import app, db
from models import User, QuizSession

def verify_gpa_storage():
    with app.app_context():
        print("\n" + "="*60)
        print("🔍 GPA STORAGE VERIFICATION")
        print("="*60)
        
        # Check all users
        users = User.query.all()
        print(f"\n📊 Found {len(users)} users in database\n")
        
        for user in users:
            print(f"👤 User: {user.username} ({user.display_name})")
            print(f"   Role: {user.role}")
            print(f"   Total Quizzes: {user.total_quizzes_completed or 0}")
            print(f"   Total Points: {user.total_lifetime_points or 0}")
            print(f"   🎓 Cumulative GPA: {user.cumulative_gpa or 0.0}")
            print(f"   🎯 Average Accuracy: {user.average_accuracy or 0.0}%")
            print(f"   ⭐ Best Grade: {user.best_grade or 'N/A'}")
            print(f"   🔥 Best Streak: {user.best_streak or 0}")
            
            # Check completed quizzes
            completed_quizzes = QuizSession.query.filter_by(
                user_id=user.id,
                completed=True
            ).all()
            
            print(f"\n   📝 Completed Quiz Sessions: {len(completed_quizzes)}")
            
            if completed_quizzes:
                print(f"   {'Date':<20} {'Accuracy':<12} {'Grade':<8} {'Points':<10}")
                print(f"   {'-'*60}")
                for quiz in completed_quizzes[:5]:  # Show last 5
                    date = quiz.started_at.strftime('%Y-%m-%d %H:%M') if quiz.started_at else 'N/A'
                    accuracy = f"{quiz.accuracy_percentage:.1f}%" if quiz.accuracy_percentage else 'N/A'
                    grade = quiz.grade or 'N/A'
                    points = quiz.points_earned or 0
                    print(f"   {date:<20} {accuracy:<12} {grade:<8} {points:<10}")
                
                if len(completed_quizzes) > 5:
                    print(f"   ... and {len(completed_quizzes) - 5} more")
            
            print("\n" + "-"*60 + "\n")
        
        # Summary
        print("\n" + "="*60)
        print("📈 SUMMARY")
        print("="*60)
        
        total_completed = QuizSession.query.filter_by(completed=True).count()
        users_with_gpa = User.query.filter(User.cumulative_gpa > 0).count()
        users_with_quizzes = User.query.filter(User.total_quizzes_completed > 0).count()
        
        print(f"Total Completed Quizzes: {total_completed}")
        print(f"Users with GPA > 0: {users_with_gpa}")
        print(f"Users with Quizzes > 0: {users_with_quizzes}")
        
        if total_completed > 0 and users_with_gpa == 0:
            print("\n⚠️  WARNING: Quizzes completed but no GPA data!")
            print("   This suggests GPA is not being calculated/stored.")
        elif users_with_quizzes > 0 and users_with_gpa > 0:
            print("\n✅ SUCCESS: GPA tracking is working correctly!")
        else:
            print("\n💡 No quizzes completed yet. Complete a quiz to test GPA tracking.")
        
        print("="*60 + "\n")

if __name__ == "__main__":
    verify_gpa_storage()
