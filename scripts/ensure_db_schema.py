import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from AjaSpellBApp import app
from models import db, BundleKey, DynamicBundle, BundleKeyRedemption

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Simple presence log for new tables
        try:
            existing = db.engine.table_names()
            for tbl in ['bundle_keys','dynamic_bundles','bundle_key_redemptions']:
                print(f"   • Table {tbl}: {'present' if tbl in existing else 'missing'}")
        except Exception:
            pass
        print('✅ Ensured database schema (db.create_all) with BeeKey tables')
