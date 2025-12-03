import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import Flask
from config import get_config
from models import db
from sqlalchemy import inspect, text

def ensure_columns(engine):
    insp = inspect(engine)
    cols = [c['name'] for c in insp.get_columns('users')]
    to_add = []
    if 'wordbank_storage_id' not in cols:
        to_add.append("ALTER TABLE users ADD COLUMN wordbank_storage_id VARCHAR(36)")
    if 'wordbank_last_updated' not in cols:
        to_add.append("ALTER TABLE users ADD COLUMN wordbank_last_updated DATETIME")
    from models import db as _db
    for stmt in to_add:
        try:
            _db.session.execute(text(stmt))
            _db.session.commit()
            print(f"✅ Executed: {stmt}")
        except Exception as e:
            _db.session.rollback()
            print(f"⚠️ Failed: {stmt} → {e}")

if __name__ == '__main__':
    app = Flask(__name__)
    app.config.from_object(get_config())
    db.init_app(app)
    with app.app_context():
        ensure_columns(db.engine)
        print("✅ Migration complete")
