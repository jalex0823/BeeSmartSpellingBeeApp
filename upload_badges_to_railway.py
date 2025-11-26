"""
Upload GLB Badge Files to Railway PostgreSQL
Stores badge 3D models in the database for CDN-free deployment
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from flask import Flask
from config import get_config
from models import db, BadgeAsset


def create_badge_assets_table(app):
    """Create badge_assets table if it doesn't exist"""
    with app.app_context():
        # Check if table exists
        inspector = db.inspect(db.engine)
        if 'badge_assets' not in inspector.get_table_names():
            print("Creating badge_assets table...")
            BadgeAsset.__table__.create(db.engine)
            print("✅ Table created successfully")
        else:
            print("✅ Table badge_assets already exists")


def upload_badge_files(app, badge_dir):
    """Upload all GLB badge files from directory to database"""
    badge_path = Path(badge_dir)
    
    if not badge_path.exists():
        print(f"❌ Badge directory not found: {badge_dir}")
        return False
    
    glb_files = list(badge_path.glob('*.glb'))
    
    if not glb_files:
        print(f"❌ No .glb files found in {badge_dir}")
        return False
    
    print(f"\n📁 Found {len(glb_files)} GLB badge files")
    print("=" * 60)
    
    with app.app_context():
        uploaded = 0
        skipped = 0
        errors = 0
        
        for glb_file in glb_files:
            badge_name = glb_file.stem  # Filename without extension
            file_name = glb_file.name
            
            try:
                # Check if already exists
                existing = BadgeAsset.query.filter_by(badge_name=badge_name).first()
                
                # Read file data
                with open(glb_file, 'rb') as f:
                    file_data = f.read()
                
                file_size = len(file_data)
                
                if existing:
                    # Update existing record
                    existing.file_data = file_data
                    existing.file_size = file_size
                    existing.uploaded_at = datetime.utcnow()
                    print(f"🔄 Updated: {badge_name:20s} ({file_size:,} bytes)")
                    skipped += 1
                else:
                    # Create new record
                    badge_asset = BadgeAsset(
                        badge_name=badge_name,
                        file_name=file_name,
                        file_data=file_data,
                        file_size=file_size,
                        mime_type='model/gltf-binary'
                    )
                    db.session.add(badge_asset)
                    print(f"✅ Uploaded: {badge_name:20s} ({file_size:,} bytes)")
                    uploaded += 1
                
                db.session.commit()
                
            except Exception as e:
                print(f"❌ Error uploading {file_name}: {e}")
                db.session.rollback()
                errors += 1
        
        print("\n" + "=" * 60)
        print(f"📊 Summary:")
        print(f"   New uploads: {uploaded}")
        print(f"   Updated:     {skipped}")
        print(f"   Errors:      {errors}")
        print(f"   Total:       {len(glb_files)}")
        
        return errors == 0


def verify_uploads(app):
    """Verify all badge files were uploaded successfully"""
    expected_badges = [
        'Novice', 'Apprentice', 'Scholar', 
        'Elite', 'Magistrate', 'BuzzDustMaster'
    ]
    
    with app.app_context():
        print("\n🔍 Verifying uploads...")
        print("=" * 60)
        
        all_badges = BadgeAsset.query.all()
        badge_names = {badge.badge_name for badge in all_badges}
        
        missing = set(expected_badges) - badge_names
        extra = badge_names - set(expected_badges)
        
        if missing:
            print(f"⚠️  Missing badges: {missing}")
        
        if extra:
            print(f"ℹ️  Extra badges: {extra}")
        
        if not missing:
            print(f"✅ All {len(expected_badges)} required badges uploaded")
        
        print(f"\n📋 Database contents ({len(all_badges)} badges):")
        for badge in sorted(all_badges, key=lambda x: x.badge_name):
            print(f"   {badge.badge_name:20s} - {badge.file_size:,} bytes - {badge.uploaded_at.strftime('%Y-%m-%d %H:%M')}")
        
        return len(missing) == 0


def main():
    """Main upload script"""
    print("🐝 BeeSmart Badge Asset Uploader")
    print("=" * 60)
    
    # Create minimal Flask app
    app = Flask(__name__)
    app.config.from_object(get_config())
    db.init_app(app)
    
    # Badge directories to check (in priority order)
    badge_dirs = [
        'static/assets/badges/glb_files',  # Primary location
        'Badges',  # Alternative location
    ]
    
    # Find first existing directory
    badge_dir = None
    for dir_path in badge_dirs:
        if os.path.exists(dir_path):
            badge_dir = dir_path
            print(f"📂 Using badge directory: {badge_dir}")
            break
    
    if not badge_dir:
        print(f"❌ No badge directory found. Tried:")
        for dir_path in badge_dirs:
            print(f"   - {dir_path}")
        return 1
    
    try:
        # Step 1: Create table
        create_badge_assets_table(app)
        
        # Step 2: Upload files
        success = upload_badge_files(app, badge_dir)
        
        if not success:
            print("\n❌ Upload failed")
            return 1
        
        # Step 3: Verify
        verified = verify_uploads(app)
        
        if verified:
            print("\n✅ All badges successfully uploaded to Railway PostgreSQL!")
            print("\nNext steps:")
            print("1. Add BadgeAsset model to models.py")
            print("2. Create /api/badges/<badge_name> endpoint to serve GLB files")
            print("3. Update badge-3d-renderer.js to fetch from database")
            return 0
        else:
            print("\n⚠️  Upload completed but some badges are missing")
            return 1
            
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
