"""
Upload GLB Avatar Files to Railway PostgreSQL
Stores avatar 3D models in the database for CDN-free deployment
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from flask import Flask
from config import get_config
from models import db, Avatar


def add_glb_columns_to_avatar(app):
    """Add glb_data and glb_file_size columns to Avatar table if they don't exist"""
    with app.app_context():
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('avatars')]
        
        if 'glb_data' not in columns or 'glb_file_size' not in columns:
            print("Adding glb_data and glb_file_size columns to avatars table...")
            try:
                # SQLite/PostgreSQL compatible ALTER TABLE
                with db.engine.connect() as conn:
                    if 'glb_data' not in columns:
                        conn.execute(db.text("ALTER TABLE avatars ADD COLUMN glb_data BYTEA"))
                        conn.commit()
                    if 'glb_file_size' not in columns:
                        conn.execute(db.text("ALTER TABLE avatars ADD COLUMN glb_file_size INTEGER"))
                        conn.commit()
                print("✅ Columns added successfully")
            except Exception as e:
                print(f"⚠️  Column addition note: {e}")
                print("   (May already exist or need manual migration)")
        else:
            print("✅ GLB columns already exist in avatars table")


def upload_avatar_files(app, avatar_dir):
    """Upload all GLB avatar files from directory to database"""
    avatar_path = Path(avatar_dir)
    
    if not avatar_path.exists():
        print(f"❌ Avatar directory not found: {avatar_dir}")
        return False
    
    glb_files = list(avatar_path.glob('*.glb'))
    
    if not glb_files:
        print(f"❌ No .glb files found in {avatar_dir}")
        return False
    
    print(f"\n📁 Found {len(glb_files)} GLB avatar files")
    print("=" * 60)
    
    with app.app_context():
        uploaded = 0
        updated = 0
        errors = 0
        skipped = 0
        
        for glb_file in glb_files:
            file_name = glb_file.stem  # Filename without extension (e.g., 'CoolBee')
            
            # Convert filename to slug format (e.g., 'CoolBee' -> 'cool-bee')
            # Handle special cases from avatar catalog
            slug_map = {
                'AlBee': 'al-bee',
                'AnxiousBee': 'anxious-bee',
                'BrotherBee': 'brother-bee',
                'BudaBee': 'buda-bee',
                'BuilderBee': 'builder-bee',
                'BuzzBee': 'buzz-bee',
                'CoolBee': 'cool-bee',
                'CutieBee': 'cutie-bee',
                'DetectiveBee': 'detective-bee',
                'DivaBee': 'diva-bee',
                'DoctorBee': 'doctor-bee',
                'ExplorerBee': 'explorer-bee',
                'FrankenBee': 'franken-bee',
                'GamerBee': 'gamer-bee',
                'HoneyComb': 'honey-comb',
                'InventorBee': 'inventor-bee',
                'JRockBee': 'j-rock-bee',
                'KnightBee': 'knight-bee',
                'LumberjackBee': 'lumberjack-bee',
                'MascotBee': 'mascot-bee',
                'MonsterBee': 'monster-bee',
                'MotorBee': 'motor-bee',
                'NurseBee': 'nurse-bee',
                'OBee': 'o-bee',
                'PlumberBee': 'plumber-bee',
                'ProfessorBee': 'professor-bee',
                'QueenBee': 'queen-bee',
                'RoboBee': 'robo-bee',
                'RockerBee': 'rocker-bee',
                'SeaBee': 'sea-bee',
                'SelfieBee': 'selfie-bee',
                'SingerBee': 'singer-bee',
                'SpaceBee': 'space-bee',
                'SuperBee': 'super-bee',
                'TechnoBee': 'techno-bee',
                'UmpireBee': 'umpire-bee',
                'VampBee': 'vamp-bee',
                'WareBee': 'ware-bee',
                'XrayBee': 'xray-bee',
                'YetiBee': 'yeti-bee',
                'ZomBee': 'zom-bee'
            }
            
            slug = slug_map.get(file_name)
            
            if not slug:
                print(f"⚠️  Unknown avatar: {file_name} - skipping")
                skipped += 1
                continue
            
            try:
                # Find avatar by slug
                avatar = Avatar.query.filter_by(slug=slug).first()
                
                if not avatar:
                    print(f"⚠️  Avatar not found in DB: {slug} ({file_name}.glb) - skipping")
                    skipped += 1
                    continue
                
                # Read file data
                with open(glb_file, 'rb') as f:
                    file_data = f.read()
                
                file_size = len(file_data)
                
                # Update avatar with GLB data
                if avatar.glb_data:
                    avatar.glb_data = file_data
                    avatar.glb_file_size = file_size
                    print(f"🔄 Updated: {slug:20s} ({file_size:,} bytes)")
                    updated += 1
                else:
                    avatar.glb_data = file_data
                    avatar.glb_file_size = file_size
                    print(f"✅ Uploaded: {slug:20s} ({file_size:,} bytes)")
                    uploaded += 1
                
                db.session.commit()
                
            except Exception as e:
                print(f"❌ Error uploading {file_name}: {e}")
                db.session.rollback()
                errors += 1
        
        print("\n" + "=" * 60)
        print(f"📊 Summary:")
        print(f"   New uploads: {uploaded}")
        print(f"   Updated:     {updated}")
        print(f"   Skipped:     {skipped}")
        print(f"   Errors:      {errors}")
        print(f"   Total files: {len(glb_files)}")
        
        return errors == 0


def verify_uploads(app):
    """Verify avatar GLB uploads"""
    with app.app_context():
        print("\n🔍 Verifying uploads...")
        print("=" * 60)
        
        avatars_with_glb = Avatar.query.filter(Avatar.glb_data.isnot(None)).all()
        total_avatars = Avatar.query.count()
        
        print(f"✅ {len(avatars_with_glb)} of {total_avatars} avatars have GLB data")
        
        if avatars_with_glb:
            total_size = sum(a.glb_file_size or 0 for a in avatars_with_glb)
            print(f"📦 Total GLB data size: {total_size:,} bytes ({total_size / 1024 / 1024:.1f} MB)")
            
            print(f"\n📋 Avatars with GLB data:")
            for avatar in sorted(avatars_with_glb, key=lambda x: x.slug):
                size_mb = (avatar.glb_file_size or 0) / 1024 / 1024
                print(f"   {avatar.slug:20s} - {size_mb:6.1f} MB - {avatar.name}")
        
        return len(avatars_with_glb) > 0


def main():
    """Main upload script"""
    print("🐝 BeeSmart Avatar Asset Uploader")
    print("=" * 60)
    
    # Create minimal Flask app
    app = Flask(__name__)
    app.config.from_object(get_config())
    db.init_app(app)
    
    # Avatar directory
    avatar_dir = 'static/assets/avatars/glb_files'
    
    if not os.path.exists(avatar_dir):
        print(f"❌ Avatar directory not found: {avatar_dir}")
        return 1
    
    # Add GLB columns if needed
    add_glb_columns_to_avatar(app)
    
    # Upload avatar files
    success = upload_avatar_files(app, avatar_dir)
    
    if not success:
        print("\n❌ Upload failed with errors")
        return 1
    
    # Verify uploads
    verify_uploads(app)
    
    print("\n✅ Avatar upload complete!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
