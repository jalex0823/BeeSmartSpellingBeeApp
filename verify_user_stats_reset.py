"""Verify BeeSmart user stats are reset (read-only).

This is a safety check script to confirm a user (default: BigDaddy2) has had
progress + aggregate counters cleared.

Usage:
  export DATABASE_URL='postgresql://...'
  python verify_user_stats_reset.py BigDaddy2

Notes:
- This script does NOT write to the DB.
- It checks both user aggregate fields and dependent row counts.
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
    parser = argparse.ArgumentParser(description="Verify a BeeSmart user's stats are reset")
    parser.add_argument("username", nargs="?", default="BigDaddy2", help="Username to check")
    args = parser.parse_args(argv)

    username = (args.username or "").strip()
    if not username:
        print("ERROR: username is required")
        return 2

    _require_db_env()

    from AjaSpellBApp import app, db  # type: ignore
    from models import Achievement, QuizResult, QuizSession, SessionLog, User, WordMastery  # type: ignore

    with app.app_context():
        user = User.query.filter(db.func.lower(User.username) == username.lower()).first()
        if not user:
            print(f"ERROR: user not found: {username}")
            return 1

        uid = user.id

        counts = {
            "quiz_results": QuizResult.query.filter_by(user_id=uid).count(),
            "quiz_sessions": QuizSession.query.filter_by(user_id=uid).count(),
            "word_mastery": WordMastery.query.filter_by(user_id=uid).count(),
            "achievements": Achievement.query.filter_by(user_id=uid).count(),
            "session_logs": SessionLog.query.filter_by(user_id=uid).count(),
        }

        fields = {
            "total_lifetime_points": user.total_lifetime_points,
            "total_quizzes_completed": user.total_quizzes_completed,
            "account_level": user.account_level,
            "honey_points": getattr(user, "honey_points", None),
            "total_buzz_dust": getattr(user, "total_buzz_dust", None),
            "bee_class": getattr(user, "bee_class", None),
            "last_rank_up_at": getattr(user, "last_rank_up_at", None),
            "cumulative_gpa": getattr(user, "cumulative_gpa", None),
            "average_accuracy": getattr(user, "average_accuracy", None),
            "best_grade": getattr(user, "best_grade", None),
            "best_streak": getattr(user, "best_streak", None),
            "current_streak": getattr(user, "current_streak", None),
            "longest_streak": getattr(user, "longest_streak", None),
        }

        print(f"User: {user.username} (id={uid}, role={user.role})")
        print("\nDependent row counts:")
        for k, v in counts.items():
            print(f"  {k}: {v}")

        print("\nAggregate fields:")
        for k, v in fields.items():
            print(f"  {k}: {v}")

        ok_counts = all(v == 0 for v in counts.values())
        ok_fields = (
            fields["total_lifetime_points"] == 0
            and fields["total_quizzes_completed"] == 0
            and fields["honey_points"] in (0, None)
            and fields["total_buzz_dust"] in (0, None)
            and fields["best_streak"] in (0, None)
            and fields["current_streak"] in (0, None)
            and fields["longest_streak"] in (0, None)
        )

        print("\nVerdict:")
        if ok_counts and ok_fields:
            print("  PASS: looks reset (core counters are zero and related tables are empty)")
            return 0

        print("  FAIL: one or more counters/rows still present")
        if not ok_counts:
            print("  - Some dependent tables still have rows")
        if not ok_fields:
            print("  - Some aggregate fields are non-zero")
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
