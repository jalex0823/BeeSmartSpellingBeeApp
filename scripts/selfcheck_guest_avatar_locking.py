"""Self-check to ensure guests can't freely select locked avatars.

Goal:
- When not logged in and with no guest entitlements, /api/avatars should still return
  the full catalog, but only ONE avatar should be unlocked (Mascot Bee Avatar preferred).

This protects the UI (picker stays consistent) while enforcing access restrictions.

Run:
  python3 scripts/selfcheck_guest_avatar_locking.py

Environment:
- Uses Flask's test client; no server needed.
- If your app requires DB/network services at import, set FAST_BOOT=1 before running.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def main() -> int:
    # Reduce startup side effects when possible.
    os.environ.setdefault("FAST_BOOT", "1")

    # Ensure repo root is on sys.path when run from scripts/.
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    import AjaSpellBApp  # noqa: E402

    app = AjaSpellBApp.app

    with app.test_client() as c:
        r = c.get("/api/avatars")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        data = r.get_json() or {}
        assert data.get("status") == "success", f"Unexpected status: {data.get('status')}"

        avatars = data.get("avatars") or []
        assert isinstance(avatars, list) and avatars, "Expected a non-empty avatars list"

        unlocked = [a for a in avatars if not a.get("is_locked")]
        locked = [a for a in avatars if a.get("is_locked")]

        # Exactly one unlocked avatar for guests (Mascot Bee / Honey Comb fallback).
        assert len(unlocked) == 1, f"Expected exactly 1 unlocked avatar for guest, got {len(unlocked)}"
        assert len(locked) == (len(avatars) - 1), "Locked count does not match expected"

        allowed = unlocked[0]
        allowed_id = (allowed.get("id") or "").lower()
        assert allowed_id in ("mascot-bee", "honey-comb"), f"Unexpected guest-allowed avatar id: {allowed_id}"

    print("OK: Guest avatar locking enforced (1 unlocked, rest locked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
