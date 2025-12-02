#!/usr/bin/env python3
"""
Add Franken Bee avatar to the database
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from AjaSpellBApp import app, db
from models import Avatar
from datetime import datetime

def add_franken_bee():
    """Add Franken Bee avatar to the database"""
    
    print("=" * 70)
    print("Adding Franken Bee Avatar to Database")
    print("=" * 70)
    print()
    
    with app.app_context():
        # Check if already exists
        existing = Avatar.query.filter_by(slug='franken-bee').first()
        if existing:
            print(f"⚠️  Franken Bee already exists (ID: {existing.id})")
            print(f"   Active: {existing.is_active}")
            print(f"   Thumbnail: {existing.thumbnail_file}")
            
            # Update if needed
            if not existing.is_active:
                existing.is_active = True
                print("   ✅ Reactivated!")
            
            if existing.thumbnail_file != 'AvatarThumbnails/FrankenBee!.png':
                existing.thumbnail_file = 'AvatarThumbnails/FrankenBee!.png'
                print("   ✅ Updated thumbnail path!")
            
            db.session.commit()
            return True
        
        # Create new Franken Bee avatar
        franken_bee = Avatar(
            slug='franken-bee',
            name='Franken Bee',
            description="Created in Dr. Franken-sting's laboratory! Spells by lightning power. 'It's alive... and spelling!'",
            category='fantasy',
            folder_path='glb_files',
            obj_file='Frankenbee.glb',
            mtl_file=None,
            texture_file=None,
            thumbnail_file='AvatarThumbnails/FrankenBee!.png',
            unlock_level=5,
            points_required=25000,
            is_premium=True,
            sort_order=110,  # Place after other avatars
            is_active=True
        )
        
        db.session.add(franken_bee)
        db.session.commit()
        
        print("✅ Franken Bee avatar added successfully!")
        print()
        print(f"   ID: {franken_bee.id}")
        print(f"   Slug: {franken_bee.slug}")
        print(f"   Name: {franken_bee.name}")
        print(f"   Folder: {franken_bee.folder_path}")
        print(f"   GLB File: {franken_bee.obj_file}")
        print(f"   Thumbnail: {franken_bee.thumbnail_file}")
        print(f"   Unlock Points: {franken_bee.points_required}")
        print(f"   Is Premium: {franken_bee.is_premium}")
        print(f"   Is Active: {franken_bee.is_active}")
        print()
        
        # Verify the thumbnail file exists
        thumbnail_path = os.path.join('static/assets/avatars', franken_bee.folder_path, franken_bee.thumbnail_file)
        if os.path.exists(thumbnail_path):
            print(f"✅ Thumbnail file verified: {thumbnail_path}")
        else:
            print(f"⚠️  WARNING: Thumbnail file not found: {thumbnail_path}")
        
        # Verify the GLB file exists
        glb_path = os.path.join('static/assets/avatars', franken_bee.folder_path, franken_bee.obj_file)
        if os.path.exists(glb_path):
            print(f"✅ GLB file verified: {glb_path}")
        else:
            print(f"⚠️  WARNING: GLB file not found: {glb_path}")
        
        print()
        print("=" * 70)
        print("✅ Franken Bee is now available in the avatar picker!")
        print("=" * 70)
        
        return True

if __name__ == "__main__":
    try:
        success = add_franken_bee()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
