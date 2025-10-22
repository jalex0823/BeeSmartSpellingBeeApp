"""
Update BigDaddy2's avatar to professor-bee in Railway PostgreSQL database
"""
import psycopg2

# Railway PostgreSQL connection URL (hardcoded)
RAILWAY_DB_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

print("\n🐝 BeeSmart Railway - Update BigDaddy2 to Professor Bee\n")
print("=" * 70)
print("🚂 UPDATING RAILWAY POSTGRESQL DATABASE")
print("=" * 70)

try:
    print("\n🔌 Connecting to Railway PostgreSQL...")
    conn = psycopg2.connect(RAILWAY_DB_URL)
    cursor = conn.cursor()
    print("✅ Connected successfully!\n")
    
    # First, show current state
    print("📊 Current avatar settings:")
    cursor.execute("""
        SELECT avatar_id, avatar_variant, avatar_last_updated
        FROM users
        WHERE username = 'BigDaddy2'
    """)
    before = cursor.fetchone()
    print(f"   Avatar ID: {before[0]}")
    print(f"   Variant: {before[1]}")
    print(f"   Last Updated: {before[2]}")
    
    # Update to professor-bee
    print("\n🔧 Updating to professor-bee...")
    cursor.execute("""
        UPDATE users
        SET 
            avatar_id = 'professor-bee',
            avatar_variant = 'default',
            avatar_last_updated = NOW()
        WHERE username = 'BigDaddy2'
    """)
    
    # Commit the changes
    conn.commit()
    print("✅ Database updated!")
    
    # Verify the change
    print("\n✅ New avatar settings:")
    cursor.execute("""
        SELECT avatar_id, avatar_variant, avatar_last_updated
        FROM users
        WHERE username = 'BigDaddy2'
    """)
    after = cursor.fetchone()
    print(f"   Avatar ID: {after[0]}")
    print(f"   Variant: {after[1]}")
    print(f"   Last Updated: {after[2]}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 70)
    print("🎓 SUCCESS! BigDaddy2 now has Professor Bee avatar")
    print("=" * 70)
    print("\n💡 Please refresh your browser to see the change!")
    print("   (You may need to hard refresh: Ctrl+Shift+R or Cmd+Shift+R)\n")
    
except Exception as e:
    print(f"❌ Error: {e}")
    if 'conn' in locals():
        conn.rollback()
