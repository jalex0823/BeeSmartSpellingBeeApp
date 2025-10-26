#!/usr/bin/env python3
"""
Test script to debug avatar rendering issues
"""

from AjaSpellBApp import app, db
from models import Avatar
from avatar_catalog import AVATAR_CATALOG
import os
import json

def test_avatar_database():
    """Test if avatars are in the database"""
    print("🔍 Testing Avatar Database...")
    
    with app.app_context():
        try:
            # Check if Avatar table exists
            avatar_count = Avatar.query.count()
            print(f"📊 Total avatars in database: {avatar_count}")
            
            if avatar_count == 0:
                print("📦 No avatars found, populating from catalog...")
                # Populate avatars from catalog
                populate_avatars()
                avatar_count = Avatar.query.count()
                print(f"✅ Populated {avatar_count} avatars")
            
            # List all avatars
            avatars = Avatar.query.all()
            print(f"\n📋 Avatar List ({len(avatars)} total):")
            for avatar in avatars:
                print(f"  - {avatar.slug}: {avatar.name} (active: {avatar.is_active})")
                print(f"    📁 Folder: {avatar.folder_path}")
                print(f"    🖼️ Thumbnail: {avatar.thumbnail_file}")
                print()
            
            return avatars
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            import traceback
            traceback.print_exc()
            return []

def populate_avatars():
    """Populate avatars from catalog"""
    try:
        for avatar_data in AVATAR_CATALOG:
            # Get thumbnail filename
            from avatar_catalog import get_avatar_info
            avatar_info = get_avatar_info(avatar_data['id'])
            thumbnail_file = avatar_info.get('thumbnail_file', f"{avatar_data['name']}!.png")
            
            avatar = Avatar(
                slug=avatar_data['id'],
                name=avatar_data['name'],
                description=avatar_data.get('description', ''),
                category=avatar_data.get('category', 'classic'),
                folder_path=avatar_data['folder'],
                obj_file=avatar_data['obj_file'],
                mtl_file=avatar_data.get('mtl_file', ''),
                texture_file=avatar_data.get('texture_file', ''),
                thumbnail_file=thumbnail_file,
                is_active=True,
                sort_order=0
            )
            db.session.add(avatar)
        
        db.session.commit()
        print("✅ Avatars populated successfully")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error populating avatars: {e}")
        import traceback
        traceback.print_exc()

def test_avatar_files():
    """Test if avatar files exist on disk"""
    print("\n🔍 Testing Avatar Files...")
    
    base_path = "static/assets/avatars"
    
    if not os.path.exists(base_path):
        print(f"❌ Avatar directory doesn't exist: {base_path}")
        return
    
    # List all avatar directories
    avatar_dirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    print(f"📁 Found {len(avatar_dirs)} avatar directories:")
    
    for avatar_dir in sorted(avatar_dirs):
        dir_path = os.path.join(base_path, avatar_dir)
        files = os.listdir(dir_path)
        
        print(f"\n  📁 {avatar_dir}/")
        for file in sorted(files):
            print(f"    📄 {file}")
        
        # Check for required files
        has_obj = any(f.endswith('.obj') for f in files)
        has_mtl = any(f.endswith('.mtl') for f in files)
        has_texture = any(f.endswith('.png') and not f.endswith('!.png') for f in files)
        has_thumbnail = any(f.endswith('!.png') for f in files)
        
        print(f"    ✅ OBJ: {has_obj}, MTL: {has_mtl}, Texture: {has_texture}, Thumbnail: {has_thumbnail}")

def test_api_response():
    """Test the avatars API endpoint"""
    print("\n🔍 Testing API Response...")
    
    with app.test_client() as client:
        try:
            response = client.get('/api/avatars')
            print(f"📡 API Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"📊 API Response: {json.dumps(data, indent=2)}")
                
                if data.get('status') == 'success':
                    avatars = data.get('avatars', [])
                    print(f"✅ API returned {len(avatars)} avatars")
                    
                    for avatar in avatars[:3]:  # Show first 3
                        print(f"  🐝 {avatar.get('id')}: {avatar.get('name')}")
                        print(f"     Thumbnail: {avatar.get('thumbnail')}")
                        print(f"     URLs: {avatar.get('urls', {})}")
                else:
                    print(f"❌ API error: {data}")
            else:
                print(f"❌ API failed with status {response.status_code}")
                print(f"Response: {response.get_data(as_text=True)}")
                
        except Exception as e:
            print(f"❌ API test error: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Run all tests"""
    print("🐝 Avatar System Diagnostic Tool")
    print("=" * 50)
    
    # Test database
    avatars = test_avatar_database()
    
    # Test files
    test_avatar_files()
    
    # Test API
    test_api_response()
    
    print("\n" + "=" * 50)
    print("🐝 Diagnostic Complete")

if __name__ == "__main__":
    main()