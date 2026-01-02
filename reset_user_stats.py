"""Reset BeeSmart user stats (quiz progress + gamification counters).

This is intended for controlled maintenance (e.g., resetting a test/admin account).

Usage (PowerShell):
  $env:DATABASE_URL = "postgresql://..."  # or DIGITALOCEAN_DATABASE_URL
  python reset_user_stats.py BigDaddy2 --yes

Notes:
- Does NOT delete the user, change password, or affect avatar selection.
- Deletes quiz sessions/results, word mastery, achievements. Optionally deletes session logs.
"""

from __future__ import annotations

import argparse
import os
import sys


def _require_db_env() -> None:
    if os.getenv("DATABASE_URL") or os.getenv("DIGITALOCEAN_DATABASE_URL"):
        return
    raise SystemExit(
        "DATABASE_URL (or DIGITALOCEAN_DATABASE_URL) must be set before running this script."
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Reset a BeeSmart user's stats")
    parser.add_argument("username", nargs="?", default="BigDaddy2", help="Username to reset")
    parser.add_argument(
        "--include-logs",
        action="store_true",
        help="Also delete SessionLog rows for the user",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm the reset (required to actually modify data)",
    )

    args = parser.parse_args(argv)
    username = (args.username or "").strip()
    if not username:
        print("ERROR: username is required")
        return 2

    if not args.yes:
        print(
            "Refusing to run without --yes. This script deletes progress data.\n"
            f"Target username: {username}"
        )
        return 2

    _require_db_env()

    # Import after env check so we fail fast if DB isn't configured.
    from AjaSpellBApp import app, db  # type: ignore
    from models import Achievement, QuizResult, QuizSession, SessionLog, User, WordMastery  # type: ignore

    with app.app_context():
        user = (
            User.query.filter(db.func.lower(User.username) == username.lower()).first()
        )
        if not user:
            print(f"ERROR: user not found: {username}")
            return 1

        uid = user.id
        print(f"Resetting stats for user: {user.username} (id={uid}, role={user.role})")

        # Delete dependent rows first (safe for FK constraints).
        deleted_quiz_results = (
            QuizResult.query.filter_by(user_id=uid).delete(synchronize_session=False)
        )
        deleted_quiz_sessions = (
            QuizSession.query.filter_by(user_id=uid).delete(synchronize_session=False)
        )
        deleted_mastery = (
            WordMastery.query.filter_by(user_id=uid).delete(synchronize_session=False)
        )
        deleted_achievements = (
            Achievement.query.filter_by(user_id=uid).delete(synchronize_session=False)
        )
        deleted_logs = 0
        if args.include_logs:
            deleted_logs = (
                SessionLog.query.filter_by(user_id=uid).delete(synchronize_session=False)
            )

        # Reset aggregate/counter fields on the user.
        user.total_lifetime_points = 0
        user.total_quizzes_completed = 0
        user.account_level = 1

        user.honey_points = 0
        user.total_buzz_dust = 0
        user.bee_class = "novice"
        user.last_rank_up_at = None

        user.cumulative_gpa = 0.0
        user.average_accuracy = 0.0
        user.best_grade = None
        user.best_streak = 0
        user.current_streak = 0
        user.longest_streak = 0

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"ERROR: commit failed: {e}")
            return 1

        print("Done.")
        print(
            "Deleted:\n"
            f"  QuizResult:   {deleted_quiz_results}\n"
            f"  QuizSession:  {deleted_quiz_sessions}\n"
            f"  WordMastery:  {deleted_mastery}\n"
            f"  Achievement:  {deleted_achievements}\n"
            f"  SessionLog:   {deleted_logs} ({'included' if args.include_logs else 'skipped'})\n"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
