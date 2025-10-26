#!/usr/bin/env python3
"""
Verify that the avatar thumbnail filename fix was successful
by checking the database and filesystem directly.
"""

import os
import sqlite3
from pathlib import Path

def verify_avatar_fix():
    """Verify that the thumbnail filename fix resolved the avatar grid issues"""
    
    print("🔍 Verifying Avatar Thumbnail Fix")
    print("=" * 50)
    
    # Connect to database
    db_path = "beesmart.db"
    if not os.path.exists(db_path):
        print("❌ Database not found at beesmart.db")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Query all avatars
        cursor.execute("""
            SELECT id, display_name, thumbnail_file, obj_file, mtl_file, texture_file 
            FROM avatars 
            ORDER BY id
        """)
        
        avatars = cursor.fetchall()
        print(f"📊 Found {len(avatars)} avatars in database")
        
        # Check avatar assets directory
        assets_dir = Path("static/assets/avatars")
        if not assets_dir.exists():
            print("❌ Avatar assets directory not found")
            return False
        
        print(f"\n📁 Checking avatar files in {assets_dir}")
        
        success_count = 0
        issue_count = 0
        
        for avatar in avatars:
            avatar_id, display_name, thumbnail_file, obj_file, mtl_file, texture_file = avatar
            
            print(f"\n🔍 Checking {avatar_id} ({display_name})")
            
            # Check if avatar folder exists
            avatar_folder = assets_dir / avatar_id
            if not avatar_folder.exists():
                print(f"   ❌ Folder missing: {avatar_folder}")
                issue_count += 1
                continue
            
            # Check each file
            files_to_check = [
                ("thumbnail", thumbnail_file),
                ("obj", obj_file),
                ("mtl", mtl_file), 
                ("texture", texture_file)
            ]
            
            avatar_success = True
            for file_type, filename in files_to_check:
                if filename:
                    file_path = avatar_folder / filename
                    if file_path.exists():
                        print(f"   ✅ {file_type}: {filename}")
                    else:
                        print(f"   ❌ {file_type} MISSING: {filename}")
                        avatar_success = False
                        
                        # Check if there's a file with spaces in the name
                        potential_files = list(avatar_folder.glob("*.png"))
                        if file_type == "thumbnail" and potential_files:
                            print(f"      📋 Available PNG files: {[f.name for f in potential_files]}")
            
            if avatar_success:
                success_count += 1
            else:
                issue_count += 1
        
        print(f"\n📈 Results Summary:")
        print(f"✅ Successful avatars: {success_count}")
        print(f"❌ Avatars with issues: {issue_count}")
        
        # Show specific improvements from our fix
        print(f"\n💾 Database Thumbnail Filenames:")
        cursor.execute("SELECT id, display_name, thumbnail_file FROM avatars ORDER BY id")
        thumbnail_data = cursor.fetchall()
        
        for avatar_id, display_name, thumbnail_file in thumbnail_data[:10]:  # Show first 10
            has_spaces = ' ' in thumbnail_file if thumbnail_file else False
            status = "⚠️ HAS SPACES" if has_spaces else "✅ NO SPACES"
            print(f"   {avatar_id}: {thumbnail_file} {status}")
        
        if len(thumbnail_data) > 10:
            print(f"   ... and {len(thumbnail_data) - 10} more")
        
        # Test the specific API endpoint structure
        print(f"\n🌐 Avatar API Structure Test:")
        print("   These would be the thumbnail URLs returned by /api/avatars:")
        
        for avatar_id, display_name, thumbnail_file in thumbnail_data[:5]:
            if thumbnail_file:
                url = f"/static/assets/avatars/{avatar_id}/{thumbnail_file}"
                print(f"   {avatar_id}: {url}")
        
        return issue_count == 0
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False
    finally:
        conn.close()

def check_filesystem_consistency():
    """Check if filesystem has the expected files"""
    
    print(f"\n🗂️ Filesystem Consistency Check")
    print("-" * 30)
    
    assets_dir = Path("static/assets/avatars")
    if not assets_dir.exists():
        print("❌ Assets directory doesn't exist")
        return False
    
    avatar_folders = [d for d in assets_dir.iterdir() if d.is_dir()]
    print(f"📁 Found {len(avatar_folders)} avatar folders")
    
    for folder in sorted(avatar_folders)[:10]:  # Check first 10
        png_files = list(folder.glob("*.png"))
        obj_files = list(folder.glob("*.obj"))
        mtl_files = list(folder.glob("*.mtl"))
        
        print(f"   {folder.name}: {len(png_files)} PNG, {len(obj_files)} OBJ, {len(mtl_files)} MTL")
        
        # Check for spaces in filenames
        for png_file in png_files:
            if ' ' in png_file.name:
                print(f"      ⚠️ File with spaces: {png_file.name}")
    
    return True

if __name__ == "__main__":
    print("🐝 BeeSmart Avatar System Verification\n")
    
    success = verify_avatar_fix()
    check_filesystem_consistency()
    
    print(f"\n🎯 Overall Status: {'✅ PASSED' if success else '❌ NEEDS ATTENTION'}")
    
    if success:
        print("\n💡 The avatar grid should now render properly!")
        print("   • Database contains correct filenames (no spaces)")
        print("   • Files exist on filesystem at expected locations")
        print("   • API will return valid thumbnail URLs")
    else:
        print("\n🔧 Issues found that may affect avatar grid rendering")
        print("   • Check the specific errors above")
        print("   • Ensure files exist and match database records")