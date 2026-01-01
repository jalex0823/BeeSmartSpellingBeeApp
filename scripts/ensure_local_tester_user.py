"""Ensure a local non-premium tester user exists.

This is intended for LOCAL development only.

It creates or updates a user:
- username: tester
- password: tester123
- role: student
- premium_member: False

Usage (zsh):
    BYPASS_AVATAR_DB_SYNC=1 FLASK_ENV=development python3 scripts/ensure_local_tester_user.py

Notes:
- This operates against whatever DB your local config points to.
- It will reset the password for the 'tester' user if it already exists.
"""

from __future__ import annotations

import os
import sys
import pathlib


def main() -> int:
    # Keep this script explicit about env to reduce surprises.
    os.environ.setdefault("FLASK_ENV", "development")

    project_root = pathlib.Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Import after env is set.
    from AjaSpellBApp import app  # noqa: WPS433
    from models import db, User  # noqa: WPS433

    username = "tester"
    password = "tester123"

    with app.app_context():
        # Make sure tables exist in local dev.
        try:
            db.create_all()
        except Exception as e:
            print(f"⚠️ db.create_all() failed (continuing): {e}")

        user = None
        try:
            user = User.query.filter(db.func.lower(User.username) == username.lower()).first()
        except Exception:
            user = User.query.filter_by(username=username).first()

        if user is None:
            user = User(
                username=username,
                display_name="Tester",
                email=None,
                role="student",
                premium_member=False,
                admin_all_access=False,
                is_active=True,
            )
            # Password setter name varies across codebases; this one is used by registration/login.
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print("✅ Created local tester user: tester / tester123 (non-premium)")
            return 0

        # Update existing
        user.premium_member = False
        if hasattr(user, "admin_all_access"):
            user.admin_all_access = False
        if hasattr(user, "is_active"):
            user.is_active = True

        user.set_password(password)
        db.session.commit()
        print("✅ Updated local tester user password and flags: tester / tester123 (non-premium)")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
