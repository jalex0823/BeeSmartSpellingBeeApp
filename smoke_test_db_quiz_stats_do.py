#!/usr/bin/env python3
"""
🐝 SMOKE TEST: Direct DB Verification of Quiz & Stats Persistence (DigitalOcean)

This script connects directly to your PostgreSQL database (e.g., DigitalOcean managed DB)
using a DSN from the environment, and verifies that quiz results and user stats are being
persisted correctly for a given user.

It does **not** run a quiz itself; instead, it assumes you've already completed at least
one quiz as a given user on the target environment (e.g., DO production), and then:

1. Looks up the user by username or email
2. Fetches their latest QuizSession rows (completed and incomplete)
3. Prints out:
   - Total quizzes completed
   - Latest quiz session details (points, accuracy, grade, completed flag)
   - User.total_lifetime_points and total_quizzes_completed
4. Compares User.total_lifetime_points against the sum of QuizSession points

Usage:

  export DO_DB_DSN="postgresql://user:pass@host:port/dbname?sslmode=require"
  python smoke_test_db_quiz_stats_do.py --user your_username_here

You can also pass --email to look up by email instead of username.
"""

from __future__ import annotations

import argparse
import io
import os
import sys
import textwrap
from typing import Any, Dict, Optional

# Ensure Windows console can handle Unicode (emojis, symbols) without crashing.
if sys.platform == "win32":
    try:
        if getattr(sys.stdout, "buffer", None) is not None and not getattr(sys.stdout, "closed", False):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        if getattr(sys.stderr, "buffer", None) is not None and not getattr(sys.stderr, "closed", False):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

import psycopg2
from psycopg2.extras import RealDictCursor


def connect_db(dsn: str):
    """Connect to PostgreSQL database using the provided DSN."""
    return psycopg2.connect(dsn)


def find_user(cur, username: Optional[str], email: Optional[str]) -> Optional[Dict[str, Any]]:
    if username:
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    elif email:
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    else:
        return None
    row = cur.fetchone()
    return dict(row) if row else None


def fetch_latest_quiz_sessions(cur, user_id: int, limit: int = 5):
    cur.execute(
        textwrap.dedent("""
            SELECT id, total_words, correct_count, incorrect_count, points_earned,
                   COALESCE(badge_bonus_points, 0) AS badge_points,
                   extra_points, total_points, accuracy_percentage, grade, completed,
                   session_start, session_end
            FROM quiz_sessions
            WHERE user_id = %s
            ORDER BY id DESC
            LIMIT %s
        """),
        (user_id, limit),
    )
    return [dict(r) for r in cur.fetchall()]


def fetch_user_stats(cur, user_id: int) -> Dict[str, Any]:
    cur.execute(
        "SELECT id, username, email, role, total_lifetime_points, total_quizzes_completed, "
        "best_streak, cumulative_gpa, average_accuracy FROM users WHERE id = %s",
        (user_id,),
    )
    row = cur.fetchone()
    return dict(row) if row else {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify quiz & stats persistence in DO Postgres")
    parser.add_argument("--user", help="Username of the user to inspect", default=None)
    parser.add_argument("--email", help="Email of the user to inspect", default=None)
    args = parser.parse_args()

    dsn = os.getenv("DO_DB_DSN") or os.getenv("DATABASE_URL") or os.getenv("DATABASE_URI")
    if not dsn:
        print("❌ DO_DB_DSN (or DATABASE_URL/DATABASE_URI) is not set.")
        print("Please set DO_DB_DSN to your DigitalOcean Postgres connection string.")
        return 1

    if not args.user and not args.email:
        print("❌ You must pass --user USERNAME or --email EMAIL to identify which user's stats to inspect.")
        return 1

    print("=" * 80)
    print("🐝 DB PERSISTENCE SMOKE TEST (DigitalOcean)")
    print("=" * 80)
    # Mask password in DSN for display
    display_dsn = dsn
    if "@" in dsn and ":" in dsn.split("@")[0]:
        parts = dsn.split("@")
        user_pass = parts[0].split("://")[1] if "://" in parts[0] else parts[0]
        if ":" in user_pass:
            user = user_pass.split(":")[0]
            display_dsn = dsn.replace(user_pass, f"{user}:***")
    print(f"Connecting to DB: {display_dsn}")

    try:
        conn = connect_db(dsn)
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return 1

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            user = find_user(cur, args.user, args.email)
            if not user:
                print("❌ User not found.")
                return 1

            print("\n✅ User found:")
            print(f"  id: {user['id']}")
            print(f"  username: {user.get('username')}")
            print(f"  email: {user.get('email')}")
            print(f"  role: {user.get('role')}")

            # Fetch latest quiz sessions
            sessions = fetch_latest_quiz_sessions(cur, user["id"], limit=5)
            if not sessions:
                print("\n⚠️  No quiz_sessions found for this user. Have you completed a quiz on DO?")
            else:
                print(f"\n✅ Latest Quiz Sessions (showing last {len(sessions)}):")
                for s in sessions:
                    print(
                        f"  - id={s['id']}, total_words={s['total_words']}, correct={s['correct_count']}, "
                        f"incorrect={s['incorrect_count']}, points_earned={s['points_earned']}, "
                        f"badge_points={s.get('badge_points', 0)}, extra={s.get('extra_points', 0)}, "
                        f"total_points={s.get('total_points', 0)}, accuracy={s.get('accuracy_percentage')}, "
                        f"grade={s.get('grade')}, completed={s['completed']}, "
                        f"start={s.get('session_start')}, end={s.get('session_end')}"
                    )

            # Fetch user stats
            stats = fetch_user_stats(cur, user["id"])
            print("\n✅ User Stats (users table):")
            print(f"  total_lifetime_points: {stats.get('total_lifetime_points')}")
            print(f"  total_quizzes_completed: {stats.get('total_quizzes_completed')}")
            print(f"  best_streak: {stats.get('best_streak')}")
            print(f"  cumulative_gpa: {stats.get('cumulative_gpa')}")
            print(f"  average_accuracy: {stats.get('average_accuracy')}")

            # Compare lifetime points vs sum of completed session points
            completed_points = 0
            completed_sessions = 0
            for s in sessions:
                if s.get("completed"):
                    completed_sessions += 1
                    # Prefer total_points if set, else sum components
                    if s.get("total_points") is not None:
                        completed_points += int(s["total_points"])
                    else:
                        p = int(s.get("points_earned") or 0) + int(s.get("badge_points") or 0) + int(s.get("extra_points") or 0)
                        completed_points += p

            print("\n📊 Comparison (based on latest fetched sessions):")
            print(f"  Completed sessions (last {len(sessions)}): {completed_sessions}")
            print(f"  Sum of completed session points (approx): {completed_points}")
            print(f"  Stored total_lifetime_points: {stats.get('total_lifetime_points')}")

            if completed_sessions > 0:
                if stats.get("total_lifetime_points") is None:
                    print("  ❌ total_lifetime_points is NULL - should be updated on quiz completion")
                elif stats["total_lifetime_points"] < completed_points:
                    print("  ⚠️  total_lifetime_points is LESS than sum of recent completed sessions (possible missing credits)")
                else:
                    print("  ✅ total_lifetime_points is >= sum of recent completed sessions (looks consistent)")
            else:
                print("  ℹ️  No completed sessions in recent history to compare against.")

    finally:
        try:
            conn.close()
        except Exception:
            pass

    print("\n✅ DB PERSISTENCE SMOKE CHECK COMPLETE")
    print("If values above look incorrect, please share this output so we can debug further.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
