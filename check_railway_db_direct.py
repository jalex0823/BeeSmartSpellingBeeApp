"""
Direct PostgreSQL connection to check Railway admin accounts
SAFE - READ ONLY - NO CHANGES TO DATABASE
"""
import psycopg2
from urllib.parse import urlparse

# Railway PostgreSQL connection string
DATABASE_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

try:
    # Parse the database URL
    result = urlparse(DATABASE_URL)
    
    # Connect to PostgreSQL
    print("🔌 Connecting to Railway PostgreSQL database...")
    conn = psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )
    
    cursor = conn.cursor()
    print("✅ Connected successfully!")
    print()
    print("=" * 60)
    print("🔍 RAILWAY ADMIN ACCOUNT CHECK (READ-ONLY)")
    print("=" * 60)
    print()
    
    # Check for BigDaddy account
    print("🔎 Searching for 'BigDaddy' account...")
    cursor.execute("""
        SELECT id, username, display_name, email, role, is_active, 
               created_at, last_login, teacher_key
        FROM users 
        WHERE LOWER(username) = 'bigdaddy'
    """)
    bigdaddy = cursor.fetchone()
    
    if bigdaddy:
        print(f"✅ FOUND: BigDaddy")
        print(f"   ID: {bigdaddy[0]}")
        print(f"   Username: {bigdaddy[1]}")
        print(f"   Display Name: {bigdaddy[2]}")
        print(f"   Email: {bigdaddy[3]}")
        print(f"   Role: {bigdaddy[4]}")
        print(f"   Is Active: {bigdaddy[5]}")
        print(f"   Created: {bigdaddy[6]}")
        print(f"   Last Login: {bigdaddy[7]}")
        print(f"   Teacher Key: {bigdaddy[8]}")
        
        if bigdaddy[4] == 'admin':
            print(f"   ✅ STATUS: Already an admin")
        else:
            print(f"   ⚠️  STATUS: Role is '{bigdaddy[4]}' (NOT admin)")
    else:
        print("❌ BigDaddy account NOT FOUND")
    
    print()
    print("-" * 60)
    print()
    
    # Check for BigDaddy2 account
    print("🔎 Searching for 'BigDaddy2' account...")
    cursor.execute("""
        SELECT id, username, display_name, email, role, is_active, 
               created_at, last_login, teacher_key,
               avatar_id, avatar_variant, avatar_locked, avatar_last_updated, preferences
        FROM users 
        WHERE LOWER(username) = 'bigdaddy2'
    """)
    bigdaddy2 = cursor.fetchone()
    
    if bigdaddy2:
        print(f"✅ FOUND: BigDaddy2")
        print(f"   ID: {bigdaddy2[0]}")
        print(f"   Username: {bigdaddy2[1]}")
        print(f"   Display Name: {bigdaddy2[2]}")
        print(f"   Email: {bigdaddy2[3]}")
        print(f"   Role: {bigdaddy2[4]}")
        print(f"   Is Active: {bigdaddy2[5]}")
        print(f"   Created: {bigdaddy2[6]}")
        print(f"   Last Login: {bigdaddy2[7]}")
        print(f"   Teacher Key: {bigdaddy2[8]}")
        print(f"\n   🎨 AVATAR INFO:")
        print(f"   Avatar ID: {bigdaddy2[9]}")
        print(f"   Avatar Variant: {bigdaddy2[10]}")
        print(f"   Avatar Locked: {bigdaddy2[11]}")
        print(f"   Avatar Last Updated: {bigdaddy2[12]}")
        print(f"   Preferences: {bigdaddy2[13]}")
        
        if bigdaddy2[4] == 'admin':
            print(f"\n   ✅ STATUS: Already an admin")
        else:
            print(f"   ⚠️  STATUS: Role is '{bigdaddy2[4]}' (NOT admin)")
    else:
        print("❌ BigDaddy2 account NOT FOUND")
    
    print()
    print("-" * 60)
    print()
    
    # List all admin accounts
    print("🔎 Searching for ALL admin accounts...")
    cursor.execute("""
        SELECT id, username, email, is_active
        FROM users 
        WHERE role = 'admin'
        ORDER BY created_at
    """)
    admins = cursor.fetchall()
    
    if admins:
        print(f"✅ Found {len(admins)} admin account(s):")
        for admin in admins:
            print(f"   • {admin[1]} (ID: {admin[0]}, Email: {admin[2]}, Active: {admin[3]})")
    else:
        print("❌ NO admin accounts found in database!")
    
    print()
    print("-" * 60)
    print()
    
    # Search for any BigDaddy variations
    print("🔎 Searching for ANY BigDaddy-related accounts...")
    cursor.execute("""
        SELECT id, username, role
        FROM users 
        WHERE username ILIKE '%daddy%'
        ORDER BY created_at
    """)
    similar = cursor.fetchall()
    
    if similar:
        print(f"✅ Found {len(similar)} BigDaddy-related account(s):")
        for u in similar:
            status = "✅ ADMIN" if u[2] == 'admin' else f"⚠️  {u[2].upper()}"
            print(f"   • {u[1]} (ID: {u[0]}, Role: {u[2]}, {status})")
    else:
        print("❌ No BigDaddy-related accounts found")
    
    print()
    print("=" * 60)
    print("✅ CHECK COMPLETE - NO CHANGES MADE TO DATABASE")
    print("=" * 60)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
