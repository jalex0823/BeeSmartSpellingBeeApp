"""
Add Zom Bee Avatar back to Railway database with all required fields
"""
import psycopg2

DATABASE_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

print("=" * 60)
print("🐝 Add Zom Bee Avatar Back")
print("=" * 60)

confirm = input("\nAdd Zom Bee Avatar to database? (YES): ")
if confirm.strip() != "YES":
    print("❌ Cancelled")
    exit(1)

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Check if it exists first
    cursor.execute("SELECT id FROM avatars WHERE slug = 'zom-bee'")
    if cursor.fetchone():
        print("⚠️  Zom Bee already exists!")
        cursor.close()
        conn.close()
        exit(0)
    
    print("\n✅ Adding Zom Bee Avatar...")
    
    # Insert with all required fields matching Brother Bee structure
    cursor.execute("""
        INSERT INTO avatars (
            slug, name, description, category, folder_path, obj_file,
            mtl_file, texture_file, thumbnail_file, unlock_level,
            points_required, is_premium, is_active
        ) VALUES (
            'zom-bee',
            'Zom Bee Avatar',
            'Zom Bee is ready to spell! 🧟‍♂️🐝',
            'classic',
            'glb_files',
            'ZomBee.glb',
            'ZomBee.mtl',
            'ZomBee.png',
            'AvatarThumbnails/ZomBee!.png',
            1,
            0,
            false,
            true
        )
    """)
    
    conn.commit()
    
    print("✅ Zom Bee Avatar added successfully!")
    
    # Final count
    cursor.execute("SELECT COUNT(*) FROM avatars WHERE is_active = true")
    total = cursor.fetchone()[0]
    
    print(f"\n📊 Total active avatars: {total}")
    
    if total == 39:
        print("🎉 PERFECT! Exactly 39 avatars in database!")
    else:
        print(f"⚠️  Expected 39, have {total}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ ZOM BEE ADDED!")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
