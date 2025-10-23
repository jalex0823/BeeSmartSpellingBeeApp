#!/usr/bin/env python3
"""
Connect to Railway PostgreSQL and delete broken avatars
"""
import psycopg2

# Railway public connection string
DATABASE_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

# List of broken avatars to delete
BROKEN_AVATARS = [
    'astro-bee', 'biker-bee', 'brother-bee', 'builder-bee', 'cool-bee',
    'detective-bee', 'diva-bee', 'doctor-bee', 'explorer-bee', 'franken-bee',
    'knight-bee', 'queen-bee', 'robo-bee', 'seabea', 'superbee'
]

def main():
    print("🔌 Connecting to Railway PostgreSQL...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Check current avatar count
        print("\n📊 BEFORE cleanup:")
        cur.execute("SELECT COUNT(*) FROM avatars")
        before_count = cur.fetchone()[0]
        print(f"   Total avatars: {before_count}")
        
        # Show all avatars
        cur.execute("SELECT slug, name FROM avatars ORDER BY slug")
        avatars = cur.fetchall()
        print(f"\n   Current avatars:")
        for slug, name in avatars:
            marker = "❌" if slug in BROKEN_AVATARS else "✅"
            print(f"   {marker} {slug} - {name}")
        
        # Delete broken avatars
        print(f"\n🗑️  Deleting {len(BROKEN_AVATARS)} broken avatars...")
        deleted_count = 0
        
        for slug in BROKEN_AVATARS:
            # Get avatar info
            cur.execute("SELECT id, name FROM avatars WHERE slug = %s", (slug,))
            result = cur.fetchone()
            
            if result:
                avatar_id, avatar_name = result
                
                # Update users who have this avatar (cast to string for comparison)
                cur.execute("SELECT COUNT(*) FROM users WHERE avatar_id::text = %s::text", (str(avatar_id),))
                user_count = cur.fetchone()[0]
                
                if user_count > 0:
                    cur.execute("UPDATE users SET avatar_id = NULL WHERE avatar_id::text = %s::text", (str(avatar_id),))
                    print(f"   🔄 Updated {user_count} user(s) with {avatar_name}")
                
                # Delete the avatar
                cur.execute("DELETE FROM avatars WHERE id = %s", (avatar_id,))
                print(f"   ✅ Deleted: {avatar_name} ({slug})")
                deleted_count += 1
            else:
                print(f"   ⚠️  Not found: {slug}")
        
        # Commit changes
        conn.commit()
        print(f"\n💾 Committed {deleted_count} deletions to database")
        
        # Check final count
        print("\n📊 AFTER cleanup:")
        cur.execute("SELECT COUNT(*) FROM avatars")
        after_count = cur.fetchone()[0]
        print(f"   Total avatars: {after_count}")
        
        # Show remaining avatars
        cur.execute("SELECT slug, name FROM avatars ORDER BY slug")
        avatars = cur.fetchall()
        print(f"\n   Remaining avatars:")
        for slug, name in avatars:
            print(f"   ✅ {slug} - {name}")
        
        # Close connection
        cur.close()
        conn.close()
        
        print("\n" + "="*60)
        print(f"✅ CLEANUP COMPLETE!")
        print(f"   Deleted: {deleted_count} broken avatars")
        print(f"   Remaining: {after_count} working avatars")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
