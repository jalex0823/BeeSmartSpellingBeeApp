#!/usr/bin/env python3
"""
Compare database filenames with actual filesystem filenames
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import get_config
from models import db, Avatar
from pathlib import Path

def compare_database_vs_filesystem():
    """Compare what database expects vs what's actually on filesystem"""
    print("🔍 Database vs Filesystem Filename Comparison")
    print("=" * 70)
    
    app = Flask(__name__)
    app.config.from_object(get_config())
    db.init_app(app)
    
    assets_dir = Path("static/assets/avatars")
    
    with app.app_context():
        try:
            avatars = Avatar.query.all()
            print(f"📊 Found {len(avatars)} avatars in database\n")
            
            mismatches = []
            
            for avatar in avatars:
                print(f"🐝 {avatar.slug} → {avatar.folder_path}")
                
                folder_path = assets_dir / avatar.folder_path
                
                if not folder_path.exists():
                    print(f"   ❌ Folder missing: {folder_path}")
                    continue
                
                # Get actual files
                actual_files = [f.name for f in folder_path.iterdir() if f.is_file()]
                actual_files.sort()
                
                # Database expectations
                db_files = {
                    'thumbnail': avatar.thumbnail_file,
                    'obj': avatar.obj_file,
                    'mtl': avatar.mtl_file,
                    'texture': avatar.texture_file
                }
                
                print(f"   📁 Actual files: {actual_files}")
                print(f"   💾 Database expects:")
                
                folder_mismatches = []
                
                for file_type, db_filename in db_files.items():
                    if db_filename:
                        if db_filename in actual_files:
                            print(f"      ✅ {file_type}: {db_filename}")
                        else:
                            print(f"      ❌ {file_type}: {db_filename} (NOT FOUND)")
                            # Try to find similar files
                            similar = [f for f in actual_files if f.lower().endswith(db_filename.split('.')[-1].lower())]
                            if similar:
                                print(f"         💡 Similar files found: {similar}")
                                folder_mismatches.append({
                                    'type': file_type,
                                    'expected': db_filename,
                                    'candidates': similar
                                })
                            else:
                                folder_mismatches.append({
                                    'type': file_type,
                                    'expected': db_filename,
                                    'candidates': []
                                })
                    else:
                        print(f"      ⚪ {file_type}: (not set)")
                
                if folder_mismatches:
                    mismatches.append({
                        'avatar': avatar,
                        'folder_path': folder_path,
                        'actual_files': actual_files,
                        'mismatches': folder_mismatches
                    })
                
                print()
            
            print("=" * 70)
            print(f"📈 Summary: {len(mismatches)} avatars with filename mismatches")
            
            if mismatches:
                print(f"\n🔧 Avatars needing filename updates:")
                for item in mismatches:
                    avatar = item['avatar']
                    print(f"\n   🐝 {avatar.slug} ({avatar.folder_path}):")
                    for mismatch in item['mismatches']:
                        print(f"      {mismatch['type']}: {mismatch['expected']} → {mismatch['candidates']}")
            
            return mismatches
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return []

if __name__ == "__main__":
    mismatches = compare_database_vs_filesystem()
    
    if mismatches:
        print(f"\n❓ Would you like to see a fix script for these {len(mismatches)} mismatches?")
        print("   This will show what database updates are needed to match your new files.")
    else:
        print("✅ All avatar files match database expectations!")