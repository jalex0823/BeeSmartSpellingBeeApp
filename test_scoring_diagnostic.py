#!/usr/bin/env python3
"""
Comprehensive Points and Grades Diagnostic Test
Tests all quiz types and scoring calculations
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from AjaSpellBApp import app, db
from models import User, QuizSession
from datetime import datetime, timedelta

def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def test_user_metrics(username="Aja"):
    """Test current user metrics from database"""
    print_section("CURRENT USER METRICS TEST")
    
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"❌ User '{username}' not found!")
            return None
        
        print(f"✅ User Found: {user.username}")
        print(f"\n📊 Current Metrics:")
        print(f"   Points: {user.points:,}")
        print(f"   Grade: {user.grade}")
        print(f"   GPA: {user.gpa:.2f}")
        print(f"   Accuracy: {user.accuracy:.2f}%")
        print(f"   Quizzes Taken: {user.quizzes_taken}")
        print(f"   Words Correct: {user.words_correct}")
        print(f"   Words Incorrect: {user.words_incorrect}")
        
        total_words = user.words_correct + user.words_incorrect
        if total_words > 0:
            calculated_accuracy = (user.words_correct / total_words) * 100
            print(f"\n🔍 Verification:")
            print(f"   Total Words: {total_words}")
            print(f"   Calculated Accuracy: {calculated_accuracy:.2f}%")
            print(f"   Stored Accuracy: {user.accuracy:.2f}%")
            
            if abs(calculated_accuracy - user.accuracy) > 0.1:
                print(f"   ⚠️  Accuracy mismatch!")
            else:
                print(f"   ✅ Accuracy matches!")
        
        return user

def test_quiz_sessions(username="Aja", limit=10):
    """Test recent quiz sessions and their scores"""
    print_section("RECENT QUIZ SESSIONS TEST")
    
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"❌ User '{username}' not found!")
            return
        
        sessions = QuizSession.query.filter_by(user_id=user.id)\
            .order_by(QuizSession.completed_at.desc())\
            .limit(limit)\
            .all()
        
        if not sessions:
            print(f"No quiz sessions found for {username}")
            return
        
        print(f"Found {len(sessions)} recent quiz sessions:\n")
        
        total_points = 0
        total_correct = 0
        total_incorrect = 0
        
        for i, session in enumerate(sessions, 1):
            print(f"{i}. Session ID: {session.id}")
            print(f"   Type: {session.quiz_type}")
            print(f"   Completed: {session.completed_at}")
            print(f"   Score: {session.score}/{session.total_words}")
            print(f"   Points Earned: {session.points_earned:,}")
            print(f"   Accuracy: {session.accuracy:.1f}%")
            print(f"   Grade: {session.grade}")
            
            total_points += session.points_earned
            total_correct += session.score
            total_incorrect += (session.total_words - session.score)
            
            # Verify session accuracy
            if session.total_words > 0:
                calc_accuracy = (session.score / session.total_words) * 100
                if abs(calc_accuracy - session.accuracy) > 0.1:
                    print(f"   ⚠️  Session accuracy mismatch! Calc: {calc_accuracy:.1f}%, Stored: {session.accuracy:.1f}%")
                else:
                    print(f"   ✅ Session accuracy correct")
            print()
        
        print(f"\n📊 Session Totals (last {len(sessions)} quizzes):")
        print(f"   Total Points from Sessions: {total_points:,}")
        print(f"   Total Correct: {total_correct}")
        print(f"   Total Incorrect: {total_incorrect}")
        
        if total_correct + total_incorrect > 0:
            overall_accuracy = (total_correct / (total_correct + total_incorrect)) * 100
            print(f"   Overall Accuracy from Sessions: {overall_accuracy:.2f}%")

def test_gpa_calculation(username="Aja"):
    """Test GPA calculation logic"""
    print_section("GPA CALCULATION TEST")
    
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"❌ User '{username}' not found!")
            return
        
        sessions = QuizSession.query.filter_by(user_id=user.id).all()
        
        if not sessions:
            print("No quiz sessions to calculate GPA from")
            return
        
        print(f"Calculating GPA from {len(sessions)} quiz sessions...\n")
        
        # GPA calculation logic from update_gpa_and_accuracy
        grade_points = {
            'A+': 4.0, 'A': 4.0, 'A-': 3.7,
            'B+': 3.3, 'B': 3.0, 'B-': 2.7,
            'C+': 2.3, 'C': 2.0, 'C-': 1.7,
            'D+': 1.3, 'D': 1.0, 'D-': 0.7,
            'F': 0.0
        }
        
        total_grade_points = 0
        valid_sessions = 0
        
        for session in sessions:
            if session.grade and session.grade in grade_points:
                total_grade_points += grade_points[session.grade]
                valid_sessions += 1
        
        if valid_sessions > 0:
            calculated_gpa = total_grade_points / valid_sessions
            print(f"✅ GPA Calculation:")
            print(f"   Valid Sessions: {valid_sessions}")
            print(f"   Total Grade Points: {total_grade_points:.2f}")
            print(f"   Calculated GPA: {calculated_gpa:.2f}")
            print(f"   Stored GPA: {user.gpa:.2f}")
            
            if abs(calculated_gpa - user.gpa) > 0.01:
                print(f"   ⚠️  GPA mismatch!")
            else:
                print(f"   ✅ GPA matches!")
            
            # Determine grade from GPA
            if calculated_gpa >= 3.7:
                expected_grade = 'A'
            elif calculated_gpa >= 3.3:
                expected_grade = 'B+'
            elif calculated_gpa >= 3.0:
                expected_grade = 'B'
            elif calculated_gpa >= 2.7:
                expected_grade = 'B-'
            elif calculated_gpa >= 2.3:
                expected_grade = 'C+'
            elif calculated_gpa >= 2.0:
                expected_grade = 'C'
            elif calculated_gpa >= 1.7:
                expected_grade = 'C-'
            elif calculated_gpa >= 1.3:
                expected_grade = 'D+'
            elif calculated_gpa >= 1.0:
                expected_grade = 'D'
            elif calculated_gpa >= 0.7:
                expected_grade = 'D-'
            else:
                expected_grade = 'F'
            
            print(f"\n   Expected Grade from GPA: {expected_grade}")
            print(f"   Stored Grade: {user.grade}")
            
            if expected_grade != user.grade:
                print(f"   ⚠️  Grade mismatch!")
            else:
                print(f"   ✅ Grade matches!")

def test_points_calculation(username="Aja"):
    """Test points calculation logic"""
    print_section("POINTS CALCULATION TEST")
    
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"❌ User '{username}' not found!")
            return
        
        sessions = QuizSession.query.filter_by(user_id=user.id).all()
        
        if not sessions:
            print("No quiz sessions to calculate points from")
            return
        
        total_session_points = sum(s.points_earned for s in sessions)
        
        print(f"✅ Points Calculation:")
        print(f"   Total Sessions: {len(sessions)}")
        print(f"   Sum of Session Points: {total_session_points:,}")
        print(f"   User Total Points: {user.points:,}")
        
        # Note: User points might include bonus points, achievements, etc.
        if total_session_points > user.points:
            print(f"   ⚠️  Session points exceed user points!")
        elif total_session_points == user.points:
            print(f"   ✅ Points match exactly!")
        else:
            diff = user.points - total_session_points
            print(f"   ℹ️  User has {diff:,} additional points (likely from bonuses/achievements)")

def test_answer_endpoint_logic():
    """Test the answer endpoint logic for point calculation"""
    print_section("ANSWER ENDPOINT LOGIC TEST")
    
    print("Testing point calculation formulas:\n")
    
    # Test cases for different scenarios
    test_cases = [
        {"word": "hello", "method": "typing", "elapsed_ms": 3000, "correct": True},
        {"word": "beautiful", "method": "typing", "elapsed_ms": 5000, "correct": True},
        {"word": "hello", "method": "voice", "elapsed_ms": 2000, "correct": True},
        {"word": "hello", "method": "multiple_choice", "elapsed_ms": 4000, "correct": True},
        {"word": "hello", "method": "typing", "elapsed_ms": 3000, "correct": False},
    ]
    
    for i, test in enumerate(test_cases, 1):
        word = test["word"]
        method = test["method"]
        elapsed_ms = test["elapsed_ms"]
        correct = test["correct"]
        
        # Calculate points (from /api/answer logic)
        base_points = len(word) * 10
        
        if correct:
            points = base_points
            
            # Time bonus (max 50% bonus)
            time_bonus_multiplier = max(0, 1 - (elapsed_ms / 10000))
            time_bonus = int(base_points * time_bonus_multiplier * 0.5)
            points += time_bonus
            
            # Method bonus
            if method == 'typing':
                points = int(points * 1.5)  # 50% bonus
            elif method == 'voice':
                points = int(points * 2.0)  # 100% bonus
            # multiple_choice gets no bonus
        else:
            points = 0
        
        print(f"Test {i}: {word} ({method}, {elapsed_ms}ms, {'✓' if correct else '✗'})")
        print(f"   Base Points: {base_points}")
        if correct:
            print(f"   Time Bonus: +{time_bonus}")
            if method == 'typing':
                print(f"   Method Bonus: 1.5x (typing)")
            elif method == 'voice':
                print(f"   Method Bonus: 2.0x (voice)")
        print(f"   Final Points: {points}")
        print()

def run_all_diagnostics(username="Aja"):
    """Run all diagnostic tests"""
    print("\n" + "="*80)
    print("  🐝 BEESMART SCORING DIAGNOSTIC TEST SUITE 🐝")
    print("="*80)
    
    # Test 1: Current user metrics
    user = test_user_metrics(username)
    
    if user:
        # Test 2: Recent quiz sessions
        test_quiz_sessions(username, limit=10)
        
        # Test 3: GPA calculation
        test_gpa_calculation(username)
        
        # Test 4: Points calculation
        test_points_calculation(username)
    
    # Test 5: Answer endpoint logic
    test_answer_endpoint_logic()
    
    print_section("DIAGNOSTIC COMPLETE")
    print("✅ All diagnostic tests completed!")
    print("\nRecommendations:")
    print("1. Check for any ⚠️  warnings above")
    print("2. Verify that points are updated after each quiz")
    print("3. Ensure GPA and grade calculations are accurate")
    print("4. Confirm accuracy percentages match expected values")

if __name__ == "__main__":
    run_all_diagnostics()
