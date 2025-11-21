"""
Check specific user's buzz dust and rank
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import db, User
from AjaSpellBApp import app
from buzz_dust_helpers import get_bee_class

with app.app_context():
    # Find user "Aja"
    user = User.query.filter_by(username='Aja').first()
    
    if not user:
        # Try display_name
        user = User.query.filter_by(display_name='Aja').first()
    
    if user:
        print("=" * 60)
        print(f"USER: {user.display_name or user.username}")
        print("=" * 60)
        print(f"Username: {user.username}")
        print(f"Total Buzz Dust: {user.total_buzz_dust or 0:,}")
        print(f"Stored Bee Class: {user.bee_class or 'None'}")
        print()
        
        # Calculate what rank SHOULD be
        calculated_rank = get_bee_class(user.total_buzz_dust or 0)
        print(f"CALCULATED RANK: {calculated_rank['label']}")
        print(f"Minimum Threshold: {calculated_rank['min_buzz_dust']:,}")
        print()
        
        if user.bee_class != calculated_rank['id']:
            print("⚠️  MISMATCH DETECTED!")
            print(f"   Stored: {user.bee_class}")
            print(f"   Should be: {calculated_rank['id']}")
        else:
            print("✅ Rank is correct!")
        print("=" * 60)
    else:
        print("User 'Aja' not found in database")
        print("\nAll users:")
        users = User.query.all()
        for u in users[:10]:
            print(f"  - {u.username} ({u.display_name}) - {u.total_buzz_dust or 0} BD")
