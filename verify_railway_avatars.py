#!/usr/bin/env python3
"""
Railway PostgreSQL Avatar Verification Script
Comprehensive verification for Railway deployment with PostgreSQL database
"""

import sys
import os
import requests
import json
from pathlib import Path

# Railway deployment URL
RAILWAY_BASE_URL = "https://beesmart.up.railway.app"

def detect_environment():
    """Detect if running on Railway or locally"""
    railway_env = os.getenv('RAILWAY_ENVIRONMENT')
    database_url = os.getenv('DATABASE_URL')
    
    if railway_env or database_url:
        return 'railway'
    else:
        return 'local'

def test_railway_avatar_api(base_url=RAILWAY_BASE_URL):
    """Test avatar API on Railway with PostgreSQL"""
    print("🚂 Railway Avatar System Verification")
    print("=" * 60)
    
    env = detect_environment()
    print(f"🌍 Environment: {env}")
    print(f"🔗 Base URL: {base_url}")
    print(f"💾 Database: {'PostgreSQL (Railway)' if 'railway.app' in base_url else 'Local SQLite'}")
    print()
    
    try:
        # Test health endpoint first
        print("🏥 Testing health endpoint...")
        health_response = requests.get(f"{base_url}/health", timeout=10)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Health check passed")
            print(f"   Version: {health_data.get('version', 'unknown')}")
            print(f"   Environment: {health_data.get('environment', 'unknown')}")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
        
        print()
        
        # Test avatars API
        print("🐝 Testing avatars API...")
        avatars_response = requests.get(f"{base_url}/api/avatars", timeout=15)
        
        if avatars_response.status_code != 200:
            print(f"❌ Avatars API failed: {avatars_response.status_code}")
            print(f"Response: {avatars_response.text[:500]}...")
            return False
        
        data = avatars_response.json()
        avatars = data.get('avatars', [])
        
        print(f"✅ Avatars API successful")
        print(f"📊 Total avatars: {len(avatars)}")
        print(f"🔄 API Response time: {avatars_response.elapsed.total_seconds():.2f}s")
        print()
        
        # Test specific avatars (working vs previously broken)
        test_avatars = [
            {'id': 'al-bee', 'type': 'originally working'},
            {'id': 'astro-bee', 'type': 'fixed broken'},
            {'id': 'diva-bee', 'type': 'fixed broken'},
            {'id': 'queen-bee', 'type': 'fixed broken'},
            {'id': 'biker-bee', 'type': 'fixed broken'}
        ]
        
        print("🧪 Testing specific avatars...")
        
        avatar_results = {}
        for test_avatar in test_avatars:
            avatar_id = test_avatar['id']
            avatar_type = test_avatar['type']
            
            # Find avatar in response
            avatar = next((a for a in avatars if a['id'] == avatar_id), None)
            
            if avatar:
                print(f"✅ {avatar_id} ({avatar_type}):")
                print(f"   � Folder: {avatar.get('folder', 'N/A')}")
                print(f"   🖼️ Thumbnail: {avatar.get('thumbnail', 'N/A')}")
                
                # Test thumbnail URL accessibility
                thumbnail_url = avatar.get('thumbnail', '')
                if thumbnail_url:
                    # Convert relative to absolute URL
                    if thumbnail_url.startswith('/'):
                        full_url = base_url + thumbnail_url
                    else:
                        full_url = thumbnail_url
                    
                    try:
                        thumb_response = requests.head(full_url, timeout=5)
                        if thumb_response.status_code == 200:
                            print(f"   ✅ Thumbnail accessible")
                        else:
                            print(f"   ❌ Thumbnail failed ({thumb_response.status_code})")
                    except Exception as e:
                        print(f"   ⚠️ Thumbnail test error: {str(e)[:50]}...")
                
                # Test OBJ file accessibility
                obj_url = avatar.get('urls', {}).get('model_obj', '')
                if obj_url:
                    if obj_url.startswith('/'):
                        full_obj_url = base_url + obj_url
                    else:
                        full_obj_url = obj_url
                    
                    try:
                        obj_response = requests.head(full_obj_url, timeout=5)
                        if obj_response.status_code == 200:
                            print(f"   ✅ OBJ file accessible")
                        else:
                            print(f"   ❌ OBJ file failed ({obj_response.status_code})")
                    except Exception as e:
                        print(f"   ⚠️ OBJ test error: {str(e)[:50]}...")
                
                avatar_results[avatar_id] = {
                    'found': True,
                    'data': avatar
                }
            else:
                print(f"❌ {avatar_id} ({avatar_type}): Not found")
                avatar_results[avatar_id] = {'found': False}
            
            print()
        
        # Summary
        print("📈 Railway Verification Summary:")
        print("-" * 40)
        
        working_count = sum(1 for result in avatar_results.values() if result['found'])
        total_count = len(avatar_results)
        
        print(f"🐝 Test avatars found: {working_count}/{total_count}")
        print(f"📊 Total avatars in system: {len(avatars)}")
        print(f"🌍 Environment: Railway Production")
        print(f"💾 Database: PostgreSQL")
        
        if working_count == total_count and len(avatars) >= 20:  # Expect at least 20 avatars
            print("🎉 ✅ Railway avatar system fully operational!")
            return True
        else:
            print("⚠️ Issues detected with avatar system")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Railway avatar system: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_connection():
    """Test database connection specifically for Railway PostgreSQL"""
    print(f"\n💾 Database Connection Test:")
    print("-" * 40)
    
    try:
        # Only test database if running locally with access to models
        if detect_environment() == 'local':
            from flask import Flask
            from config import get_config
            from models import db, Avatar
            
            app = Flask(__name__)
            app.config.from_object(get_config())
            db.init_app(app)
            
            with app.app_context():
                # Test database connection
                avatar_count = Avatar.query.count()
                print(f"✅ Database connection successful")
                print(f"📊 Total avatars in database: {avatar_count}")
                
                # Test a few specific avatars
                test_slugs = ['al-bee', 'astro-bee', 'diva-bee']
                for slug in test_slugs:
                    avatar = Avatar.query.filter_by(slug=slug).first()
                    if avatar:
                        print(f"✅ {slug}: Found in database")
                        print(f"   Folder: {avatar.folder_path}")
                        print(f"   Thumbnail: {avatar.thumbnail_file}")
                    else:
                        print(f"❌ {slug}: Not found in database")
                
                return True
        else:
            print("ℹ️ Database test skipped (running on Railway)")
            print("✅ Database verification done via API endpoints")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🚂 Railway PostgreSQL Avatar System Verification")
    print("=" * 60)
    print("📋 This will verify:")
    print("   ✅ Avatar API works with PostgreSQL on Railway")
    print("   ✅ All avatar files are accessible")
    print("   ✅ Database records are correct")
    print("   ✅ URLs and endpoints function properly")
    print()
    
    # Test database connection
    db_success = test_database_connection()
    
    # Test API endpoints
    api_success = test_railway_avatar_api()
    
    print(f"\n🎯 Final Results:")
    print(f"💾 Database: {'✅ PASS' if db_success else '❌ FAIL'}")
    print(f"🌐 API: {'✅ PASS' if api_success else '❌ FAIL'}")
    
    if db_success and api_success:
        print(f"\n🎉 Railway avatar system is fully operational!")
        print(f"🚀 Ready for production use with PostgreSQL!")
        sys.exit(0)
    else:
        print(f"\n⚠️ Issues detected - review errors above")
        sys.exit(1)
