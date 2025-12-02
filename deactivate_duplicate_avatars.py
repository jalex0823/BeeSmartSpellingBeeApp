#!/usr/bin/env python3
"""
Deactivate duplicate/old avatar entries in Railway database.
- bee-knight (old) -> we use knight-bee GLB now
- obee (old) -> we use o-bee GLB now
"""

import psycopg2

DATABASE_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

def deactivate_duplicates():
    """Deactivate old duplicate avatars"""
    
    print("🔌 Connecting to Railway PostgreSQL database...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("✅ Connected successfully\n")
        
        # Deactivate old entries
        old_slugs = ['bee-knight', 'obee']
        
        for slug in old_slugs:
            cursor.execute("""
                UPDATE avatars 
                SET is_active = false, updated_at = NOW()
                WHERE slug = %s
                RETURNING slug, name
            """, (slug,))
            
            result = cursor.fetchone()
            if result:
                print(f"🗑️  Deactivated: {result[0]:20} | {result[1]}")
            else:
                print(f"⚠️  Not found: {slug}")
        
        # Commit changes
        conn.commit()
        print(f"\n✅ Successfully deactivated {len(old_slugs)} duplicate avatars!")
        
        # Close connection
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("🐝 BeeSmart - Deactivate Duplicate Avatars")
    print("=" * 70)
    print()
    
    success = deactivate_duplicates()
    
    if success:
        print("\n" + "=" * 70)
        print("✅ CLEANUP COMPLETE!")
        print("=" * 70)
        exit(0)
    else:
        exit(1)
