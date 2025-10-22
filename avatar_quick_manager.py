#!/usr/bin/env python3
"""
BeeSmart Avatar Quick Manager
Simplified version for quick avatar addition with minimal dependencies

Usage Examples:
    # Add new avatar from folder
    python avatar_quick_manager.py --add "NewBee" --source "C:/path/to/newbee/files/"
    
    # List all current avatars
    python avatar_quick_manager.py --list
    
    # Validate all avatars
    python avatar_quick_manager.py --validate
    
    # Create backup before changes
    python avatar_quick_manager.py --backup
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class SimpleAvatarManager:
    def __init__(self):
        # Define paths relative to script location
        self.base_path = Path(__file__).parent
        self.static_avatars_path = self.base_path / "static" / "Avatars" / "3D Avatar Files"
        self.js_avatar_loader_path = self.base_path / "static" / "js" / "user-avatar-loader.js"
        self.backup_path = self.base_path / "backups" / "avatars"
        
        # Required files for each avatar
        self.required_extensions = ['.obj', '.mtl', '.png']
        self.thumbnail_suffix = '!.png'
        
        print(f"🐝 BeeSmart Simple Avatar Manager")
        print(f"📂 Avatars Directory: {self.static_avatars_path}")

    def validate_avatar_name(self, name: str) -> Tuple[bool, str]:
        """Basic avatar name validation"""
        if not name or len(name) < 3:
            return False, "Avatar name must be at least 3 characters"
        
        if not name.replace('_', '').replace('-', '').isalnum():
            return False, "Avatar name can only contain letters, numbers, hyphens, and underscores"
        
        # Check if already exists
        if (self.static_avatars_path / name).exists():
            return False, f"Avatar '{name}' already exists"
        
        return True, "Valid"

    def validate_source_files(self, source_path: Path, avatar_name: str) -> Tuple[bool, List[str]]:
        """Check if source directory has required files"""
        errors = []
        
        if not source_path.exists():
            return False, [f"Source directory not found: {source_path}"]
        
        # Check for required files
        for ext in self.required_extensions:
            file_path = source_path / f"{avatar_name}{ext}"
            if not file_path.exists():
                errors.append(f"Missing: {avatar_name}{ext}")
        
        # Check for thumbnail
        thumbnail_path = source_path / f"{avatar_name}{self.thumbnail_suffix}"
        if not thumbnail_path.exists():
            errors.append(f"Missing: {avatar_name}{self.thumbnail_suffix}")
        
        return len(errors) == 0, errors

    def create_backup(self) -> Path:
        """Create timestamped backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.backup_path / f"backup_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📦 Creating backup: {backup_dir}")
        
        # Backup avatars
        if self.static_avatars_path.exists():
            shutil.copytree(self.static_avatars_path, backup_dir / "avatars")
        
        # Backup JS file
        if self.js_avatar_loader_path.exists():
            shutil.copy2(self.js_avatar_loader_path, backup_dir / "user-avatar-loader.js")
        
        print(f"✅ Backup created")
        return backup_dir

    def list_avatars(self) -> List[Dict]:
        """List all current avatars"""
        avatars = []
        
        if not self.static_avatars_path.exists():
            print(f"❌ Avatars directory not found")
            return avatars
        
        print(f"\n🎨 Current Avatars:")
        print(f"{'Name':<20} {'Files':<8} {'Complete'}")
        print("-" * 35)
        
        for avatar_dir in sorted(self.static_avatars_path.glob('*')):
            if avatar_dir.is_dir():
                files = list(avatar_dir.glob('*'))
                file_count = len(files)
                
                # Check completeness
                has_obj = any(f.suffix == '.obj' for f in files)
                has_mtl = any(f.suffix == '.mtl' for f in files)
                has_png = any(f.suffix == '.png' and '!' not in f.name for f in files)
                has_thumb = any('!' in f.name and f.suffix == '.png' for f in files)
                
                complete = has_obj and has_mtl and has_png and has_thumb
                status = "✅" if complete else "❌"
                
                print(f"{avatar_dir.name:<20} {file_count:<8} {status}")
                
                avatars.append({
                    'name': avatar_dir.name,
                    'file_count': file_count,
                    'complete': complete,
                    'files': [f.name for f in files]
                })
        
        print(f"\n📊 Total: {len(avatars)} avatars")
        return avatars

    def add_avatar(self, avatar_name: str, source_path: Path) -> bool:
        """Add new avatar to system"""
        print(f"\n🎨 Adding avatar: {avatar_name}")
        
        # Validate name
        name_valid, name_msg = self.validate_avatar_name(avatar_name)
        if not name_valid:
            print(f"❌ {name_msg}")
            return False
        
        # Validate files
        files_valid, errors = self.validate_source_files(source_path, avatar_name)
        if not files_valid:
            print(f"❌ Source validation failed:")
            for error in errors:
                print(f"   • {error}")
            return False
        
        print(f"✅ Validation passed")
        
        try:
            # Create destination folder
            dest_dir = self.static_avatars_path / avatar_name
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy files
            copied_files = []
            for ext in self.required_extensions + [self.thumbnail_suffix]:
                if ext == self.thumbnail_suffix:
                    src_file = source_path / f"{avatar_name}{ext}"
                else:
                    src_file = source_path / f"{avatar_name}{ext}"
                
                if src_file.exists():
                    dest_file = dest_dir / src_file.name
                    shutil.copy2(src_file, dest_file)
                    copied_files.append(src_file.name)
                    print(f"📄 Copied: {src_file.name}")
            
            # Update JavaScript mapping
            js_updated = self.update_js_mapping(avatar_name)
            if js_updated:
                print(f"✅ JavaScript mapping updated")
            else:
                print(f"⚠️ Manual JS update needed")
            
            print(f"🎉 Avatar '{avatar_name}' added successfully!")
            print(f"📁 Location: {dest_dir}")
            print(f"📄 Files: {', '.join(copied_files)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def update_js_mapping(self, avatar_name: str) -> bool:
        """Update JavaScript avatar mapping"""
        try:
            if not self.js_avatar_loader_path.exists():
                print(f"⚠️ JS file not found: {self.js_avatar_loader_path}")
                return False
            
            # Read file
            with open(self.js_avatar_loader_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Generate mapping entry
            avatar_key = avatar_name.lower()
            new_mapping = f"""            '{avatar_key}': {{
                obj: '/static/Avatars/3D Avatar Files/{avatar_name}/{avatar_name}.obj',
                mtl: '/static/Avatars/3D Avatar Files/{avatar_name}/{avatar_name}.mtl',
                texture: '/static/Avatars/3D Avatar Files/{avatar_name}/{avatar_name}.png',
                thumbnail: '/static/Avatars/3D Avatar Files/{avatar_name}/{avatar_name}!.png'
            }},"""
            
            # Find insertion point (look for closing brace of avatarMap)
            insertion_pattern = r'(this\.avatarMap\s*=\s*\{[^}]*)(        \}\s*;)'
            
            import re
            match = re.search(insertion_pattern, content, re.DOTALL)
            if match:
                # Insert new mapping before closing
                updated_content = (
                    content[:match.start(2)] + 
                    new_mapping + "\n" + 
                    content[match.start(2):]
                )
                
                # Write back
                with open(self.js_avatar_loader_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                return True
            else:
                print(f"⚠️ Could not find avatarMap in JS file")
                return False
                
        except Exception as e:
            print(f"⚠️ JS update error: {e}")
            return False

    def validate_all(self) -> Dict:
        """Validate all existing avatars"""
        avatars = self.list_avatars()
        
        complete = sum(1 for a in avatars if a['complete'])
        incomplete = [a['name'] for a in avatars if not a['complete']]
        
        print(f"\n🔍 Validation Summary:")
        print(f"✅ Complete: {complete}/{len(avatars)}")
        print(f"❌ Incomplete: {len(incomplete)}")
        
        if incomplete:
            print(f"\n⚠️ Incomplete avatars: {', '.join(incomplete)}")
        
        return {
            'total': len(avatars),
            'complete': complete,
            'incomplete': incomplete
        }

    def show_example_structure(self, avatar_name: str = "NewBee"):
        """Show expected file structure"""
        print(f"\n📋 Expected file structure for '{avatar_name}':")
        print(f"📁 {avatar_name}/")
        print(f"   📄 {avatar_name}.obj     (3D model)")
        print(f"   📄 {avatar_name}.mtl     (material definition)")  
        print(f"   📄 {avatar_name}.png     (texture image)")
        print(f"   📄 {avatar_name}!.png    (thumbnail for UI)")
        print(f"\n💡 All files must use exact same name as folder")


def main():
    parser = argparse.ArgumentParser(description='BeeSmart Simple Avatar Manager')
    parser.add_argument('--add', metavar='NAME', help='Add avatar with this name')
    parser.add_argument('--source', metavar='PATH', help='Source directory with avatar files')
    parser.add_argument('--list', action='store_true', help='List all avatars')
    parser.add_argument('--validate', action='store_true', help='Validate all avatars')
    parser.add_argument('--backup', action='store_true', help='Create backup')
    parser.add_argument('--example', metavar='NAME', nargs='?', const='NewBee', 
                       help='Show expected file structure')
    
    args = parser.parse_args()
    
    manager = SimpleAvatarManager()
    
    try:
        if args.add:
            if not args.source:
                print(f"❌ Error: --source required when adding avatar")
                print(f"Example: --add MyBee --source 'C:/path/to/mybee/files/'")
                sys.exit(1)
            
            source_path = Path(args.source)
            success = manager.add_avatar(args.add, source_path)
            sys.exit(0 if success else 1)
            
        elif args.list:
            manager.list_avatars()
            
        elif args.validate:
            manager.validate_all()
            
        elif args.backup:
            manager.create_backup()
            
        elif args.example:
            manager.show_example_structure(args.example)
            
        else:
            print(f"🐝 BeeSmart Avatar Manager")
            print(f"\nQuick Commands:")
            print(f"  --list                    List all avatars")
            print(f"  --validate                Check all avatars")
            print(f"  --example [NAME]          Show file structure")
            print(f"  --backup                  Create backup")
            print(f"  --add NAME --source PATH  Add new avatar")
            print(f"\nExample:")
            print(f"  python avatar_quick_manager.py --add 'CyberBee' --source 'C:/Downloads/CyberBee/'")
            
    except KeyboardInterrupt:
        print(f"\n⏹️ Cancelled")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()