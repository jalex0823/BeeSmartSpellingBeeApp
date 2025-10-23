#!/usr/bin/env python3
"""
Check what thumbnail files are stored in Railway database for the 4 broken avatars
"""
import psycopg2

DATABASE_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

PROBLEM_AVATARS = ['mascot-bee', 'professor-bee', 'vamp-bee', 'ware-bee']

print("🔍 Checking thumbnail files in Railway database...\n")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    for slug in PROBLEM_AVATARS:
        cur.execute("""
            SELECT slug, name, thumbnail_file, texture_file 
            FROM avatars 
            WHERE slug = %s
        """, (slug,))
        
        result = cur.fetchone()
        if result:
            slug, name, thumbnail, texture = result
            print(f"📋 {name} ({slug}):")
            print(f"   Thumbnail: {thumbnail}")
            print(f"   Texture:   {texture}")
            
            # Check if thumbnail is incorrectly pointing to texture
            if thumbnail == texture:
                print(f"   ❌ PROBLEM: Thumbnail is same as texture!")
            elif '.png' not in thumbnail.lower():
                print(f"   ❌ PROBLEM: Thumbnail doesn't look like a PNG file!")
            elif '!' not in thumbnail:
                print(f"   ⚠️  WARNING: Thumbnail missing '!' marker")
            else:
                print(f"   ✅ Looks correct")
            print()
        else:
            print(f"❌ {slug} not found in database\n")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
