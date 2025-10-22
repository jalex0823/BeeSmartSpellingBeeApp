"""
Quick script to check and reset BigDaddy2's avatar to MascotBee
"""
from AjaSpellBApp import app, db, User

with app.app_context():
    # Find BigDaddy2's account
    user = User.query.filter_by(username='BigDaddy2').first()
    
    if not user:
        print("❌ BigDaddy2 account not found")
        print("\nSearching for similar usernames...")
        similar = User.query.filter(User.username.like('%BigDaddy%')).all()
        if similar:
            for u in similar:
                print(f"   Found: {u.username} (ID: {u.id}, Role: {u.role})")
    else:
        print(f"✅ Found {user.username} account")
        print(f"   Display Name: {user.display_name}")
        print(f"   ID: {user.id}")
        print(f"   Role: {user.role}")
        print(f"   Email: {user.email}")
        print(f"   Teacher Key: {user.teacher_key}")
        print(f"   Current avatar_id: {user.avatar_id}")
        print(f"   Current avatar_variant: {user.avatar_variant}")
        
        # Reset to mascot-bee
        if user.avatar_id and user.avatar_id != 'mascot-bee':
            print(f"\n🔄 Resetting avatar from '{user.avatar_id}' to 'mascot-bee'...")
            user.avatar_id = 'mascot-bee'
            user.avatar_variant = 'default'
            db.session.commit()
            print("✅ Avatar reset to MascotBee!")
        elif not user.avatar_id or user.avatar_id == 'cool-bee':
            print(f"\n🔄 Setting avatar to 'mascot-bee' (was {user.avatar_id or 'NULL'})...")
            user.avatar_id = 'mascot-bee'
            user.avatar_variant = 'default'
            db.session.commit()
            print("✅ Avatar set to MascotBee!")
        else:
            print("\n✅ Avatar is already set to MascotBee")


