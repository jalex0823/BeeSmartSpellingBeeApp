"""
Check Aja's (PRINCESS) admin key assignment in Railway PostgreSQL
"""
import psycopg2

# Railway PostgreSQL connection URL
RAILWAY_DB_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

print("\nChecking Aja's Account (PRINCESS) in Railway Database\n")
print("=" * 70)

try:
    conn = psycopg2.connect(RAILWAY_DB_URL)
    cursor = conn.cursor()
    print("Connected to Railway PostgreSQL\n")
    
    # Query for PRINCESS account
    cursor.execute("""
        SELECT 
            id,
            username,
            display_name,
            email,
            role,
            teacher_key,
            created_at,
            is_active
        FROM users
        WHERE username = 'PRINCESS'
    """)
    
    result = cursor.fetchone()
    
    if result:
        user_id, username, display_name, email, role, teacher_key, created_at, is_active = result
        
        print(f"Username: {username}")
        print(f"Display Name: {display_name}")
        print(f"Email: {email}")
        print(f"Role: {role}")
        print(f"Teacher Key: {teacher_key if teacher_key else 'NOT ASSIGNED'}")
        print(f"Created: {created_at}")
        print(f"Active: {'Yes' if is_active else 'No'}")
        print("\n" + "=" * 70)
        
        if not teacher_key:
            print("\nISSUE: Aja does not have a teacher_key assigned!")
            print("This is why she doesn't appear in BigDaddy2's dashboard.")
            print("\nTo fix: Run update_aja_key.py to assign BigDaddy2's key to Aja")
        else:
            # Check if it matches BigDaddy2's key
            cursor.execute("""
                SELECT teacher_key, display_name
                FROM users
                WHERE username = 'BigDaddy2'
            """)
            bigdaddy_result = cursor.fetchone()
            
            if bigdaddy_result:
                bigdaddy_key, bigdaddy_name = bigdaddy_result
                print(f"\nBigDaddy2's Key: {bigdaddy_key}")
                print(f"Aja's Key: {teacher_key}")
                
                if teacher_key == bigdaddy_key:
                    print("\nSTATUS: Aja is correctly linked to BigDaddy2!")
                else:
                    print("\nISSUE: Keys don't match! Aja won't appear in BigDaddy2's dashboard")
    else:
        print("PRINCESS account not found!")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
