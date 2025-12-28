"""
Deactivate Anxious Bee and Monster Bee to get to exactly 39 avatars
These are not in the official 39 avatar catalog
"""
import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("DIGITALOCEAN_DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit(
        "DATABASE_URL (or DIGITALOCEAN_DATABASE_URL) must be set before running this script."
    )

print("=" * 60)
print("🐝 Final Fix - Deactivate Extra Avatars")
print("=" * 60)
print("\nAnxious Bee and Monster Bee are NOT in the official 39 avatar catalog")

confirm = input("\nDeactivate Anxious Bee and Monster Bee? (YES): ")
if confirm.strip() != "YES":
    print("❌ Cancelled")
    exit(1)

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("\n🔧 Deactivating Anxious Bee Avatar...")
    cursor.execute("UPDATE avatars SET is_active = false WHERE slug = 'anxious-bee'")
    
    print("🔧 Deactivating Monster Bee Avatar...")
    cursor.execute("UPDATE avatars SET is_active = false WHERE slug = 'monster-bee'")
    
    conn.commit()
    
    # Final count
    cursor.execute("SELECT COUNT(*) FROM avatars WHERE is_active = true")
    total = cursor.fetchone()[0]
    
    print(f"\n📊 Total active avatars: {total}")
    
    if total == 39:
        print("\n" + "=" * 60)
        print("🎉 PERFECT! Exactly 39 avatars - matches catalog!")
        print("=" * 60)
    else:
        print(f"\n⚠️  Expected 39, have {total}")
    
    # List all 39
    print("\n✅ Final 39 Active Avatars:")
    cursor.execute("""
        SELECT name FROM avatars 
        WHERE is_active = true
        ORDER BY name
    """)
    for i, (name,) in enumerate(cursor.fetchall(), 1):
        print(f"   {i:2d}. {name}")
    
    cursor.close()
    conn.close()

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
