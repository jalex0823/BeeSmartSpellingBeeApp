"""
Comprehensive Avatar File Structure Validator
Checks all avatar directories for required files and reports any issues.
"""

import os
from pathlib import Path
from avatar_catalog import AVATAR_CATALOG

# Base path for avatars
AVATAR_BASE_PATH = Path("static/assets/avatars")

# Required files for each avatar
REQUIRED_FILES = [
    "model.obj",
    "model.mtl",
    "texture.png",
    "thumbnail.png"
]

def validate_avatar_directory(avatar_id, folder_name):
    """Validate a single avatar directory for required files."""
    avatar_path = AVATAR_BASE_PATH / folder_name
    issues = []
    
    # Check if directory exists
    if not avatar_path.exists():
        return {
            'id': avatar_id,
            'folder': folder_name,
            'exists': False,
            'issues': [f"❌ Directory not found: {avatar_path}"],
            'files': {}
        }
    
    # Check for required files
    files_status = {}
    for required_file in REQUIRED_FILES:
        file_path = avatar_path / required_file
        exists = file_path.exists()
        files_status[required_file] = {
            'exists': exists,
            'path': str(file_path),
            'size': file_path.stat().st_size if exists else 0
        }
        
        if not exists:
            issues.append(f"❌ Missing: {required_file}")
    
    # List all files in directory
    all_files = []
    if avatar_path.exists():
        all_files = [f.name for f in avatar_path.iterdir() if f.is_file()]
    
    return {
        'id': avatar_id,
        'folder': folder_name,
        'exists': True,
        'path': str(avatar_path),
        'issues': issues,
        'files': files_status,
        'all_files': all_files,
        'file_count': len(all_files)
    }

def main():
    """Run validation on all avatars in catalog."""
    print("=" * 80)
    print("🐝 BEESMART AVATAR FILE STRUCTURE VALIDATION")
    print("=" * 80)
    print()
    
    total_avatars = len(AVATAR_CATALOG)
    valid_avatars = 0
    avatars_with_issues = 0
    
    results = []
    
    for avatar in AVATAR_CATALOG:
        avatar_id = avatar.get('id')
        folder_name = avatar.get('folder')
        name = avatar.get('name')
        
        print(f"Checking: {name} ({avatar_id})")
        print(f"  Folder: {folder_name}")
        
        result = validate_avatar_directory(avatar_id, folder_name)
        results.append(result)
        
        if result['exists']:
            if not result['issues']:
                print(f"  ✅ All required files present ({result['file_count']} total files)")
                valid_avatars += 1
            else:
                print(f"  ⚠️  Issues found:")
                for issue in result['issues']:
                    print(f"      {issue}")
                avatars_with_issues += 1
        else:
            print(f"  ❌ Directory does not exist!")
            avatars_with_issues += 1
        
        print()
    
    # Summary Report
    print("=" * 80)
    print("📊 VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Total Avatars in Catalog: {total_avatars}")
    print(f"✅ Valid Avatars: {valid_avatars}")
    print(f"⚠️  Avatars with Issues: {avatars_with_issues}")
    print()
    
    # Detailed Issues Report
    if avatars_with_issues > 0:
        print("=" * 80)
        print("⚠️  DETAILED ISSUES REPORT")
        print("=" * 80)
        
        for result in results:
            if result['issues'] or not result['exists']:
                print(f"\n{result['id']} ({result['folder']}):")
                if not result['exists']:
                    print(f"  ❌ Directory does not exist: {AVATAR_BASE_PATH / result['folder']}")
                else:
                    for issue in result['issues']:
                        print(f"  {issue}")
                    print(f"  Files found: {', '.join(result['all_files'])}")
    
    # File Size Report (for valid avatars)
    print("\n" + "=" * 80)
    print("📁 FILE SIZE REPORT (Valid Avatars)")
    print("=" * 80)
    
    for result in results:
        if result['exists'] and not result['issues']:
            print(f"\n{result['id']}:")
            total_size = 0
            for file_name, file_info in result['files'].items():
                size_kb = file_info['size'] / 1024
                total_size += file_info['size']
                print(f"  {file_name}: {size_kb:.1f} KB")
            print(f"  Total: {total_size / 1024:.1f} KB")
    
    print("\n" + "=" * 80)
    print("✅ VALIDATION COMPLETE")
    print("=" * 80)
    
    return valid_avatars == total_avatars

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
