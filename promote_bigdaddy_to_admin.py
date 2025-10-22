"""
Promote BigDaddy account to admin role on Railway
Run this with: railway run python promote_bigdaddy_to_admin.py
"""
from AjaSpellBApp import app, db, User

with app.app_context():
    # Find BigDaddy account (case-insensitive)
    bigdaddy = User.query.filter(
        db.func.lower(User.username) == 'bigdaddy'
    ).first()
    
    if not bigdaddy:
        print("❌ BigDaddy account not found")
        print("\nSearching for similar usernames...")
        similar = User.query.filter(
            User.username.ilike('%daddy%')
        ).all()
        if similar:
            for u in similar:
                print(f"   • {u.username} (ID: {u.id}, Role: {u.role})")
        else:
            print("❌ No similar accounts found")
    else:
        print(f"✅ Found: {bigdaddy.username}")
        print(f"   ID: {bigdaddy.id}")
        print(f"   Current Role: {bigdaddy.role}")
        print(f"   Email: {bigdaddy.email}")
        print(f"   Display Name: {bigdaddy.display_name}")
        
        if bigdaddy.role == 'admin':
            print(f"\n✅ Already admin!")
        else:
            print(f"\n🔄 Promoting from '{bigdaddy.role}' to 'admin'...")
            bigdaddy.role = 'admin'
            bigdaddy.is_active = True
            db.session.commit()
            print(f"✅ Successfully promoted to admin!")
            print(f"\n🎉 {bigdaddy.username} is now an admin!")
