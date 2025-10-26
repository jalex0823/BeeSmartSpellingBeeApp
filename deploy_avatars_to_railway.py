"""
Deploy 13 New Avatars to Railway PostgreSQL Database

This script connects to Railway's PostgreSQL database and adds the 13 new avatar records.
The 3D files will be deployed via git push (they're in static/assets/avatars/).

Railway Database:
postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway
"""

import psycopg2
from datetime import datetime

# Railway PostgreSQL connection
RAILWAY_DB_URL = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

# 13 new avatars to add
NEW_AVATARS = [
    {
        'slug': 'beedoctor',
        'name': 'Doctor Bee',
        'description': 'A caring bee doctor ready to help friends feel better! 🏥',
        'category': 'professional',
        'folder_path': 'beedoctor',
        'obj_file': 'DoctorBee.obj',
        'mtl_file': 'DoctorBee.mtl',
        'texture_file': 'DoctorBee.png',
        'thumbnail_file': 'BeeDoctor!.png',
        'unlock_level': 1,
        'points_required': 0,
        'is_premium': False,
        'sort_order': 11,
        'is_active': True
    },
    {
        'slug': 'beeknight',
        'name': 'Knight Bee',
        'description': 'A brave knight bee protecting the hive with honor! ⚔️',
        'category': 'adventure',
        'folder_path': 'beeknight',
        'obj_file': 'KnightBee.obj',
        'mtl_file': 'KnightBee.mtl',
        'texture_file': 'KnightBee.png',
        'thumbnail_file': 'BeeKnight!.png',
        'unlock_level': 1,
        'points_required': 0,
        'is_premium': False,
        'sort_order': 12,
        'is_active': True
    },
    {
        'slug': 'builderbee',
        'name': 'Builder Bee',
        'description': 'A hardworking builder bee constructing amazing things! 🔨',
        'category': 'professional',
        'folder_path': 'builderbee',
        'obj_file': 'BuilderBee.obj',
        'mtl_file': 'BuilderBee.mtl',
        'texture_file': 'BuilderBee.png',
        'thumbnail_file': 'BuilderBee!.png',
        'unlock_level': 1,
        'points_required': 0,
        'is_premium': False,
        'sort_order': 13,
        'is_active': True
    },
    {
        'slug': 'buzzbotbee',
        'name': 'Buzzbot Bee',
        'description': 'A futuristic robot bee from the future! 🤖',
        'category': 'tech',
        'folder_path': 'buzzbotbee',
        'obj_file': 'BuzzBot.obj',
        'mtl_file': 'BuzzBot.mtl',
        'texture_file': 'BuzzBot.png',
        'thumbnail_file': 'BuzzBot!.png',
        'unlock_level': 1,
        'points_required': 0,
        'is_premium': False,
        'sort_order': 14,
        'is_active': True
    },
    {
        'slug': 'buzzhero',
        'name': 'Buzzhero Bee',
        'description': 'A heroic bee always ready to save the day! 🦸',
        'category': 'superhero',
        'folder_path': 'buzzhero',
        'obj_file': 'BuzzHeroBee.obj',
        'mtl_file': 'BuzzHeroBee.mtl',
        'texture_file': 'BuzzHeroBee.png',
        'thumbnail_file': 'BuzzHero!.png',
        'unlock_level': 1,
        'points_required': 0,
        'is_premium': False,
        'sort_order': 15,
        'is_active': True
    },
    {
        'slug': 'detectivebee',
        'name': 'Detective Bee',
        'description': 'A clever detective bee solving mysteries! 🔍',
        'category': 'adventure',
        'folder_path': 'detectivebee',
        'obj_file': 'DetectiveBee.obj',
        'mtl_file': 'DetectiveBee.mtl',
        'texture_file': 'DetectiveBee.png',
        'thumbnail_file': 'DetectiveBee!.png',
        'unlock_level': 1,
        'points_required': 0,
        'is_premium': False,
        'sort_order': 16,
        'is_active': True
    },
    {
        'slug': 'explorerbee',
        'name': 'Explorer Bee',
        'description': 'An adventurous bee exploring new worlds! 🧭',
        'category': 'adventure',
        'folder_path': 'explorerbee',
        'obj_file': 'ExplorerBee.obj',
        'mtl_file': 'ExplorerBee.mtl',
        'texture_file': 'ExplorerBee.png',
        'thumbnail_file': 'ExplorerBee!.png',
        'unlock_level': 1,
        'points_required': 0,
        'is_premium': False,
        'sort_order': 17,
        'is_active': True
    },
    {
        'slug': 'frankenbee',
        'name': 'Franken Bee',
        'description': 'A friendly monster bee who loves to make friends! 👻',
        'category': 'spooky',
        'folder_path': 'frankenbee',
        'obj_file': 'FrankenBee.obj',
        'mtl_file': 'FrankenBee.mtl',
        'texture_file': 'FrankenBee.png',
        'thumbnail_file': 'FrankenBee!.png',
        'unlock_level': 1,
        'points_required': 0,
        'is_premium': False,
        'sort_order': 18,
        'is_active': True
    },
    {
        'slug': 'motorcyclebuzzbee',
        'name': 'Motorcyclebuzz Bee',
        'description': 'A cool biker bee cruising on two wheels! 🏍️',
        'category': 'sports',
        'folder_path': 'motorcyclebuzzbee',
        'obj_file': 'MotorcycleBuzzBee.obj',
        'mtl_file': 'MotorcycleBuzzBee.mtl',
        'texture_file': 'MotorcycleBuzzBee.png',
        'thumbnail_file': 'MotorcycleBuzzBee!.png',
        'unlock_level': 1,
        'points_required': 0,
        'is_premium': False,
        'sort_order': 19,
        'is_active': True
    },
    {
        'slug': 'queenbeemajesty',
        'name': 'Queen Bee Majesty',
        'description': 'The royal queen bee ruling with wisdom and grace! 👑',
        'category': 'royal',
        'folder_path': 'queenbeemajesty',
        'obj_file': 'QueenBeeMajesty.obj',
        'mtl_file': 'QueenBeeMajesty.mtl',
        'texture_file': 'QueenBeeMajesty.png',
        'thumbnail_file': 'QueenMajesty!.png',
        'unlock_level': 1,
        'points_required': 0,
        'is_premium': False,
        'sort_order': 20,
        'is_active': True
    },
    {
        'slug': 'seabee',
        'name': 'Sea Bee',
        'description': 'An underwater bee exploring the ocean depths! 🌊',
        'category': 'adventure',
        'folder_path': 'seabee',
        'obj_file': 'SeaBee.obj',
        'mtl_file': 'SeaBee.mtl',
        'texture_file': 'SeaBee.png',
        'thumbnail_file': 'SeaBee!.png',
        'unlock_level': 1,
        'points_required': 0,
        'is_premium': False,
        'sort_order': 21,
        'is_active': True
    },
    {
        'slug': 'spacebeeexplorer',
        'name': 'Space Bee Explorer',
        'description': 'An astronaut bee exploring the cosmos! 🚀',
        'category': 'space',
        'folder_path': 'spacebeeexplorer',
        'obj_file': 'SpaceBeeExplorer.obj',
        'mtl_file': 'SpaceBeeExplorer.mtl',
        'texture_file': 'SpaceBeeExplorer.png',
        'thumbnail_file': 'SpaceBeeExplorer!.png',
        'unlock_level': 1,
        'points_required': 0,
        'is_premium': False,
        'sort_order': 22,
        'is_active': True
    },
    {
        'slug': 'superbeehero',
        'name': 'Super Bee Hero',
        'description': 'A super-powered bee hero defending the hive! 💪',
        'category': 'superhero',
        'folder_path': 'superbeehero',
        'obj_file': 'SuperBeeHero.obj',
        'mtl_file': 'SuperBeeHero.mtl',
        'texture_file': 'SuperBeeHero.png',
        'thumbnail_file': 'SuperBeeHero!.png',
        'unlock_level': 1,
        'points_required': 0,
        'is_premium': False,
        'sort_order': 23,
        'is_active': True
    }
]


def connect_to_railway():
    """Connect to Railway PostgreSQL database"""
    try:
        conn = psycopg2.connect(RAILWAY_DB_URL)
        print("✅ Connected to Railway PostgreSQL database")
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to Railway database: {e}")
        return None


def check_existing_avatars(conn):
    """Check which avatars already exist in Railway database"""
    cursor = conn.cursor()
    
    slugs = [avatar['slug'] for avatar in NEW_AVATARS]
    placeholders = ','.join(['%s'] * len(slugs))
    
    cursor.execute(f"""
        SELECT slug FROM avatars 
        WHERE slug IN ({placeholders})
    """, slugs)
    
    existing = [row[0] for row in cursor.fetchall()]
    cursor.close()
    
    return existing


def add_avatar_to_railway(conn, avatar_data):
    """Add a single avatar record to Railway database"""
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO avatars (
                slug, name, description, category,
                folder_path, obj_file, mtl_file, texture_file, thumbnail_file,
                unlock_level, points_required, is_premium, sort_order, is_active,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s
            )
        """, (
            avatar_data['slug'],
            avatar_data['name'],
            avatar_data['description'],
            avatar_data['category'],
            avatar_data['folder_path'],
            avatar_data['obj_file'],
            avatar_data['mtl_file'],
            avatar_data['texture_file'],
            avatar_data['thumbnail_file'],
            avatar_data['unlock_level'],
            avatar_data['points_required'],
            avatar_data['is_premium'],
            avatar_data['sort_order'],
            avatar_data['is_active'],
            datetime.utcnow(),
            datetime.utcnow()
        ))
        
        conn.commit()
        cursor.close()
        return True
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        print(f"   ❌ Error adding {avatar_data['slug']}: {e}")
        return False


def main():
    """Main deployment function"""
    print("\n" + "="*80)
    print("🚀 DEPLOYING 13 NEW AVATARS TO RAILWAY POSTGRESQL DATABASE")
    print("="*80 + "\n")
    
    # Connect to Railway database
    conn = connect_to_railway()
    if not conn:
        print("\n❌ Deployment failed - could not connect to database")
        return
    
    # Check existing avatars
    print("\n📋 Checking for existing avatars in Railway database...")
    existing_slugs = check_existing_avatars(conn)
    
    if existing_slugs:
        print(f"⚠️  Found {len(existing_slugs)} avatars already in database:")
        for slug in existing_slugs:
            print(f"   - {slug}")
        print("\n   These will be skipped to avoid duplicates")
    else:
        print("✅ No duplicate avatars found - all 13 will be added")
    
    # Add new avatars
    print("\n🐝 Adding avatars to Railway database...\n")
    
    added_count = 0
    skipped_count = 0
    failed_count = 0
    
    for avatar in NEW_AVATARS:
        if avatar['slug'] in existing_slugs:
            print(f"⏭️  Skipped: {avatar['name']} ({avatar['slug']}) - already exists")
            skipped_count += 1
            continue
        
        print(f"📝 Adding: {avatar['name']} ({avatar['slug']})...")
        success = add_avatar_to_railway(conn, avatar)
        
        if success:
            print(f"   ✅ Successfully added {avatar['name']}")
            added_count += 1
        else:
            failed_count += 1
    
    # Close connection
    conn.close()
    
    # Summary
    print("\n" + "="*80)
    print("📊 DEPLOYMENT SUMMARY")
    print("="*80)
    print(f"✅ Successfully added: {added_count} avatars")
    print(f"⏭️  Skipped (existing): {skipped_count} avatars")
    print(f"❌ Failed: {failed_count} avatars")
    print(f"📦 Total in batch: {len(NEW_AVATARS)} avatars")
    
    if added_count > 0:
        print("\n🎉 New avatars added to Railway database!")
        print("📝 Next steps:")
        print("   1. Commit and push the 13 avatar folders to git")
        print("   2. Railway will auto-deploy the 3D files from git")
        print("   3. Test at https://beesmart.up.railway.app/test/avatar-picker")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
