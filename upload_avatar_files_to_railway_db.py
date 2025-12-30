"""
Upload 3D Avatar Files as Binary Data to PostgreSQL Database

This script reads the .obj, .mtl, .png files from the local filesystem
and uploads them as binary data directly into your PostgreSQL database.
"""

import os
import psycopg2
from pathlib import Path

# IMPORTANT: Do not hardcode production DB credentials.
DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    raise SystemExit("DATABASE_URL is not set. Provide your PostgreSQL connection string via env vars.")

# Base path for avatar files
AVATAR_BASE_PATH = Path("static/assets/avatars")

# 13 new avatars to upload
NEW_AVATARS = [
    'beedoctor', 'beeknight', 'builderbee', 'buzzbotbee', 'buzzhero',
    'detectivebee', 'explorerbee', 'frankenbee', 'motorcyclebuzzbee',
    'queenbeemajesty', 'seabee', 'spacebeeexplorer', 'superbeehero'
]


def connect_to_railway():
    """Connect to PostgreSQL database (configured via DATABASE_URL)."""
    try:
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL is not set")
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Connected to PostgreSQL database")
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return None


def add_binary_columns_if_needed(conn):
    """Add binary data columns to avatars table if they don't exist"""
    cursor = conn.cursor()
    
    print("\n📋 Checking database schema...")
    
    try:
        # Check if binary columns exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'avatars' 
            AND column_name IN ('obj_data', 'mtl_data', 'texture_data', 'thumbnail_data')
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        if len(existing_columns) == 4:
            print("✅ Binary data columns already exist")
            cursor.close()
            return True
        
        print(f"⚠️  Found {len(existing_columns)}/4 binary columns, adding missing ones...")
        
        # Add missing columns
        columns_to_add = {
            'obj_data': 'BYTEA',
            'mtl_data': 'BYTEA',
            'texture_data': 'BYTEA',
            'thumbnail_data': 'BYTEA'
        }
        
        for col_name, col_type in columns_to_add.items():
            if col_name not in existing_columns:
                cursor.execute(f"""
                    ALTER TABLE avatars 
                    ADD COLUMN IF NOT EXISTS {col_name} {col_type}
                """)
                print(f"   ✅ Added column: {col_name}")
        
        conn.commit()
        cursor.close()
        print("✅ Database schema updated successfully")
        return True
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        print(f"❌ Error updating schema: {e}")
        return False


def read_avatar_files(slug):
    """Read all 4 files for an avatar from local filesystem"""
    folder_path = AVATAR_BASE_PATH / slug
    
    if not folder_path.exists():
        print(f"   ❌ Folder not found: {folder_path}")
        return None
    
    # Find the files (they have different naming patterns)
    files = list(folder_path.glob("*.obj"))
    if not files:
        print(f"   ❌ No .obj file found in {folder_path}")
        return None
    
    obj_file = files[0]
    mtl_file = obj_file.with_suffix('.mtl')
    texture_file = obj_file.with_suffix('.png')
    
    # Find thumbnail (has ! in name)
    thumbnail_files = list(folder_path.glob("*!.png"))
    if not thumbnail_files:
        print(f"   ❌ No thumbnail (*!.png) found in {folder_path}")
        return None
    
    thumbnail_file = thumbnail_files[0]
    
    # Read binary data
    try:
        with open(obj_file, 'rb') as f:
            obj_data = f.read()
        
        with open(mtl_file, 'rb') as f:
            mtl_data = f.read()
        
        with open(texture_file, 'rb') as f:
            texture_data = f.read()
        
        with open(thumbnail_file, 'rb') as f:
            thumbnail_data = f.read()
        
        file_sizes = {
            'obj': len(obj_data),
            'mtl': len(mtl_data),
            'texture': len(texture_data),
            'thumbnail': len(thumbnail_data)
        }
        
        total_size = sum(file_sizes.values())
        
        print(f"   📁 Read files: OBJ={file_sizes['obj']:,} MTL={file_sizes['mtl']:,} "
              f"TEX={file_sizes['texture']:,} THUMB={file_sizes['thumbnail']:,} bytes "
              f"(Total: {total_size:,} bytes)")
        
        return {
            'obj_data': obj_data,
            'mtl_data': mtl_data,
            'texture_data': texture_data,
            'thumbnail_data': thumbnail_data
        }
        
    except Exception as e:
        print(f"   ❌ Error reading files: {e}")
        return None


def upload_avatar_files(conn, slug, file_data):
    """Upload binary file data to Railway database"""
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE avatars
            SET obj_data = %s,
                mtl_data = %s,
                texture_data = %s,
                thumbnail_data = %s,
                updated_at = NOW()
            WHERE slug = %s
        """, (
            psycopg2.Binary(file_data['obj_data']),
            psycopg2.Binary(file_data['mtl_data']),
            psycopg2.Binary(file_data['texture_data']),
            psycopg2.Binary(file_data['thumbnail_data']),
            slug
        ))
        
        if cursor.rowcount == 0:
            cursor.close()
            return False, "Avatar record not found in database"
        
        conn.commit()
        cursor.close()
        return True, "Files uploaded successfully"
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        return False, str(e)


def main():
    """Main upload function"""
    print("\n" + "="*80)
    print("🚀 UPLOADING 3D AVATAR FILES TO RAILWAY POSTGRESQL DATABASE")
    print("="*80 + "\n")
    
    # Connect to Railway database
    conn = connect_to_railway()
    if not conn:
        print("\n❌ Upload failed - could not connect to database")
        return
    
    # Add binary columns if needed
    if not add_binary_columns_if_needed(conn):
        print("\n❌ Upload failed - could not update database schema")
        conn.close()
        return
    
    # Upload each avatar
    print("\n🐝 Uploading avatar files...\n")
    
    success_count = 0
    failed_count = 0
    total_bytes = 0
    
    for slug in NEW_AVATARS:
        print(f"📝 Processing: {slug}")
        
        # Read files from local filesystem
        file_data = read_avatar_files(slug)
        if not file_data:
            failed_count += 1
            continue
        
        # Upload to database
        success, message = upload_avatar_files(conn, slug, file_data)
        
        if success:
            size = sum(len(data) for data in file_data.values())
            total_bytes += size
            print(f"   ✅ Uploaded successfully")
            success_count += 1
        else:
            print(f"   ❌ Upload failed: {message}")
            failed_count += 1
    
    # Close connection
    conn.close()
    
    # Summary
    print("\n" + "="*80)
    print("📊 UPLOAD SUMMARY")
    print("="*80)
    print(f"✅ Successfully uploaded: {success_count} avatars")
    print(f"❌ Failed: {failed_count} avatars")
    print(f"📦 Total data uploaded: {total_bytes:,} bytes ({total_bytes / 1024 / 1024:.2f} MB)")
    
    if success_count > 0:
        print("\n🎉 Avatar files uploaded to Railway database!")
        print("📝 Next steps:")
        print("   1. Commit and push the models.py changes to git")
        print("   2. Create endpoints to serve files from database")
        print("   3. Test at https://beesmart.up.railway.app/test/avatar-picker")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
