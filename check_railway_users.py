"""
Check Railway PostgreSQL Database for Users
Connects directly to Railway's PostgreSQL database to check user accounts
"""

import os
import sys

# Database URL from Railway (correct URL without space)
RAILWAY_DB_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("❌ psycopg2 not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2
    from psycopg2 import sql

def check_railway_database():
    """Check Railway database for users"""
    print("\n" + "="*70)
    print("🚂 CHECKING RAILWAY POSTGRESQL DATABASE")
    print("="*70)
    
    try:
        # Connect to Railway database
        print(f"\n🔌 Connecting to Railway PostgreSQL...")
        conn = psycopg2.connect(RAILWAY_DB_URL)
        cursor = conn.cursor()
        print("✅ Connected successfully!")
        
        # Check if users table exists
        print(f"\n📊 Checking for 'users' table...")
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            );
        """)
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("❌ Users table does not exist in Railway database")
            print("💡 You may need to run database initialization")
            cursor.close()
            conn.close()
            return False
        
        print("✅ Users table exists!")
        
        # Get all users
        print(f"\n👥 Fetching all users...")
        cursor.execute("""
            SELECT id, username, email, role, display_name, created_at, 
                   is_active, last_login, teacher_key
            FROM users
            ORDER BY created_at DESC;
        """)
        
        users = cursor.fetchall()
        
        if not users:
            print("❌ No users found in Railway database")
            cursor.close()
            conn.close()
            return False
        
        print(f"\n✅ Found {len(users)} users:\n")
        print("-" * 70)
        
        admin_found = False
        bigdaddy2_found = False
        
        for user in users:
            user_id, username, email, role, display_name, created_at, is_active, last_login, teacher_key = user
            
            print(f"👤 Username: {username}")
            print(f"   ID: {user_id}")
            print(f"   Email: {email}")
            print(f"   Role: {role}")
            print(f"   Display Name: {display_name}")
            print(f"   Created: {created_at}")
            print(f"   Is Active: {'✅ Yes' if is_active else '❌ No'}")
            print(f"   Last Login: {last_login if last_login else 'Never'}")
            
            if role == 'admin':
                admin_found = True
                print(f"   🔑 ADMIN ACCOUNT")
            
            if username.lower() == 'bigdaddy2':
                bigdaddy2_found = True
                print(f"   ⭐ THIS IS THE ACCOUNT YOU'RE LOOKING FOR!")
            
            if teacher_key:
                print(f"   👨‍🏫 Teacher Key: {teacher_key}")
            
            print("-" * 70)
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"   Total users: {len(users)}")
        print(f"   Admin accounts: {'✅ Yes' if admin_found else '❌ None'}")
        print(f"   BigDaddy2 account: {'✅ Found' if bigdaddy2_found else '❌ Not found'}")
        
        cursor.close()
        conn.close()
        
        return bigdaddy2_found
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection error: {e}")
        print(f"\n💡 Possible issues:")
        print(f"   - Database URL might be incorrect")
        print(f"   - Database might not be accessible")
        print(f"   - Firewall blocking connection")
        return False
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return False


def check_specific_user(username):
    """Check if a specific user exists and show details"""
    print("\n" + "="*70)
    print(f"🔍 SEARCHING FOR USER: {username}")
    print("="*70)
    
    try:
        conn = psycopg2.connect(RAILWAY_DB_URL)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, email, role, display_name, created_at, 
                   is_active, last_login, teacher_key, password_hash
            FROM users
            WHERE LOWER(username) = LOWER(%s);
        """, (username,))
        
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ User '{username}' not found in Railway database")
            cursor.close()
            conn.close()
            return False
        
        user_id, username, email, role, display_name, created_at, is_active, last_login, teacher_key, password_hash = user
        
        print(f"\n✅ USER FOUND!\n")
        print(f"👤 Username: {username}")
        print(f"📧 Email: {email}")
        print(f"🎭 Role: {role}")
        print(f"📝 Display Name: {display_name}")
        print(f"📅 Created: {created_at}")
        print(f"✅ Is Active: {'Yes' if is_active else 'No'}")
        print(f"🕐 Last Login: {last_login if last_login else 'Never logged in'}")
        print(f"🔑 Has Password: {'✅ Yes' if password_hash else '❌ No'}")
        
        if role == 'admin':
            print(f"👑 ADMIN PRIVILEGES: ✅ YES")
        
        if teacher_key:
            print(f"👨‍🏫 Teacher Key: {teacher_key}")
        
        print("\n" + "="*70)
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return False


if __name__ == "__main__":
    print("\n🐝 BeeSmart Railway Database User Checker")
    
    # Check for specific user if provided
    if len(sys.argv) > 1:
        username = sys.argv[1]
        check_specific_user(username)
    else:
        # Check all users
        check_railway_database()
    
    print("\n✨ Check complete!\n")
