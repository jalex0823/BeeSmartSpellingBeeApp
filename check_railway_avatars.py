"""
Check what avatars exist in Railway PostgreSQL and how they work
"""

import os
import psycopg2
import requests

# Railway PostgreSQL connection
# IMPORTANT: Do not hardcode production DB credentials.
# Provide DATABASE_URL via environment variables.
RAILWAY_DB_URL = os.getenv("DATABASE_URL", "")

def check_railway_database():
    """Check what's in Railway's avatar table"""
    print("\n" + "="*80)
    print("📊 CHECKING RAILWAY POSTGRESQL DATABASE")
    print("="*80 + "\n")
    
    conn = psycopg2.connect(RAILWAY_DB_URL)
    cursor = conn.cursor()
    
    # Get all avatars
    cursor.execute("""
        SELECT id, slug, name, folder_path, obj_file, thumbnail_file, is_active
        FROM avatars
        ORDER BY id
    """)
    
    rows = cursor.fetchall()
    
    print(f"Total avatars in Railway database: {len(rows)}\n")
    print(f"{'ID':<5} {'Slug':<25} {'Name':<25} {'Folder':<25} {'Active'}")
    print("-" * 110)
    
    for row in rows:
        avatar_id, slug, name, folder_path, obj_file, thumbnail_file, is_active = row
        active_mark = "✅" if is_active else "❌"
        print(f"{avatar_id:<5} {slug:<25} {name:<25} {folder_path:<25} {active_mark}")
    
    cursor.close()
    conn.close()
    
    return rows


def check_railway_api():
    """Check what the Railway API returns"""
    print("\n" + "="*80)
    print("🌐 CHECKING RAILWAY API ENDPOINT")
    print("="*80 + "\n")
    
    try:
        response = requests.get('https://beesmart.up.railway.app/api/avatars', timeout=10)
        avatars = response.json()
        
        print(f"API returned {len(avatars)} avatars\n")
        print(f"{'Slug':<25} {'Name':<25} {'Thumbnail URL'}")
        print("-" * 110)
        
        for avatar in avatars:
            slug = avatar.get('id', avatar.get('slug', 'unknown'))
            name = avatar.get('name', 'Unknown')
            thumbnail = avatar.get('thumbnailUrl', avatar.get('thumbnail', 'none'))
            print(f"{slug:<25} {name:<25} {thumbnail}")
        
        return avatars
        
    except Exception as e:
        print(f"❌ Failed to fetch Railway API: {e}")
        return []


def check_file_accessibility():
    """Check if avatar files are accessible on Railway"""
    print("\n" + "="*80)
    print("📁 CHECKING FILE ACCESSIBILITY ON RAILWAY")
    print("="*80 + "\n")
    
    # Test a few known working avatars
    test_avatars = [
        ('cool-bee', 'CoolBee.obj'),
        ('al-bee', 'AlBee.obj'),
        ('beedoctor', 'DoctorBee.obj'),
    ]
    
    for folder, obj_file in test_avatars:
        url = f"https://beesmart.up.railway.app/static/assets/avatars/{folder}/{obj_file}"
        try:
            response = requests.head(url, timeout=5)
            status = "✅ ACCESSIBLE" if response.status_code == 200 else f"❌ {response.status_code}"
            print(f"{folder:<20} {obj_file:<20} {status}")
        except Exception as e:
            print(f"{folder:<20} {obj_file:<20} ❌ ERROR: {e}")


if __name__ == "__main__":
    # Check database
    db_avatars = check_railway_database()
    
    # Check API
    api_avatars = check_railway_api()
    
    # Check file accessibility
    check_file_accessibility()
    
    # Summary
    print("\n" + "="*80)
    print("📋 SUMMARY")
    print("="*80)
    print(f"Database has: {len(db_avatars)} avatar records")
    print(f"API returns: {len(api_avatars)} avatars")
    
    if len(db_avatars) != len(api_avatars):
        print("\n⚠️  MISMATCH: Database and API counts don't match!")
        print("   This means some avatars in database are not being returned by API")
    else:
        print("\n✅ Database and API counts match")
    
    print("\n")
