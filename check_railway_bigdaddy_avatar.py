"""
Check BigDaddy2's avatar in Railway PostgreSQL database
"""
import psycopg2

# Railway PostgreSQL connection URL (hardcoded)
RAILWAY_DB_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

print("\n🐝 BeeSmart Railway - Check BigDaddy2 Avatar\n")
print("=" * 70)
print("🚂 CHECKING RAILWAY POSTGRESQL DATABASE")
print("=" * 70)

try:
    print("\n🔌 Connecting to Railway PostgreSQL...")
    conn = psycopg2.connect(RAILWAY_DB_URL)
    cursor = conn.cursor()
    print("✅ Connected successfully!\n")
    
    # Query BigDaddy2's avatar info
    query = """
    SELECT 
        id,
        username,
        display_name,
        avatar_id,
        avatar_variant,
        avatar_locked,
        avatar_last_updated
    FROM users
    WHERE username = 'BigDaddy2'
    """
    
    cursor.execute(query)
    result = cursor.fetchone()
    
    if result:
        user_id, username, display_name, avatar_id, avatar_variant, avatar_locked, avatar_last_updated = result
        
        print("-" * 70)
        print(f"👤 Username: {username}")
        print(f"   ID: {user_id}")
        print(f"   Display Name: {display_name}")
        print(f"   🎭 Avatar ID: {avatar_id}")
        print(f"   🎨 Avatar Variant: {avatar_variant}")
        print(f"   🔒 Avatar Locked: {avatar_locked}")
        print(f"   📅 Last Updated: {avatar_last_updated}")
        print("-" * 70)
        
        if avatar_id == 'cool-bee':
            print("\n⚠️  ISSUE FOUND: Avatar is set to 'cool-bee' instead of 'professor-bee'")
            print("\n🔧 Would you like to update it to 'professor-bee'? (Run update script)")
        elif avatar_id == 'professor-bee':
            print("\n✅ Avatar is correctly set to 'professor-bee'")
            print("   If Cool Bee is still showing, this might be a cache or frontend issue")
        else:
            print(f"\n📝 Current avatar: {avatar_id}")
    else:
        print("❌ BigDaddy2 account not found")
    
    cursor.close()
    conn.close()
    print("\n✨ Check complete!\n")
    
except Exception as e:
    print(f"❌ Error: {e}")
