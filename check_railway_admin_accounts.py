"""
SAFE CHECK ONLY - No database changes
Check BigDaddy and BigDaddy2 accounts on Railway PostgreSQL
Run this with: railway run python check_railway_admin_accounts.py
"""
from AjaSpellBApp import app, db, User

with app.app_context():
    print("=" * 60)
    print("🔍 RAILWAY ADMIN ACCOUNT CHECK (READ-ONLY)")
    print("=" * 60)
    print()
    
    # Check for BigDaddy account
    print("🔎 Searching for 'BigDaddy' account...")
    bigdaddy = User.query.filter(
        db.func.lower(User.username) == 'bigdaddy'
    ).first()
    
    if bigdaddy:
        print(f"✅ FOUND: BigDaddy")
        print(f"   ID: {bigdaddy.id}")
        print(f"   Username: {bigdaddy.username}")
        print(f"   Display Name: {bigdaddy.display_name}")
        print(f"   Email: {bigdaddy.email}")
        print(f"   Role: {bigdaddy.role}")
        print(f"   Is Active: {bigdaddy.is_active}")
        print(f"   Created: {bigdaddy.created_at}")
        print(f"   Last Login: {bigdaddy.last_login}")
        print(f"   Teacher Key: {bigdaddy.teacher_key}")
        
        if bigdaddy.role == 'admin':
            print(f"   ✅ STATUS: Already an admin")
        else:
            print(f"   ⚠️  STATUS: Role is '{bigdaddy.role}' (NOT admin)")
    else:
        print("❌ BigDaddy account NOT FOUND")
    
    print()
    print("-" * 60)
    print()
    
    # Check for BigDaddy2 account
    print("🔎 Searching for 'BigDaddy2' account...")
    bigdaddy2 = User.query.filter(
        db.func.lower(User.username) == 'bigdaddy2'
    ).first()
    
    if bigdaddy2:
        print(f"✅ FOUND: BigDaddy2")
        print(f"   ID: {bigdaddy2.id}")
        print(f"   Username: {bigdaddy2.username}")
        print(f"   Display Name: {bigdaddy2.display_name}")
        print(f"   Email: {bigdaddy2.email}")
        print(f"   Role: {bigdaddy2.role}")
        print(f"   Is Active: {bigdaddy2.is_active}")
        print(f"   Created: {bigdaddy2.created_at}")
        print(f"   Last Login: {bigdaddy2.last_login}")
        print(f"   Teacher Key: {bigdaddy2.teacher_key}")
        
        if bigdaddy2.role == 'admin':
            print(f"   ✅ STATUS: Already an admin")
        else:
            print(f"   ⚠️  STATUS: Role is '{bigdaddy2.role}' (NOT admin)")
    else:
        print("❌ BigDaddy2 account NOT FOUND")
    
    print()
    print("-" * 60)
    print()
    
    # List all admin accounts
    print("🔎 Searching for ALL admin accounts...")
    admins = User.query.filter_by(role='admin').all()
    
    if admins:
        print(f"✅ Found {len(admins)} admin account(s):")
        for admin in admins:
            print(f"   • {admin.username} (ID: {admin.id}, Email: {admin.email}, Active: {admin.is_active})")
    else:
        print("❌ NO admin accounts found in database!")
    
    print()
    print("-" * 60)
    print()
    
    # Search for any BigDaddy variations
    print("🔎 Searching for ANY BigDaddy-related accounts...")
    similar = User.query.filter(
        User.username.ilike('%daddy%')
    ).all()
    
    if similar:
        print(f"✅ Found {len(similar)} BigDaddy-related account(s):")
        for u in similar:
            status = "✅ ADMIN" if u.role == 'admin' else f"⚠️  {u.role.upper()}"
            print(f"   • {u.username} (ID: {u.id}, Role: {u.role}, {status})")
    else:
        print("❌ No BigDaddy-related accounts found")
    
    print()
    print("=" * 60)
    print("✅ CHECK COMPLETE - NO CHANGES MADE TO DATABASE")
    print("=" * 60)
