import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from AjaSpellBApp import app
from models import db

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print('✅ Ensured database schema (db.create_all)')
