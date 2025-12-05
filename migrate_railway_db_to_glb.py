"""
Railway Database Migration: Update all avatar obj_file fields to GLB format
This script connects to Railway's PostgreSQL database and updates avatar records
"""
import os
import sys

# Railway DATABASE_URL is set as environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL environment variable not set")
    print("This script must be run on Railway or with Railway DATABASE_URL exported")
    sys.exit(1)

# Import after checking DATABASE_URL
from sqlalchemy import create_engine, text
from avatar_catalog import AVATAR_CATALOG

def migrate_railway_database():
    """Update Railway PostgreSQL database with GLB filenames"""
    print("=" * 70)
    print("🚀 RAILWAY DATABASE GLB MIGRATION")
    print("=" * 70)
    
    # Create engine for Railway PostgreSQL
    engine = create_engine(DATABASE_URL)
    
    # Create mapping from catalog
    catalog_map = {entry.get('id'): entry.get('obj_file') for entry in AVATAR_CATALOG}
    
    with engine.connect() as conn:
        # Get all avatars from Railway database
        result = conn.execute(text("SELECT id, slug, obj_file FROM avatars WHERE is_active = true"))
        db_avatars = result.fetchall()
        
        print(f"\n📊 Found {len(db_avatars)} active avatars in Railway database")
        print(f"📊 Found {len(AVATAR_CATALOG)} avatars in catalog\n")
        
        updates_needed = 0
        updates_made = 0
        
        for avatar in db_avatars:
            avatar_id, slug, current_obj_file = avatar
            
            # Get correct GLB filename from catalog
            catalog_obj_file = catalog_map.get(slug)
            
            if not catalog_obj_file:
                print(f"⚠️ No catalog entry for: {slug}")
                continue
            
            # Check if update needed
            if current_obj_file != catalog_obj_file:
                is_obj_to_glb = str(current_obj_file).endswith('.obj') and catalog_obj_file.endswith('.glb')
                marker = "🔄 OBJ→GLB" if is_obj_to_glb else "🔄 UPDATE"
                
                print(f"{marker} {slug:20s} | {current_obj_file:25s} → {catalog_obj_file}")
                
                # Update the database
                conn.execute(
                    text("UPDATE avatars SET obj_file = :new_file WHERE id = :avatar_id"),
                    {"new_file": catalog_obj_file, "avatar_id": avatar_id}
                )
                updates_needed += 1
            else:
                if catalog_obj_file.endswith('.glb'):
                    print(f"✅ OK       {slug:20s} | {catalog_obj_file}")
        
        # Commit changes
        if updates_needed > 0:
            conn.commit()
            updates_made = updates_needed
            print(f"\n✅ Successfully updated {updates_made} avatar records!")
        else:
            print("\n✅ No updates needed - all avatars already using GLB format!")
        
        print("\n" + "=" * 70)
        print("📊 MIGRATION SUMMARY")
        print("=" * 70)
        print(f"  Total avatars:     {len(db_avatars)}")
        print(f"  Updates made:      {updates_made}")
        print(f"  Already correct:   {len(db_avatars) - updates_made}")
        print("=" * 70)
        
        return updates_made

if __name__ == '__main__':
    try:
        updates = migrate_railway_database()
        print(f"\n✅ Railway database migration completed successfully!")
        print(f"🔄 Updated {updates} avatar records to GLB format")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
