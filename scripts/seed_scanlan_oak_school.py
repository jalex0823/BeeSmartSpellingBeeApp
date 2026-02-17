#!/usr/bin/env python3
"""
Seed Scanlan Oak Elementary for School Edition testing.

Creates:
- School: Scanlan Oak Elementary (school_code SCANLAN-OAK-2026)
- SchoolKey: one TEACHER, one STUDENT (for login testing)
- Avatar: Scanlan Bee (school-only, uses static file ScanlanBee.glb)

Run after migrate_school_tables.py. Usage: python scripts/seed_scanlan_oak_school.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AjaSpellBApp import app, db
from models import School, SchoolKey, Avatar


SCHOOL_CODE = "SCANLAN-OAK-2026"
TEACHER_KEY = "BEE-2026-SCANLAN-TEACH"
STUDENT_KEY = "BEE-2026-SCANLAN-STUD"


def seed():
    with app.app_context():
        school = School.query.filter_by(school_code=SCHOOL_CODE).first()
        if school:
            print(f"School already exists: {school.name} (id={school.id})")
            if not school.mascot_asset_key:
                school.mascot_asset_key = "scanlan-bee"
                db.session.add(school)
                print("  Set default avatar slug: mascot_asset_key=scanlan-bee")
        else:
            school = School(
                name="Scanlan Oak Elementary",
                school_code=SCHOOL_CODE,
                mascot_name="Scanlan Bee",
                mascot_asset_key="scanlan-bee",  # default avatar slug for auto-assign
            )
            db.session.add(school)
            db.session.flush()
            print(f"Created school: {school.name} (id={school.id}, code={SCHOOL_CODE})")

        for key_code, key_type in [(TEACHER_KEY, "TEACHER"), (STUDENT_KEY, "STUDENT")]:
            existing = SchoolKey.query.filter_by(key_code=key_code).first()
            if existing:
                print(f"Key already exists: {key_code}")
            else:
                db.session.add(SchoolKey(
                    school_id=school.id,
                    key_code=key_code,
                    key_type=key_type,
                    is_active=True,
                ))
                print(f"Created key: {key_code} ({key_type})")

        avatar = Avatar.query.filter_by(slug="scanlan-bee").first()
        if avatar:
            if avatar.school_id != school.id:
                avatar.school_id = school.id
                db.session.add(avatar)
                print("Updated Scanlan Bee avatar to Scanlan Oak school.")
            else:
                print("Scanlan Bee avatar already linked to Scanlan Oak.")
        else:
            avatar = Avatar(
                slug="scanlan-bee",
                name="Scanlan Bee",
                description="Scanlan Oak Elementary school mascot.",
                category="school",
                folder_path="glb_files",
                obj_file="ScanlanBee.glb",
                school_id=school.id,
                is_active=True,
                sort_order=0,
            )
            db.session.add(avatar)
            print("Created avatar: Scanlan Bee (school-only, ScanlanBee.glb)")

        db.session.commit()
        print("\nDone. Use these for testing:")
        print(f"  School code / key: {SCHOOL_CODE}")
        print(f"  Teacher key: {TEACHER_KEY}")
        print(f"  Student key: {STUDENT_KEY}")


if __name__ == "__main__":
    seed()
