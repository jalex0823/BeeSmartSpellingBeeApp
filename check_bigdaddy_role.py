"""
Check BigDaddy account role and fix if needed
"""
from AjaSpellBApp import app, db, User

with app.app_context():
    # Find BigDaddy account
    bigdaddy = User.query.filter_by(username='BigDaddy').first()
    
    if not bigdaddy:
        print("❌ BigDaddy account not found")
        print("\nSearching for all admin accounts...")
        admins = User.query.filter_by(role='admin').all()
        if admins:
            print(f"\n✅ Found {len(admins)} admin account(s):")
            for admin in admins:
                print(f"   • {admin.username} (ID: {admin.id}, Email: {admin.email})")
        else:
            print("❌ No admin accounts found!")
        
        print("\nSearching for BigDaddy-related usernames...")
        similar = User.query.filter(User.username.like('%BigDaddy%')).all()
        if similar:
            for u in similar:
                print(f"   • {u.username} (ID: {u.id}, Role: {u.role})")
    else:
        print(f"✅ Found BigDaddy account")
        print(f"   Display Name: {bigdaddy.display_name}")
        print(f"   ID: {bigdaddy.id}")
        print(f"   Role: {bigdaddy.role}")
        print(f"   Email: {bigdaddy.email}")
        print(f"   Teacher Key: {bigdaddy.teacher_key}")
        print(f"   Is Active: {bigdaddy.is_active}")
        
        # Check if role is admin
        if bigdaddy.role != 'admin':
            print(f"\n⚠️  WARNING: BigDaddy role is '{bigdaddy.role}' not 'admin'")
            print(f"   Fixing role to 'admin'...")
            bigdaddy.role = 'admin'
            db.session.commit()
            print(f"   ✅ Role updated to 'admin'")
        else:
            print(f"\n✅ Role is correctly set to 'admin'")
