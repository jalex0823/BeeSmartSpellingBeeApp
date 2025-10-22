"""
Create Admin User - Big Daddy
Creates a new admin user with specified credentials.
"""

from AjaSpellBApp import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_admin_user():
    """Create admin user: Big Daddy"""
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username='BigDaddy').first()
        if existing_user:
            print("\n⚠️  User 'BigDaddy' already exists!")
            print(f"   ID: {existing_user.id}")
            print(f"   Email: {existing_user.email}")
            print(f"   Role: {existing_user.role}")
            print(f"   Created: {existing_user.created_at}")
            
            response = input("\n❓ Do you want to update the password? (yes/no): ").strip().lower()
            if response == 'yes':
                existing_user.password_hash = generate_password_hash('Aja121514!')
                db.session.commit()
                print("\n✅ Password updated successfully!")
                print(f"   Username: BigDaddy")
                print(f"   New Password: Aja121514!")
            else:
                print("\n❌ Operation cancelled.")
            return
        
        # Create new admin user
        new_admin = User(
            username='BigDaddy',
            display_name='Big Daddy',
            email='bigdaddy@beesmart.app',
            password_hash=generate_password_hash('Aja121514!'),
            role='admin',
            is_active=True,
            email_verified=True
        )
        
        db.session.add(new_admin)
        db.session.commit()
        
        print("\n" + "="*60)
        print("✅ ADMIN USER CREATED SUCCESSFULLY!")
        print("="*60)
        print(f"\n📝 Account Details:")
        print(f"   User ID (Database): {new_admin.id}")
        print(f"   Username: BigDaddy")
        print(f"   Password: Aja121514!")
        print(f"   Display Name: Big Daddy")
        print(f"   Email: bigdaddy@beesmart.app")
        print(f"   Role: admin")
        print(f"   Status: Active")
        print(f"   Email Verified: Yes")
        
        print(f"\n🔐 Login Instructions:")
        print(f"   1. Go to: http://localhost:5000/auth/login")
        print(f"   2. Username: BigDaddy")
        print(f"   3. Password: Aja121514!")
        
        print(f"\n🎯 Admin Capabilities:")
        print(f"   ✅ Full database access")
        print(f"   ✅ User management")
        print(f"   ✅ Teacher key management")
        print(f"   ✅ System administration")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    create_admin_user()
