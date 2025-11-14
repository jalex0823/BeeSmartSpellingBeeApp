#!/usr/bin/env python3
"""
Remove duplicate inactive avatars from Railway database
"""
import os
from sqlalchemy import create_engine, text

# Railway PostgreSQL connection string
DATABASE_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

# Inactive duplicate slugs to remove
DUPLICATES_TO_REMOVE = [
    'buzzbotbee',      # Duplicate of robo-bee
    'beedoctor',       # Duplicate of doc-bee
]

try:
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("🗑️  Removing duplicate inactive avatars from database...")
        
        for slug in DUPLICATES_TO_REMOVE:
            # First, verify it's inactive
            result = conn.execute(text("""
                SELECT slug, name, is_active 
                FROM avatars 
                WHERE slug = :slug
            """), {"slug": slug})
            
            avatar = result.fetchone()
            
            if avatar:
                if not avatar[2]:  # is_active is False
                    print(f"   ✓ Removing inactive '{slug}' ({avatar[1]})")
                    conn.execute(text("""
                        DELETE FROM avatars 
                        WHERE slug = :slug
                    """), {"slug": slug})
                    conn.commit()
                else:
                    print(f"   ⚠️  Skipping '{slug}' - it's marked as ACTIVE")
            else:
                print(f"   ℹ️  '{slug}' not found in database")
        
        # Verify removal
        result = conn.execute(text("""
            SELECT COUNT(*) FROM avatars WHERE is_active = true
        """))
        active_count = result.scalar()
        
        result = conn.execute(text("""
            SELECT COUNT(*) FROM avatars
        """))
        total_count = result.scalar()
        
        print(f"\n✅ Cleanup complete!")
        print(f"   Active avatars: {active_count}")
        print(f"   Total avatars: {total_count}")
        print(f"   Inactive avatars: {total_count - active_count}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
