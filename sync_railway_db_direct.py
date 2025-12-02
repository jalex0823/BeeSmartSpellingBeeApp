#!/usr/bin/env python3
"""
Direct database update: Sync avatar names with catalog (Apple Store compliance).
Connects directly to Railway PostgreSQL database.
"""

import psycopg2
from avatar_catalog import AVATAR_CATALOG

# Railway PostgreSQL connection string
DATABASE_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

def sync_avatar_names():
    """Update avatar names in Railway database to match catalog"""
    
    # Build catalog lookup
    catalog_map = {a['id']: a for a in AVATAR_CATALOG}
    
    print("🔌 Connecting to Railway PostgreSQL database...")
    
    try:
        # Connect to Railway database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("✅ Connected successfully\n")
        
        # Get current avatars from database
        cursor.execute("""
            SELECT id, slug, name 
            FROM avatars 
            WHERE is_active = true 
            ORDER BY slug
        """)
        
        db_avatars = cursor.fetchall()
        print(f"📊 Found {len(db_avatars)} active avatars in database\n")
        
        updated_count = 0
        updates = []
        
        # Check each avatar
        for avatar_id, slug, current_name in db_avatars:
            catalog_entry = catalog_map.get(slug)
            
            if catalog_entry:
                catalog_name = catalog_entry['name']
                
                if current_name != catalog_name:
                    # Update the name
                    cursor.execute("""
                        UPDATE avatars 
                        SET name = %s, updated_at = NOW()
                        WHERE id = %s
                    """, (catalog_name, avatar_id))
                    
                    updated_count += 1
                    updates.append({
                        'slug': slug,
                        'old_name': current_name,
                        'new_name': catalog_name
                    })
                    print(f"✏️  Updated: {slug:20} | {current_name:30} → {catalog_name}")
                else:
                    print(f"✅ OK:      {slug:20} | {current_name}")
            else:
                print(f"⚠️  Warning: {slug:20} | Not in catalog")
        
        if updated_count > 0:
            # Commit changes
            conn.commit()
            print(f"\n✅ Successfully updated {updated_count} avatar names!")
            print("\n📝 Changes committed to Railway database")
        else:
            print("\n✅ All avatar names already match catalog - no updates needed")
        
        # Close connection
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("🐝 BeeSmart Avatar Name Sync - Railway Database")
    print("=" * 70)
    print()
    
    success = sync_avatar_names()
    
    if success:
        print("\n" + "=" * 70)
        print("✅ SYNC COMPLETE - Avatar names now Apple Store compliant!")
        print("=" * 70)
        exit(0)
    else:
        print("\n" + "=" * 70)
        print("❌ SYNC FAILED - See errors above")
        print("=" * 70)
        exit(1)
