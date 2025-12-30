"""
Direct SQL fix for avatar paths - no Flask dependencies
"""
import os
import psycopg2

# PostgreSQL database connection
# IMPORTANT: Do not hardcode production DB credentials.
DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    raise SystemExit("DATABASE_URL is not set. Provide your PostgreSQL connection string via env vars.")

print("=" * 60)
print("🐝 Avatar GLB Fix - Direct SQL")
print("=" * 60)

confirm = input("\nType 'YES' to update all .obj to .glb in Railway: ")
if confirm.strip() != "YES":
    print("❌ Cancelled")
    exit(1)

print("\n🔌 Connecting to Railway database...")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Check current state
    print("\n📊 Checking current avatar paths...")
    cursor.execute("SELECT COUNT(*) FROM avatars WHERE obj_file LIKE '%.obj'")
    obj_count = cursor.fetchone()[0]
    print(f"   Found {obj_count} avatars with .obj paths")
    
    if obj_count == 0:
        print("\n✅ All avatars already have .glb paths!")
        cursor.close()
        conn.close()
        exit(0)
    
    # Show what will be fixed
    cursor.execute("SELECT id, name, obj_file FROM avatars WHERE obj_file LIKE '%.obj' ORDER BY name")
    avatars_to_fix = cursor.fetchall()
    
    print("\n📝 Avatars to fix:")
    for avatar_id, name, obj_file in avatars_to_fix:
        new_path = obj_file.replace('.obj', '.glb')
        print(f"   • {name}: {obj_file} → {new_path}")
    
    # Execute the fix
    print(f"\n🔧 Updating {obj_count} avatars...")
    cursor.execute("""
        UPDATE avatars 
        SET obj_file = REPLACE(obj_file, '.obj', '.glb')
        WHERE obj_file LIKE '%.obj'
    """)
    
    rows_updated = cursor.rowcount
    conn.commit()
    
    print(f"\n✅ Successfully updated {rows_updated} avatars!")
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM avatars WHERE obj_file LIKE '%.glb'")
    glb_count = cursor.fetchone()[0]
    print(f"📊 Verification: {glb_count} avatars now have .glb paths")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ DATABASE UPDATE COMPLETE!")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ Error: {e}")
    exit(1)
