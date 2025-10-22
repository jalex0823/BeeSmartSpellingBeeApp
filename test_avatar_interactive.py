#!/usr/bin/env python3
"""
Interactive Avatar System Test
Test avatar loading and generation in real-time
"""

import os
import json
from avatar_catalog import get_avatar_info, get_avatar_catalog, validate_avatar

def test_avatar_generation():
    """Interactive test for avatar generation"""
    print("🎯 Interactive Avatar Generation Test")
    print("=" * 50)
    
    # Get all available avatars
    catalog = get_avatar_catalog()
    print(f"📊 Available avatars: {len(catalog)}")
    
    # Display avatar options
    print("\n🐝 Available Avatars:")
    for i, avatar in enumerate(catalog, 1):
        print(f"{i:2d}. {avatar['name']} ({avatar['id']}) - {avatar['description'][:50]}...")
    
    # Test a few random avatars
    test_avatars = ['professor-bee', 'queen-bee', 'robo-bee', 'mascot-bee']
    
    print(f"\n🧪 Testing Sample Avatars...")
    for avatar_id in test_avatars:
        print(f"\n--- Testing {avatar_id} ---")
        
        # Validate avatar
        is_valid, reason = validate_avatar(avatar_id)
        print(f"Validation: {'✅' if is_valid else '❌'} {reason if reason else 'Valid'}")
        
        if is_valid:
            # Get avatar info from catalog directly
            from avatar_catalog import AVATAR_CATALOG
            avatar_data = next((a for a in AVATAR_CATALOG if a['id'] == avatar_id), None)
            
            if avatar_data:
                print(f"Name: {avatar_data['name']}")
                print(f"Category: {avatar_data['category']}")
                print(f"Files: OBJ={avatar_data['obj_file']}, MTL={avatar_data['mtl_file']}, Texture={avatar_data['texture_file']}")
                
                # Check if files exist
                folder_path = f"static/Avatars/3D Avatar Files/{avatar_data['folder']}"
                files_exist = []
                for file_type, filename in [
                    ('OBJ', avatar_data['obj_file']),
                    ('MTL', avatar_data['mtl_file']), 
                    ('Texture', avatar_data['texture_file']),
                    ('Thumbnail', avatar_data['obj_file'].replace('.obj', '!.png'))
                ]:
                    file_path = os.path.join(folder_path, filename)
                    exists = os.path.exists(file_path)
                    files_exist.append(exists)
                    print(f"  {file_type}: {'✅' if exists else '❌'} {filename}")
                
                if all(files_exist):
                    print(f"✅ {avatar_id}: Ready for 3D rendering!")
                else:
                    print(f"❌ {avatar_id}: Missing files - cannot render")
                    
                # Test the API URLs too
                info = get_avatar_info(avatar_id)
                print(f"API URLs:")
                print(f"  Model OBJ: {info['model_obj_url']}")
                print(f"  Model MTL: {info['model_mtl_url']}")
                print(f"  Texture: {info['texture_url']}")
                print(f"  Thumbnail: {info['thumbnail_url']}")
    
    print(f"\n🎉 Avatar generation test complete!")

def show_avatar_statistics():
    """Show detailed avatar system statistics"""
    print("\n📊 Avatar System Statistics")
    print("=" * 40)
    
    catalog = get_avatar_catalog()
    
    # Category breakdown
    categories = {}
    for avatar in catalog:
        cat = avatar.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"📈 Avatars by Category:")
    for category, count in categories.items():
        print(f"  {category.title()}: {count} avatars")
    
    # File size analysis
    total_size = 0
    file_counts = {'obj': 0, 'mtl': 0, 'png': 0, 'thumbnail': 0}
    
    for avatar in catalog:
        folder_path = f"static/Avatars/3D Avatar Files/{avatar['folder']}"
        
        files_to_check = [
            (avatar['obj_file'], 'obj'),
            (avatar['mtl_file'], 'mtl'),
            (avatar['texture_file'], 'png'),
            (avatar['obj_file'].replace('.obj', '!.png'), 'thumbnail')
        ]
        
        for filename, file_type in files_to_check:
            file_path = os.path.join(folder_path, filename)
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                total_size += size
                file_counts[file_type] += 1
    
    print(f"\n💾 Storage Analysis:")
    print(f"  Total size: {total_size / (1024*1024):.1f} MB")
    print(f"  Files: {sum(file_counts.values())} total")
    for file_type, count in file_counts.items():
        print(f"    {file_type.upper()}: {count} files")
    
    print(f"\n🎯 System Health: {'✅ Excellent' if len(catalog) > 15 else '⚠️ Needs attention'}")

if __name__ == "__main__":
    # Change to app directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    test_avatar_generation()
    show_avatar_statistics()