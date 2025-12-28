#!/usr/bin/env python3
"""Update BigDaddy2's avatar to professor-bee in Railway database"""

import os
import psycopg2

# Database connection (use your current environment: DigitalOcean, Railway, local, etc.)
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("DIGITALOCEAN_DATABASE_URL")
if not DATABASE_URL:
    raise SystemExit(
        "DATABASE_URL (or DIGITALOCEAN_DATABASE_URL) must be set before running this script."
    )

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("=" * 70)
    print("🎓 UPDATING BIGDADDY2 TO PROFESSOR BEE")
    print("=" * 70)
    
    # Update BigDaddy2's avatar
    cursor.execute("""
        UPDATE users 
        SET avatar_id = 'professor-bee',
            avatar_last_updated = NOW()
        WHERE username = 'BigDaddy2'
        RETURNING id, username, avatar_id
    """)
    
    result = cursor.fetchone()
    
    if result:
        print(f"\n✅ Updated successfully!")
        print(f"   User ID: {result[0]}")
        print(f"   Username: {result[1]}")
        print(f"   New Avatar: {result[2]}")
        
        conn.commit()
        print("\n💾 Changes committed to database")
    else:
        print("\n❌ User not found!")
        
    cursor.close()
    conn.close()
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
