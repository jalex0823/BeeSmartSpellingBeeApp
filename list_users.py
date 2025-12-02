#!/usr/bin/env python3
"""List all users in the database"""

from AjaSpellBApp import app, db
from models import User

with app.app_context():
    users = User.query.all()
    
    print(f"\n📋 Total Users: {len(users)}\n")
    
    for user in users:
        admin_marker = "👑" if user.role == 'admin' else ""
        premium_marker = "⭐" if user.premium_member else ""
        admin_access_marker = "🔓" if user.admin_all_access else ""
        
        print(f"{admin_marker}{premium_marker}{admin_access_marker} {user.username} ({user.display_name})")
        print(f"   Role: {user.role}, ID: {user.id}")
        if user.role == 'admin' or user.admin_all_access or user.premium_member:
            print(f"   admin_all_access={user.admin_all_access}, premium_member={user.premium_member}")
        print()
