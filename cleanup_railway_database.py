#!/usr/bin/env python3
"""
Cleanup Railway database - deactivate avatars not in the official 28-avatar catalog.
Keep only the 28 avatars defined in avatar_catalog.py
"""

import psycopg2
from avatar_catalog import AVATAR_CATALOG

DATABASE_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

def cleanup_database():
    """Deactivate avatars not in catalog, update names for those in catalog"""
    
    # Get official catalog IDs
    catalog_ids = {a['id'] for a in AVATAR_CATALOG}
    catalog_map = {a['id']: a for a in AVATAR_CATALOG}
    
    print("📋 Official catalog has", len(catalog_ids), "avatars")
    print("🔌 Connecting to Railway PostgreSQL database...\n")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Get all currently active avatars
        cursor.execute("""
            SELECT slug, name, is_active 
            FROM avatars 
            ORDER BY slug
        """)
        
        all_avatars = cursor.fetchall()
        
        deactivated = []
        updated = []
        kept = []
        
        for slug, name, is_active in all_avatars:
            if slug in catalog_ids:
                # This avatar should be active
                catalog_entry = catalog_map[slug]
                catalog_name = catalog_entry['name']
                
                if not is_active:
                    # Reactivate it
                    cursor.execute("""
                        UPDATE avatars 
                        SET is_active = true, name = %s, updated_at = NOW()
                        WHERE slug = %s
                    """, (catalog_name, slug))
                    updated.append(f"✅ Reactivated: {slug:20} → {catalog_name}")
                elif name != catalog_name:
                    # Update name to match catalog
                    cursor.execute("""
                        UPDATE avatars 
                        SET name = %s, updated_at = NOW()
                        WHERE slug = %s
                    """, (catalog_name, slug))
                    updated.append(f"✏️  Updated:     {slug:20} | {name:30} → {catalog_name}")
                else:
                    kept.append(f"✅ OK:          {slug:20} → {catalog_name}")
            else:
                # This avatar should be deactivated
                if is_active:
                    cursor.execute("""
                        UPDATE avatars 
                        SET is_active = false, updated_at = NOW()
                        WHERE slug = %s
                    """, (slug,))
                    deactivated.append(f"🗑️  Deactivated: {slug:20} | {name}")
        
        # Commit all changes
        conn.commit()
        
        print("\n📊 RESULTS:")
        print("=" * 70)
        
        if kept:
            print(f"\n✅ Kept active ({len(kept)}):")
            for item in kept:
                print(f"   {item}")
        
        if updated:
            print(f"\n✏️  Updated ({len(updated)}):")
            for item in updated:
                print(f"   {item}")
        
        if deactivated:
            print(f"\n🗑️  Deactivated ({len(deactivated)}):")
            for item in deactivated:
                print(f"   {item}")
        
        print("\n" + "=" * 70)
        print(f"SUMMARY: {len(catalog_ids)} avatars active, {len(deactivated)} deactivated, {len(updated)} updated")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("🐝 BeeSmart - Cleanup Database to Match Catalog")
    print("=" * 70)
    print()
    
    success = cleanup_database()
    
    if success:
        print("\n✅ DATABASE CLEANUP COMPLETE!")
        exit(0)
    else:
        exit(1)
