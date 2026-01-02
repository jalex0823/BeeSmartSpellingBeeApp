#!/usr/bin/env python3
"""Self-check: avatar catalog default-free policy.

Contract:
- There are exactly 5 DEFAULT_FREE avatars in `avatar_catalog.AVATAR_CATALOG`.
- These are the only avatars automatically unlocked for registered non-premium users.
- Admin is allowed to unlock everything (enforced elsewhere), but this script focuses
  on catalog invariants used by the backend unlock logic.

This script is intentionally DB-free and safe to run in CI.
"""

from __future__ import annotations

import os
import sys


def main() -> int:
    # Ensure repo root is importable when running from scripts/
    try:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        if repo_root not in sys.path:
            sys.path.insert(0, repo_root)
    except Exception:
        pass
    try:
        from avatar_catalog import AVATAR_CATALOG
    except Exception as e:
        print(f"FAIL: could not import AVATAR_CATALOG: {e}")
        return 2

    # NOTE: The catalog marks the mascot as is_default_free=True for legacy UI,
    # but monetization rules treat it as a separate guest default.
    default_free = [a for a in AVATAR_CATALOG if str(a.get("tier", "")).lower() == "default_free"]
    mascot = [a for a in AVATAR_CATALOG if str(a.get("tier", "")).lower() in ("mascot", "mascot_free")]

    print(f"Total avatars: {len(AVATAR_CATALOG)}")
    print(f"Default-free avatars: {len(default_free)}")
    for a in default_free:
        print(f"  - {a.get('id')} :: {a.get('name')} :: tier={a.get('tier')} is_default_free={a.get('is_default_free')}")

    if len(default_free) != 5:
        print("FAIL: expected exactly 5 default-free avatars")
        return 1

    if len(mascot) < 1:
        # Not fatal for registered policy, but used for guest experience.
        print("WARN: no mascot tier avatars found")

    print("OK: default-free avatar policy matches expected 5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
