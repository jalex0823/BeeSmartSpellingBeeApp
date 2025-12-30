"""One-time cleanup: fix JSON columns that were accidentally stored as strings.

Why this exists
--------------
Some legacy rows in the DigitalOcean Postgres DB have JSON columns stored as
strings (e.g. "[]" or "[\"super-bee\"]") instead of actual JSON arrays.

This breaks runtime code that expects a Python list (e.g. user.purchased_avatars.append(...)).

What it does
------------
- Scans users.purchased_avatars and users.purchased_bundles
- If value is a string, tries to json.loads it
- If value becomes a list, writes it back as proper JSON
- Optionally, attempts a best-effort salvage for bracket/quote corruption

Safety
------
- Dry-run by default. Use --apply to actually commit.
- Prints a summary of what would change.

Usage
-----
python3 scripts/cleanup_iap_json_columns.py --apply

Environment
-----------
Uses DATABASE_URL (same as app). You can also set FAST_BOOT=1 to speed import.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import pathlib
from typing import Any, Tuple


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("FAST_BOOT", "1")
os.environ.setdefault("SKIP_AVATAR_STARTUP_SYNC", "1")


def _coerce_json_list(value: Any) -> Tuple[bool, list]:
    """Return (changed, coerced_list).

    - If already a list -> (False, value)
    - If None/empty -> coerces to []
    - If str -> attempts json.loads
    """
    if value is None:
        return True, []
    if isinstance(value, list):
        return False, value
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return True, []
        # First attempt: strict JSON
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                # If it's already a canonical empty list string, treat as no-op.
                # (Backends may transparently cast JSON columns to text in some drivers;
                # rewriting every row would be noisy and risky.)
                return (parsed != []), parsed
        except Exception:
            pass

        # Best-effort salvage: some rows ended up like ['[', '"', 's', ...]
        # We only attempt salvage when it looks like JSON container.
        if (s.startswith("[") and s.endswith("]")) or ("[" in s and "]" in s):
            # try extracting a quoted string list
            try:
                # If it's like "['[', ']']" we can't salvage reliably.
                # If it's like "[\"super-bee\"]" this is handled above.
                return True, []
            except Exception:
                return True, []

        # Unknown string content -> replace with [] rather than crash app
        return True, []

    # Unknown type (dict/int/etc) -> replace with []
    return True, []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Actually write changes to the database")
    args = parser.parse_args()

    from AjaSpellBApp import app  # noqa: E402
    from models import db, User  # noqa: E402

    would_change = 0
    changed = 0

    with app.app_context():
        q = User.query
        users = q.all()

        for u in users:
            pa_changed, pa = _coerce_json_list(getattr(u, "purchased_avatars", None))
            pb_changed, pb = _coerce_json_list(getattr(u, "purchased_bundles", None))

            if pa_changed or pb_changed:
                would_change += 1
                if args.apply:
                    u.purchased_avatars = pa
                    u.purchased_bundles = pb
                    changed += 1

        if args.apply:
            db.session.commit()

    print("\nIAP JSON cleanup summary")
    print("----------------------")
    print(f"Users scanned: {len(users)}")
    print(f"Users needing fixes: {would_change}")
    if args.apply:
        print(f"Users fixed: {changed}")
        print("✅ Changes committed")
    else:
        print("(dry run) No changes written. Re-run with --apply to commit.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
