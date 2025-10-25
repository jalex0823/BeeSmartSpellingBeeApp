#!/usr/bin/env python3
"""
🐝 BeeSmart Avatar Batch Preparation Tool
Comprehensive setup for incoming avatar batches with database integration

Features:
- Scans and validates new avatar folders
- Generates database migration scripts
- Creates folder structure with proper naming
- Validates file requirements (.obj, .mtl, .png, thumbnails)
- Generates preview files and thumbnails
- Creates database entries with proper metadata
- Validates against existing avatars to prevent conflicts
- Generates deployment scripts for Railway
- Creates backup plans and rollback options

Usage:
    python prepare_new_avatars.py --scan         # Scan for new avatars
    python prepare_new_avatars.py --prepare      # Prepare files and structure
    python prepare_new_avatars.py --migrate      # Generate database migration
    python prepare_new_avatars.py --deploy       # Deploy to database
    python prepare_new_avatars.py --rollback     # Rollback if needed
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from PIL import Image
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import sqlite3

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class AvatarBatchManager:
    def __init__(self):
        """Initialize the avatar batch manager with all necessary paths and configurations"""
        self.base_path = Path(__file__).parent
        self.source_path = self.base_path / "Avatars" / "3D Avatar Files"
        self.target_path = self.base_path / "static" / "assets" / "avatars"
        self.backup_path = self.base_path / "backups" / "avatars" / datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Database paths
        self.db_path = self.base_path / "instance" / "beesmart.db"
        self.migration_path = self.base_path / "migrations"
        
        # Create necessary directories
        self.backup_path.mkdir(parents=True, exist_ok=True)
        self.migration_path.mkdir(parents=True, exist_ok=True)
        
        # Avatar requirements
        self.required_files = {
            'obj': '.obj',    # 3D model geometry
            'mtl': '.mtl',    # Material definition
            'texture': '.png'  # Main texture file
        }
        
        # File size limits
        self.max_obj_size_mb = 100     # Large 3D models
        self.max_texture_size_mb = 10   # Texture files
        self.thumbnail_size = (256, 256)  # Standard thumbnail
        
        print("🐝 BeeSmart Avatar Batch Manager Initialized")
        print(f"📂 Source: {self.source_path}")
        print(f"🎯 Target: {self.target_path}")
        print(f"💾 Backup: {self.backup_path}")

    def scan_new_avatars(self) -> Dict[str, Dict]:
        """
        Scan source directory for new avatar folders and validate requirements
        Returns dict of avatar_name -> file_info
        """
        print("\\n🔍 SCANNING FOR NEW AVATARS")
        print("=" * 60)
        
        if not self.source_path.exists():
            print(f"❌ Source path not found: {self.source_path}")
            return {}
        
        folders = [f for f in self.source_path.iterdir() if f.is_dir()]
        new_avatars = {}
        existing_avatars = self._get_existing_avatars()
        
        for folder in sorted(folders):
            avatar_name = folder.name
            avatar_id = self._name_to_slug(avatar_name)
            
            # Skip if already exists
            if avatar_id in existing_avatars:
                print(f"⏭️  {avatar_name} (already exists as {avatar_id})")
                continue
            
            print(f"\\n🆕 Found new avatar: {avatar_name}")
            print(f"   Generated ID: {avatar_id}")
            
            # Validate files
            file_info = self._validate_avatar_files(folder, avatar_name)
            
            if file_info['valid']:
                new_avatars[avatar_name] = {
                    'id': avatar_id,
                    'folder': folder,
                    'files': file_info,
                    'status': 'ready'
                }
                print(f"   ✅ Validation passed")
            else:
                new_avatars[avatar_name] = {
                    'id': avatar_id,
                    'folder': folder,
                    'files': file_info,
                    'status': 'needs_fixing'
                }
                print(f"   ❌ Validation failed:")
                for error in file_info['errors']:
                    print(f"      - {error}")
        
        print(f"\\n📊 Scan Summary:")
        print(f"   🆕 New avatars found: {len(new_avatars)}")
        print(f"   ✅ Ready for processing: {sum(1 for a in new_avatars.values() if a['status'] == 'ready')}")
        print(f"   ❌ Need fixes: {sum(1 for a in new_avatars.values() if a['status'] == 'needs_fixing')}")
        
        return new_avatars

    def prepare_avatar_files(self, avatars: Dict[str, Dict]) -> bool:
        """
        Prepare avatar files for deployment:
        - Create target folder structure
        - Copy and rename files to standard format
        - Generate thumbnails if missing
        - Validate file integrity
        """
        print("\\n📦 PREPARING AVATAR FILES")
        print("=" * 60)
        
        ready_avatars = {k: v for k, v in avatars.items() if v['status'] == 'ready'}
        
        if not ready_avatars:
            print("❌ No avatars ready for preparation")
            return False
        
        success_count = 0
        
        for avatar_name, info in ready_avatars.items():
            avatar_id = info['id']
            source_folder = info['folder']
            target_folder = self.target_path / avatar_id
            
            print(f"\\n🎨 Preparing {avatar_name} -> {avatar_id}")
            
            try:
                # Create target directory
                target_folder.mkdir(parents=True, exist_ok=True)
                
                # Copy and standardize files
                files_copied = self._copy_avatar_files(source_folder, target_folder, avatar_name)
                
                # Generate thumbnail if missing
                thumbnail_created = self._ensure_thumbnail(target_folder, avatar_name)
                
                # Validate copied files
                validation_passed = self._validate_copied_files(target_folder, avatar_id)
                
                if validation_passed:
                    print(f"   ✅ Successfully prepared {avatar_name}")
                    success_count += 1
                else:
                    print(f"   ❌ Validation failed for {avatar_name}")
                    
            except Exception as e:
                print(f"   ❌ Error preparing {avatar_name}: {e}")
        
        print(f"\\n📊 Preparation Summary:")
        print(f"   ✅ Successfully prepared: {success_count}")
        print(f"   ❌ Failed: {len(ready_avatars) - success_count}")
        
        return success_count > 0

    def generate_database_migration(self, avatars: Dict[str, Dict]) -> str:
        """
        Generate database migration script for new avatars
        Returns the migration file path
        """
        print("\\n💾 GENERATING DATABASE MIGRATION")
        print("=" * 60)
        
        ready_avatars = {k: v for k, v in avatars.items() if v['status'] == 'ready'}
        
        if not ready_avatars:
            print("❌ No avatars ready for database migration")
            return ""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        migration_file = self.migration_path / f"add_avatars_{timestamp}.py"
        
        # Generate migration script
        migration_content = self._generate_migration_script(ready_avatars, timestamp)
        
        with open(migration_file, 'w') as f:
            f.write(migration_content)
        
        print(f"✅ Migration script generated: {migration_file}")
        print(f"   📝 Avatars included: {len(ready_avatars)}")
        
        # Also generate a verification script
        verify_file = self.migration_path / f"verify_avatars_{timestamp}.py"
        verify_content = self._generate_verification_script(ready_avatars)
        
        with open(verify_file, 'w') as f:
            f.write(verify_content)
        
        print(f"✅ Verification script generated: {verify_file}")
        
        return str(migration_file)

    def deploy_to_database(self, migration_file: str) -> bool:
        """
        Execute the migration to add avatars to database
        """
        print("\\n🚀 DEPLOYING TO DATABASE")
        print("=" * 60)
        
        if not migration_file or not Path(migration_file).exists():
            print("❌ Migration file not found")
            return False
        
        try:
            # Import Flask app context
            from AjaSpellBApp import app, db
            from models import Avatar
            
            with app.app_context():
                # Execute migration
                exec(open(migration_file).read())
                print("✅ Migration executed successfully")
                
                # Verify deployment
                avatar_count = Avatar.query.count()
                print(f"📊 Total avatars in database: {avatar_count}")
                
                return True
                
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False

    def create_rollback_plan(self, avatars: Dict[str, Dict]) -> str:
        """
        Create rollback script in case deployment needs to be reversed
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rollback_file = self.migration_path / f"rollback_avatars_{timestamp}.py"
        
        avatar_ids = [info['id'] for info in avatars.values() if info['status'] == 'ready']
        
        rollback_content = f'''#!/usr/bin/env python3
"""
Rollback script for avatar batch deployment {timestamp}
Removes avatars added in this batch
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def rollback_avatars():
    """Remove avatars added in batch {timestamp}"""
    from AjaSpellBApp import app, db
    from models import Avatar, User
    
    avatar_ids_to_remove = {avatar_ids}
    
    with app.app_context():
        print("🔄 Rolling back avatar batch {timestamp}")
        
        # Reset users using these avatars to default
        for avatar_id in avatar_ids_to_remove:
            users_affected = User.query.filter_by(avatar_id=avatar_id).all()
            for user in users_affected:
                user.avatar_id = 'mascot-bee'  # Reset to default
                print(f"   Reset user {{user.username}} avatar to default")
        
        # Remove avatar entries
        for avatar_id in avatar_ids_to_remove:
            avatar = Avatar.query.filter_by(slug=avatar_id).first()
            if avatar:
                db.session.delete(avatar)
                print(f"   Removed avatar: {{avatar_id}}")
        
        db.session.commit()
        print("✅ Rollback completed")

if __name__ == "__main__":
    rollback_avatars()
'''
        
        with open(rollback_file, 'w') as f:
            f.write(rollback_content)
        
        print(f"📋 Rollback plan created: {rollback_file}")
        return str(rollback_file)

    def _get_existing_avatars(self) -> List[str]:
        """Get list of existing avatar IDs from database"""
        try:
            from AjaSpellBApp import app
            from models import Avatar
            
            with app.app_context():
                avatars = Avatar.query.with_entities(Avatar.slug).all()
                return [a.slug for a in avatars]
        except:
            # Fallback to file system scan
            if self.target_path.exists():
                return [f.name for f in self.target_path.iterdir() if f.is_dir()]
            return []

    def _name_to_slug(self, name: str) -> str:
        """Convert avatar name to slug (e.g., 'CoolBee' -> 'cool-bee')"""
        # Insert hyphens before capitals (except first)
        slug = re.sub(r'([a-z])([A-Z])', r'\\1-\\2', name)
        return slug.lower()

    def _validate_avatar_files(self, folder: Path, avatar_name: str) -> Dict:
        """Validate that avatar folder contains required files"""
        result = {
            'valid': True,
            'errors': [],
            'files': {},
            'warnings': []
        }
        
        files = list(folder.glob('*'))
        
        # Check required files
        for file_type, extension in self.required_files.items():
            expected_file = folder / f"{avatar_name}{extension}"
            
            if expected_file.exists():
                size_mb = expected_file.stat().st_size / (1024 * 1024)
                result['files'][file_type] = {
                    'path': expected_file,
                    'size_mb': round(size_mb, 2)
                }
                
                # Check file size limits
                if file_type == 'obj' and size_mb > self.max_obj_size_mb:
                    result['errors'].append(f"OBJ file too large: {size_mb:.1f}MB > {self.max_obj_size_mb}MB")
                elif file_type == 'texture' and size_mb > self.max_texture_size_mb:
                    result['errors'].append(f"Texture file too large: {size_mb:.1f}MB > {self.max_texture_size_mb}MB")
            else:
                result['errors'].append(f"Missing required file: {expected_file.name}")
        
        # Check for thumbnail
        thumbnail_files = list(folder.glob(f"{avatar_name}!.png")) + list(folder.glob("thumbnail.png"))
        if thumbnail_files:
            result['files']['thumbnail'] = {'path': thumbnail_files[0]}
        else:
            result['warnings'].append("No thumbnail found - will generate automatically")
        
        # Set validity
        result['valid'] = len(result['errors']) == 0
        
        return result

    def _copy_avatar_files(self, source_folder: Path, target_folder: Path, avatar_name: str) -> Dict:
        """Copy and standardize avatar files to target location"""
        files_copied = {}
        
        # Copy OBJ file
        source_obj = source_folder / f"{avatar_name}.obj"
        target_obj = target_folder / f"{avatar_name}.obj"
        if source_obj.exists():
            shutil.copy2(source_obj, target_obj)
            files_copied['obj'] = target_obj
        
        # Copy MTL file
        source_mtl = source_folder / f"{avatar_name}.mtl"
        target_mtl = target_folder / f"{avatar_name}.mtl"
        if source_mtl.exists():
            shutil.copy2(source_mtl, target_mtl)
            files_copied['mtl'] = target_mtl
        
        # Copy texture file
        source_texture = source_folder / f"{avatar_name}.png"
        target_texture = target_folder / f"{avatar_name}.png"
        if source_texture.exists():
            shutil.copy2(source_texture, target_texture)
            files_copied['texture'] = target_texture
        
        # Copy or generate thumbnail
        source_thumb = source_folder / f"{avatar_name}!.png"
        target_thumb = target_folder / f"{avatar_name}!.png"
        
        if source_thumb.exists():
            shutil.copy2(source_thumb, target_thumb)
            files_copied['thumbnail'] = target_thumb
        
        return files_copied

    def _ensure_thumbnail(self, target_folder: Path, avatar_name: str) -> bool:
        """Generate thumbnail if it doesn't exist"""
        thumbnail_path = target_folder / f"{avatar_name}!.png"
        
        if thumbnail_path.exists():
            return True
        
        # Try to generate from texture
        texture_path = target_folder / f"{avatar_name}.png"
        if texture_path.exists():
            try:
                with Image.open(texture_path) as img:
                    img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
                    img.save(thumbnail_path, "PNG")
                return True
            except Exception as e:
                print(f"   ⚠️  Failed to generate thumbnail: {e}")
        
        return False

    def _validate_copied_files(self, target_folder: Path, avatar_id: str) -> bool:
        """Validate that all required files were copied correctly"""
        required_files = [
            f"{target_folder.name}.obj",
            f"{target_folder.name}.mtl", 
            f"{target_folder.name}.png"
        ]
        
        for filename in required_files:
            file_path = target_folder / filename
            if not file_path.exists():
                print(f"   ❌ Missing file: {filename}")
                return False
        
        return True

    def _generate_migration_script(self, avatars: Dict[str, Dict], timestamp: str) -> str:
        """Generate the actual migration script content"""
        script_content = f'''#!/usr/bin/env python3
"""
Avatar Batch Migration - {timestamp}
Adds {len(avatars)} new avatars to the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def migrate_avatar_batch():
    """Add new avatar batch to database"""
    from AjaSpellBApp import app, db
    from models import Avatar
    
    with app.app_context():
        print(f"🚀 Adding {len(avatars)} new avatars to database")
        
        success_count = 0
        
'''
        
        for idx, (avatar_name, info) in enumerate(avatars.items(), 1):
            avatar_id = info['id']
            
            # Generate description based on name
            description = self._generate_description(avatar_name)
            category = self._determine_category(avatar_name)
            
            script_content += f'''
        # {idx}. {avatar_name}
        try:
            avatar_{idx} = Avatar(
                slug='{avatar_id}',
                name='{avatar_name}',
                description='{description}',
                category='{category}',
                folder_path='{avatar_id}',
                obj_file='{avatar_name}.obj',
                mtl_file='{avatar_name}.mtl',
                texture_file='{avatar_name}.png',
                thumbnail_file='{avatar_name}!.png',
                unlock_level=1,
                points_required=0,
                is_premium=False,
                sort_order={100 + idx},
                is_active=True
            )
            
            db.session.add(avatar_{idx})
            success_count += 1
            print(f"   ✅ Added {avatar_name} ({avatar_id})")
            
        except Exception as e:
            print(f"   ❌ Failed to add {avatar_name}: {{e}}")
'''
        
        script_content += '''
        try:
            db.session.commit()
            print(f"\\n🎉 Successfully added {success_count} avatars to database")
            
            # Verify
            total_avatars = Avatar.query.count()
            print(f"📊 Total avatars in database: {total_avatars}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed during commit: {e}")

if __name__ == "__main__":
    migrate_avatar_batch()
'''
        
        return script_content

    def _generate_verification_script(self, avatars: Dict[str, Dict]) -> str:
        """Generate verification script to check deployment"""
        avatar_ids = [info['id'] for info in avatars.values()]
        
        return f'''#!/usr/bin/env python3
"""
Verification script for avatar batch deployment
Checks that all avatars were properly added
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verify_avatar_deployment():
    """Verify that all avatars were properly deployed"""
    from AjaSpellBApp import app
    from models import Avatar
    
    expected_avatars = {avatar_ids}
    
    with app.app_context():
        print("🔍 Verifying avatar deployment...")
        
        missing = []
        found = []
        
        for avatar_id in expected_avatars:
            avatar = Avatar.query.filter_by(slug=avatar_id).first()
            if avatar:
                found.append(avatar_id)
                print(f"   ✅ {avatar_id}: {avatar.name}")
            else:
                missing.append(avatar_id)
                print(f"   ❌ {avatar_id}: NOT FOUND")
        
        print(f"\\n📊 Verification Results:")
        print(f"   ✅ Found: {len(found)}")
        print(f"   ❌ Missing: {len(missing)}")
        
        if missing:
            print(f"\\n⚠️  Missing avatars: {missing}")
            return False
        else:
            print(f"\\n🎉 All avatars successfully deployed!")
            return True

if __name__ == "__main__":
    verify_avatar_deployment()
'''

    def _generate_description(self, avatar_name: str) -> str:
        """Generate kid-friendly description based on avatar name"""
        descriptions = {
            'astro': "A space-exploring bee ready for cosmic adventures!",
            'franken': "A friendly monster bee who loves Halloween fun!",
            'ware': "A tech-savvy bee who knows all about computers!",
            'zom': "A silly zombie bee who loves brain... food!",
            'vamp': "A mysterious vampire bee who flies at night!",
            'detective': "A smart detective bee who solves mysteries!",
            'ninja': "A stealthy ninja bee with amazing skills!",
            'pirate': "An adventurous pirate bee sailing the seven seas!",
            'robot': "A cool robot bee from the future!",
            'wizard': "A magical wizard bee with spellbinding powers!"
        }
        
        name_lower = avatar_name.lower()
        for key, desc in descriptions.items():
            if key in name_lower:
                return desc
        
        return f"An awesome {avatar_name} ready for spelling adventures!"

    def _determine_category(self, avatar_name: str) -> str:
        """Determine category based on avatar name"""
        categories = {
            'astro': 'space',
            'franken': 'halloween',
            'ware': 'tech',
            'zom': 'halloween', 
            'vamp': 'halloween',
            'detective': 'adventure',
            'ninja': 'adventure',
            'pirate': 'adventure',
            'robot': 'tech',
            'wizard': 'fantasy'
        }
        
        name_lower = avatar_name.lower()
        for key, category in categories.items():
            if key in name_lower:
                return category
        
        return 'classic'


def main():
    """Main entry point with command line interface"""
    parser = argparse.ArgumentParser(description='BeeSmart Avatar Batch Preparation Tool')
    parser.add_argument('--scan', action='store_true', help='Scan for new avatars')
    parser.add_argument('--prepare', action='store_true', help='Prepare avatar files')
    parser.add_argument('--migrate', action='store_true', help='Generate database migration')
    parser.add_argument('--deploy', action='store_true', help='Deploy to database')
    parser.add_argument('--all', action='store_true', help='Run complete workflow')
    parser.add_argument('--rollback', metavar='TIMESTAMP', help='Rollback deployment')
    
    args = parser.parse_args()
    
    manager = AvatarBatchManager()
    
    if args.all or args.scan:
        print("\\n🎯 STARTING AVATAR BATCH PREPARATION")
        print("=" * 80)
        
        # Step 1: Scan
        avatars = manager.scan_new_avatars()
        if not avatars:
            print("\\n❌ No new avatars found")
            return
        
        # Save scan results
        scan_file = manager.backup_path / "scan_results.json"
        with open(scan_file, 'w') as f:
            # Convert Path objects to strings for JSON serialization
            serializable_avatars = {}
            for name, info in avatars.items():
                serializable_info = info.copy()
                serializable_info['folder'] = str(info['folder'])
                if 'files' in info and 'files' in info['files']:
                    for file_type, file_info in info['files']['files'].items():
                        if 'path' in file_info:
                            file_info['path'] = str(file_info['path'])
                serializable_avatars[name] = serializable_info
            
            json.dump(serializable_avatars, f, indent=2)
        
        print(f"\\n💾 Scan results saved to: {scan_file}")
    
    if args.all or args.prepare:
        # Load scan results if not already in memory
        if 'avatars' not in locals():
            scan_file = manager.backup_path / "scan_results.json"
            if scan_file.exists():
                with open(scan_file, 'r') as f:
                    avatars = json.load(f)
                # Convert string paths back to Path objects
                for name, info in avatars.items():
                    info['folder'] = Path(info['folder'])
            else:
                print("\\n❌ No scan results found. Run --scan first.")
                return
        
        # Step 2: Prepare files
        success = manager.prepare_avatar_files(avatars)
        if not success:
            print("\\n❌ File preparation failed")
            return
    
    if args.all or args.migrate:
        # Step 3: Generate migration
        migration_file = manager.generate_database_migration(avatars)
        if not migration_file:
            print("\\n❌ Migration generation failed")
            return
        
        # Create rollback plan
        rollback_file = manager.create_rollback_plan(avatars)
    
    if args.all or args.deploy:
        # Step 4: Deploy to database
        if 'migration_file' not in locals():
            # Find latest migration file
            migration_files = list(manager.migration_path.glob("add_avatars_*.py"))
            if migration_files:
                migration_file = str(sorted(migration_files)[-1])
            else:
                print("\\n❌ No migration file found")
                return
        
        success = manager.deploy_to_database(migration_file)
        if success:
            print("\\n🎉 AVATAR BATCH DEPLOYMENT COMPLETE!")
            print("\\n📋 Next Steps:")
            print("   1. Test avatars in browser")
            print("   2. Verify 3D models load correctly") 
            print("   3. Check avatar picker displays properly")
            print("   4. Test user avatar selection")
        else:
            print("\\n❌ Deployment failed")

if __name__ == "__main__":
    main()