"""Quick script to verify avatar database state"""
from AjaSpellBApp import app, db
from models import Avatar

with app.app_context():
    avatars = Avatar.query.filter_by(is_active=True).all()
    print(f'\n✅ Active avatars in database: {len(avatars)}')
    print('\nAvatar list:')
    for a in sorted(avatars, key=lambda x: x.slug):
        print(f'  - {a.slug}: {a.name}')
        print(f'    Thumbnail: {a.thumbnail_file}')
