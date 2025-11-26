"""
Final check - identify the 2 extra avatars
"""
import psycopg2

DATABASE_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

# The definitive 39 avatars from your catalog
CATALOG_39 = {
    'al-bee', 'anxious-bee', 'brother-bee', 'buda-bee', 'builder-bee',
    'buzz-bee', 'cool-bee', 'cutie-bee', 'detective-bee', 'diva-bee',
    'doc-bee', 'explorer-bee', 'franken-bee', 'gamer-bee', 'honey-comb',
    'inventor-bee', 'j-rock-bee', 'knight-bee', 'lumberjack-bee', 'mascot-bee',
    'monster-bee', 'motor-bee', 'nurse-bee', 'o-bee', 'plumber-bee',
    'professor-bee', 'queen-bee', 'robo-bee', 'rocker-bee', 'sea-bee',
    'selfie-bee', 'singer-bee', 'space-bee', 'super-bee', 'techno-bee',
    'umpire-bee', 'vamp-bee', 'ware-bee', 'xray-bee', 'yeti-bee', 'zom-bee'
}

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    cursor.execute("SELECT slug, name FROM avatars WHERE is_active = true ORDER BY slug")
    db_avatars = cursor.fetchall()
    db_slugs = {slug for slug, _ in db_avatars}
    
    print("=" * 60)
    print(f"Database: {len(db_slugs)} active | Catalog: {len(CATALOG_39)} should have")
    print("=" * 60)
    
    # Find extras (in DB but not in catalog)
    extras = db_slugs - CATALOG_39
    if extras:
        print(f"\n❌ EXTRA avatars in database ({len(extras)}):")
        for slug in sorted(extras):
            cursor.execute("SELECT id, name FROM avatars WHERE slug = %s", (slug,))
            avatar_id, name = cursor.fetchone()
            print(f"   • [{avatar_id}] {name} ({slug})")
    
    # Find missing (in catalog but not in DB)
    missing = CATALOG_39 - db_slugs
    if missing:
        print(f"\n⚠️  MISSING from database ({len(missing)}):")
        for slug in sorted(missing):
            print(f"   • {slug}")
    
    if not extras and not missing:
        print("\n✅ PERFECT MATCH!")
    else:
        print(f"\nTo fix: Remove {len(extras)} extras, Add {len(missing)} missing")
        
        if extras and not missing:
            print("\n🔧 Suggested action:")
            print(f"   Deactivate these {len(extras)} avatar(s) to get to 39:")
            for slug in sorted(extras):
                cursor.execute("SELECT id FROM avatars WHERE slug = %s", (slug,))
                avatar_id = cursor.fetchone()[0]
                print(f"   UPDATE avatars SET is_active = false WHERE id = {avatar_id}; -- {slug}")
    
    cursor.close()
    conn.close()

except Exception as e:
    print(f"Error: {e}")
