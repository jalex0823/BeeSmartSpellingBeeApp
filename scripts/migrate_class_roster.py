#!/usr/bin/env python3
"""
Migration: Class + RosterStudent (Teacher Key → Managed Roster)
- Creates classes and roster_students tables
- Adds roster_student_id to quiz_sessions and quiz_results
- Makes user_id nullable on quiz_sessions and quiz_results (PostgreSQL)
- Creates one Class per teacher/parent/admin that has teacher_key, using that key as class.teacher_key
Run from repo root: python scripts/migrate_class_roster.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

def run():
    from AjaSpellBApp import app, db
    from models import User, Class, RosterStudent

    with app.app_context():
        dialect = db.engine.dialect.name
        print(f"Database dialect: {dialect}")

        # 1) Create classes table
        inspector = db.inspect(db.engine)
        if 'classes' not in inspector.get_table_names():
            print("Creating classes table...")
            db.session.execute(text("""
                CREATE TABLE classes (
                    id SERIAL PRIMARY KEY,
                    uuid VARCHAR(36) UNIQUE NOT NULL,
                    teacher_id INTEGER NOT NULL REFERENCES users(id),
                    name VARCHAR(200) NOT NULL DEFAULT 'Default Class',
                    teacher_key VARCHAR(50) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """ if dialect == 'postgresql' else """
                CREATE TABLE classes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uuid VARCHAR(36) UNIQUE NOT NULL,
                    teacher_id INTEGER NOT NULL REFERENCES users(id),
                    name VARCHAR(200) NOT NULL DEFAULT 'Default Class',
                    teacher_key VARCHAR(50) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            db.session.commit()
            print("  Created classes.")
        else:
            print("  classes table already exists.")

        # 2) Create roster_students table
        if 'roster_students' not in inspector.get_table_names():
            print("Creating roster_students table...")
            db.session.execute(text("""
                CREATE TABLE roster_students (
                    id SERIAL PRIMARY KEY,
                    uuid VARCHAR(36) UNIQUE NOT NULL,
                    class_id INTEGER NOT NULL REFERENCES classes(id),
                    display_name VARCHAR(200) NOT NULL,
                    external_student_id VARCHAR(100),
                    grade_level VARCHAR(20),
                    pin_hash VARCHAR(255),
                    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """ if dialect == 'postgresql' else """
                CREATE TABLE roster_students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uuid VARCHAR(36) UNIQUE NOT NULL,
                    class_id INTEGER NOT NULL REFERENCES classes(id),
                    display_name VARCHAR(200) NOT NULL,
                    external_student_id VARCHAR(100),
                    grade_level VARCHAR(20),
                    pin_hash VARCHAR(255),
                    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            db.session.execute(text("CREATE INDEX ix_roster_students_class_status ON roster_students (class_id, status)"))
            db.session.commit()
            print("  Created roster_students.")
        else:
            print("  roster_students table already exists.")

        # 3) Add roster_student_id to quiz_sessions
        inspector = db.inspect(db.engine)
        qs_cols = [c['name'] for c in inspector.get_columns('quiz_sessions')]
        if 'roster_student_id' not in qs_cols:
            print("Adding roster_student_id to quiz_sessions...")
            db.session.execute(text("ALTER TABLE quiz_sessions ADD COLUMN roster_student_id INTEGER REFERENCES roster_students(id)"))
            db.session.commit()
        if dialect == 'postgresql':
            # Make user_id nullable
            db.session.execute(text("ALTER TABLE quiz_sessions ALTER COLUMN user_id DROP NOT NULL"))
            db.session.commit()
            print("  quiz_sessions.user_id is now nullable (PostgreSQL).")

        # 4) Add roster_student_id to quiz_results, user_id nullable
        qr_cols = [c['name'] for c in inspector.get_columns('quiz_results')]
        if 'roster_student_id' not in qr_cols:
            print("Adding roster_student_id to quiz_results...")
            db.session.execute(text("ALTER TABLE quiz_results ADD COLUMN roster_student_id INTEGER REFERENCES roster_students(id)"))
            db.session.commit()
        if dialect == 'postgresql':
            db.session.execute(text("ALTER TABLE quiz_results ALTER COLUMN user_id DROP NOT NULL"))
            db.session.commit()
            print("  quiz_results.user_id is now nullable (PostgreSQL).")

        # 5) Create default class per teacher/parent/admin with teacher_key
        teachers = User.query.filter(
            User.teacher_key.isnot(None),
            User.teacher_key != '',
            User.role.in_(['teacher', 'parent', 'admin'])
        ).all()
        for u in teachers:
            existing = Class.query.filter_by(teacher_key=u.teacher_key).first()
            if not existing:
                c = Class(
                    teacher_id=u.id,
                    name=u.display_name and f"{u.display_name}'s Class" or "Default Class",
                    teacher_key=u.teacher_key
                )
                db.session.add(c)
                print(f"  Created class for {u.username} ({u.teacher_key})")
        db.session.commit()

        # 6) Add user_id to roster_students (auto-created login account)
        inspector = db.inspect(db.engine)
        if 'roster_students' in inspector.get_table_names():
            rs_cols = [c['name'] for c in inspector.get_columns('roster_students')]
            if 'user_id' not in rs_cols:
                print("Adding user_id to roster_students...")
                db.session.execute(text(
                    "ALTER TABLE roster_students ADD COLUMN user_id INTEGER REFERENCES users(id)"
                ))
                db.session.commit()
                print("  Added user_id.")

        print("Migration complete.")


if __name__ == '__main__':
    run()
