"""
Final avatar cleanup - activate missing avatars and remove buzzhero duplicate
"""
import psycopg2

DATABASE_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

print("=" * 60)
print("🐝 Final Avatar Cleanup to 39")
print("=" * 60)

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Check current inactive avatars
    print("\n📊 Checking inactive avatars...")
    cursor.execute("""
        SELECT id, name, slug, obj_file 
        FROM avatars 
        WHERE is_active = false
        ORDER BY name
    """)
    inactive = cursor.fetchall()
    
    print(f"Found {len(inactive)} inactive avatars:")
    for avatar_id, name, slug, obj_file in inactive:
        print(f"   • [{avatar_id}] {name} ({slug}) - {obj_file}")
    
    confirm = input("\nActivate Anxious Bee and Monster Bee, delete Buzzhero? (YES): ")
    if confirm.strip() != "YES":
        print("❌ Cancelled")
        exit(1)
    
    # Activate Anxious Bee and Monster Bee
    print("\n✅ Activating Anxious Bee Avatar...")
    cursor.execute("UPDATE avatars SET is_active = true WHERE slug = 'anxious-bee'")
    
    print("✅ Activating Monster Bee Avatar...")
    cursor.execute("UPDATE avatars SET is_active = true WHERE slug = 'monster-bee'")
    
    # Delete Buzzhero (duplicate of Super Bee)
    print("🗑️  Deleting Buzzhero Avatar (duplicate of Super Bee)...")
    cursor.execute("DELETE FROM avatars WHERE slug = 'buzzhero'")
    
    conn.commit()
    
    # Final count
    print("\n📊 Final state:")
    cursor.execute("SELECT COUNT(*) FROM avatars WHERE is_active = true")
    active_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM avatars")
    total_count = cursor.fetchone()[0]
    
    print(f"   Active avatars: {active_count}")
    print(f"   Total avatars: {total_count}")
    
    # List all active avatars
    print("\n✅ All 39 Active Avatars:")
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
    print(f"✅ COMPLETE! You now have exactly {active_count} active avatars!")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
