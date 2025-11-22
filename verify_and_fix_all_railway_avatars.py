#!/usr/bin/env python3
"""
Comprehensive Railway Avatar Verification & Fix Script
======================================================
Verifies all avatars in Railway database are using GLB format and fixes any OBJ references.
Also validates thumbnail paths and provides detailed reporting.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import sys
from datetime import datetime

# Railway PostgreSQL connection
RAILWAY_DB = "postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway"

def get_all_avatars():
    """Fetch all avatars from Railway database."""
    conn = psycopg2.connect(RAILWAY_DB)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, slug, name, folder_path, obj_file, thumbnail_file, 
                       category, is_active, created_at, updated_at
                FROM avatars 
                ORDER BY slug
            """)
            avatars = cur.fetchall()
            return avatars
    finally:
        conn.close()

def analyze_avatar_issues(avatars):
    """Analyze all avatars and categorize issues."""
    issues = {
        'obj_references': [],      # Avatars still using .obj files
        'wrong_folder': [],         # Avatars not in glb_files folder
        'missing_thumbnail': [],    # Avatars without thumbnails
        'inactive': [],             # Inactive avatars
        'correct': []               # Avatars already correct
    }
    
    for avatar in avatars:
        slug = avatar['slug']
        obj_file = avatar['obj_file'] or ''
        folder_path = avatar['folder_path'] or ''
        thumbnail = avatar['thumbnail_file'] or ''
        is_active = avatar['is_active']
        
        if not is_active:
            issues['inactive'].append({
                'slug': slug,
                'reason': 'Avatar is inactive'
            })
            continue
        
        has_obj = obj_file.lower().endswith('.obj')
        wrong_folder = folder_path != 'glb_files' and not folder_path.startswith('glb_files/')
        missing_thumb = not thumbnail or thumbnail.strip() == ''
        
        if has_obj:
            issues['obj_references'].append({
                'slug': slug,
                'obj_file': obj_file,
                'folder_path': folder_path,
                'issue': 'Using .obj instead of .glb'
            })
        
        if wrong_folder and is_active:
            issues['wrong_folder'].append({
                'slug': slug,
                'folder_path': folder_path,
                'issue': f'Folder should be glb_files, not {folder_path}'
            })
        
        if missing_thumb:
            issues['missing_thumbnail'].append({
                'slug': slug,
                'thumbnail': thumbnail,
                'issue': 'Missing or empty thumbnail path'
            })
        
        # Check if correct
        if not has_obj and not wrong_folder and not missing_thumb:
            issues['correct'].append({
                'slug': slug,
                'obj_file': obj_file,
                'folder_path': folder_path,
                'thumbnail': thumbnail
            })
    
    return issues

def fix_avatar(slug, new_obj_file=None, new_folder_path=None, new_thumbnail=None):
    """Fix a single avatar in Railway database."""
    conn = psycopg2.connect(RAILWAY_DB)
    try:
        with conn.cursor() as cur:
            updates = []
            params = []
            
            if new_obj_file:
                updates.append("obj_file = %s")
                params.append(new_obj_file)
            
            if new_folder_path:
                updates.append("folder_path = %s")
                params.append(new_folder_path)
            
            if new_thumbnail:
                updates.append("thumbnail_file = %s")
                params.append(new_thumbnail)
            
            if updates:
                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(slug)
                
                sql = f"""
                    UPDATE avatars 
                    SET {', '.join(updates)}
                    WHERE slug = %s
                """
                cur.execute(sql, params)
                conn.commit()
                return True
            return False
    except Exception as e:
        print(f"❌ Error fixing {slug}: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def generate_glb_filename(obj_filename):
    """Convert .obj filename to .glb filename."""
    if obj_filename.lower().endswith('.obj'):
        return obj_filename[:-4] + '.glb'
    return obj_filename

def generate_thumbnail_filename(slug):
    """Generate thumbnail filename from slug."""
    # Convert slug to PascalCase for thumbnail naming
    parts = slug.split('-')
    pascal_name = ''.join(word.capitalize() for word in parts)
    return f"AvatarThumbnails/{pascal_name}!.png"

def print_report(issues):
    """Print comprehensive issue report."""
    print("\n" + "="*70)
    print("🐝 RAILWAY AVATAR DATABASE VERIFICATION REPORT")
    print("="*70)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Database: Railway PostgreSQL")
    print("="*70)
    
    total = sum(len(v) for v in issues.values())
    print(f"\n📊 SUMMARY: {total} avatars analyzed")
    print(f"  ✅ Correct: {len(issues['correct'])}")
    print(f"  ⚠️  OBJ References: {len(issues['obj_references'])}")
    print(f"  📁 Wrong Folder: {len(issues['wrong_folder'])}")
    print(f"  🖼️  Missing Thumbnails: {len(issues['missing_thumbnail'])}")
    print(f"  💤 Inactive: {len(issues['inactive'])}")
    
    if issues['obj_references']:
        print(f"\n{'='*70}")
        print(f"⚠️  AVATARS WITH OBJ REFERENCES ({len(issues['obj_references'])})")
        print(f"{'='*70}")
        for item in issues['obj_references']:
            print(f"  • {item['slug']}")
            print(f"    Current: {item['folder_path']}/{item['obj_file']}")
            print(f"    Issue: {item['issue']}")
    
    if issues['wrong_folder']:
        print(f"\n{'='*70}")
        print(f"📁 AVATARS IN WRONG FOLDER ({len(issues['wrong_folder'])})")
        print(f"{'='*70}")
        for item in issues['wrong_folder']:
            print(f"  • {item['slug']}: {item['folder_path']} → glb_files")
    
    if issues['missing_thumbnail']:
        print(f"\n{'='*70}")
        print(f"🖼️  AVATARS WITH MISSING THUMBNAILS ({len(issues['missing_thumbnail'])})")
        print(f"{'='*70}")
        for item in issues['missing_thumbnail']:
            print(f"  • {item['slug']}: '{item['thumbnail']}'")
    
    if issues['correct']:
        print(f"\n{'='*70}")
        print(f"✅ CORRECT AVATARS ({len(issues['correct'])})")
        print(f"{'='*70}")
        for item in issues['correct'][:5]:  # Show first 5
            print(f"  • {item['slug']}: {item['folder_path']}/{item['obj_file']}")
        if len(issues['correct']) > 5:
            print(f"  ... and {len(issues['correct']) - 5} more")
    
    print(f"\n{'='*70}")

def main():
    """Main verification and fix routine."""
    print("🐝 BeeSmart Railway Avatar Verification & Fix Tool")
    print("="*70)
    
    # Fetch all avatars
    print("\n📡 Connecting to Railway database...")
    try:
        avatars = get_all_avatars()
        print(f"✅ Fetched {len(avatars)} avatars from database")
    except Exception as e:
        print(f"❌ Failed to connect to Railway database: {e}")
        sys.exit(1)
    
    # Analyze issues
    print("\n🔍 Analyzing avatar configurations...")
    issues = analyze_avatar_issues(avatars)
    
    # Print report
    print_report(issues)
    
    # Ask user if they want to fix issues
    total_issues = len(issues['obj_references']) + len(issues['wrong_folder']) + len(issues['missing_thumbnail'])
    
    if total_issues == 0:
        print("\n🎉 All avatars are correctly configured!")
        return
    
    print(f"\n⚠️  Found {total_issues} issues that can be fixed automatically.")
    response = input("\n🔧 Do you want to fix these issues? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("\n❌ Fix cancelled. No changes made.")
        return
    
    print("\n🔧 Starting fixes...\n")
    fixed_count = 0
    failed_count = 0
    
    # Fix OBJ references
    for item in issues['obj_references']:
        slug = item['slug']
        old_obj = item['obj_file']
        new_obj = generate_glb_filename(old_obj)
        
        print(f"🔄 Fixing {slug}: {old_obj} → {new_obj}")
        if fix_avatar(slug, new_obj_file=new_obj, new_folder_path='glb_files'):
            print(f"  ✅ Updated {slug}")
            fixed_count += 1
        else:
            print(f"  ❌ Failed to update {slug}")
            failed_count += 1
    
    # Fix wrong folders
    for item in issues['wrong_folder']:
        if item['slug'] not in [i['slug'] for i in issues['obj_references']]:  # Skip if already fixed above
            slug = item['slug']
            print(f"📁 Fixing folder for {slug}: {item['folder_path']} → glb_files")
            if fix_avatar(slug, new_folder_path='glb_files'):
                print(f"  ✅ Updated {slug}")
                fixed_count += 1
            else:
                print(f"  ❌ Failed to update {slug}")
                failed_count += 1
    
    # Fix missing thumbnails
    for item in issues['missing_thumbnail']:
        if item['slug'] not in [i['slug'] for i in issues['obj_references']]:  # Skip if already fixed above
            slug = item['slug']
            new_thumb = generate_thumbnail_filename(slug)
            print(f"🖼️  Fixing thumbnail for {slug}: → {new_thumb}")
            if fix_avatar(slug, new_thumbnail=new_thumb):
                print(f"  ✅ Updated {slug}")
                fixed_count += 1
            else:
                print(f"  ❌ Failed to update {slug}")
                failed_count += 1
    
    # Final summary
    print(f"\n{'='*70}")
    print("🎯 FIX SUMMARY")
    print(f"{'='*70}")
    print(f"✅ Successfully fixed: {fixed_count}")
    print(f"❌ Failed to fix: {failed_count}")
    print(f"{'='*70}\n")
    
    if fixed_count > 0:
        print("💡 Tip: Clear your browser cache and refresh Railway to see changes.")
    
    # Verify fixes
    if fixed_count > 0:
        response = input("\n🔍 Verify fixes by running analysis again? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            print("\n🔄 Re-analyzing database...\n")
            avatars = get_all_avatars()
            issues = analyze_avatar_issues(avatars)
            print_report(issues)

if __name__ == "__main__":
    main()
