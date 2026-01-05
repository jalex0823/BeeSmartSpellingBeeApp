"""Ensure App Store review users exist (production-safe, idempotent).

Creates or updates three accounts required for Apple review:
- Student
- Teacher
- Parent
Optional:
- Admin (reviewer)

Design goals:
- Safe for production: does NOT drop tables, does NOT create arbitrary test data.
- Idempotent: running repeatedly updates password + role + key fields.
- Credentials come from environment variables (so secrets aren't committed).
- Minimal output: never prints passwords.

Required env vars (default mode):
    APP_REVIEW_STUDENT_PASS
    APP_REVIEW_TEACHER_PASS
    APP_REVIEW_PARENT_PASS
    (Optional) APP_REVIEW_*_USER overrides usernames

Optional admin reviewer env vars (default mode):
    APP_REVIEW_ADMIN_PASS
    (Optional) APP_REVIEW_ADMIN_USER override

Dangerous / review-only modes (opt-in):
    APP_REVIEW_RECREATE_USERS=1
            Deletes the review users (if present) and recreates them.
            Use ONLY when you want to guarantee a clean state.

    APP_REVIEW_USE_HARDCODED_CREDS=1
            Uses hardcoded usernames/passwords for App Review convenience.
            WARNING: This puts credentials in the repo. Only enable temporarily and
            consider reverting after App Review.

Optional:
  APP_REVIEW_STUDENT_DISPLAY
  APP_REVIEW_TEACHER_DISPLAY
  APP_REVIEW_PARENT_DISPLAY
    APP_REVIEW_ADMIN_DISPLAY
  APP_REVIEW_TEACHER_SCHOOL
  APP_REVIEW_STUDENT_GRADE

Operational flags:
  FAST_BOOT=1                     (recommended: avoid heavy startup checks)
  BYPASS_AVATAR_DB_SYNC=1         (recommended: avoid avatar sync side effects)
  ENSURE_REVIEW_USERS_LINK=1      (optional: link teacher+parent to student)

Usage:
  # Run locally OR in your DigitalOcean App Platform / Droplet container
  # with DATABASE_URL already configured there.
  python3 scripts/ensure_app_review_users.py

Notes:
- This script uses the same app+models as production.
- It updates/creates teacher_key for teacher/parent if missing.
"""

from __future__ import annotations

import os
import sys
import pathlib
from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewUserSpec:
    username_env: str
    password_env: str
    role: str
    default_username: str
    default_display: str
    display_env: str | None = None


SPECS: list[ReviewUserSpec] = [
    ReviewUserSpec(
        username_env="APP_REVIEW_STUDENT_USER",
        password_env="APP_REVIEW_STUDENT_PASS",
        role="student",
        default_username="apple_review_student",
        default_display="Apple Review Student",
        display_env="APP_REVIEW_STUDENT_DISPLAY",
    ),
    ReviewUserSpec(
        username_env="APP_REVIEW_TEACHER_USER",
        password_env="APP_REVIEW_TEACHER_PASS",
        role="teacher",
        default_username="apple_review_teacher",
        default_display="Apple Review Teacher",
        display_env="APP_REVIEW_TEACHER_DISPLAY",
    ),
    ReviewUserSpec(
        username_env="APP_REVIEW_PARENT_USER",
        password_env="APP_REVIEW_PARENT_PASS",
        role="parent",
        default_username="apple_review_parent",
        default_display="Apple Review Parent",
        display_env="APP_REVIEW_PARENT_DISPLAY",
    ),
]


ADMIN_SPEC = ReviewUserSpec(
    username_env="APP_REVIEW_ADMIN_USER",
    password_env="APP_REVIEW_ADMIN_PASS",
    role="admin",
    default_username="apple_review_admin",
    default_display="Apple Review Admin",
    display_env="APP_REVIEW_ADMIN_DISPLAY",
)


def _get_required_env(name: str) -> str:
    value = (os.getenv(name) or "").strip()
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def _get_optional_env(name: str, default: str = "") -> str:
    value = (os.getenv(name) or "").strip()
    return value if value else default


def _has_env(name: str) -> bool:
    return bool((os.getenv(name) or "").strip())


def _normalize_role(role: str) -> str:
    return (role or "student").strip().lower()


def _truthy_env(name: str) -> bool:
    return (os.getenv(name, "").strip().lower() in ("1", "true", "yes", "on"))


def _review_hardcoded_resolved() -> list[tuple[ReviewUserSpec, str, str, str]]:
    """Hardcoded App Review creds (temporary)."""
    return [
        (
            SPECS[0],
            "apple_review_student",
            "StudentReview#2026",
            "Apple Review Student",
        ),
        (
            SPECS[1],
            "apple_review_teacher",
            "TeacherReview#2026",
            "Apple Review Teacher",
        ),
        (
            SPECS[2],
            "apple_review_parent",
            "ParentReview#2026",
            "Apple Review Parent",
        ),
        (
            ADMIN_SPEC,
            "apple_review_admin",
            "AdminReview#2026",
            "Apple Review Admin",
        ),
    ]


def main() -> int:
    # Strongly recommend these in production runs to avoid side effects / slow boots.
    os.environ.setdefault("FAST_BOOT", "1")
    os.environ.setdefault("BYPASS_AVATAR_DB_SYNC", "1")

    project_root = pathlib.Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Import after env is set.
    from AjaSpellBApp import app  # noqa: WPS433
    from models import db, User, TeacherStudent  # noqa: WPS433

    created_or_updated: dict[str, int] = {}
    users_by_role: dict[str, User] = {}

    use_hardcoded = _truthy_env("APP_REVIEW_USE_HARDCODED_CREDS")
    recreate_users = _truthy_env("APP_REVIEW_RECREATE_USERS")

    if use_hardcoded:
        resolved = _review_hardcoded_resolved()
    else:
        # Resolve credentials from env; fail fast if any are missing.
        resolved = []
        for spec in SPECS:
            username = _get_optional_env(spec.username_env, spec.default_username)
            password = _get_required_env(spec.password_env)
            display_name = (
                _get_optional_env(spec.display_env, spec.default_display)
                if spec.display_env
                else spec.default_display
            )
            resolved.append((spec, username, password, display_name))

        # Admin reviewer is optional: only provision if APP_REVIEW_ADMIN_PASS is set.
        if _has_env(ADMIN_SPEC.password_env):
            admin_username = _get_optional_env(ADMIN_SPEC.username_env, ADMIN_SPEC.default_username)
            admin_password = _get_required_env(ADMIN_SPEC.password_env)
            admin_display = (
                _get_optional_env(ADMIN_SPEC.display_env, ADMIN_SPEC.default_display)
                if ADMIN_SPEC.display_env
                else ADMIN_SPEC.default_display
            )
            resolved.append((ADMIN_SPEC, admin_username, admin_password, admin_display))

    with app.app_context():
        # Ensure DB schema exists (safe: create_all is non-destructive)
        try:
            db.create_all()
        except Exception as e:
            print(f"⚠️ db.create_all() failed (continuing): {e}")

        # Optional: delete-and-recreate to guarantee a clean state.
        if recreate_users:
            usernames_to_recreate = [u for (_, u, _, _) in resolved]
            print("🧹 APP_REVIEW_RECREATE_USERS=1 → deleting existing review users (if any)")
            try:
                existing_users = User.query.filter(User.username.in_(usernames_to_recreate)).all()
                if existing_users:
                    # Best-effort cleanup of teacher_students links for these users.
                    try:
                        teacher_keys = [getattr(u, "teacher_key", None) for u in existing_users]
                        teacher_keys = [k for k in teacher_keys if k]
                        if teacher_keys:
                            TeacherStudent.query.filter(TeacherStudent.teacher_key.in_(teacher_keys)).delete(
                                synchronize_session=False
                            )
                    except Exception as e:
                        print(f"⚠️ Could not delete teacher_student links (continuing): {e}")

                    # Delete users.
                    for u in existing_users:
                        db.session.delete(u)
                    db.session.commit()
                    print(f"   ✅ Deleted {len(existing_users)} existing review user(s)")
            except Exception as e:
                print(f"⚠️ Failed deleting review users (continuing): {e}")

        for spec, username, password, display_name in resolved:
            # Case-insensitive lookup when possible
            user = None
            try:
                user = User.query.filter(db.func.lower(User.username) == username.lower()).first()
            except Exception:
                user = User.query.filter_by(username=username).first()

            if user is None:
                user = User(
                    username=username,
                    display_name=display_name,
                    email=None,
                    role=_normalize_role(spec.role),
                    premium_member=False,
                    admin_all_access=(_normalize_role(spec.role) == "admin"),
                    is_active=True,
                )
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                created_or_updated[username] = int(user.id)
                print(f"✅ Created {spec.role} user: {username} (id={user.id})")
            else:
                user.display_name = display_name
                user.role = _normalize_role(spec.role)
                if hasattr(user, "premium_member"):
                    user.premium_member = False
                if hasattr(user, "admin_all_access"):
                    user.admin_all_access = (_normalize_role(spec.role) == "admin")
                if hasattr(user, "is_active"):
                    user.is_active = True
                user.set_password(password)
                db.session.commit()
                created_or_updated[username] = int(user.id)
                print(f"✅ Updated {spec.role} user: {username} (id={user.id})")

            # Ensure teacher_key exists for teacher/parent where used
            if _normalize_role(spec.role) in ("teacher", "parent"):
                if not getattr(user, "teacher_key", None):
                    try:
                        user.generate_teacher_key()
                        db.session.commit()
                        print(f"   🔑 Generated teacher_key for {username}")
                    except Exception as e:
                        print(f"⚠️ Could not generate teacher_key for {username}: {e}")

            users_by_role[_normalize_role(spec.role)] = user

        # Optional: link teacher + parent to student
        if (os.getenv("ENSURE_REVIEW_USERS_LINK", "0").strip().lower() in ("1", "true", "yes", "on")):
            student = users_by_role.get("student")
            teacher = users_by_role.get("teacher")
            parent = users_by_role.get("parent")

            if not student or not teacher or not parent:
                print("⚠️ Link requested but missing one of student/teacher/parent; skipping links")
            else:
                for rel_user, rel_type in ((teacher, "teacher"), (parent, "parent")):
                    try:
                        existing = TeacherStudent.query.filter_by(
                            teacher_key=rel_user.teacher_key,
                            student_id=student.id,
                            is_active=True,
                        ).first()
                        if existing:
                            # Ensure relationship_type matches
                            if hasattr(existing, "relationship_type") and existing.relationship_type != rel_type:
                                existing.relationship_type = rel_type
                                db.session.commit()
                            continue

                        link = TeacherStudent(
                            teacher_key=rel_user.teacher_key,
                            teacher_user_id=rel_user.id,
                            student_id=student.id,
                            relationship_type=rel_type,
                            is_active=True,
                        )
                        db.session.add(link)
                        db.session.commit()
                        print(f"🔗 Linked {rel_type} ({rel_user.username}) -> student ({student.username})")
                    except Exception as e:
                        print(f"⚠️ Failed linking {rel_type} -> student: {e}")

    print("\n✅ App review users ensured. Passwords were NOT printed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
