"""
Add Zom Bee back and verify we have exactly 39 avatars matching the catalog
"""
import psycopg2

DATABASE_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

# The 39 avatars from your catalog
CATALOG_AVATARS = [
    'al-bee', 'anxious-bee', 'brother-bee', 'buda-bee', 'builder-bee',
    'buzz-bee', 'cool-bee', 'cutie-bee', 'detective-bee', 'diva-bee',
    'doc-bee', 'explorer-bee', 'franken-bee', 'gamer-bee', 'honey-comb',
    'inventor-bee', 'j-rock-bee', 'knight-bee', 'lumberjack-bee', 'mascot-bee',
    'monster-bee', 'motor-bee', 'nurse-bee', 'o-bee', 'plumber-bee',
    'professor-bee', 'queen-bee', 'robo-bee', 'rocker-bee', 'sea-bee',
    'selfie-bee', 'singer-bee', 'space-bee', 'super-bee', 'techno-bee',
    'umpire-bee', 'vamp-bee', 'ware-bee', 'xray-bee', 'yeti-bee', 'zom-bee'
]

print("=" * 60)
print("🐝 Add Zom Bee Back")
print("=" * 60)

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Check if Zom Bee exists
    cursor.execute("SELECT id, is_active FROM avatars WHERE slug = 'zom-bee'")
    result = cursor.fetchone()
    
    if result:
        avatar_id, is_active = result
        if is_active:
            print(f"✅ Zom Bee already exists and is active (ID: {avatar_id})")
        else:
            print(f"⚠️  Zom Bee exists but is inactive (ID: {avatar_id})")
            cursor.execute("UPDATE avatars SET is_active = true WHERE slug = 'zom-bee'")
            conn.commit()
            print("✅ Activated Zom Bee")
    else:
        print("❌ Zom Bee not found in database - it was deleted")
        confirm = input("\nAdd Zom Bee Avatar back to database? (YES): ")
        if confirm.strip() != "YES":
            print("❌ Cancelled")
            exit(1)
        
        # Add Zom Bee back
        cursor.execute("""
            INSERT INTO avatars (name, slug, obj_file, is_active)
            VALUES ('Zom Bee Avatar', 'zom-bee', 'ZomBee.glb', true)
        """)
        conn.commit()
        print("✅ Added Zom Bee Avatar back to database")
    
    # Final verification
    print("\n📊 Final Count:")
    cursor.execute("SELECT COUNT(*) FROM avatars WHERE is_active = true")
    total = cursor.fetchone()[0]
    print(f"   Active avatars: {total}")
    
    # Check which ones we have vs catalog
    cursor.execute("SELECT slug FROM avatars WHERE is_active = true ORDER BY slug")
    db_slugs = [row[0] for row in cursor.fetchall()]
    
    missing = set(CATALOG_AVATARS) - set(db_slugs)
    extra = set(db_slugs) - set(CATALOG_AVATARS)
    
    if missing:
        print(f"\n⚠️  Missing from database: {missing}")
    if extra:
        print(f"\n⚠️  Extra in database: {extra}")
    
    if not missing and not extra and total == 39:
        print("\n✅ PERFECT! Database matches catalog exactly with 39 avatars!")
    
    cursor.close()
    conn.close()

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
