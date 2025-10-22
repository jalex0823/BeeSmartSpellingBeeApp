"""
Database Initialization Script
Run this to create all database tables and optionally add test data
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import get_config
from models import db, User, QuizSession, QuizResult, WordMastery, TeacherStudent
from models import WordList, WordListItem, Achievement, SessionLog, ExportRequest


def create_app():
    """Create Flask app with database configuration"""
    app = Flask(__name__)
    app.config.from_object(get_config())
    db.init_app(app)
    return app


def init_database(create_test_data=False, drop_tables=False):
    """Initialize database tables"""
    app = create_app()
    
    with app.app_context():
        print("🐝 BeeSmart Database Initialization")
        print("=" * 50)
        
        # Drop all tables (WARNING: This deletes all data!)
        if drop_tables:
            print("🗑️  Dropping all tables...")
            db.drop_all()
            print("✅ Tables dropped")
        
        # Create all tables (this is safe - won't drop existing data)
        print("\n📊 Creating database tables...")
        db.create_all()
        
        # List created tables
        tables = db.metadata.tables.keys()
        print(f"\n✅ Created {len(tables)} tables:")
        for table in sorted(tables):
            print(f"   - {table}")
        
        # Create test data if requested
        if create_test_data:
            print("\n🧪 Creating test data...")
            create_test_users(app)
        
        print("\n✨ Database initialization complete!")
        print(f"📍 Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")


def create_test_users(app):
    """Create test users for development"""
    with app.app_context():
        # Check if users already exist
        if User.query.first():
            print("   ⚠️  Users already exist, skipping test data creation")
            return
        
        # Create admin user
        admin = User(
            username='admin',
            display_name='Administrator',
            email='admin@beesmart.app',
            role='admin'
        )
        admin.set_password('admin123')
        admin.generate_teacher_key()
        
        # Create test teacher
        teacher = User(
            username='teacher_smith',
            display_name='Mrs. Smith',
            email='smith@school.edu',
            role='teacher',
            school_name='Example Elementary School'
        )
        teacher.set_password('teacher123')
        teacher.generate_teacher_key()
        
        # Create test student 1
        student1 = User(
            username='alex_student',
            display_name='Alex Johnson',
            email='alex@example.com',
            role='student',
            grade_level='5th Grade'
        )
        student1.set_password('student123')
        
        # Create test student 2
        student2 = User(
            username='sara_student',
            display_name='Sara Martinez',
            email='sara@example.com',
            role='student',
            grade_level='4th Grade'
        )
        student2.set_password('student123')
        
        db.session.add_all([admin, teacher, student1, student2])
        db.session.commit()
        
        # Link teacher to students
        link1 = TeacherStudent(
            teacher_key=teacher.teacher_key,
            teacher_user_id=teacher.id,
            student_id=student1.id,
            relationship_type='teacher'
        )
        link2 = TeacherStudent(
            teacher_key=teacher.teacher_key,
            teacher_user_id=teacher.id,
            student_id=student2.id,
            relationship_type='teacher'
        )
        db.session.add_all([link1, link2])
        db.session.commit()
        
        print("\n✅ Test users created:")
        print(f"   👑 Admin:    admin / admin123")
        print(f"   👩‍🏫 Teacher:  teacher_smith / teacher123")
        print(f"      Teacher Key: {teacher.teacher_key}")
        print(f"   👦 Student 1: alex_student / student123")
        print(f"   👧 Student 2: sara_student / student123")


def check_database():
    """Check database connection and table status"""
    app = create_app()
    
    with app.app_context():
        print("🐝 BeeSmart Database Status Check")
        print("=" * 50)
        print(f"📍 Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        try:
            # Try to query database
            user_count = User.query.count()
            session_count = QuizSession.query.count()
            result_count = QuizResult.query.count()
            
            print(f"\n✅ Database connection successful!")
            print(f"\n📊 Current data:")
            print(f"   Users: {user_count}")
            print(f"   Quiz Sessions: {session_count}")
            print(f"   Quiz Results: {result_count}")
            
            # List all users
            if user_count > 0:
                print(f"\n👥 Users in database:")
                users = User.query.all()
                for user in users:
                    print(f"   - {user.username} ({user.role}) - {user.display_name}")
                    if user.teacher_key:
                        print(f"     Teacher Key: {user.teacher_key}")
        
        except Exception as e:
            print(f"\n❌ Database error: {e}")
            print("\n💡 Try running: python init_db.py")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'init':
            # Initialize database with optional test data
            create_test = '--test-data' in sys.argv
            init_database(create_test_data=create_test, drop_tables=False)
        
        elif command == 'check':
            # Check database status
            check_database()
        
        elif command == 'test-data':
            # Just create test data
            app = create_app()
            create_test_users(app)
        
        else:
            print("❌ Unknown command")
            print("\nUsage:")
            print("  python init_db.py init [--test-data]  # Initialize database")
            print("  python init_db.py check                # Check database status")
            print("  python init_db.py test-data            # Create test users")
    
    else:
        # Interactive mode
        print("🐝 BeeSmart Database Setup")
        print("\nWhat would you like to do?")
        print("1. Initialize database (create tables)")
        print("2. Initialize + create test data")
        print("3. Check database status")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ")
        
        if choice == '1':
            init_database(create_test_data=False, drop_tables=False)
        elif choice == '2':
            init_database(create_test_data=True, drop_tables=False)
        elif choice == '3':
            check_database()
        elif choice == '4':
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")
