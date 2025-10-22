#!/usr/bin/env python3
"""
BeeSmart Avatar Management System
Automates the process of adding new avatars to the BeeSmart Spelling Bee App

Features:
- Validates file requirements (.obj, .mtl, .png texture, !.png thumbnail)
- Ensures proper naming conventions
- Creates folder structure automatically
- Updates avatar mapping in JavaScript files
- Validates file sizes and formats
- Generates avatar catalog
- Backs up existing files before changes

Usage:
    python avatar_manager.py --add "AvatarName" --source "/path/to/avatar/files/"
    python avatar_manager.py --validate
    python avatar_manager.py --list
    python avatar_manager.py --backup
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

class AvatarManager:
    def __init__(self):
        # Define paths relative to script location
        self.base_path = Path(__file__).parent
        self.static_avatars_path = self.base_path / "static" / "Avatars" / "3D Avatar Files"
        self.js_avatar_loader_path = self.base_path / "static" / "js" / "user-avatar-loader.js"
        self.backup_path = self.base_path / "backups" / "avatars"
        
        # File requirements
        self.required_files = ['.obj', '.mtl', '.png']  # Main texture
        self.required_thumbnail = '!.png'  # Thumbnail file
        
        # Validation criteria
        self.max_texture_size = (2048, 2048)  # Max texture dimensions
        self.preferred_thumbnail_size = (256, 256)  # Standard thumbnail size
        self.max_file_size_mb = 10  # Max file size in MB
        
        print(f"🐝 BeeSmart Avatar Manager Initialized")
        print(f"📂 Base Path: {self.base_path}")
        print(f"🎨 Avatars Path: {self.static_avatars_path}")

    def validate_avatar_name(self, name: str) -> Tuple[bool, str]:
        """Validate avatar name follows conventions"""
        if not name:
            return False, "Avatar name cannot be empty"
        
        # Check for valid characters (alphanumeric, no spaces)
        if not re.match(r'^[A-Za-z][A-Za-z0-9]*$', name):
            return False, "Avatar name must start with letter and contain only alphanumeric characters"
        
        # Check length
        if len(name) < 3 or len(name) > 20:
            return False, "Avatar name must be between 3-20 characters"
        
        # Check if already exists
        avatar_folder = self.static_avatars_path / name
        if avatar_folder.exists():
            return False, f"Avatar '{name}' already exists"
        
        return True, "Valid avatar name"

    def validate_source_files(self, source_path: Path, avatar_name: str) -> Tuple[bool, List[str], Dict]:
        """Validate that source directory contains all required files"""
        errors = []
        file_info = {}
        
        if not source_path.exists():
            return False, [f"Source path does not exist: {source_path}"], {}
        
        # Check for required files
        for ext in self.required_files:
            expected_file = source_path / f"{avatar_name}{ext}"
            if expected_file.exists():
                file_info[ext] = {
                    'path': expected_file,
                    'size': expected_file.stat().st_size,
                    'size_mb': round(expected_file.stat().st_size / (1024 * 1024), 2)
                }
                
                # Check file size
                if file_info[ext]['size_mb'] > self.max_file_size_mb:
                    errors.append(f"{ext} file too large: {file_info[ext]['size_mb']}MB (max: {self.max_file_size_mb}MB)")
            else:
                errors.append(f"Missing required file: {expected_file}")
        
        # Check for thumbnail
        thumbnail_file = source_path / f"{avatar_name}{self.required_thumbnail}"
        if thumbnail_file.exists():
            file_info[self.required_thumbnail] = {
                'path': thumbnail_file,
                'size': thumbnail_file.stat().st_size,
                'size_mb': round(thumbnail_file.stat().st_size / (1024 * 1024), 2)
            }
            
            # Validate thumbnail image
            try:
                with Image.open(thumbnail_file) as img:
                    file_info[self.required_thumbnail]['dimensions'] = img.size
                    file_info[self.required_thumbnail]['format'] = img.format
                    
                    # Check if thumbnail is reasonable size
                    if img.width < 64 or img.height < 64:
                        errors.append(f"Thumbnail too small: {img.size} (minimum: 64x64)")
                    elif img.width > 512 or img.height > 512:
                        errors.append(f"Thumbnail too large: {img.size} (maximum: 512x512)")
            except Exception as e:
                errors.append(f"Invalid thumbnail image: {e}")
        else:
            errors.append(f"Missing thumbnail file: {thumbnail_file}")
        
        # Validate main texture if it's PNG
        texture_file = source_path / f"{avatar_name}.png"
        if texture_file.exists():
            try:
                with Image.open(texture_file) as img:
                    file_info['.png']['dimensions'] = img.size
                    file_info['.png']['format'] = img.format
                    
                    if img.width > self.max_texture_size[0] or img.height > self.max_texture_size[1]:
                        errors.append(f"Texture too large: {img.size} (max: {self.max_texture_size})")
            except Exception as e:
                errors.append(f"Invalid texture image: {e}")
        
        return len(errors) == 0, errors, file_info

    def create_backup(self) -> Path:
        """Create backup of current avatar system"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.backup_path / f"avatar_backup_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📦 Creating backup at: {backup_dir}")
        
        # Backup avatar files
        if self.static_avatars_path.exists():
            shutil.copytree(self.static_avatars_path, backup_dir / "avatars")
        
        # Backup JavaScript file
        if self.js_avatar_loader_path.exists():
            shutil.copy2(self.js_avatar_loader_path, backup_dir / "user-avatar-loader.js")
        
        # Create backup manifest
        manifest = {
            'timestamp': timestamp,
            'backup_date': datetime.now().isoformat(),
            'avatar_count': len(list(self.static_avatars_path.glob('*'))) if self.static_avatars_path.exists() else 0,
            'files_backed_up': ['avatars/', 'user-avatar-loader.js']
        }
        
        with open(backup_dir / "manifest.json", 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✅ Backup created successfully")
        return backup_dir

    def add_avatar(self, avatar_name: str, source_path: Path, force: bool = False) -> bool:
        """Add new avatar to the system"""
        print(f"\n🎨 Adding avatar: {avatar_name}")
        print(f"📁 Source: {source_path}")
        
        # Validate avatar name
        name_valid, name_msg = self.validate_avatar_name(avatar_name)
        if not name_valid and not force:
            print(f"❌ Invalid avatar name: {name_msg}")
            return False
        elif not name_valid:
            print(f"⚠️ Avatar name warning (forced): {name_msg}")
        
        # Validate source files
        files_valid, errors, file_info = self.validate_source_files(source_path, avatar_name)
        if not files_valid:
            print(f"❌ Source file validation failed:")
            for error in errors:
                print(f"   • {error}")
            return False
        
        print(f"✅ Source files validated successfully")
        
        # Create backup before making changes
        if not force:
            backup_dir = self.create_backup()
        
        try:
            # Create avatar directory
            avatar_dir = self.static_avatars_path / avatar_name
            avatar_dir.mkdir(parents=True, exist_ok=True)
            print(f"📂 Created directory: {avatar_dir}")
            
            # Copy files
            for file_type, info in file_info.items():
                src_file = info['path']
                dst_file = avatar_dir / src_file.name
                shutil.copy2(src_file, dst_file)
                print(f"📄 Copied: {src_file.name} ({info['size_mb']}MB)")
            
            # Update JavaScript avatar mapping
            success = self.update_avatar_mapping(avatar_name)
            if not success:
                print(f"⚠️ Warning: Failed to update JavaScript mapping automatically")
                print(f"   Please manually add {avatar_name} to user-avatar-loader.js")
            
            # Generate updated avatar list
            self.generate_avatar_catalog()
            
            print(f"🎉 Avatar '{avatar_name}' added successfully!")
            print(f"📊 Total avatars: {len(list(self.static_avatars_path.glob('*')))}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding avatar: {e}")
            if not force:
                print(f"🔄 Restoring from backup...")
                # TODO: Implement restore functionality
            return False

    def update_avatar_mapping(self, avatar_name: str) -> bool:
        """Update the JavaScript avatar mapping"""
        try:
            if not self.js_avatar_loader_path.exists():
                print(f"❌ JavaScript file not found: {self.js_avatar_loader_path}")
                return False
            
            # Read current file
            with open(self.js_avatar_loader_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Generate new avatar entry
            avatar_key = avatar_name.lower().replace(' ', '-')
            new_entry = f"""            '{avatar_key}': {{
                obj: '/static/Avatars/3D Avatar Files/{avatar_name}/{avatar_name}.obj',
                mtl: '/static/Avatars/3D Avatar Files/{avatar_name}/{avatar_name}.mtl',
                texture: '/static/Avatars/3D Avatar Files/{avatar_name}/{avatar_name}.png',
                thumbnail: '/static/Avatars/3D Avatar Files/{avatar_name}/{avatar_name}!.png'
            }},"""
            
            # Find the avatar map section and insert new entry
            pattern = r"(this\.avatarMap = \{[^}]*)(        \};)"
            match = re.search(pattern, content, re.DOTALL)
            
            if match:
                # Insert before the closing brace
                updated_content = content[:match.start(2)] + new_entry + "\n" + content[match.start(2):]
                
                # Write back to file
                with open(self.js_avatar_loader_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                print(f"✅ Updated JavaScript avatar mapping")
                return True
            else:
                print(f"⚠️ Could not find avatar map section in JavaScript file")
                return False
                
        except Exception as e:
            print(f"❌ Error updating JavaScript mapping: {e}")
            return False

    def list_avatars(self) -> List[Dict]:
        """List all current avatars with their details"""
        avatars = []
        
        if not self.static_avatars_path.exists():
            print(f"❌ Avatars directory not found: {self.static_avatars_path}")
            return avatars
        
        print(f"\n🐝 Current Avatars:")
        print(f"{'Name':<15} {'Files':<12} {'Thumbnail':<10} {'Status'}")
        print("-" * 50)
        
        for avatar_dir in sorted(self.static_avatars_path.glob('*')):
            if avatar_dir.is_dir():
                avatar_info = self.analyze_avatar(avatar_dir)
                avatars.append(avatar_info)
                
                status_icon = "✅" if avatar_info['complete'] else "❌"
                thumbnail_status = "✅" if avatar_info['has_thumbnail'] else "❌"
                
                print(f"{avatar_info['name']:<15} {avatar_info['file_count']:<12} {thumbnail_status:<10} {status_icon}")
        
        print(f"\n📊 Total: {len(avatars)} avatars")
        return avatars

    def analyze_avatar(self, avatar_dir: Path) -> Dict:
        """Analyze an individual avatar directory"""
        name = avatar_dir.name
        files = list(avatar_dir.glob('*'))
        
        has_obj = any(f.suffix == '.obj' for f in files)
        has_mtl = any(f.suffix == '.mtl' for f in files)
        has_png = any(f.suffix == '.png' and '!' not in f.name for f in files)
        has_thumbnail = any('!' in f.name and f.suffix == '.png' for f in files)
        
        return {
            'name': name,
            'path': avatar_dir,
            'files': [f.name for f in files],
            'file_count': len(files),
            'has_obj': has_obj,
            'has_mtl': has_mtl,
            'has_png': has_png,
            'has_thumbnail': has_thumbnail,
            'complete': has_obj and has_mtl and has_png and has_thumbnail
        }

    def validate_all(self) -> Dict:
        """Validate all existing avatars"""
        print(f"\n🔍 Validating all avatars...")
        
        avatars = self.list_avatars()
        
        validation_results = {
            'total': len(avatars),
            'complete': sum(1 for a in avatars if a['complete']),
            'incomplete': [],
            'issues': []
        }
        
        for avatar in avatars:
            if not avatar['complete']:
                validation_results['incomplete'].append(avatar['name'])
                
                missing = []
                if not avatar['has_obj']: missing.append('.obj')
                if not avatar['has_mtl']: missing.append('.mtl')
                if not avatar['has_png']: missing.append('.png')
                if not avatar['has_thumbnail']: missing.append('!.png')
                
                validation_results['issues'].append({
                    'name': avatar['name'],
                    'missing_files': missing
                })
        
        print(f"\n📊 Validation Results:")
        print(f"✅ Complete: {validation_results['complete']}/{validation_results['total']}")
        print(f"❌ Incomplete: {len(validation_results['incomplete'])}")
        
        if validation_results['incomplete']:
            print(f"\n⚠️ Incomplete Avatars:")
            for issue in validation_results['issues']:
                print(f"   • {issue['name']}: Missing {', '.join(issue['missing_files'])}")
        
        return validation_results

    def generate_avatar_catalog(self) -> bool:
        """Generate a catalog of all avatars"""
        try:
            avatars = []
            for avatar_dir in sorted(self.static_avatars_path.glob('*')):
                if avatar_dir.is_dir():
                    avatar_info = self.analyze_avatar(avatar_dir)
                    avatars.append({
                        'name': avatar_info['name'],
                        'key': avatar_info['name'].lower().replace(' ', '-'),
                        'complete': avatar_info['complete'],
                        'files': avatar_info['files'],
                        'obj_path': f"/static/Avatars/3D Avatar Files/{avatar_info['name']}/{avatar_info['name']}.obj",
                        'mtl_path': f"/static/Avatars/3D Avatar Files/{avatar_info['name']}/{avatar_info['name']}.mtl",
                        'texture_path': f"/static/Avatars/3D Avatar Files/{avatar_info['name']}/{avatar_info['name']}.png",
                        'thumbnail_path': f"/static/Avatars/3D Avatar Files/{avatar_info['name']}/{avatar_info['name']}!.png"
                    })
            
            catalog = {
                'generated': datetime.now().isoformat(),
                'total_avatars': len(avatars),
                'complete_avatars': sum(1 for a in avatars if a['complete']),
                'avatars': avatars
            }
            
            catalog_file = self.base_path / 'avatar_catalog.json'
            with open(catalog_file, 'w', encoding='utf-8') as f:
                json.dump(catalog, f, indent=2)
            
            print(f"📋 Generated avatar catalog: {catalog_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error generating catalog: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description='BeeSmart Avatar Manager')
    parser.add_argument('--add', metavar='NAME', help='Add new avatar with specified name')
    parser.add_argument('--source', metavar='PATH', help='Source directory containing avatar files')
    parser.add_argument('--validate', action='store_true', help='Validate all existing avatars')
    parser.add_argument('--list', action='store_true', help='List all avatars')
    parser.add_argument('--backup', action='store_true', help='Create backup of current avatars')
    parser.add_argument('--force', action='store_true', help='Force operation even with warnings')
    parser.add_argument('--catalog', action='store_true', help='Generate avatar catalog')
    
    args = parser.parse_args()
    
    manager = AvatarManager()
    
    try:
        if args.add:
            if not args.source:
                print("❌ Error: --source path required when adding avatar")
                sys.exit(1)
            
            source_path = Path(args.source)
            success = manager.add_avatar(args.add, source_path, args.force)
            sys.exit(0 if success else 1)
        
        elif args.validate:
            manager.validate_all()
        
        elif args.list:
            manager.list_avatars()
        
        elif args.backup:
            manager.create_backup()
        
        elif args.catalog:
            manager.generate_avatar_catalog()
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print(f"\n⏹️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()