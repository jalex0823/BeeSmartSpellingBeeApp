"""Reset a BeeSmart user's stats to zero (writes to DB).

This script is intended for controlled admin/ops use. It removes per-user
history rows and zeros aggregate counters so that `verify_user_stats_reset.py`
reports PASS.

Safety features:
- Requires DATABASE_URL or DIGITALOCEAN_DATABASE_URL.
- Defaults to --dry-run (no DB writes).
- To actually write, you must provide BOTH --apply and --yes.

Usage:
  export DIGITALOCEAN_DATABASE_URL='postgresql://...'
  python reset_user_stats_to_zero.py BigDaddy2 --dry-run
  python reset_user_stats_to_zero.py BigDaddy2 --apply --yes

Notes:
- This deletes quiz history tables for the user (quiz_results, quiz_sessions,
  word_mastery, achievements, session_logs) which is what the verifier expects.
- It then zeros key aggregate fields on the User row.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass


def _require_db_env() -> None:
    if os.getenv("DATABASE_URL") or os.getenv("DIGITALOCEAN_DATABASE_URL"):
        return
    raise SystemExit(
        "DATABASE_URL (or DIGITALOCEAN_DATABASE_URL) must be set before running this script."
    )


@dataclass(frozen=True)
class Plan:
    user_id: int
    username: str
    delete_counts: dict[str, int]
    user_field_updates: dict[str, object]


def _build_plan(db, models, username: str) -> Plan:
    User = models.User

    user = User.query.filter(db.func.lower(User.username) == username.lower()).first()
    if not user:
        raise SystemExit(f"ERROR: user not found: {username}")

    uid = user.id

    # Dependent rows the verifier checks
    delete_counts = {
        "quiz_results": models.QuizResult.query.filter_by(user_id=uid).count(),
        "quiz_sessions": models.QuizSession.query.filter_by(user_id=uid).count(),
        "word_mastery": models.WordMastery.query.filter_by(user_id=uid).count(),
        "achievements": models.Achievement.query.filter_by(user_id=uid).count(),
        "session_logs": models.SessionLog.query.filter_by(user_id=uid).count(),
    }

    # Aggregate fields the verifier cares about + nearby ones that should logically reset.
    user_field_updates: dict[str, object] = {}

    def _maybe_set(attr: str, value: object) -> None:
        if hasattr(user, attr):
            user_field_updates[attr] = value

    _maybe_set("total_lifetime_points", 0)
    _maybe_set("total_quizzes_completed", 0)
    _maybe_set("account_level", 0)
    _maybe_set("honey_points", 0)
    _maybe_set("total_buzz_dust", 0)
    _maybe_set("cumulative_gpa", 0)
    _maybe_set("average_accuracy", 0)
    _maybe_set("best_grade", None)
    _maybe_set("best_streak", 0)
    _maybe_set("current_streak", 0)
    _maybe_set("longest_streak", 0)
    _maybe_set("bee_class", None)
    _maybe_set("last_rank_up_at", None)

    # Extra conservative resets (don’t hurt verifier, but aligns with “everything to 0”).
    _maybe_set("avatar_last_updated", None)

    return Plan(user_id=uid, username=user.username, delete_counts=delete_counts, user_field_updates=user_field_updates)


def _apply_plan(db, models, plan: Plan) -> None:
    uid = plan.user_id

    # Use bulk deletes for speed; keep session in sync off.
    # IMPORTANT: quiz_results may reference quiz_sessions via FK (session_id)
    # so we must delete results first using a session_id join, then sessions.
    session_ids_subq = models.QuizSession.query.with_entities(models.QuizSession.id).filter_by(user_id=uid)

    models.QuizResult.query.filter(models.QuizResult.session_id.in_(session_ids_subq)).delete(
        synchronize_session=False
    )
    # Defensive cleanup: if any results exist with session_id NULL, delete them too.
    models.QuizResult.query.filter_by(user_id=uid).delete(synchronize_session=False)

    models.QuizSession.query.filter_by(user_id=uid).delete(synchronize_session=False)
    models.WordMastery.query.filter_by(user_id=uid).delete(synchronize_session=False)
    models.Achievement.query.filter_by(user_id=uid).delete(synchronize_session=False)
    models.SessionLog.query.filter_by(user_id=uid).delete(synchronize_session=False)

    user = models.User.query.get(uid)
    if not user:
        raise SystemExit(f"ERROR: user disappeared during apply: id={uid}")

    for k, v in plan.user_field_updates.items():
        setattr(user, k, v)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Reset a BeeSmart user's stats to zero")
    parser.add_argument("username", help="Username to reset")

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Show what would change (default)")
    mode.add_argument("--apply", action="store_true", help="Apply changes to the database")

    parser.add_argument(
        "--yes",
        action="store_true",
        help="Required with --apply. Confirms you intend to write to production data.",
    )

    args = parser.parse_args(argv)

    username = (args.username or "").strip()
    if not username:
        print("ERROR: username is required")
        return 2

    _require_db_env()

    # Import app/db/models only after env is validated.
    from AjaSpellBApp import app, db  # type: ignore
    import models as m  # type: ignore

    apply_changes = bool(args.apply)
    dry_run = bool(args.dry_run) or not apply_changes

    if apply_changes and not args.yes:
        print("ERROR: refusing to run --apply without --yes")
        return 2

    with app.app_context():
        plan = _build_plan(db, m, username)

        print(f"Target user: {plan.username} (id={plan.user_id})")
        print("\nRows to delete:")
        for k, v in plan.delete_counts.items():
            print(f"  {k}: {v}")

        print("\nUser fields to reset:")
        for k, v in plan.user_field_updates.items():
            print(f"  {k} -> {v}")

        if dry_run:
            print("\nDRY RUN: no changes written.")
            return 0

        # Apply within an explicit transaction.
        # Some app startup paths touch the scoped session (starting a transaction).
        # begin_nested() works even when an outer transaction already exists.
        try:
            with db.session.begin_nested():
                _apply_plan(db, m, plan)
            db.session.commit()
        except Exception as exc:
            db.session.rollback()
            print(f"\nERROR: transaction failed, rolled back: {exc}")
            raise

        print("\nAPPLIED: stats reset transaction committed.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
