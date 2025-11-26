"""
Clean up Railway avatar database to exactly 39 avatars
- Remove duplicates (keep hyphenated slugs)
- Delete inactive avatars
"""
import psycopg2

DATABASE_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

print("=" * 60)
print("🐝 Avatar Database Cleanup - Get to 39 Avatars")
print("=" * 60)

# IDs to delete based on audit
AVATARS_TO_DELETE = [
    # Duplicates - old slugs without hyphens
    27,  # builderbee (keep builder-bee)
    30,  # detectivebee (keep detective-bee)
    31,  # explorerbee (inactive, keep explorer-bee)
    32,  # frankenbee (keep franken-bee)
    26,  # beeknight (inactive, keep knight-bee)
    33,  # motorcyclebuzzbee (keep motor-bee)
    35,  # seabee (keep sea-bee)
    36,  # spacebeeexplorer (keep space-bee)
    37,  # superbeehero (keep super-bee)
    
    # Already inactive - legacy entries
    39,  # anxious-bee (inactive)
    24,  # buzzhero (inactive)
    52,  # monster-bee (inactive)
    34,  # obee (inactive)
    25,  # queenbeemajesty (inactive)
]

confirm = input(f"\nType 'YES' to delete {len(AVATARS_TO_DELETE)} avatar entries: ")
if confirm.strip() != "YES":
    print("❌ Cancelled")
    exit(1)

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("\n📊 Current state:")
    cursor.execute("SELECT COUNT(*) FROM avatars")
    before_total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM avatars WHERE is_active = true")
    before_active = cursor.fetchone()[0]
    print(f"   Total: {before_total}, Active: {before_active}")
    
    print(f"\n🗑️  Deleting {len(AVATARS_TO_DELETE)} avatars...")
    
    # Show what's being deleted
    for avatar_id in AVATARS_TO_DELETE:
        cursor.execute("SELECT name, slug, is_active FROM avatars WHERE id = %s", (avatar_id,))
        result = cursor.fetchone()
        if result:
            name, slug, is_active = result
            status = "active" if is_active else "inactive"
            print(f"   • [{avatar_id}] {name} ({slug}) - {status}")
    
    # Delete them
    cursor.execute("DELETE FROM avatars WHERE id = ANY(%s)", (AVATARS_TO_DELETE,))
    deleted = cursor.rowcount
    conn.commit()
    
    print(f"\n✅ Deleted {deleted} avatars")
    
    # Show final state
    print("\n📊 Final state:")
    cursor.execute("SELECT COUNT(*) FROM avatars")
    after_total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM avatars WHERE is_active = true")
    after_active = cursor.fetchone()[0]
    print(f"   Total: {after_total}, Active: {after_active}")
    
    # List remaining avatars
    print("\n✅ Remaining active avatars:")
    cursor.execute("""
        SELECT name, slug 
        FROM avatars 
        WHERE is_active = true
        ORDER BY name
    """)
    avatars = cursor.fetchall()
    for i, (name, slug) in enumerate(avatars, 1):
        print(f"   {i:2d}. {name:30s} ({slug})")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print(f"✅ CLEANUP COMPLETE! Now have {after_active} active avatars")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
