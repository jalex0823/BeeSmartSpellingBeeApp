#!/usr/bin/env python3
"""
Insert missing avatars into Railway database
"""
import psycopg2
from avatar_catalog import AVATAR_CATALOG

conn = psycopg2.connect(
    "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"
)
cur = conn.cursor()

# Missing avatars that need to be inserted
missing_ids = ['cool-bee', 'honey-comb', 'robo-bee', 'singer-bee']

# Find them in catalog
catalog_map = {avatar['id']: avatar for avatar in AVATAR_CATALOG}

print("=" * 70)
print("🐝 Insert Missing Avatars into Database")
print("=" * 70)

inserted = []
for avatar_id in missing_ids:
    if avatar_id in catalog_map:
        avatar = catalog_map[avatar_id]
        
        # Insert new avatar with all required fields
        cur.execute("""
            INSERT INTO avatars (
                slug, name, description, category, folder_path, 
                obj_file, mtl_file, texture_file,
                unlock_level, points_required, is_premium, is_active,
                created_at, updated_at
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s,
                1, 0, FALSE, TRUE,
                NOW(), NOW()
            )
            RETURNING id
        """, (
            avatar_id,
            avatar['name'],
            avatar.get('description', ''),
            avatar.get('category', 'classic'),
            avatar.get('folder', 'glb_files'),
            avatar.get('obj_file', ''),
            avatar.get('mtl_file', ''),
            avatar.get('texture_file', '')
        ))
        
        new_id = cur.fetchone()[0]
        inserted.append((new_id, avatar_id, avatar['name']))
        print(f"✅ INSERTED: ID={new_id:3} {avatar_id:20} → {avatar['name']}")

conn.commit()

print(f"\n" + "=" * 70)
print(f"SUMMARY: Inserted {len(inserted)} avatars")
print("=" * 70)

# Count total active
cur.execute("SELECT COUNT(*) FROM avatars WHERE is_active = TRUE")
total_active = cur.fetchone()[0]
print(f"\n📊 Total active avatars in database: {total_active}")
print(f"📋 Total avatars in catalog: {len(AVATAR_CATALOG)}")

if total_active == len(AVATAR_CATALOG):
    print(f"✅ PERFECT MATCH!")
else:
    print(f"⚠️  Still {abs(total_active - len(AVATAR_CATALOG))} off")

conn.close()
