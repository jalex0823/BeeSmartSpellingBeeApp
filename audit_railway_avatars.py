"""
Audit production avatar database (PostgreSQL) - check for duplicates and extra entries
"""
import os
import psycopg2

# IMPORTANT: Do not hardcode production DB credentials.
# Provide DATABASE_URL via environment variables (DigitalOcean-managed PostgreSQL in production).
DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    raise SystemExit("DATABASE_URL is not set. Provide your PostgreSQL connection string via env vars.")

print("=" * 60)
print("🐝 Avatar Database Audit")
print("=" * 60)

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Get total count
    cursor.execute("SELECT COUNT(*) FROM avatars")
    total = cursor.fetchone()[0]
    print(f"\n📊 Total avatars in database: {total}")
    
    # Get active count
    cursor.execute("SELECT COUNT(*) FROM avatars WHERE is_active = true")
    active = cursor.fetchone()[0]
    print(f"✅ Active avatars: {active}")
    
    cursor.execute("SELECT COUNT(*) FROM avatars WHERE is_active = false")
    inactive = cursor.fetchone()[0]
    print(f"❌ Inactive avatars: {inactive}")
    
    # List all avatars
    print("\n" + "=" * 60)
    print("📝 All Avatars in Database:")
    print("=" * 60)
    cursor.execute("""
        SELECT id, name, slug, obj_file, is_active 
        FROM avatars 
        ORDER BY name
    """)
    
    avatars = cursor.fetchall()
    for avatar_id, name, slug, obj_file, is_active in avatars:
        status = "✅" if is_active else "❌"
        print(f"{status} {name:30s} | {slug:25s} | {obj_file}")
    
    # Check for duplicates by name
    print("\n" + "=" * 60)
    print("🔍 Checking for duplicate names:")
    print("=" * 60)
    cursor.execute("""
        SELECT name, COUNT(*) as count
        FROM avatars
        GROUP BY name
        HAVING COUNT(*) > 1
        ORDER BY count DESC, name
    """)
    
    duplicates = cursor.fetchall()
    if duplicates:
        print(f"\n⚠️  Found {len(duplicates)} duplicate names:")
        for name, count in duplicates:
            print(f"   • {name}: {count} entries")
            cursor.execute("SELECT id, slug, is_active FROM avatars WHERE name = %s", (name,))
            entries = cursor.fetchall()
            for entry_id, slug, is_active in entries:
                status = "active" if is_active else "inactive"
                print(f"      - ID {entry_id}: {slug} ({status})")
    else:
        print("✅ No duplicate names found")
    
    cursor.close()
    conn.close()

except Exception as e:
    print(f"\n❌ Error: {e}")
