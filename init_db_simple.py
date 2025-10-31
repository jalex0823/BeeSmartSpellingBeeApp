#!/usr/bin/env python
"""Initialize database tables"""
import sys
sys.path.insert(0, '.')

from AjaSpellBApp import app, db

with app.app_context():
    print("🔧 Creating database tables...")
    db.create_all()
    print("✅ Database initialized successfully!")
