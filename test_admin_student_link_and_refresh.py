"""Tests for student linking via teacher_key/admin key and dynamic stats refresh.

Focus areas:
1. Registration with teacher_key referencing an admin user creates TeacherStudent link.
2. Admin refresh endpoint `/api/admin/my-students` returns linked student with quiz_count and last_active.
3. Adding a new quiz session updates quiz_count and last_active on subsequent refresh.
4. A newly linked student with no sessions falls back to created_at for last_active.

These tests use the existing sqlite database; usernames are randomized to avoid collisions.
"""

from __future__ import annotations

import json
import random
import string
from datetime import datetime, timedelta

from AjaSpellBApp import app
from models import db, User, TeacherStudent, QuizSession


def _rand(suffix_len: int = 6) -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=suffix_len))


def create_admin() -> User:
    admin_username = f"admin_test_{_rand()}"
    admin = User(
        username=admin_username,
        display_name="Admin Test",
        email=f"{admin_username}@example.com",
        role="admin",
    )
    admin.set_password("Passw0rd!")
    # Manually generate a teacher_key for admin (not auto-generated in constructor)
    admin.generate_teacher_key()
    db.session.add(admin)
    db.session.commit()
    return admin


def register_student_with_key(client, teacher_key: str, *, with_session: bool = True) -> User:
    username = f"student_test_{_rand()}"
    payload = {
        "username": username,
        "display_name": "Student Test",
        "password": "Passw0rd!",
        "role": "student",
        "teacher_key": teacher_key,
        "avatar_id": "cool-bee",
    }
    resp = client.post(
        "/auth/register",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 200, resp.get_data(as_text=True)
    data = resp.get_json()
    assert data["success"] is True
    assert data.get("linked_to_admin") is True, "Expected student to link via teacher_key"

    student = User.query.filter_by(username=username).first()
    assert student is not None

    # Optionally create an initial completed quiz session for activity tracking
    if with_session:
        qs = QuizSession(
            user_id=student.id,
            teacher_key=teacher_key,
            total_words=10,
            correct_count=7,
            incorrect_count=3,
            completed=True,
        )
        # Ensure deterministic ordering by setting explicit start/end
        qs.session_start = datetime.utcnow() - timedelta(minutes=5)
        qs.complete_session()
        db.session.add(qs)
        db.session.commit()
    return student


def call_admin_students_endpoint(admin: User):
    """Return parsed JSON for /api/admin/my-students as admin.

    Uses real login flow to avoid session nuances in different test clients.
    """
    client = app.test_client()
    # Perform login via API
    login_resp = client.post(
        "/auth/login",
        data=json.dumps({"username": admin.username, "password": "Passw0rd!"}),
        content_type="application/json",
    )
    assert login_resp.status_code == 200, login_resp.get_data(as_text=True)
    login_json = login_resp.get_json()
    assert login_json.get("success") is True, login_json
    resp = client.get('/api/admin/my-students')
    assert resp.status_code == 200, resp.get_data(as_text=True)
    data = resp.get_json()
    assert data.get('success') is True, data
    return data


def test_admin_student_link_and_dynamic_refresh():  # pragma: no cover - executed as script
    with app.app_context():
        db.create_all()

        # 1. Create isolated admin with unique teacher_key
        admin = create_admin()
        teacher_key = admin.teacher_key
        assert teacher_key, "Admin should have generated teacher_key"

        # 2. Register student linked via teacher_key (with initial quiz session)
        student_client = app.test_client()
        student = register_student_with_key(student_client, teacher_key, with_session=True)

        # Verify TeacherStudent link exists
        link = TeacherStudent.query.filter_by(teacher_key=teacher_key, student_id=student.id).first()
        assert link is not None, "TeacherStudent link missing"

        # 3. Initial endpoint call
        data_initial = call_admin_students_endpoint(admin)
        assert data_initial['count'] >= 1
        record = next((s for s in data_initial['students'] if s['id'] == student.id), None)
        assert record, "Linked student not returned from endpoint"
        initial_quiz_count = record['quiz_count']
        initial_last_active = record['last_active']
        assert initial_quiz_count >= 1

        # 4. Add a newer quiz session to simulate recent activity
        qs_new = QuizSession(
            user_id=student.id,
            teacher_key=teacher_key,
            total_words=8,
            correct_count=6,
            incorrect_count=2,
            completed=True,
        )
        qs_new.session_start = datetime.utcnow() - timedelta(minutes=1)
        qs_new.complete_session()
        db.session.add(qs_new)
        db.session.commit()

        # 5. Refresh endpoint and verify updated stats
        data_updated = call_admin_students_endpoint(admin)
        record_updated = next((s for s in data_updated['students'] if s['id'] == student.id), None)
        assert record_updated, "Student missing after refresh"
        assert record_updated['quiz_count'] >= initial_quiz_count + 1, (
            f"quiz_count did not increase: before={initial_quiz_count} after={record_updated['quiz_count']}"
        )
        assert record_updated['last_active'] != initial_last_active, (
            "last_active did not change after new quiz session"
        )

        # 6. Register a second student with no quiz sessions to test fallback last_active
        student_client2 = app.test_client()
        student2 = register_student_with_key(student_client2, teacher_key, with_session=False)
        data_after_second = call_admin_students_endpoint(admin)
        record2 = next((s for s in data_after_second['students'] if s['id'] == student2.id), None)
        assert record2, "Second student missing in endpoint results"
        # Fallback last_active should still be present (created_at) and human readable
        assert record2['last_active'] is not None
        assert record2['last_active_human'], "Expected human-friendly last_active string for student with no sessions"

        print("✅ test_admin_student_link_and_dynamic_refresh passed: linkage and dynamic stats verified.")


if __name__ == "__main__":  # Allow ad-hoc execution
    test_admin_student_link_and_dynamic_refresh()
