"""
Avatar Migration Script
Migrates avatar data from avatar_catalog.py to database avatars table
Run once to populate the avatars table with all 24 bee avatars
"""

from AjaSpellBApp import app, db
from models import Avatar
from avatar_catalog import AVATAR_CATALOG
from datetime import datetime


def populate_avatars_from_filesystem():
    """
    Populate avatars table from AVATAR_CATALOG
    Safe to call multiple times - skips if avatars already exist
    Returns: number of avatars populated
    """
    try:
        import os
        import glob
        
        # Check if avatars already exist
        existing_count = Avatar.query.count()
        if existing_count > 0:
            print(f"ℹ️  {existing_count} avatars already exist, skipping population")
            return existing_count
        
        print(f"📋 Starting avatar population from {len(AVATAR_CATALOG)} entries in AVATAR_CATALOG")
        
        # Migrate each avatar from AVATAR_CATALOG
        success_count = 0
        error_count = 0
        
        for idx, avatar_data in enumerate(AVATAR_CATALOG):
            try:
                # Extract data from catalog
                slug = avatar_data['id']
                name = avatar_data['name']
                folder = avatar_data['folder']
                obj_file = avatar_data['obj_file']
                mtl_file = avatar_data.get('mtl_file', '')
                texture_file = avatar_data.get('texture_file', '')
                description = avatar_data.get('description', '')
                category = avatar_data.get('category', 'classic')
                
                # Find thumbnail PNG file (look for any .png in folder)
                avatar_folder_path = os.path.join('static', 'assets', 'avatars', folder)
                
                # Check if folder exists
                if not os.path.exists(avatar_folder_path):
                    print(f"⚠️  Folder not found: {avatar_folder_path}, using default thumbnail")
                    thumbnail_file = 'thumbnail.png'
                else:
                    png_files = glob.glob(os.path.join(avatar_folder_path, '*.png'))
                    thumbnail_file = os.path.basename(png_files[0]) if png_files else 'thumbnail.png'
                
                # Create Avatar model instance
                avatar = Avatar(
                    slug=slug,
                    name=name,
                    description=description,
                    category=category,
                    folder_path=folder,
                    obj_file=obj_file,
                    mtl_file=mtl_file,
                    texture_file=texture_file,
                    thumbnail_file=thumbnail_file,
                    sort_order=idx,
                    unlock_level=0,
                    points_required=0,
                    is_premium=False,
                    is_active=True
                )
                
                db.session.add(avatar)
                success_count += 1
                print(f"  ✓ Added: {name} ({slug})")
                
            except Exception as e:
                error_count += 1
                print(f"  ✗ Error migrating {avatar_data.get('id', 'unknown')}: {e}")
        
        # Commit all at once
        if success_count > 0:
            db.session.commit()
            print(f"✅ Successfully populated {success_count} avatars from filesystem")
            if error_count > 0:
                print(f"⚠️  {error_count} avatars had errors")
        else:
            print(f"❌ No avatars were added")
            
        return success_count
        
    except Exception as e:
        import traceback
        print(f"❌ Population failed: {e}")
        print(traceback.format_exc())
        db.session.rollback()
        return 0


def migrate_avatars():
    """Migrate AVATAR_CATALOG to database avatars table"""
    
    with app.app_context():
        print("🐝 BeeSmart Avatar Migration")
        print("=" * 60)
        
        # Check if avatars already exist
        existing_count = Avatar.query.count()
        if existing_count > 0:
            print(f"⚠️  Found {existing_count} existing avatars in database")
            response = input("Delete and recreate all avatars? (yes/no): ")
            if response.lower() != 'yes':
                print("❌ Migration cancelled")
                return
            
            # Delete all existing avatars
            Avatar.query.delete()
            db.session.commit()
            print(f"🗑️  Deleted {existing_count} existing avatars")
        
        # Migrate each avatar from AVATAR_CATALOG
        success_count = 0
        error_count = 0
        
        for idx, avatar_data in enumerate(AVATAR_CATALOG):
            try:
                # Extract data from catalog
                slug = avatar_data['id']
                name = avatar_data['name']
                folder = avatar_data['folder']
                obj_file = avatar_data['obj_file']
                mtl_file = avatar_data.get('mtl_file', '')
                texture_file = avatar_data.get('texture_file', '')
                description = avatar_data.get('description', '')
                category = avatar_data.get('category', 'classic')
                
                # Create thumbnail filename (look for existing PNG files)
                thumbnail = f"{slug}-thumb.png"  # Default
                
                # Create Avatar model instance
                avatar = Avatar(
                    slug=slug,
                    name=name,
                    description=description,
                    category=category,
                    folder_path=folder,
                    obj_file=obj_file,
                    mtl_file=mtl_file,
                    texture_file=texture_file,
                    thumbnail_file=thumbnail,
                    unlock_level=1,  # All avatars unlocked by default
                    points_required=0,
                    is_premium=False,
                    sort_order=idx,  # Preserve catalog order
                    is_active=True
                )
                
                db.session.add(avatar)
                success_count += 1
                print(f"✅ {success_count:2d}. {name:20s} ({slug})")
                
            except Exception as e:
                error_count += 1
                print(f"❌ Error migrating {avatar_data.get('id', 'unknown')}: {e}")
        
        # Commit all changes
        try:
            db.session.commit()
            print("\n" + "=" * 60)
            print(f"🎉 Migration Complete!")
            print(f"   ✅ Successfully migrated: {success_count}")
            print(f"   ❌ Errors: {error_count}")
            print(f"   📊 Total avatars in database: {Avatar.query.count()}")
            
            # Show sample avatars
            print("\n📋 Sample avatars:")
            samples = Avatar.query.limit(5).all()
            for avatar in samples:
                print(f"   - {avatar.name} ({avatar.slug}) - Category: {avatar.category}")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Migration failed during commit: {e}")
            return False
        
        return True


def verify_migration():
    """Verify migration was successful"""
    
    with app.app_context():
        print("\n🔍 Verifying Migration")
        print("=" * 60)
        
        total = Avatar.query.count()
        print(f"Total avatars: {total}")
        
        # Check categories
        categories = db.session.query(Avatar.category, db.func.count(Avatar.id))\
            .group_by(Avatar.category).all()
        print("\n📊 Avatars by category:")
        for category, count in categories:
            print(f"   {category:15s}: {count}")
        
        # Check that all catalog IDs are in database
        catalog_ids = {a['id'] for a in AVATAR_CATALOG}
        db_slugs = {a.slug for a in Avatar.query.all()}
        
        missing = catalog_ids - db_slugs
        extra = db_slugs - catalog_ids
        
        if missing:
            print(f"\n⚠️  Missing from database: {missing}")
        if extra:
            print(f"\n⚠️  Extra in database: {extra}")
        
        if not missing and not extra:
            print("\n✅ All catalog avatars migrated successfully!")
        
        # Test get_by_slug
        print("\n🧪 Testing Avatar.get_by_slug('cool-bee'):")
        cool_bee = Avatar.get_by_slug('cool-bee')
        if cool_bee:
            print(f"   ✅ Found: {cool_bee.name}")
            print(f"   📂 Folder: {cool_bee.folder_path}")
            print(f"   🎨 OBJ: {cool_bee.obj_file}")
        else:
            print("   ❌ Not found")


if __name__ == '__main__':
    print("\n" + "🐝" * 30)
    print("BeeSmart Avatar Database Migration")
    print("🐝" * 30 + "\n")
    
    # Run migration
    if migrate_avatars():
        # Verify results
        verify_migration()
    else:
        print("\n❌ Migration failed")
