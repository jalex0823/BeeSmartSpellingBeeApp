"""
One-time script to drop all tables and recreate with current schema
USE CAREFULLY - This deletes all database data!
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import get_config
from models import db, User, QuizSession, QuizResult, WordMastery, TeacherStudent
from models import WordList, WordListItem, Achievement, SessionLog, ExportRequest

def create_app():
    """Create Flask app with database configuration"""
    app = Flask(__name__)
    app.config.from_object(get_config())
    db.init_app(app)
    return app

def drop_and_recreate():
    """Drop all tables and recreate with current schema"""
    app = create_app()
    
    with app.app_context():
        print("🐝 BeeSmart Database Reset")
        print("=" * 50)
        print("⚠️  WARNING: This will delete ALL data!")
        print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
        print()
        
        # Drop all tables
        print("🗑️  Dropping all tables...")
        db.drop_all()
        print("✅ All tables dropped")
        
        # Create all tables with current schema
        print("\n📊 Creating tables with current schema...")
        db.create_all()
        
        # List created tables
        tables = db.metadata.tables.keys()
        print(f"\n✅ Created {len(tables)} tables:")
        for table in sorted(tables):
            print(f"   - {table}")
        
        print("\n🎉 Database reset complete!")
        print("You can now create users and start using the app.")

if __name__ == '__main__':
    drop_and_recreate()
