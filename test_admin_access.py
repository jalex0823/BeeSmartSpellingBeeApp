#!/usr/bin/env python3
"""
Quick test script to check admin access and routes
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from AjaSpellBApp import app, db, User
from flask import url_for

def check_admin_routes():
    """Check if admin routes are properly registered"""
    with app.app_context():
        try:
            admin_url = url_for('admin_dashboard')
            print(f"✅ Admin dashboard URL: {admin_url}")
            return True
        except Exception as e:
            print(f"❌ Admin route error: {e}")
            return False

def check_admin_users():
    """Check for existing admin users"""
    with app.app_context():
        try:
            admin_users = User.query.filter_by(role='admin').all()
            print(f"\n📊 Admin users found: {len(admin_users)}")
            
            for user in admin_users:
                print(f"   - {user.username} (ID: {user.id}) - Teacher Key: {user.teacher_key}")
                
            if not admin_users:
                print("⚠️  No admin users found!")
                print("💡 You may need to create an admin user or promote an existing user")
                
        except Exception as e:
            print(f"❌ Database error: {e}")

def check_routes():
    """List all registered routes"""
    with app.app_context():
        admin_routes = []
        for rule in app.url_map.iter_rules():
            if 'admin' in rule.rule:
                admin_routes.append(f"{rule.rule} -> {rule.endpoint}")
        
        print(f"\n🔗 Admin routes registered: {len(admin_routes)}")
        for route in admin_routes:
            print(f"   {route}")

if __name__ == "__main__":
    print("🐝 BeeSmart Admin Access Test")
    print("=" * 40)
    
    # Test 1: Check routes
    routes_ok = check_admin_routes()
    
    # Test 2: Check admin users
    check_admin_users()
    
    # Test 3: List all admin routes
    check_routes()
    
    print("\n" + "=" * 40)
    if routes_ok:
        print("✅ Admin routes are properly registered")
        print("💡 If you can't access admin, check:")
        print("   1. Are you logged in as an admin user?")
        print("   2. Does the admin user exist?")
        print("   3. Is the user's role set to 'admin'?")
    else:
        print("❌ Admin routes have issues")