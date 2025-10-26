#!/usr/bin/env python3
"""
Compare working vs previously broken avatars to ensure identical API structure
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import get_config
from models import db, Avatar
from pathlib import Path
import requests
import json

def compare_avatar_endpoints():
    """Compare working vs fixed avatars to ensure identical API structure"""
    print("🔍 Avatar Endpoint Comparison Analysis")
    print("=" * 70)
    
    # Working avatar (one of the original 9)
    working_avatar = 'al-bee'
    
    # Previously broken avatar (one of the fixed 15)
    fixed_avatar = 'astro-bee'
    
    print(f"📊 Comparing:")
    print(f"   ✅ Working Avatar: {working_avatar}")
    print(f"   🔧 Fixed Avatar: {fixed_avatar}")
    print()
    
    try:
        # Get API data
        response = requests.get('http://127.0.0.1:5000/api/avatars', timeout=10)
        if response.status_code != 200:
            print(f"❌ API failed: {response.status_code}")
            return
        
        data = response.json()
        avatars = data.get('avatars', [])
        
        # Find our test avatars
        working_data = next((a for a in avatars if a['id'] == working_avatar), None)
        fixed_data = next((a for a in avatars if a['id'] == fixed_avatar), None)
        
        if not working_data:
            print(f"❌ Working avatar {working_avatar} not found")
            return
            
        if not fixed_data:
            print(f"❌ Fixed avatar {fixed_avatar} not found")
            return
        
        print("🎯 API Data Structure Comparison:")
        print("-" * 50)
        
        # Compare API structure
        compare_api_structure(working_data, fixed_data, working_avatar, fixed_avatar)
        
        print("\n🔗 URL Structure Comparison:")
        print("-" * 50)
        
        # Compare URL patterns
        compare_url_patterns(working_data, fixed_data, working_avatar, fixed_avatar)
        
        print("\n📁 Filesystem Verification:")
        print("-" * 50)
        
        # Verify filesystem files exist
        verify_filesystem_files(working_data, fixed_data, working_avatar, fixed_avatar)
        
        print("\n🧪 Full Avatar Samples:")
        print("-" * 50)
        
        # Show complete data for both
        show_complete_data(working_data, fixed_data, working_avatar, fixed_avatar)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def compare_api_structure(working, fixed, working_name, fixed_name):
    """Compare the API data structure between working and fixed avatars"""
    
    # Get all keys from both avatars
    working_keys = set(working.keys())
    fixed_keys = set(fixed.keys())
    
    print(f"📋 API Fields Comparison:")
    print(f"   Working ({working_name}): {len(working_keys)} fields")
    print(f"   Fixed ({fixed_name}): {len(fixed_keys)} fields")
    
    # Check for missing fields
    missing_in_fixed = working_keys - fixed_keys
    missing_in_working = fixed_keys - working_keys
    
    if missing_in_fixed:
        print(f"   ❌ Missing in fixed: {missing_in_fixed}")
    
    if missing_in_working:
        print(f"   ❌ Missing in working: {missing_in_working}")
    
    if not missing_in_fixed and not missing_in_working:
        print(f"   ✅ Both have identical field structure")
    
    # Compare specific important fields
    important_fields = ['id', 'name', 'folder', 'thumbnail', 'preview', 'urls']
    
    print(f"\n📊 Key Field Values:")
    for field in important_fields:
        if field in working and field in fixed:
            print(f"   {field}:")
            print(f"      Working: {working[field]}")
            print(f"      Fixed:   {fixed[field]}")
            
            # Check if URLs field structure matches
            if field == 'urls' and isinstance(working[field], dict) and isinstance(fixed[field], dict):
                working_url_keys = set(working[field].keys())
                fixed_url_keys = set(fixed[field].keys())
                
                if working_url_keys == fixed_url_keys:
                    print(f"      ✅ URL structure identical")
                else:
                    print(f"      ❌ URL structure differs:")
                    print(f"         Working URLs: {working_url_keys}")
                    print(f"         Fixed URLs: {fixed_url_keys}")
            print()

def compare_url_patterns(working, fixed, working_name, fixed_name):
    """Compare URL patterns and path structure"""
    
    # Extract URL paths
    working_urls = working.get('urls', {})
    fixed_urls = fixed.get('urls', {})
    
    print(f"🔗 URL Pattern Analysis:")
    
    url_types = ['model_obj', 'model_mtl', 'texture', 'thumbnail', 'preview']
    
    for url_type in url_types:
        if url_type in working_urls and url_type in fixed_urls:
            working_url = working_urls[url_type]
            fixed_url = fixed_urls[url_type]
            
            print(f"\n   {url_type}:")
            print(f"      Working: {working_url}")
            print(f"      Fixed:   {fixed_url}")
            
            # Analyze URL structure
            if working_url and fixed_url:
                # Check if both follow same pattern: /static/assets/avatars/{folder}/{file}
                working_parts = working_url.split('/')
                fixed_parts = fixed_url.split('/')
                
                if len(working_parts) == len(fixed_parts):
                    print(f"      ✅ Same URL depth ({len(working_parts)} parts)")
                    
                    # Check base path consistency
                    if working_parts[:-2] == fixed_parts[:-2]:  # Everything except folder and filename
                        print(f"      ✅ Same base path structure")
                    else:
                        print(f"      ❌ Different base paths")
                else:
                    print(f"      ❌ Different URL depths: {len(working_parts)} vs {len(fixed_parts)}")

def verify_filesystem_files(working, fixed, working_name, fixed_name):
    """Verify that all URLs point to actual files that exist"""
    
    assets_dir = Path("static/assets/avatars")
    
    print(f"📁 File Existence Check:")
    
    def check_avatar_files(avatar_data, avatar_name):
        folder = avatar_data.get('folder', '')
        folder_path = assets_dir / folder
        
        print(f"\n   {avatar_name} → {folder}")
        
        if not folder_path.exists():
            print(f"      ❌ Folder missing: {folder_path}")
            return False
        
        urls = avatar_data.get('urls', {})
        all_exist = True
        
        for url_type, url in urls.items():
            if url:
                # Extract filename from URL
                filename = url.split('/')[-1]
                file_path = folder_path / filename
                
                if file_path.exists():
                    print(f"      ✅ {url_type}: {filename}")
                else:
                    print(f"      ❌ {url_type}: {filename} (NOT FOUND)")
                    all_exist = False
        
        return all_exist
    
    working_ok = check_avatar_files(working, working_name)
    fixed_ok = check_avatar_files(fixed, fixed_name)
    
    print(f"\n📈 Filesystem Summary:")
    print(f"   Working avatar files: {'✅ All exist' if working_ok else '❌ Missing files'}")
    print(f"   Fixed avatar files: {'✅ All exist' if fixed_ok else '❌ Missing files'}")

def show_complete_data(working, fixed, working_name, fixed_name):
    """Show complete JSON data for both avatars"""
    
    print(f"📄 Complete Avatar Data:")
    
    print(f"\n🟢 {working_name} (Working Avatar):")
    print(json.dumps(working, indent=2))
    
    print(f"\n🔧 {fixed_name} (Fixed Avatar):")
    print(json.dumps(fixed, indent=2))

def run_database_comparison():
    """Compare database records for working vs fixed avatars"""
    print(f"\n💾 Database Record Comparison:")
    print("-" * 50)
    
    app = Flask(__name__)
    app.config.from_object(get_config())
    db.init_app(app)
    
    with app.app_context():
        working_avatar = Avatar.query.filter_by(slug='al-bee').first()
        fixed_avatar = Avatar.query.filter_by(slug='astro-bee').first()
        
        if working_avatar and fixed_avatar:
            print(f"🔍 Database Fields:")
            
            db_fields = ['slug', 'folder_path', 'thumbnail_file', 'obj_file', 'mtl_file', 'texture_file']
            
            for field in db_fields:
                working_val = getattr(working_avatar, field, 'N/A')
                fixed_val = getattr(fixed_avatar, field, 'N/A')
                
                print(f"   {field}:")
                print(f"      Working: {working_val}")
                print(f"      Fixed:   {fixed_val}")
                print()

if __name__ == "__main__":
    print("🐝 Avatar Endpoint Comparison Analysis")
    print("=" * 70)
    print("📋 This will compare a working avatar vs a fixed avatar to ensure:")
    print("   ✅ Identical API structure and field names")
    print("   ✅ Consistent URL patterns and endpoints")
    print("   ✅ All files exist on filesystem")
    print("   ✅ Database records are properly configured")
    
    compare_avatar_endpoints()
    run_database_comparison()
    
    print("\n🎉 Analysis complete! Review results above.")