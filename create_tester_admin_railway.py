"""
Create Tester1 admin account on Railway PostgreSQL
Run with: railway run python create_tester_admin_railway.py

Credentials:
- Username: Tester1
- Password: Password0823
- Role: admin
- Admin All Access: True
"""
from AjaSpellBApp import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    print("=" * 70)
    print("🐝 RAILWAY - Creating Tester1 Admin Account")
    print("=" * 70)
    print()
    
    # Check if user already exists
    existing = User.query.filter(
        db.func.lower(User.username) == 'tester1'
    ).first()
    
    if existing:
        print("⚠️  User 'Tester1' already exists on Railway!")
        print(f"   Username: {existing.username}")
        print(f"   Display Name: {existing.display_name}")
        print(f"   Role: {existing.role}")
        print(f"   Admin All Access: {existing.admin_all_access}")
        print(f"   Premium Member: {existing.premium_member}")
        print(f"   Is Active: {existing.is_active}")
        print(f"   Created: {existing.created_at}")
        print()
        print("✅ Account already configured correctly!")
        print("=" * 70)
    else:
        # Create new Tester1 admin
        print("🔧 Creating new Tester1 admin account...")
        
        tester = User(
            username='Tester1',
            display_name='Tester Admin',
            password_hash=generate_password_hash('Password0823'),
            role='admin',
            admin_all_access=True,
            premium_member=True,
            is_active=True,
            email_verified=True
        )
        
        db.session.add(tester)
        db.session.commit()
        
        print()
        print("✅ TESTER1 ADMIN ACCOUNT CREATED ON RAILWAY!")
        print("=" * 70)
        print("📋 Account Details:")
        print(f"   Username: Tester1")
        print(f"   Password: Password0823")
        print(f"   Display Name: {tester.display_name}")
        print(f"   Role: {tester.role}")
        print(f"   Admin All Access: {tester.admin_all_access}")
        print(f"   Premium Member: {tester.premium_member}")
        print(f"   Is Active: {tester.is_active}")
        print(f"   Database ID: {tester.id}")
        print()
        print("🎯 Ready to share with beta testers!")
        print("=" * 70)
