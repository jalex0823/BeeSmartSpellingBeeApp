"""
Update all guest users to have display_name = 'NewBee'
"""
from AjaSpellBApp import app, db, User
from sqlalchemy import or_

with app.app_context():
    # Find all guest users
    guests = User.query.filter(
        or_(
            User.username.like('guest_%'),
            User.display_name.like('Guest %')
        )
    ).all()
    
    print(f'Found {len(guests)} guest users')
    
    # Update their display names
    for guest in guests:
        old_name = guest.display_name
        guest.display_name = 'NewBee'
        print(f'  Updated: {old_name} -> NewBee (username: {guest.username})')
    
    # Commit changes
    db.session.commit()
    print(f'\n✅ Successfully updated {len(guests)} guest users to "NewBee"')
