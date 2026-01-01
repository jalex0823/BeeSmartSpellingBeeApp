"""Selfcheck: guest users must NOT access avatar picker UI routes.

This repo has two kinds of "guests":
- Unauthenticated (no session) -> should be redirected by @login_required
- Session/DB guest users (session['is_guest']=True and/or username guest_*)
  -> must be redirected to registration, per product requirement.

Run:
  python3 scripts/selfcheck_guest_picker_blocked.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure repo root is importable
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _build_app():
    os.environ.setdefault("FAST_BOOT", "1")
    import AjaSpellBApp  # noqa: F401

    return AjaSpellBApp.app


def main() -> int:
    app = _build_app()
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)

    with app.test_client() as client:
        # 1) Completely unauthenticated should be redirected by login_required
        r = client.get("/avatar-picker", follow_redirects=False)
        assert r.status_code in (301, 302), f"Expected redirect for unauthenticated, got {r.status_code}"

        # 2) Simulate a logged-in guest user by forcing the session guest flag.
        # We don't need a fully valid login for the behavior we want to assert:
        # the guard checks session['is_guest'] and redirects to /register.
        with client.session_transaction() as sess:
            sess["is_guest"] = True

        r2 = client.get("/avatar-picker", follow_redirects=False)
        assert r2.status_code in (301, 302), f"Expected redirect for guest session, got {r2.status_code}"
        loc = r2.headers.get("Location", "")
        assert "/register" in loc, f"Expected redirect to /register for guest session, got Location={loc!r}"

        r3 = client.get("/honeycomb-picker", follow_redirects=False)
        assert r3.status_code in (301, 302), f"Expected redirect for guest session, got {r3.status_code}"
        loc3 = r3.headers.get("Location", "")
        assert "/register" in loc3, f"Expected redirect to /register for guest session, got Location={loc3!r}"

    print("OK: guest users are blocked from avatar picker pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
