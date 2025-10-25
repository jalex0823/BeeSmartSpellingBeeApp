#!/usr/bin/env python3
"""
🐝 Avatar System Readiness Check
Validates that the avatar system is ready for new batch processing

Checks:
- Database connectivity and schema
- File system structure
- Existing avatar integrity
- Required dependencies
- Migration system readiness
"""

import os
import sys
from pathlib import Path
import sqlite3
from typing import List, Dict, Tuple

class AvatarSystemValidator:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.errors = []
        self.warnings = []
        self.info = []
        
    def run_full_validation(self) -> bool:
        """Run complete system validation"""
        print("🔍 AVATAR SYSTEM READINESS CHECK")
        print("=" * 60)
        
        checks = [
            ("📁 File System Structure", self.check_file_structure),
            ("💾 Database Connectivity", self.check_database),
            ("📊 Database Schema", self.check_schema),
            ("🎨 Existing Avatars", self.check_existing_avatars),
            ("🛠️ Dependencies", self.check_dependencies),
            ("📋 Migration System", self.check_migration_system),
            ("🔧 Utilities", self.check_utilities)
        ]
        
        all_passed = True
        
        for check_name, check_func in checks:
            print(f"\\n{check_name}")
            print("-" * 40)
            
            try:
                passed = check_func()
                if passed:
                    print("✅ PASSED")
                else:
                    print("❌ FAILED")
                    all_passed = False
            except Exception as e:
                print(f"❌ ERROR: {e}")
                all_passed = False
        
        # Summary
        print("\\n" + "=" * 60)
        print("📋 VALIDATION SUMMARY")
        print("=" * 60)
        
        if self.errors:
            print("\\n❌ ERRORS:")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print("\\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if self.info:
            print("\\n💡 INFO:")
            for info in self.info:
                print(f"   • {info}")
        
        if all_passed:
            print("\\n🎉 SYSTEM READY FOR NEW AVATAR BATCH!")
            print("\\nNext steps:")
            print("   1. Place new avatar folders in: Avatars/3D Avatar Files/")
            print("   2. Run: python prepare_new_avatars.py --all")
        else:
            print("\\n⚠️  SYSTEM NEEDS ATTENTION BEFORE PROCESSING NEW AVATARS")
        
        return all_passed
    
    def check_file_structure(self) -> bool:
        """Check required directory structure"""
        required_dirs = [
            "Avatars/3D Avatar Files",
            "static/assets/avatars",
            "static/js",
            "templates",
            "instance"
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            full_path = self.base_path / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
            else:
                print(f"   ✅ {dir_path}")
        
        if missing_dirs:
            for missing in missing_dirs:
                self.errors.append(f"Missing directory: {missing}")
                print(f"   ❌ {missing}")
            return False
        
        # Check source avatar files
        source_path = self.base_path / "Avatars" / "3D Avatar Files"
        if source_path.exists():
            avatar_folders = [f for f in source_path.iterdir() if f.is_dir()]
            self.info.append(f"Found {len(avatar_folders)} potential new avatar folders")
            
            for folder in sorted(avatar_folders)[:5]:  # Show first 5
                print(f"   📁 {folder.name}")
            if len(avatar_folders) > 5:
                print(f"   📁 ... and {len(avatar_folders) - 5} more")
        
        return True
    
    def check_database(self) -> bool:
        """Check database connectivity"""
        try:
            # Try to import Flask app
            sys.path.append(str(self.base_path))
            from AjaSpellBApp import app, db
            
            with app.app_context():
                # Test database connection
                db.engine.execute("SELECT 1").fetchone()
                print("   ✅ Database connection successful")
                
                # Check if in development vs production
                if 'sqlite' in str(db.engine.url):
                    self.info.append("Using SQLite database (development)")
                else:
                    self.info.append(f"Using {db.engine.url.drivername} database (production)")
                
                return True
                
        except ImportError as e:
            self.errors.append(f"Cannot import Flask app: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Database connection failed: {e}")
            return False
    
    def check_schema(self) -> bool:
        """Check database schema for avatar tables"""
        try:
            from AjaSpellBApp import app, db
            from models import Avatar, User
            
            with app.app_context():
                # Check Avatar table exists
                avatar_count = Avatar.query.count()
                print(f"   ✅ Avatar table exists ({avatar_count} avatars)")
                
                # Check User table has avatar columns
                user_columns = db.inspect(db.engine).get_columns('users')
                column_names = [col['name'] for col in user_columns]
                
                required_columns = ['avatar_id', 'avatar_variant', 'avatar_locked', 'avatar_last_updated']
                missing_columns = [col for col in required_columns if col not in column_names]
                
                if missing_columns:
                    self.errors.append(f"Missing user avatar columns: {missing_columns}")
                    return False
                
                print("   ✅ User avatar columns present")
                return True
                
        except Exception as e:
            self.errors.append(f"Schema validation failed: {e}")
            return False
    
    def check_existing_avatars(self) -> bool:
        """Check integrity of existing avatars"""
        try:
            from AjaSpellBApp import app
            from models import Avatar
            
            with app.app_context():
                avatars = Avatar.query.filter_by(is_active=True).all()
                
                if not avatars:
                    self.warnings.append("No active avatars in database")
                    return True
                
                print(f"   📊 Found {len(avatars)} active avatars")
                
                broken_avatars = []
                for avatar in avatars:
                    avatar_path = self.base_path / "static" / "assets" / "avatars" / avatar.folder_path
                    
                    if not avatar_path.exists():
                        broken_avatars.append(f"{avatar.slug} (missing folder)")
                        continue
                    
                    # Check required files
                    required_files = [avatar.obj_file, avatar.mtl_file, avatar.texture_file]
                    missing_files = []
                    
                    for filename in required_files:
                        if filename and not (avatar_path / filename).exists():
                            missing_files.append(filename)
                    
                    if missing_files:
                        broken_avatars.append(f"{avatar.slug} (missing: {', '.join(missing_files)})")
                
                if broken_avatars:
                    self.warnings.append(f"Avatars with issues: {len(broken_avatars)}")
                    for broken in broken_avatars:
                        print(f"   ⚠️  {broken}")
                else:
                    print("   ✅ All avatars have required files")
                
                return True
                
        except Exception as e:
            self.errors.append(f"Avatar integrity check failed: {e}")
            return False
    
    def check_dependencies(self) -> bool:
        """Check required Python dependencies"""
        required_packages = [
            ('PIL', 'Pillow'),
            ('flask', 'Flask'),
            ('sqlalchemy', 'SQLAlchemy')
        ]
        
        missing_packages = []
        
        for module, package in required_packages:
            try:
                __import__(module)
                print(f"   ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"   ❌ {package}")
        
        if missing_packages:
            self.errors.append(f"Missing packages: {', '.join(missing_packages)}")
            return False
        
        return True
    
    def check_migration_system(self) -> bool:
        """Check migration system readiness"""
        migrations_dir = self.base_path / "migrations"
        if not migrations_dir.exists():
            migrations_dir.mkdir(parents=True, exist_ok=True)
            print("   ✅ Created migrations directory")
        else:
            print("   ✅ Migrations directory exists")
        
        # Check for existing migration files
        migration_files = list(migrations_dir.glob("*.py"))
        if migration_files:
            self.info.append(f"Found {len(migration_files)} existing migration files")
        
        return True
    
    def check_utilities(self) -> bool:
        """Check avatar management utilities"""
        utilities = [
            "avatar_catalog.py",
            "avatar_db_helpers.py", 
            "models.py",
            "scan_avatar_folders.py"
        ]
        
        missing_utils = []
        
        for util in utilities:
            util_path = self.base_path / util
            if util_path.exists():
                print(f"   ✅ {util}")
            else:
                missing_utils.append(util)
                print(f"   ❌ {util}")
        
        if missing_utils:
            self.warnings.append(f"Missing utilities: {', '.join(missing_utils)}")
        
        return len(missing_utils) == 0

def main():
    """Run the validation"""
    validator = AvatarSystemValidator()
    validator.run_full_validation()

if __name__ == "__main__":
    main()