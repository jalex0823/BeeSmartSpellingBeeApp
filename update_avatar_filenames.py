"""
Update Avatar Filenames Script
Updates existing avatars in database with corrected OBJ/MTL filenames from avatar_catalog.py
Run this after fixing avatar_catalog.py to update the database
"""

from AjaSpellBApp import app, db
from models import Avatar
from avatar_catalog import AVATAR_CATALOG


def update_avatar_filenames():
    """
    Update all existing avatars with corrected filenames from AVATAR_CATALOG
    """
    with app.app_context():
        try:
            print("🔧 Updating avatar filenames in database from AVATAR_CATALOG...")
            
            updated_count = 0
            error_count = 0
            
            for avatar_data in AVATAR_CATALOG:
                try:
                    slug = avatar_data['id']
                    
                    # Find existing avatar in database
                    avatar = Avatar.query.filter_by(slug=slug).first()
                    
                    if not avatar:
                        print(f"  ⚠️  Avatar not found in DB: {slug}")
                        error_count += 1
                        continue
                    
                    # Update filenames from catalog
                    old_obj = avatar.obj_file
                    old_mtl = avatar.mtl_file
                    old_texture = avatar.texture_file
                    
                    avatar.obj_file = avatar_data['obj_file']
                    avatar.mtl_file = avatar_data.get('mtl_file', '')
                    avatar.texture_file = avatar_data.get('texture_file', '')
                    
                    # Check if anything changed
                    if (old_obj != avatar.obj_file or 
                        old_mtl != avatar.mtl_file or 
                        old_texture != avatar.texture_file):
                        
                        print(f"  ✓ Updated: {avatar.name} ({slug})")
                        print(f"    OBJ: {old_obj} → {avatar.obj_file}")
                        print(f"    MTL: {old_mtl} → {avatar.mtl_file}")
                        print(f"    TEX: {old_texture} → {avatar.texture_file}")
                        updated_count += 1
                    else:
                        print(f"  ✓ No changes needed: {avatar.name} ({slug})")
                
                except Exception as e:
                    error_count += 1
                    print(f"  ✗ Error updating {avatar_data.get('id', 'unknown')}: {e}")
            
            # Commit all changes
            if updated_count > 0:
                db.session.commit()
                print(f"\n✅ Successfully updated {updated_count} avatars")
            else:
                print(f"\nℹ️  No avatars needed updating")
                
            if error_count > 0:
                print(f"⚠️  {error_count} avatars had errors")
                
            return updated_count
            
        except Exception as e:
            import traceback
            print(f"\n❌ Update failed: {e}")
            print(traceback.format_exc())
            db.session.rollback()
            return 0


if __name__ == '__main__':
    update_avatar_filenames()
