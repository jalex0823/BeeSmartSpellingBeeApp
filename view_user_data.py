"""
Database Access Tool - View and Manage User Data
Provides easy access to user information including emails for password resets.
"""

from AjaSpellBApp import app, db
from models import User, QuizSession
from datetime import datetime

def show_all_users():
    """Display all users with their email addresses"""
    with app.app_context():
        print("\n" + "="*80)
        print("👥 ALL USERS IN DATABASE")
        print("="*80)
        
        users = User.query.order_by(User.created_at.desc()).all()
        
        if not users:
            print("\n⚠️  No users found in database")
            return
        
        print(f"\n📊 Total Users: {len(users)}\n")
        
        # Table header
        print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Role':<10} {'Created':<12}")
        print("-" * 80)
        
        for user in users:
            user_id = str(user.id)
            username = user.username[:20]
            email = (user.email or 'No email')[:30]
            role = user.role
            created = user.created_at.strftime('%Y-%m-%d') if user.created_at else 'N/A'
            
            print(f"{user_id:<5} {username:<20} {email:<30} {role:<10} {created:<12}")
        
        print("\n" + "="*80 + "\n")


def show_user_details(username_or_email):
    """Show detailed information for a specific user"""
    with app.app_context():
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if not user:
            print(f"\n❌ User not found: {username_or_email}")
            return
        
        print("\n" + "="*80)
        print(f"👤 USER DETAILS: {user.display_name}")
        print("="*80)
        
        print(f"\n📝 Basic Information:")
        print(f"   ID: {user.id}")
        print(f"   UUID: {user.uuid}")
        print(f"   Username: {user.username}")
        print(f"   Display Name: {user.display_name}")
        print(f"   Email: {user.email or 'No email set'}")
        print(f"   Role: {user.role}")
        print(f"   Active: {'Yes' if user.is_active else 'No'}")
        print(f"   Email Verified: {'Yes' if user.email_verified else 'No'}")
        
        print(f"\n📊 Stats:")
        print(f"   Total Quizzes: {user.total_quizzes_completed or 0}")
        print(f"   Total Points: {user.total_lifetime_points or 0}")
        print(f"   Cumulative GPA: {user.cumulative_gpa or 0.0}")
        print(f"   Average Accuracy: {user.average_accuracy or 0.0}%")
        print(f"   Best Grade: {user.best_grade or 'N/A'}")
        print(f"   Best Streak: {user.best_streak or 0}")
        
        print(f"\n🕐 Account Info:")
        print(f"   Created: {user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else 'N/A'}")
        print(f"   Last Login: {user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never'}")
        print(f"   Last Login IP: {user.last_login_ip or 'N/A'}")
        
        if user.role in ['teacher', 'parent']:
            print(f"\n👨‍🏫 Teacher/Parent Info:")
            print(f"   Teacher Key: {user.teacher_key or 'N/A'}")
        
        # Show recent quiz sessions
        recent_sessions = QuizSession.query.filter_by(
            user_id=user.id,
            completed=True
        ).order_by(QuizSession.session_start.desc()).limit(5).all()
        
        if recent_sessions:
            print(f"\n📝 Recent Quiz Sessions (Last 5):")
            print(f"   {'Date':<12} {'Words':<8} {'Accuracy':<10} {'Grade':<6} {'Points':<8}")
            print(f"   {'-'*50}")
            for session in recent_sessions:
                date = session.started_at.strftime('%Y-%m-%d') if session.started_at else 'N/A'
                words = f"{session.correct_count}/{session.total_words}"
                accuracy = f"{session.accuracy_percentage:.1f}%" if session.accuracy_percentage else 'N/A'
                grade = session.grade or 'N/A'
                points = session.points_earned or 0
                print(f"   {date:<12} {words:<8} {accuracy:<10} {grade:<6} {points:<8}")
        
        print("\n" + "="*80 + "\n")


def update_user_email(username, new_email):
    """Update a user's email address"""
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"\n❌ User not found: {username}")
            return
        
        # Check if email already exists
        existing = User.query.filter_by(email=new_email).first()
        if existing and existing.id != user.id:
            print(f"\n❌ Email already in use: {new_email}")
            return
        
        old_email = user.email
        user.email = new_email
        db.session.commit()
        
        print(f"\n✅ Email updated successfully!")
        print(f"   User: {username}")
        print(f"   Old Email: {old_email or 'None'}")
        print(f"   New Email: {new_email}")


def search_users(search_term):
    """Search users by username or email"""
    with app.app_context():
        users = User.query.filter(
            (User.username.like(f'%{search_term}%')) |
            (User.email.like(f'%{search_term}%')) |
            (User.display_name.like(f'%{search_term}%'))
        ).all()
        
        if not users:
            print(f"\n❌ No users found matching: {search_term}")
            return
        
        print(f"\n🔍 Search Results for '{search_term}':")
        print(f"   Found {len(users)} user(s)\n")
        
        print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Display Name':<25}")
        print("-" * 80)
        
        for user in users:
            print(f"{user.id:<5} {user.username:<20} {(user.email or 'No email'):<30} {user.display_name:<25}")
        
        print()


def show_users_without_email():
    """Show users who don't have an email set"""
    with app.app_context():
        users = User.query.filter(
            (User.email == None) | (User.email == '')
        ).all()
        
        if not users:
            print("\n✅ All users have email addresses!")
            return
        
        print(f"\n⚠️  Users Without Email Addresses ({len(users)}):")
        print(f"{'ID':<5} {'Username':<20} {'Display Name':<25} {'Role':<10}")
        print("-" * 70)
        
        for user in users:
            print(f"{user.id:<5} {user.username:<20} {user.display_name:<25} {user.role:<10}")
        
        print("\n💡 Tip: Use update_user_email() to add email addresses")
        print()


def main_menu():
    """Interactive menu for database access"""
    print("\n" + "="*80)
    print("🐝 BEESMART DATABASE ACCESS TOOL")
    print("="*80)
    print("\nOptions:")
    print("  1. Show all users")
    print("  2. Show user details")
    print("  3. Search users")
    print("  4. Show users without email")
    print("  5. Update user email")
    print("  6. Exit")
    print()
    
    choice = input("Select option (1-6): ").strip()
    
    if choice == '1':
        show_all_users()
    elif choice == '2':
        username = input("Enter username or email: ").strip()
        if username:
            show_user_details(username)
    elif choice == '3':
        search_term = input("Enter search term: ").strip()
        if search_term:
            search_users(search_term)
    elif choice == '4':
        show_users_without_email()
    elif choice == '5':
        username = input("Enter username: ").strip()
        email = input("Enter new email: ").strip()
        if username and email:
            update_user_email(username, email)
    elif choice == '6':
        print("\n👋 Goodbye!")
        return False
    else:
        print("\n❌ Invalid option")
    
    return True


if __name__ == "__main__":
    # Quick access functions - uncomment the one you need:
    
    # Show all users with emails
    show_all_users()
    
    # Show users without email addresses
    # show_users_without_email()
    
    # Show details for specific user
    # show_user_details('admin')
    
    # Search for users
    # search_users('student')
    
    # Update user email
    # update_user_email('admin', 'admin@example.com')
    
    # Interactive menu
    # while main_menu():
    #     pass
