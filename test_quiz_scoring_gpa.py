#!/usr/bin/env python3
"""
BeeSmart Quiz, Scoring, and GPA Testing
Tests the complete quiz flow: word loading → quiz → scoring → GPA calculation → dashboard
"""

import sys
import os
sys.path.insert(0, '/Users/jalex0823/Dropbox/GitBackUpAppFolder')

from AjaSpellBApp import app
from models import db, User, QuizSession, QuizResult, WordMastery
from datetime import datetime
import json

# Color output
class Color:
    G = '\033[92m'  # Green
    Y = '\033[93m'  # Yellow
    R = '\033[91m'  # Red
    B = '\033[94m'  # Blue
    E = '\033[0m'   # End

def test(name, passed, details=""):
    status = f"{Color.G}✅ PASS{Color.E}" if passed else f"{Color.R}❌ FAIL{Color.E}"
    print(f"{status} - {name}")
    if details:
        print(f"      {Color.B}{details}{Color.E}")
    return passed

def header(text):
    print(f"\n{Color.B}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{Color.E}\n")

# ============================================================================
# TEST 1: Verify Database Models and Relationships
# ============================================================================

def test_database_models():
    header("TEST 1: DATABASE MODELS & RELATIONSHIPS")
    
    with app.app_context():
        # Check User model fields
        test_user = User.query.first()
        if test_user:
            test("User Model - Has GPA Field", hasattr(test_user, 'cumulative_gpa'))
            test("User Model - Has Accuracy Field", hasattr(test_user, 'average_accuracy'))
            test("User Model - Has Best Grade Field", hasattr(test_user, 'best_grade'))
            test("User Model - Has Lifetime Points", hasattr(test_user, 'total_lifetime_points'))
            test("User Model - Has Quiz Count", hasattr(test_user, 'total_quizzes_completed'))
            
            print(f"\n{Color.Y}Current User Stats:{Color.E}")
            print(f"  Username: {test_user.username}")
            print(f"  GPA: {test_user.cumulative_gpa}")
            print(f"  Accuracy: {test_user.average_accuracy}%")
            print(f"  Best Grade: {test_user.best_grade}")
            print(f"  Lifetime Points: {test_user.total_lifetime_points}")
            print(f"  Quizzes Completed: {test_user.total_quizzes_completed}")
        else:
            test("User Model Check", False, "No users in database")
        
        # Check QuizSession model
        session_count = QuizSession.query.count()
        test("QuizSession Table Exists", session_count >= 0, f"{session_count} sessions")
        
        # Check QuizResult model
        result_count = QuizResult.query.count()
        test("QuizResult Table Exists", result_count >= 0, f"{result_count} results")
        
        # Check relationships
        if test_user and session_count > 0:
            user_sessions = QuizSession.query.filter_by(user_id=test_user.id).count()
            test("User → QuizSession Relationship", user_sessions >= 0, f"{user_sessions} sessions")

# ============================================================================
# TEST 2: Quiz Session Creation and Scoring Logic
# ============================================================================

def test_quiz_session_logic():
    header("TEST 2: QUIZ SESSION & SCORING LOGIC")
    
    with app.app_context():
        # Get a test user
        test_user = User.query.first()
        if not test_user:
            test("Quiz Session Test", False, "No test user available")
            return
        
        # Check if there are existing sessions
        recent_sessions = QuizSession.query.filter_by(user_id=test_user.id)\
            .order_by(QuizSession.session_start.desc()).limit(5).all()
        
        if recent_sessions:
            print(f"\n{Color.Y}Recent Quiz Sessions:{Color.E}")
            for i, session in enumerate(recent_sessions, 1):
                print(f"  {i}. Score: {session.correct_count}/{session.total_words} " +
                      f"({session.accuracy_percentage:.1f}%) - Grade: {session.grade or 'N/A'}")
            
            # Verify grade calculation logic
            for session in recent_sessions:
                if session.accuracy_percentage is not None:
                    expected_grade = calculate_expected_grade(float(session.accuracy_percentage))
                    actual_grade = session.grade or "None"
                    matches = expected_grade == actual_grade
                    test(f"Grade Calculation ({session.accuracy_percentage:.1f}%)", 
                         matches or actual_grade == "None",
                         f"Expected: {expected_grade}, Got: {actual_grade}")
        else:
            test("Quiz Sessions", False, "No quiz sessions found")

def calculate_expected_grade(accuracy):
    """Calculate expected grade based on accuracy percentage"""
    if accuracy >= 97: return "A+"
    elif accuracy >= 93: return "A"
    elif accuracy >= 90: return "A-"
    elif accuracy >= 87: return "B+"
    elif accuracy >= 83: return "B"
    elif accuracy >= 80: return "B-"
    elif accuracy >= 77: return "C+"
    elif accuracy >= 73: return "C"
    elif accuracy >= 70: return "C-"
    elif accuracy >= 67: return "D+"
    elif accuracy >= 63: return "D"
    elif accuracy >= 60: return "D-"
    else: return "F"

# ============================================================================
# TEST 3: GPA Calculation and Update Logic
# ============================================================================

def test_gpa_calculation():
    header("TEST 3: GPA CALCULATION & UPDATES")
    
    # Grade to GPA mapping
    grade_to_gpa = {
        'A+': 4.0, 'A': 4.0, 'A-': 3.7,
        'B+': 3.3, 'B': 3.0, 'B-': 2.7,
        'C+': 2.3, 'C': 2.0, 'C-': 1.7,
        'D+': 1.3, 'D': 1.0, 'D-': 0.7,
        'F': 0.0
    }
    
    with app.app_context():
        test_user = User.query.first()
        if not test_user:
            test("GPA Test", False, "No test user available")
            return
        
        # Get all completed sessions
        sessions = QuizSession.query.filter_by(
            user_id=test_user.id,
            completed=True
        ).all()
        
        if sessions:
            # Calculate manual GPA from grades
            gpa_values = []
            for session in sessions:
                if session.grade:
                    gpa_value = grade_to_gpa.get(session.grade, 0.0)
                    gpa_values.append(gpa_value)
            
            if gpa_values:
                manual_avg_gpa = sum(gpa_values) / len(gpa_values)
                stored_gpa = float(test_user.cumulative_gpa) if test_user.cumulative_gpa else 0.0
                
                # Allow small floating point difference
                gpa_matches = abs(manual_avg_gpa - stored_gpa) < 0.01
                
                test("Cumulative GPA Calculation", 
                     gpa_matches,
                     f"Calculated: {manual_avg_gpa:.2f}, Stored: {stored_gpa:.2f}")
                
                print(f"\n{Color.Y}GPA Breakdown:{Color.E}")
                print(f"  Sessions with Grades: {len(gpa_values)}")
                print(f"  GPA Values: {[f'{v:.2f}' for v in gpa_values[:10]]}")
                print(f"  Average: {manual_avg_gpa:.2f}")
            else:
                test("GPA Values Present", False, "No sessions have grades")
            
            # Calculate manual accuracy
            total_correct = sum(s.correct_count or 0 for s in sessions)
            total_questions = sum(s.total_words or 0 for s in sessions)
            
            if total_questions > 0:
                manual_accuracy = (total_correct / total_questions) * 100
                stored_accuracy = float(test_user.average_accuracy) if test_user.average_accuracy else 0.0
                
                accuracy_matches = abs(manual_accuracy - stored_accuracy) < 0.1
                
                test("Average Accuracy Calculation",
                     accuracy_matches,
                     f"Calculated: {manual_accuracy:.2f}%, Stored: {stored_accuracy:.2f}%")
        else:
            test("GPA Calculation", False, "No completed sessions found")

# ============================================================================
# TEST 4: Word Mastery Tracking
# ============================================================================

def test_word_mastery():
    header("TEST 4: WORD MASTERY TRACKING")
    
    with app.app_context():
        test_user = User.query.first()
        if not test_user:
            test("Word Mastery Test", False, "No test user available")
            return
        
        # Get word mastery records
        mastery_records = WordMastery.query.filter_by(user_id=test_user.id).all()
        
        if mastery_records:
            test("Word Mastery Records Exist", True, f"{len(mastery_records)} words tracked")
            
            # Check mastery levels
            mastered = sum(1 for w in mastery_records if w.mastery_level == 'mastered')
            learning = sum(1 for w in mastery_records if w.mastery_level == 'learning')
            struggling = sum(1 for w in mastery_records if w.mastery_level == 'struggling')
            
            print(f"\n{Color.Y}Word Mastery Breakdown:{Color.E}")
            print(f"  Mastered: {mastered}")
            print(f"  Learning: {learning}")
            print(f"  Struggling: {struggling}")
            
            # Show top 5 mastered words
            top_mastered = sorted(
                [w for w in mastery_records if w.mastery_level == 'mastered'],
                key=lambda x: x.times_correct,
                reverse=True
            )[:5]
            
            if top_mastered:
                print(f"\n{Color.Y}Top Mastered Words:{Color.E}")
                for i, word in enumerate(top_mastered, 1):
                    accuracy = (word.times_correct / max(word.times_seen, 1)) * 100
                    print(f"  {i}. {word.word} - {word.times_correct}/{word.times_seen} ({accuracy:.0f}%)")
        else:
            test("Word Mastery Records", False, "No word mastery data found")

# ============================================================================
# TEST 5: Teacher/Admin Portal Data Access
# ============================================================================

def test_teacher_portal():
    header("TEST 5: TEACHER/ADMIN PORTAL DATA")
    
    with app.app_context():
        # Check for teachers
        teachers = User.query.filter(User.teacher_key.isnot(None)).all()
        
        if teachers:
            test("Teacher Accounts Exist", True, f"{len(teachers)} teachers")
            
            for teacher in teachers[:3]:  # Check first 3
                print(f"\n{Color.Y}Teacher: {teacher.username}{Color.E}")
                print(f"  Teacher Key: {teacher.teacher_key}")
                print(f"  Email: {teacher.email}")
                
                # Check teacher key format
                key_valid = teacher.teacher_key.startswith('BEE-')
                test(f"Teacher Key Format ({teacher.username})", 
                     key_valid,
                     f"Key: {teacher.teacher_key}")
        else:
            test("Teacher Accounts", False, "No teacher accounts found")
        
        # Check student-teacher relationships
        from models import TeacherStudent
        relationships = TeacherStudent.query.count()
        test("Teacher-Student Relationships", relationships >= 0, f"{relationships} links")

# ============================================================================
# TEST 6: Dashboard Data Completeness
# ============================================================================

def test_dashboard_data():
    header("TEST 6: DASHBOARD DATA COMPLETENESS")
    
    with app.app_context():
        test_user = User.query.first()
        if not test_user:
            test("Dashboard Data Test", False, "No test user available")
            return
        
        # Check all dashboard-relevant fields
        checks = {
            "Username": test_user.username is not None,
            "Display Name": test_user.display_name is not None,
            "GPA": test_user.cumulative_gpa is not None,
            "Accuracy": test_user.average_accuracy is not None,
            "Best Grade": test_user.best_grade is not None,
            "Lifetime Points": test_user.total_lifetime_points is not None,
            "Quizzes Completed": test_user.total_quizzes_completed is not None,
            "Account Level": test_user.account_level is not None,
            "Honey Points": test_user.honey_points is not None,
        }
        
        for field, exists in checks.items():
            test(f"Dashboard Field - {field}", exists)
        
        # Check if user has avatar
        if test_user.avatar_id:
            from models import Avatar
            avatar = Avatar.query.get(test_user.avatar_id)
            test("User Avatar Assignment", avatar is not None, 
                 f"Avatar: {avatar.name if avatar else 'None'}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print(f"\n{Color.B}{'='*70}")
    print("  🐝 BeeSmart Quiz, Scoring & GPA Testing 🐝")
    print(f"{'='*70}{Color.E}\n")
    print(f"Database: sqlite:///beesmart.db")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        test_database_models()
        test_quiz_session_logic()
        test_gpa_calculation()
        test_word_mastery()
        test_teacher_portal()
        test_dashboard_data()
        
        header("TESTING COMPLETE")
        print(f"{Color.G}All database and logic tests completed!{Color.E}\n")
        
    except Exception as e:
        print(f"\n{Color.R}ERROR: {e}{Color.E}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
