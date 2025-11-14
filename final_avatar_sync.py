#!/usr/bin/env python3
"""
Final sync: Reactivate missing avatars and update all names to match catalog
"""
import psycopg2
from avatar_catalog import AVATAR_CATALOG

# Railway PostgreSQL connection
conn = psycopg2.connect(
    "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"
)
cur = conn.cursor()

# Create mapping of base names to catalog entries
catalog_map = {}
for avatar in AVATAR_CATALOG:
    avatar_id = avatar['id']
    catalog_map[avatar_id] = avatar

print("=" * 70)
print("🐝 Final Avatar Database Sync - Reactivate & Update Names")
print("=" * 70)
print(f"\n📋 Catalog has {len(AVATAR_CATALOG)} avatars\n")

# Name mappings for database IDs that don't match catalog IDs
db_to_catalog_mapping = {
    "Builder Bee": "builder-bee",
    "Cool Bee": "cool-bee", 
    "Detective Bee": "detective-bee",
    "Franken Bee": "franken-bee",
    "Motorcyclebuzz Bee": "motor-bee",
    "Sea Bee": "sea-bee",
    "Space Bee Explorer": "space-bee",
    "Super Bee Hero": "super-bee",
    # Also check for these
    "Honey Comb": "honey-comb",
    "Robo Bee": "robo-bee",
    "Singer Bee": "singer-bee",
}

# Get all inactive avatars
cur.execute("""
    SELECT id, name, is_active
    FROM avatars
    WHERE is_active = FALSE
    ORDER BY name
""")

inactive_avatars = cur.fetchall()
print(f"📊 Found {len(inactive_avatars)} inactive avatars in database\n")

reactivated = []
for db_id, db_name, is_active in inactive_avatars:
    # Try to find matching catalog entry
    catalog_id = db_to_catalog_mapping.get(db_name)
    
    if catalog_id and catalog_id in catalog_map:
        catalog_entry = catalog_map[catalog_id]
        correct_name = catalog_entry['name']
        
        # Reactivate and update name
        cur.execute("""
            UPDATE avatars
            SET is_active = TRUE, name = %s
            WHERE id = %s
        """, (correct_name, db_id))
        
        reactivated.append((db_id, catalog_id, correct_name))
        print(f"✅ REACTIVATED: ID={db_id:3} {db_name:30} → {correct_name}")

conn.commit()

print(f"\n" + "=" * 70)
print(f"SUMMARY: Reactivated {len(reactivated)} avatars")
print("=" * 70)

# Now count total active
cur.execute("SELECT COUNT(*) FROM avatars WHERE is_active = TRUE")
total_active = cur.fetchone()[0]
print(f"\n📊 Total active avatars in database: {total_active}")

if total_active == len(AVATAR_CATALOG):
    print(f"✅ PERFECT! Database matches catalog ({len(AVATAR_CATALOG)} avatars)")
else:
    print(f"⚠️  MISMATCH! Database has {total_active}, catalog has {len(AVATAR_CATALOG)}")

conn.close()
print("\n✅ SYNC COMPLETE!")
