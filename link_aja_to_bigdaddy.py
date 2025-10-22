"""
Link Aja (PRINCESS) to BigDaddy2 using TeacherStudent table in Railway
"""
import psycopg2
from datetime import datetime

# Railway PostgreSQL connection URL
RAILWAY_DB_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

print("\nLinking Aja to BigDaddy2's Dashboard\n")
print("=" * 70)

try:
    conn = psycopg2.connect(RAILWAY_DB_URL)
    cursor = conn.cursor()
    print("Connected to Railway PostgreSQL\n")
    
    # Get BigDaddy2's info
    cursor.execute("""
        SELECT id, username, teacher_key
        FROM users
        WHERE username = 'BigDaddy2'
    """)
    bigdaddy = cursor.fetchone()
    
    if not bigdaddy:
        print("ERROR: BigDaddy2 not found!")
        exit(1)
    
    bigdaddy_id, bigdaddy_username, bigdaddy_key = bigdaddy
    print(f"Admin: {bigdaddy_username} (ID: {bigdaddy_id})")
    print(f"Admin Key: {bigdaddy_key}\n")
    
    # Get Aja's info
    cursor.execute("""
        SELECT id, username, display_name
        FROM users
        WHERE username = 'PRINCESS'
    """)
    aja = cursor.fetchone()
    
    if not aja:
        print("ERROR: PRINCESS (Aja) not found!")
        exit(1)
    
    aja_id, aja_username, aja_display_name = aja
    print(f"Student: {aja_display_name} (username: {aja_username}, ID: {aja_id})\n")
    
    # Check if link already exists
    cursor.execute("""
        SELECT id, is_active
        FROM teacher_students
        WHERE teacher_key = %s AND student_id = %s
    """, (bigdaddy_key, aja_id))
    
    existing_link = cursor.fetchone()
    
    if existing_link:
        link_id, is_active = existing_link
        if is_active:
            print(f"Link already exists and is active (ID: {link_id})")
            print("Aja should already appear in BigDaddy2's dashboard!")
        else:
            print(f"Reactivating existing link (ID: {link_id})...")
            cursor.execute("""
                UPDATE teacher_students
                SET is_active = true
                WHERE id = %s
            """, (link_id,))
            conn.commit()
            print("Link reactivated!")
    else:
        print("Creating new link...")
        cursor.execute("""
            INSERT INTO teacher_students 
                (teacher_key, teacher_user_id, student_id, assigned_date, relationship_type, is_active)
            VALUES 
                (%s, %s, %s, %s, %s, %s)
        """, (bigdaddy_key, bigdaddy_id, aja_id, datetime.utcnow(), 'parent', True))
        
        conn.commit()
        print("Link created successfully!")
    
    print("\n" + "=" * 70)
    print("SUCCESS! Aja is now linked to BigDaddy2's dashboard")
    print("=" * 70)
    print("\nRefresh the dashboard to see Aja appear in 'My Students/Family'\n")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"ERROR: {e}")
    if 'conn' in locals():
        conn.rollback()
