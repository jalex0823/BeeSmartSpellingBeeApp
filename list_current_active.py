"""
List all 41 current active avatars in database
"""
import psycopg2

DATABASE_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name, slug 
        FROM avatars 
        WHERE is_active = true
        ORDER BY name
    """)
    
    avatars = cursor.fetchall()
    
    print(f"Current active avatars in database: {len(avatars)}\n")
    for i, (name, slug) in enumerate(avatars, 1):
        print(f"{i:2d}. {name:30s} ({slug})")
    
    cursor.close()
    conn.close()

except Exception as e:
    print(f"Error: {e}")
