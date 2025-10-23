#!/usr/bin/env python3
"""
Manual database cleanup script - connects to Railway PostgreSQL
Run this locally to clean up the 15 broken avatars
"""
import sys

# Database connection string (Railway internal - need external URL)
INTERNAL_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@postgres.railway.internal:5432/railway"

print("⚠️  WARNING: The connection string you provided uses 'postgres.railway.internal'")
print("   This hostname is only accessible from INSIDE Railway's network.")
print()
print("To connect from your local machine, you need the EXTERNAL connection string.")
print()
print("📋 Steps to get the correct connection string:")
print("   1. Go to Railway dashboard: https://railway.app")
print("   2. Select your BeeSmart project")
print("   3. Click on the PostgreSQL service")
print("   4. Click 'Variables' tab")
print("   5. Look for 'DATABASE_PUBLIC_URL' or similar")
print("   6. It should look like: postgresql://postgres:password@EXTERNAL-HOST:PORT/railway")
print()
print("Once you have the external URL, update this script and run it again.")
print()

# If you get the external URL, paste it here:
EXTERNAL_URL = None  # Example: "postgresql://postgres:HkctC...@monorail.proxy.rlwy.net:12345/railway"

if EXTERNAL_URL:
    try:
        import psycopg2
        
        print("🔌 Connecting to Railway PostgreSQL...")
        conn = psycopg2.connect(EXTERNAL_URL)
        cur = conn.cursor()
        
        # List of broken avatars to delete
        BROKEN_AVATARS = [
            'astro-bee', 'biker-bee', 'brother-bee', 'builder-bee', 'cool-bee',
            'detective-bee', 'diva-bee', 'doctor-bee', 'explorer-bee', 'franken-bee',
            'knight-bee', 'queen-bee', 'robo-bee', 'seabea', 'superbee'
        ]
        
        print("\n📊 Current avatar count:")
        cur.execute("SELECT COUNT(*) FROM avatars")
        before_count = cur.fetchone()[0]
        print(f"   Total avatars: {before_count}")
        
        print("\n🗑️  Deleting broken avatars...")
        deleted_count = 0
        
        for slug in BROKEN_AVATARS:
            # Check if avatar exists
            cur.execute("SELECT id, name FROM avatars WHERE slug = %s", (slug,))
            result = cur.fetchone()
            
            if result:
                avatar_id, avatar_name = result
                
                # Update users who have this avatar
                cur.execute("UPDATE users SET avatar_id = NULL WHERE avatar_id = %s", (avatar_id,))
                users_updated = cur.rowcount
                
                # Delete the avatar
                cur.execute("DELETE FROM avatars WHERE id = %s", (avatar_id,))
                
                print(f"   ✅ Deleted: {avatar_name} ({slug})")
                if users_updated > 0:
                    print(f"      Updated {users_updated} user(s) to default avatar")
                
                deleted_count += 1
            else:
                print(f"   ⚠️  Not found (already deleted?): {slug}")
        
        # Commit changes
        conn.commit()
        
        print("\n📊 After cleanup:")
        cur.execute("SELECT COUNT(*) FROM avatars")
        after_count = cur.fetchone()[0]
        print(f"   Total avatars: {after_count}")
        print(f"   Deleted: {deleted_count}")
        
        print("\n✅ Cleanup complete!")
        
        # Close connection
        cur.close()
        conn.close()
        
    except ImportError:
        print("❌ psycopg2 not installed. Install it with:")
        print("   pip install psycopg2-binary")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
else:
    print("💡 Alternative: Use Railway's web shell")
    print("   1. Go to Railway dashboard")
    print("   2. Click on PostgreSQL service")
    print("   3. Click 'Data' tab")
    print("   4. Use the built-in query interface")
    print()
    print("   Run this SQL:")
    print("   " + "="*60)
    print("""
-- Delete broken avatars
DELETE FROM users WHERE avatar_id IN (
    SELECT id FROM avatars WHERE slug IN (
        'astro-bee', 'biker-bee', 'brother-bee', 'builder-bee', 'cool-bee',
        'detective-bee', 'diva-bee', 'doctor-bee', 'explorer-bee', 'franken-bee',
        'knight-bee', 'queen-bee', 'robo-bee', 'seabea', 'superbee'
    )
);

-- Update users to default avatar
UPDATE users SET avatar_id = NULL WHERE avatar_id IN (
    SELECT id FROM avatars WHERE slug IN (
        'astro-bee', 'biker-bee', 'brother-bee', 'builder-bee', 'cool-bee',
        'detective-bee', 'diva-bee', 'doctor-bee', 'explorer-bee', 'franken-bee',
        'knight-bee', 'queen-bee', 'robo-bee', 'seabea', 'superbee'
    )
);

-- Delete the avatars
DELETE FROM avatars WHERE slug IN (
    'astro-bee', 'biker-bee', 'brother-bee', 'builder-bee', 'cool-bee',
    'detective-bee', 'diva-bee', 'doctor-bee', 'explorer-bee', 'franken-bee',
    'knight-bee', 'queen-bee', 'robo-bee', 'seabea', 'superbee'
);

-- Verify
SELECT COUNT(*) as remaining_avatars FROM avatars;
    """)
    print("   " + "="*60)
