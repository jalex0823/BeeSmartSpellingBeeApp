"""
Check Aja's complete profile and teacher relationship
"""
import os
import os

# Use the DB configured in your environment (.env / shell).
if not (os.getenv("DATABASE_URL") or os.getenv("DIGITALOCEAN_DATABASE_URL")):
    raise SystemExit(
        "DATABASE_URL (or DIGITALOCEAN_DATABASE_URL) must be set before running this script."
    )

from AjaSpellBApp import app, db
from models import User, TeacherStudent

with app.app_context():
    # Find both users
    aja = User.query.filter_by(username='PRINCESS').first()
    bigdaddy = User.query.filter_by(username='BigDaddy2').first()
    
    if aja and bigdaddy:
        print("=" * 60)
        print("👑 AJA'S PROFILE")
        print("=" * 60)
        print(f"Username: {aja.username}")
        print(f"Display Name: {aja.display_name}")
        print(f"Role: {aja.role}")
        print(f"Avatar: {aja.avatar_id}")
        print(f"Teacher Key (should be None): {aja.teacher_key}")
        print(f"Total Points: {aja.total_lifetime_points}")
        print(f"Quizzes Completed: {aja.total_quizzes_completed}")
        
        print("\n" + "=" * 60)
        print("👨 BIGDADDY2'S PROFILE")
        print("=" * 60)
        print(f"Username: {bigdaddy.username}")
        print(f"Display Name: {bigdaddy.display_name}")
        print(f"Role: {bigdaddy.role}")
        print(f"Teacher Key (this is HIS key): {bigdaddy.teacher_key}")
        
        print("\n" + "=" * 60)
        print("🔗 TEACHER-STUDENT RELATIONSHIP")
        print("=" * 60)
        
        # Check TeacherStudent link
        link = TeacherStudent.query.filter_by(student_id=aja.id).first()
        
        if link:
            print(f"✅ Link exists!")
            print(f"   Student ID: {link.student_id} (Aja)")
            print(f"   Teacher ID: {link.teacher_user_id} (BigDaddy2)")
            print(f"   Teacher Key: {link.teacher_key}")
            print(f"   Relationship Type: {link.relationship_type}")
            print(f"   Active: {link.is_active}")
            
            # Verify it matches
            if link.teacher_user_id == bigdaddy.id and link.teacher_key == bigdaddy.teacher_key:
                print("\n✅ ✅ ✅ EVERYTHING IS CORRECT! ✅ ✅ ✅")
                print("\nAja IS properly linked to BigDaddy2 through the TeacherStudent table.")
                print("She should appear in BigDaddy2's 'My Students/Family' section.")
            else:
                print("\n⚠️ WARNING: Link data doesn't match!")
        else:
            print("❌ No TeacherStudent link found!")
            print("\nThis means Aja is NOT linked to BigDaddy2.")
            print("We need to create this link.")
        
        print("\n" + "=" * 60)
        print("💡 IMPORTANT NOTES")
        print("=" * 60)
        print("1. Students should NOT have teacher_key in their User record")
        print("2. Only teachers/parents/admins have teacher_key values")
        print("3. Students are linked via the TeacherStudent join table")
        print("4. The admin panel showing '-' for Aja's teacher_key is CORRECT")
        print("5. Don't try to set teacher_key on student accounts!")
        
    else:
        print("❌ Could not find one or both users")
