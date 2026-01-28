#!/usr/bin/env python3
"""
Clear subscription-related data for specific users (by email).

Used when Tinfox/Kumari requests a reset of subscription state for test or
review accounts so they can re-test purchase/restore flows.

Clears:
- users.premium_member = False
- users.subscription_* columns (if they exist from migrate_subscription_fields)
- PurchaseRecord rows for subscription product_ids for those users

Emails are from Kumari's request (Jan 2026). Override with env CLEAR_SUB_EMAILS
(comma-separated) if needed.

Usage:
  # Default: clear for the 5 emails from Kumari
  python scripts/clear_subscription_data_for_users.py

  # Custom list (comma-separated)
  CLEAR_SUB_EMAILS="a@b.com,c@d.com" python scripts/clear_subscription_data_for_users.py

  # Dry run (print what would be done, no DB changes)
  CLEAR_SUB_DRY_RUN=1 python scripts/clear_subscription_data_for_users.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Default emails from Kumari's request (Jan 2026)
DEFAULT_EMAILS = [
    "skumar@tinfoxconsulting.com",
    "skumar+11@tinfoxconsulting.com",
    "skumar+22@tinfoxconsulting.com",
    "satya_785@yahoo.co.in",
    "skumar+01@tinfoxconsulting.com",
]


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    dry_run = (os.getenv("CLEAR_SUB_DRY_RUN", "").strip().lower() in ("1", "true", "yes"))
    emails_env = (os.getenv("CLEAR_SUB_EMAILS") or "").strip()
    emails = [e.strip() for e in emails_env.split(",") if e.strip()] if emails_env else DEFAULT_EMAILS

    if not emails:
        print("No emails provided. Set CLEAR_SUB_EMAILS or use defaults in script.")
        return 1

    os.environ.setdefault("FAST_BOOT", "1")
    os.environ.setdefault("BYPASS_AVATAR_DB_SYNC", "1")

    from AjaSpellBApp import app
    from models import db, User
    from sqlalchemy import inspect

    # Subscription product IDs we treat as "subscription" for purge
    try:
        from AjaSpellBApp import SUBSCRIPTION_PRODUCT_IDS
        sub_pids = set(v for v in (SUBSCRIPTION_PRODUCT_IDS or {}).values() if v)
    except Exception:
        sub_pids = {"com.beesmart.premium.monthly", "com.beesmart.premium.yearly", "com.beesmart.premium.family.monthly"}

    # Optional: PurchaseRecord for subscription purges
    try:
        from models import PurchaseRecord
        have_purchase_record = True
    except Exception:
        have_purchase_record = False

    with app.app_context():
        inspector = inspect(db.engine)
        user_columns = [c["name"] for c in inspector.get_columns("users")]

        updated_users = 0
        cleared_premium = 0
        cleared_sub_cols = 0
        deleted_records = 0

        for email in emails:
            user = User.query.filter_by(email=email).first()
            if not user:
                print(f"  Skip (not found): {email}")
                continue

            uid = getattr(user, "id", None)
            if dry_run:
                print(f"  Would clear subscription data for: {email} (id={uid})")
                updated_users += 1
                continue

            # 1) premium_member = False
            if getattr(user, "premium_member", False):
                user.premium_member = False
                cleared_premium += 1

            # 2) Clear subscription_* columns if they exist
            sub_cols = [
                "subscription_type", "subscription_product_id", "subscription_status",
                "subscription_expires_at", "subscription_auto_renew", "original_transaction_id",
                "latest_receipt_data", "subscription_started_at", "subscription_canceled_at",
                "family_shared_from",
            ]
            for col in sub_cols:
                if col in user_columns:
                    try:
                        val = "none" if col == "subscription_status" else None
                        setattr(user, col, val)
                        cleared_sub_cols += 1
                    except Exception as e:
                        print(f"  Warning: could not clear {col} for {email}: {e}")

            updated_users += 1
            print(f"  Cleared user: {email} (id={uid})")

        if not dry_run and updated_users:
            try:
                db.session.commit()
                print(f"Committed: premium_member cleared for {cleared_premium} field(s), subscription cols cleared {cleared_sub_cols} time(s).")
            except Exception as e:
                print(f"Commit failed: {e}")
                db.session.rollback()
                return 2

        # 3) Delete PurchaseRecord rows for subscription products for these users
        if have_purchase_record and emails and not dry_run:
            users_by_email = {u.email: u for u in User.query.filter(User.email.in_(emails)).all()}
            ids_to_clear = [u.id for u in users_by_email.values()]
            if ids_to_clear and sub_pids:
                try:
                    deleted = db.session.query(PurchaseRecord).filter(
                        PurchaseRecord.user_id.in_(ids_to_clear),
                        PurchaseRecord.product_id.in_(list(sub_pids)),
                    ).delete(synchronize_session=False)
                    if deleted:
                        db.session.commit()
                        deleted_records = deleted
                        print(f"Deleted {deleted} subscription PurchaseRecord row(s).")
                except Exception as e:
                    print(f"Warning: could not delete PurchaseRecords: {e}")
                    db.session.rollback()

        if dry_run:
            print("Dry run — no changes made.")
        else:
            print(f"Done. Users updated: {updated_users}, purchase records deleted: {deleted_records}.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
