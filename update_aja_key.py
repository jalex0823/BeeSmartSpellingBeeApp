"""
Quick script to update Aja's teacher_key
"""
import os
os.environ['DATABASE_URL'] = 'postgresql://postgres:HkctClwSCljJtdOEpWICVhsSMqxKPbQf@shuttle.proxy.rlwy.net:46186/railway'

from AjaSpellBApp import app, db
from models import User

with app.app_context():
    # Find Aja by username (her username is PRINCESS)
    aja = User.query.filter_by(username='PRINCESS').first()
    
    if aja:
        print(f"Found user: {aja.display_name} (username: {aja.username})")
        print(f"Current teacher_key: {aja.teacher_key}")
        
        # Update teacher_key
        aja.teacher_key = 'BEE-2025-BIG-P7TC'
        db.session.commit()
        
        print(f"✅ Updated teacher_key to: {aja.teacher_key}")
        print(f"\nAja should now appear in BigDaddy2's admin dashboard!")
    else:
        print("❌ User 'Aja' not found")
        print("\nAvailable users:")
        all_users = User.query.all()
        for user in all_users:
            print(f"  - {user.username} ({user.display_name}) - Role: {user.role}")
