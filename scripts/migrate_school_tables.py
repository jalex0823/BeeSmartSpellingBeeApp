#!/usr/bin/env python3
"""
Database Migration: School Edition tables and users.school_id

Creates schools and school_keys via ORM; adds users.school_id if missing.
Usage: python scripts/migrate_school_tables.py
"""

import os
import sys
from sqlalchemy import inspect, text

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AjaSpellBApp import app, db
from models import School, SchoolKey


def migrate_school_tables():
    with app.app_context():
        inspector = inspect(db.engine)
        migrations_done = []

        if not inspector.has_table('users'):
            print("users table does not exist; run app init first.")
            return False

        # 1) Create schools and school_keys via ORM (dialect-agnostic)
        if not inspector.has_table('schools'):
            print("Creating schools table...")
            db.create_all(tables=[School.__table__])
            db.session.commit()
            migrations_done.append("schools")
        if not inspector.has_table('school_keys'):
            print("Creating school_keys table...")
            db.create_all(tables=[SchoolKey.__table__])
            db.session.commit()
            migrations_done.append("school_keys")

        # 2) Add school_id to users if missing
        columns = [c["name"] for c in inspector.get_columns("users")]
        if "school_id" not in columns:
            print("Adding school_id to users...")
            db.session.execute(text(
                "ALTER TABLE users ADD COLUMN school_id INTEGER REFERENCES schools(id)"
            ))
            try:
                db.session.execute(text("CREATE INDEX ix_users_school_id ON users(school_id)"))
            except Exception:
                pass
            db.session.commit()
            migrations_done.append("users.school_id")

        if migrations_done:
            print("Migration completed:", migrations_done)
        return True


if __name__ == "__main__":
    try:
        ok = migrate_school_tables()
        sys.exit(0 if ok else 1)
    except Exception as e:
        print(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
