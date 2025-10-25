#!/usr/bin/env python3
"""
Add New Avatars to BeeSmart Spelling Bee App
============================================

This script helps add 13 new avatars from the source directory
to the BeeSmart app, including copying files and updating the database.

Usage:
    python add_new_avatars.py --scan          # Scan source directory and show what would be added
    python add_new_avatars.py --copy          # Copy files and add to database
    python add_new_avatars.py --verify        # Verify all avatars are working
"""

import os
import shutil
import sys
from pathlib import Path
import argparse
from models import Avatar, db
from AjaSpellBApp import app

# Source and destination paths
SOURCE_DIR = Path("C:/Users/jeff/Dropbox/NewSmartBeeAvatars")
DEST_DIR = Path("C:/Users/jeff/Dropbox/BeeSmartSpellingBeeApp/static/assets/avatars")

# Expected file extensions for avatars
REQUIRED_FILES = {
    'obj': '.obj',      # 3D model file
    'mtl': '.mtl',      # Material file
    'texture': '.png',  # Texture file
    'thumbnail': '!.png'  # Thumbnail with ! suffix
}

def scan_source_directory():
    """Scan the source directory and show what avatars would be added."""
    print("🔍 Scanning source directory for new avatars...")
    print(f"📁 Source: {SOURCE_DIR}")
    print("=" * 60)
    
    if not SOURCE_DIR.exists():
        print(f"❌ ERROR: Source directory does not exist: {SOURCE_DIR}")
        return []
    
    found_avatars = []
    
    # Look for avatar folders or files
    for item in SOURCE_DIR.iterdir():
        if item.is_dir():
            # Directory-based avatar (preferred structure)
            avatar_info = analyze_avatar_directory(item)
            if avatar_info:
                found_avatars.append(avatar_info)
        elif item.is_file() and item.suffix.lower() in ['.obj', '.glb', '.fbx']:
            # File-based avatar (needs organization)
            avatar_info = analyze_avatar_file(item)
            if avatar_info:
                found_avatars.append(avatar_info)
    
    print(f"\n✅ Found {len(found_avatars)} potential avatars:")
    for i, avatar in enumerate(found_avatars, 1):
        print(f"\n{i}. {avatar['name']}")
        print(f"   📁 Folder: {avatar['folder_name']}")
        print(f"   📄 Files found:")
        for file_type, path in avatar['files'].items():
            status = "✅" if path and Path(path).exists() else "❌"
            print(f"      {status} {file_type}: {Path(path).name if path else 'MISSING'}")
        print(f"   🎯 Completeness: {avatar['completeness']:.0%}")
    
    return found_avatars

def analyze_avatar_directory(dir_path):
    """Analyze a directory to see if it contains a complete avatar."""
    folder_name = dir_path.name.lower().replace(' ', '-').replace('_', '-')
    avatar_name = format_avatar_name(dir_path.name)
    
    files = {}
    potential_base_names = [
        dir_path.name,
        avatar_name.replace(' ', ''),
        avatar_name.replace(' ', '_'),
        folder_name.replace('-', ''),
        folder_name.replace('-', '_')
    ]
    
    # Look for each required file type
    for file_type, extension in REQUIRED_FILES.items():
        found_file = None
        
        for base_name in potential_base_names:
            candidates = [
                dir_path / f"{base_name}{extension}",
                dir_path / f"{base_name.lower()}{extension}",
                dir_path / f"{base_name.title()}{extension}",
            ]
            
            for candidate in candidates:
                if candidate.exists():
                    found_file = candidate
                    break
            
            if found_file:
                break
        
        # Special case for thumbnail (may have ! in name)
        if not found_file and file_type == 'thumbnail':
            for file in dir_path.glob("*!.png"):
                found_file = file
                break
            if not found_file:
                for file in dir_path.glob("*.png"):
                    if file.name.lower() != files.get('texture', '').lower():
                        found_file = file
                        break
        
        files[file_type] = str(found_file) if found_file else None
    
    # Calculate completeness
    required_count = len(REQUIRED_FILES)
    found_count = sum(1 for f in files.values() if f)
    completeness = found_count / required_count
    
    return {
        'name': avatar_name,
        'folder_name': folder_name,
        'source_path': dir_path,
        'files': files,
        'completeness': completeness,
        'type': 'directory'
    }

def analyze_avatar_file(file_path):
    """Analyze a single avatar file."""
    base_name = file_path.stem
    folder_name = base_name.lower().replace(' ', '-').replace('_', '-')
    avatar_name = format_avatar_name(base_name)
    
    # Look for related files in the same directory
    files = {'obj': None, 'mtl': None, 'texture': None, 'thumbnail': None}
    
    if file_path.suffix.lower() == '.obj':
        files['obj'] = str(file_path)
        
        # Look for MTL file
        mtl_file = file_path.with_suffix('.mtl')
        if mtl_file.exists():
            files['mtl'] = str(mtl_file)
        
        # Look for texture file
        for ext in ['.png', '.jpg', '.jpeg']:
            texture_file = file_path.with_suffix(ext)
            if texture_file.exists():
                files['texture'] = str(texture_file)
                break
        
        # Look for thumbnail
        thumbnail_file = file_path.with_suffix('!.png')
        if thumbnail_file.exists():
            files['thumbnail'] = str(thumbnail_file)
    
    # Calculate completeness
    found_count = sum(1 for f in files.values() if f)
    completeness = found_count / len(REQUIRED_FILES)
    
    return {
        'name': avatar_name,
        'folder_name': folder_name,
        'source_path': file_path.parent,
        'files': files,
        'completeness': completeness,
        'type': 'file'
    }

def format_avatar_name(raw_name):
    """Format a raw name into a proper avatar name."""
    # Remove common suffixes and clean up
    name = raw_name.replace('Bee', '').replace('bee', '').strip()
    name = name.replace('_', ' ').replace('-', ' ')
    
    # Capitalize each word
    words = []
    for word in name.split():
        if word.lower() in ['3d', 'ai', 'vr', 'ar']:
            words.append(word.upper())
        else:
            words.append(word.capitalize())
    
    formatted = ' '.join(words)
    
    # Add "Bee" suffix if not present
    if not formatted.lower().endswith('bee'):
        formatted += ' Bee'
    
    return formatted

def copy_avatar_files(avatar_info):
    """Copy avatar files to the destination directory."""
    dest_folder = DEST_DIR / avatar_info['folder_name']
    dest_folder.mkdir(exist_ok=True)
    
    print(f"📁 Creating directory: {dest_folder}")
    
    copied_files = {}
    
    for file_type, source_path in avatar_info['files'].items():
        if not source_path or not Path(source_path).exists():
            print(f"   ⚠️  Skipping {file_type}: file not found")
            continue
        
        source_file = Path(source_path)
        
        # Determine destination filename
        if file_type == 'thumbnail':
            dest_name = f"{avatar_info['name'].replace(' ', '')}.png"
        else:
            dest_name = f"{avatar_info['name'].replace(' ', '')}{REQUIRED_FILES[file_type]}"
        
        dest_file = dest_folder / dest_name
        
        try:
            shutil.copy2(source_file, dest_file)
            print(f"   ✅ Copied {file_type}: {dest_name}")
            copied_files[file_type] = dest_name
        except Exception as e:
            print(f"   ❌ Failed to copy {file_type}: {e}")
    
    return copied_files

def add_avatar_to_database(avatar_info, copied_files):
    """Add the avatar to the database."""
    with app.app_context():
        # Check if avatar already exists
        existing = Avatar.query.filter_by(slug=avatar_info['folder_name']).first()
        if existing:
            print(f"   ⚠️  Avatar {avatar_info['folder_name']} already exists in database")
            return existing
        
        # Get next sort order
        max_sort = db.session.query(db.func.max(Avatar.sort_order)).scalar() or 0
        
        # Create new avatar record
        avatar = Avatar(
            slug=avatar_info['folder_name'],
            name=avatar_info['name'],
            description=f"A {avatar_info['name'].lower()} character for spelling adventures",
            category='classic',
            folder_path=avatar_info['folder_name'],
            obj_file=copied_files.get('obj'),
            mtl_file=copied_files.get('mtl'),
            texture_file=copied_files.get('texture'),
            thumbnail_file=copied_files.get('thumbnail'),
            unlock_level=1,
            points_required=0,
            is_premium=False,
            sort_order=max_sort + 1,
            is_active=True
        )
        
        try:
            db.session.add(avatar)
            db.session.commit()
            print(f"   ✅ Added to database: ID {avatar.id}")
            return avatar
        except Exception as e:
            db.session.rollback()
            print(f"   ❌ Database error: {e}")
            return None

def copy_all_avatars(avatars):
    """Copy all avatars and add them to the database."""
    print("\n🚀 Starting avatar integration process...")
    print("=" * 60)
    
    success_count = 0
    
    for i, avatar_info in enumerate(avatars, 1):
        print(f"\n{i}/{len(avatars)}. Processing {avatar_info['name']}...")
        
        if avatar_info['completeness'] < 0.5:
            print(f"   ⚠️  Skipping: completeness too low ({avatar_info['completeness']:.0%})")
            continue
        
        # Copy files
        copied_files = copy_avatar_files(avatar_info)
        
        if not copied_files:
            print(f"   ❌ No files copied, skipping database entry")
            continue
        
        # Add to database
        avatar_record = add_avatar_to_database(avatar_info, copied_files)
        
        if avatar_record:
            success_count += 1
            print(f"   🎉 Successfully integrated {avatar_info['name']}")
    
    print(f"\n✅ Integration complete! Added {success_count}/{len(avatars)} avatars")
    return success_count

def verify_avatars():
    """Verify all avatars are working correctly."""
    print("🔍 Verifying avatar integration...")
    print("=" * 60)
    
    with app.app_context():
        avatars = Avatar.query.filter_by(is_active=True).order_by(Avatar.sort_order).all()
        
        print(f"📊 Found {len(avatars)} active avatars in database:")
        
        issues = []
        
        for avatar in avatars:
            print(f"\n🐝 {avatar.name} ({avatar.slug})")
            avatar_folder = DEST_DIR / avatar.folder_path
            
            # Check folder exists
            if not avatar_folder.exists():
                issue = f"❌ Folder missing: {avatar_folder}"
                print(f"   {issue}")
                issues.append(issue)
                continue
            
            # Check each file
            file_checks = [
                ('OBJ', avatar.obj_file),
                ('MTL', avatar.mtl_file),
                ('Texture', avatar.texture_file),
                ('Thumbnail', avatar.thumbnail_file)
            ]
            
            for file_type, filename in file_checks:
                if filename:
                    file_path = avatar_folder / filename
                    if file_path.exists():
                        print(f"   ✅ {file_type}: {filename}")
                    else:
                        issue = f"❌ {avatar.name}: Missing {file_type} file: {filename}"
                        print(f"   {issue}")
                        issues.append(issue)
                else:
                    issue = f"⚠️  {avatar.name}: No {file_type} filename in database"
                    print(f"   {issue}")
                    issues.append(issue)
        
        if issues:
            print(f"\n⚠️  Found {len(issues)} issues:")
            for issue in issues:
                print(f"   {issue}")
            return False
        else:
            print(f"\n🎉 All {len(avatars)} avatars verified successfully!")
            return True

def main():
    parser = argparse.ArgumentParser(description="Add new avatars to BeeSmart app")
    parser.add_argument('--scan', action='store_true', help='Scan source directory')
    parser.add_argument('--copy', action='store_true', help='Copy files and add to database')
    parser.add_argument('--verify', action='store_true', help='Verify existing avatars')
    
    args = parser.parse_args()
    
    if args.scan:
        avatars = scan_source_directory()
        if avatars:
            print(f"\n💡 Next steps:")
            print(f"   python add_new_avatars.py --copy     # Copy files and add to database")
            print(f"   python add_new_avatars.py --verify   # Verify everything works")
    
    elif args.copy:
        avatars = scan_source_directory()
        if avatars:
            response = input(f"\n❓ Copy {len(avatars)} avatars to the app? (y/N): ")
            if response.lower() in ['y', 'yes']:
                copy_all_avatars(avatars)
            else:
                print("❌ Operation cancelled")
    
    elif args.verify:
        verify_avatars()
    
    else:
        print(__doc__)
        print("\nAvailable commands:")
        print("  --scan    Scan source directory for new avatars")
        print("  --copy    Copy avatars and add to database")
        print("  --verify  Verify all avatars are working")

if __name__ == "__main__":
    main()