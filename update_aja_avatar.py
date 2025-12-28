"""
Script to update Aja's avatar to Queen Bee (if not already)
and verify she's linked to BigDaddy2 via TeacherStudent table
"""
import os

# Use the DB configured in your environment (.env / shell).
if not (os.getenv("DATABASE_URL") or os.getenv("DIGITALOCEAN_DATABASE_URL")):
    raise SystemExit(
        "DATABASE_URL (or DIGITALOCEAN_DATABASE_URL) must be set before running this script."
    )

from AjaSpellBApp import app, db
from models import User, TeacherStudent

with app.app_context():
    # Find Aja by username (her username is PRINCESS)
    aja = User.query.filter_by(username='PRINCESS').first()
    
    if aja:
        print(f"✅ Found user: {aja.display_name} (username: {aja.username})")
        print(f"📝 Current avatar: {aja.avatar_id}")
        print(f"📝 Current variant: {aja.avatar_variant}")
        
        changes_made = []
        
        # Update to Queen Bee if not already
        if aja.avatar_id != 'queen-bee':
            aja.avatar_id = 'queen-bee'
            aja.avatar_variant = 'default'
            changes_made.append("avatar updated to Queen Bee")
        else:
            print(f"✅ Already using Queen Bee avatar!")
        
        if changes_made:
            db.session.commit()
            print(f"\n🎉 SUCCESS! Changes made:")
            for change in changes_made:
                print(f"  ✅ {change}")
        else:
            print(f"\n✨ No changes needed - avatar already set correctly!")
        
        # Check TeacherStudent link
        print(f"\n🔗 Checking teacher/parent link...")
        teacher_link = TeacherStudent.query.filter_by(student_id=aja.id).first()
        
        if teacher_link:
            teacher = User.query.get(teacher_link.teacher_user_id)
            print(f"✅ Linked to: {teacher.display_name} ({teacher.username})")
            print(f"✅ Teacher Key: {teacher_link.teacher_key}")
        else:
            print(f"⚠️ No teacher/parent link found")
            print(f"💡 Aja should be linked to BigDaddy2 via TeacherStudent table")
        
        # Show final state
        print(f"\n📋 Final state:")
        print(f"  👑 Avatar: {aja.avatar_id}")
        print(f"  � Linked: {'Yes' if teacher_link else 'No'}")
        
    else:
        print("❌ User 'PRINCESS' not found")
        
        # Show available users
        print("\nAvailable users:")
        all_users = User.query.all()
        for user in all_users:
            print(f"  - {user.username} ({user.display_name}) - Role: {user.role}")
