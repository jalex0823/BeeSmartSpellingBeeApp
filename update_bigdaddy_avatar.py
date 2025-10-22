"""
Script to update BigDaddy2's avatar to Professor Bee
"""
import os
os.environ['DATABASE_URL'] = 'postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway'

from AjaSpellBApp import app, db
from models import User

with app.app_context():
    # Find BigDaddy2
    bigdaddy = User.query.filter_by(username='BigDaddy2').first()
    
    if bigdaddy:
        print(f"✅ Found user: {bigdaddy.display_name} (username: {bigdaddy.username})")
        print(f"📝 Current avatar: {bigdaddy.avatar_id}")
        print(f"📝 Current variant: {bigdaddy.avatar_variant}")
        
        # Update to Professor Bee
        bigdaddy.avatar_id = 'professor-bee'
        bigdaddy.avatar_variant = 'default'
        
        db.session.commit()
        
        print(f"\n🎉 SUCCESS! Avatar updated!")
        print(f"✅ New avatar: professor-bee")
        print(f"✅ New variant: default")
        print(f"\n🐝 Professor Bee is now active on your account!")
        
    else:
        print("❌ User 'BigDaddy2' not found")
        
        # Show available users
        print("\nAvailable users:")
        all_users = User.query.all()
        for user in all_users:
            print(f"  - {user.username} ({user.display_name}) - Role: {user.role}")
