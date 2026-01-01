"""Local smoke probe for honeycomb picker + avatar bank protection.

What it checks
- Ensures a local non-premium tester user exists: tester / tester123
- Logs in via /auth/login (JSON)
- Loads /honeycomb-picker (must be 200)
- Calls POST /api/avatar/select:
  - unlocked avatar -> 200 success
  - locked avatar -> 403 with reason premium_locked (or other lock reasons)

This is meant for local developer confidence and quick regressions.
It does NOT attempt to use production credentials.

Usage (zsh):
    # Start server separately (example):
    #   BYPASS_AVATAR_DB_SYNC=1 FLASK_ENV=development PORT=5051 python3 AjaSpellBApp.py
    python3 scripts/smoke_honeycomb_picker_local.py --base http://127.0.0.1:5051

Exit codes
- 0: pass
- 1: fail
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import pathlib
from typing import Any, Dict, Optional

import requests


def ensure_local_tester_user() -> None:
    """Create/update local tester user in the configured DB."""
    # Make this deterministic for local dev.
    os.environ.setdefault("FLASK_ENV", "development")
    os.environ.setdefault("BYPASS_AVATAR_DB_SYNC", "1")

    project_root = pathlib.Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    try:
        # Reuse the helper script logic (without shelling out).
        from AjaSpellBApp import app  # noqa: WPS433
        from models import db, User  # noqa: WPS433
    except Exception as e:  # pragma: no cover
        raise RuntimeError(f"Failed importing app/models for tester creation: {e}") from e

    with app.app_context():
        try:
            db.create_all()
        except Exception:
            # Non-fatal; some envs may not allow create_all.
            pass

        username = "tester"
        password = "tester123"

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
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return

        user.premium_member = False
        if hasattr(user, "admin_all_access"):
            user.admin_all_access = False
        if hasattr(user, "is_active"):
            user.is_active = True
        user.set_password(password)
        db.session.commit()


def _pick_unlocked_and_locked(avatars: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    unlocked = None
    locked = None

    for a in avatars:
        if not a.get("is_locked") and unlocked is None:
            unlocked = a
        if a.get("is_locked") and locked is None:
            locked = a
        if unlocked and locked:
            break

    if not unlocked:
        raise AssertionError("No unlocked avatar found in /api/avatars")
    if not locked:
        raise AssertionError("No locked avatar found in /api/avatars")

    return unlocked, locked


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:5051")
    ap.add_argument("--no-seed", action="store_true", help="Skip ensuring local tester user")
    args = ap.parse_args()

    base = args.base.rstrip("/")

    if not args.no_seed:
        ensure_local_tester_user()

    s = requests.Session()

    # Login
    r = s.post(
        f"{base}/auth/login",
        json={"username": "tester", "password": "tester123", "remember": False},
        timeout=15,
    )
    if r.status_code != 200:
        raise AssertionError(f"login expected 200, got {r.status_code}: {r.text[:200]}")
    data = r.json()
    assert data.get("success") is True, data

    # Picker page should load
    r = s.get(f"{base}/honeycomb-picker", allow_redirects=False, timeout=15)
    if r.status_code != 200:
        raise AssertionError(f"/honeycomb-picker expected 200, got {r.status_code} loc={r.headers.get('Location')}")

    # Avatars list
    r = s.get(f"{base}/api/avatars", timeout=15)
    if r.status_code != 200:
        raise AssertionError(f"/api/avatars expected 200, got {r.status_code}")
    payload: Dict[str, Any] = r.json()
    avatars = payload.get("avatars") or []
    if not avatars:
        raise AssertionError("/api/avatars returned empty avatars list")

    unlocked, locked = _pick_unlocked_and_locked(avatars)
    unlocked_slug = unlocked.get("id")
    locked_slug = locked.get("id")

    # Select unlocked
    r = s.post(f"{base}/api/avatar/select", json={"avatar_slug": unlocked_slug}, timeout=60)
    if r.status_code != 200:
        raise AssertionError(f"select unlocked expected 200, got {r.status_code}: {r.text[:220]}")
    j = r.json()
    assert j.get("success") is True, j

    # Select locked
    r = s.post(f"{base}/api/avatar/select", json={"avatar_slug": locked_slug}, timeout=20)
    if r.status_code != 403:
        raise AssertionError(f"select locked expected 403, got {r.status_code}: {r.text[:220]}")
    j = r.json()
    if j.get("reason") not in {"premium_locked", "locked", "points_locked", "not_owned"}:
        raise AssertionError(f"select locked unexpected reason: {j}")

    print("✅ Honeycomb picker smoke probe passed")
    print(f"   unlocked avatar: {unlocked_slug} ({unlocked.get('name')})")
    print(f"   locked avatar:   {locked_slug} ({locked.get('name')}) reason={j.get('reason')}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"❌ Honeycomb picker smoke probe failed: {e}")
        raise
