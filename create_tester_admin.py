"""
Create Tester Admin Account
Creates a tester admin account (Tester1) with password Password0823
"""

from AjaSpellBApp import app, db
from models import User
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_tester_admin():
    """Create Tester1 admin account"""
    
    with app.app_context():
        # Check if tester account already exists
        existing_user = User.query.filter_by(username='Tester1').first()
        if existing_user:
            print("⚠️  User 'Tester1' already exists!")
            print(f"   Username: Tester1")
            print(f"   Role: {existing_user.role}")
            print(f"   Admin All Access: {existing_user.admin_all_access}")
            return
        
        # Create new Tester1 admin account
        tester = User(
            username='Tester1',
            display_name='Tester Admin',
            password_hash=generate_password_hash('Password0823'),
            role='admin',  # Full admin privileges
            admin_all_access=True,  # Bypass all monetization/restrictions
            premium_member=True,  # Premium features
            is_active=True,
            email_verified=True
        )
        
        # Add to database
        db.session.add(tester)
        db.session.commit()
        
        print("\n✅ Tester Admin Account Created Successfully!")
        print("=" * 60)
        print(f"   👤 Username: Tester1")
        print(f"   🔑 Password: Password0823")
        print(f"   📧 Display Name: Tester Admin")
        print(f"   👑 Role: admin")
        print(f"   ✨ Admin All Access: True")
        print(f"   💎 Premium Member: True")
        print(f"   🆔 User ID: {tester.id}")
        print("=" * 60)
        print("\n🔐 Share these credentials with your testers!")
        print("   They have full admin access to test all app features. 🐝\n")

if __name__ == '__main__':
    try:
        create_tester_admin()
    except Exception as e:
        print(f"\n❌ Error creating tester admin: {e}")
        import traceback
        traceback.print_exc()
