#!/usr/bin/env python3
"""
Recalculate GPA and grades for all users in the system.

This script re-runs the update_gpa_and_accuracy() method for all users
to ensure GPA, best_grade, and average_accuracy are correctly calculated
based on their quiz/speed round history.

Usage:
    python scripts/recalculate_all_gpa.py
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import db, User
from AjaSpellBApp import app

def recalculate_all_gpa():
    """Recalculate GPA and grades for all users."""
    
    with app.app_context():
        print("🔄 Recalculating GPA and grades for all users...\n")
        
        # Get all users
        users = User.query.all()
        print(f"📊 Found {len(users)} users in database\n")
        
        updated_count = 0
        skipped_count = 0
        
        for user in users:
            old_gpa = float(user.cumulative_gpa) if user.cumulative_gpa else 0.0
            old_grade = user.best_grade or "N/A"
            old_accuracy = float(user.average_accuracy) if user.average_accuracy else 0.0
            
            # Recalculate
            try:
                user.update_gpa_and_accuracy()
                db.session.commit()
                
                new_gpa = float(user.cumulative_gpa) if user.cumulative_gpa else 0.0
                new_grade = user.best_grade or "N/A"
                new_accuracy = float(user.average_accuracy) if user.average_accuracy else 0.0
                
                # Check if anything changed
                if (old_gpa != new_gpa or old_grade != new_grade or 
                    abs(old_accuracy - new_accuracy) > 0.01):
                    print(f"✅ Updated {user.username} ({user.role}):")
                    print(f"   GPA: {old_gpa:.2f} → {new_gpa:.2f}")
                    print(f"   Grade: {old_grade} → {new_grade}")
                    print(f"   Accuracy: {old_accuracy:.1f}% → {new_accuracy:.1f}%\n")
                    updated_count += 1
                else:
                    skipped_count += 1
                    
            except Exception as e:
                print(f"❌ Error updating {user.username}: {e}\n")
                db.session.rollback()
        
        print(f"\n{'='*60}")
        print(f"📈 Recalculation complete!")
        print(f"   Updated: {updated_count} users")
        print(f"   Unchanged: {skipped_count} users")
        print(f"   Total: {len(users)} users")
        print(f"{'='*60}\n")

if __name__ == "__main__":
    print("="*60)
    print("🎯 GPA & Grade Recalculation Tool")
    print("="*60)
    print("\nThis will recalculate GPA and grades for ALL users")
    print("based on their quiz and speed round history.\n")
    
    confirm = input("Continue? (yes/no): ").strip().lower()
    
    if confirm in ['yes', 'y']:
        recalculate_all_gpa()
        print("✨ Done!")
    else:
        print("❌ Cancelled")
