#!/usr/bin/env python3
"""
Sync 9 new avatars to Railway database
Adds: Gamer, Inventor, Lumberjack, Nurse, Plumber, Techno, Umpire, Xray, Yeti
"""

import psycopg2
from avatar_catalog import AVATAR_CATALOG

DATABASE_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

# 9 new avatars to add
NEW_AVATAR_SLUGS = [
    'gamer_bee',
    'inventor_bee', 
    'lumberjack_bee',
    'nurse_bee',
    'plumber_bee',
    'techno_bee',
    'umpire_bee',
    'xray_bee',
    'yeti_bee'
]

def sync_new_avatars():
    """Add 9 new avatars to Railway database"""
    
    print("🐝 BeeSmart Avatar Sync - Adding 9 New Avatars")
    print("=" * 60)
    
    # Get new avatars from catalog
    new_avatars = [a for a in AVATAR_CATALOG if a['id'] in NEW_AVATAR_SLUGS]
    
    if len(new_avatars) != 9:
        print(f"❌ ERROR: Expected 9 avatars, found {len(new_avatars)}")
        return
    
    print(f"\n✅ Found all 9 new avatars in catalog")
    print(f"🔌 Connecting to Railway PostgreSQL...\n")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        added = 0
        updated = 0
        skipped = 0
        
        for avatar in new_avatars:
            slug = avatar['id']
            
            # Check if avatar already exists
            cursor.execute("SELECT id, name, tier, price FROM avatars WHERE slug = %s", (slug,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing avatar
                cursor.execute("""
                    UPDATE avatars 
                    SET 
                        name = %s,
                        tier = %s,
                        price = %s,
                        product_id = %s,
                        description = %s,
                        glb_file = %s,
                        thumbnail = %s,
                        is_active = true,
                        updated_at = NOW()
                    WHERE slug = %s
                """, (
                    avatar['name'],
                    avatar['tier'],
                    avatar['price'],
                    avatar['product_id'],
                    avatar.get('description', ''),
                    avatar.get('glb_file', ''),
                    avatar.get('thumbnail', ''),
                    slug
                ))
                print(f"📝 Updated: {avatar['name']} (${avatar['price']})")
                updated += 1
            else:
                # Insert new avatar
                cursor.execute("""
                    INSERT INTO avatars (
                        slug, name, tier, price, product_id, 
                        description, glb_file, thumbnail, 
                        is_active, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, 
                        %s, %s, %s, 
                        true, NOW(), NOW()
                    )
                """, (
                    slug,
                    avatar['name'],
                    avatar['tier'],
                    avatar['price'],
                    avatar['product_id'],
                    avatar.get('description', ''),
                    avatar.get('glb_file', ''),
                    avatar.get('thumbnail', '')
                ))
                print(f"✨ Added: {avatar['name']} (${avatar['price']})")
                added += 1
        
        # Commit changes
        conn.commit()
        
        print("\n" + "=" * 60)
        print("✅ DATABASE SYNC COMPLETE")
        print(f"   • {added} avatars added")
        print(f"   • {updated} avatars updated")
        
        # Verify total count
        cursor.execute("SELECT COUNT(*) FROM avatars WHERE is_active = true")
        total = cursor.fetchone()[0]
        print(f"   • Total active avatars in database: {total}")
        
        if total == 39:
            print("\n🎉 SUCCESS! Database now has all 39 avatars!")
        else:
            print(f"\n⚠️ WARNING: Expected 39 avatars, found {total}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ DATABASE ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    sync_new_avatars()
