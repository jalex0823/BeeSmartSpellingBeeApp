import os, sys

# Create minimal Flask app WITHOUT importing the full AjaSpellBApp (avoids 13K line initialization)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import only what we need - no full app import
from flask import Flask
from config import get_config
from models import db

# Try to import BeeKey tables if they exist
try:
    from models import BundleKey, DynamicBundle, BundleKeyRedemption
    BEEKEY_MODELS_AVAILABLE = True
except ImportError as e:
    print(f'⚠️ BeeKey models not available yet: {e}')
    BEEKEY_MODELS_AVAILABLE = False

if __name__ == '__main__':
    # Create minimal app just for schema check
    minimal_app = Flask(__name__)
    minimal_app.config.from_object(get_config())
    
    # Initialize ONLY the database (no sessions, no login manager, no socketio)
    db.init_app(minimal_app)
    
    with minimal_app.app_context():
        print('🔧 Running db.create_all() to ensure schema...')
        db.create_all()
        
        # Simple presence log for tables
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            print(f'   📋 Found {len(existing_tables)} tables in database')
            
            if BEEKEY_MODELS_AVAILABLE:
                for tbl in ['bundle_keys','dynamic_bundles','bundle_key_redemptions']:
                    print(f"   • Table {tbl}: {'present' if tbl in existing_tables else 'missing'}")
        except Exception as e:
            print(f"   ⚠️ Could not inspect tables: {e}")
        
        print('✅ Ensured database schema (db.create_all)')

