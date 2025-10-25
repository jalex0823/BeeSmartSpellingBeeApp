#!/usr/bin/env python3
"""
🐝 Add BeeDiva Avatar to Database
Script to add the new BeeDiva avatar to the avatar system
"""

from AjaSpellBApp import app, db
from models import Avatar
from datetime import datetime

def add_bee_diva():
    """Add BeeDiva avatar to the database"""
    
    with app.app_context():
        # Check if BeeDiva already exists
        existing = Avatar.get_by_slug('bee-diva')
        if existing:
            print("✅ BeeDiva avatar already exists in database")
            print(f"   ID: {existing.slug}")
            print(f"   Name: {existing.name}")
            return
        
        # Get current max sort_order to add BeeDiva at the end
        max_sort = db.session.query(db.func.max(Avatar.sort_order)).scalar() or 0
        
        # Create BeeDiva avatar entry
        bee_diva = Avatar(
            slug='bee-diva',
            name='Bee Diva',
            description='A glamorous queen bee with royal style and elegance',
            category='classic',
            folder_path='bee-diva',
            obj_file='BeeDiva.obj',
            mtl_file='BeeDiva.mtl',
            texture_file='BeeDiva.png',
            thumbnail_file='BeeDiva!.png',  # The thumbnail is always the PNG with !
            unlock_level=1,  # Available to all users
            points_required=0,
            is_premium=False,
            sort_order=max_sort + 1,
            is_active=True
        )
        
        try:
            # Add to database
            db.session.add(bee_diva)
            db.session.commit()
            
            print("🎉 Successfully added BeeDiva avatar!")
            print(f"   ✅ Slug: {bee_diva.slug}")
            print(f"   ✅ Name: {bee_diva.name}")
            print(f"   ✅ Folder: {bee_diva.folder_path}")
            print(f"   ✅ OBJ File: {bee_diva.obj_file}")
            print(f"   ✅ MTL File: {bee_diva.mtl_file}")
            print(f"   ✅ Texture: {bee_diva.texture_file}")
            print(f"   ✅ Thumbnail: {bee_diva.thumbnail_file}")
            print(f"   ✅ Sort Order: {bee_diva.sort_order}")
            
            # Verify the addition
            total_avatars = Avatar.query.filter_by(is_active=True).count()
            print(f"\n📊 Total active avatars in database: {total_avatars}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding BeeDiva: {e}")
            return False
            
        return True

if __name__ == '__main__':
    print("🐝 BeeSmart Avatar System - Adding BeeDiva")
    print("=" * 50)
    success = add_bee_diva()
    if success:
        print("=" * 50)
        print("✨ BeeDiva is ready for avatar selection!")
    else:
        print("=" * 50)
        print("❌ Failed to add BeeDiva. Check the error above.")