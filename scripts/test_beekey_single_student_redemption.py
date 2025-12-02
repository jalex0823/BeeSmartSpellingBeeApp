"""Test script for /api/beekey/redeem-for-student endpoint.
Run directly: python scripts/test_beekey_single_student_redemption.py

Validates:
 1. Teacher login succeeds
 2. Student is linked via TeacherStudent
 3. BeeKey dynamic bundle created with avatars
 4. Redemption endpoint unlocks avatars for student
 5. Student avatar API returns locked_reason == teacher_unlocked for redeemed avatars
 6. Preferences provenance tagging (beekey_unlocked_avatars)
"""
import os, sys
# Ensure project root on path when run from scripts/ subdirectory
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from AjaSpellBApp import app
from models import db, User, TeacherStudent, DynamicBundle, BundleKey
from werkzeug.security import generate_password_hash
import sys

# Configuration for test bundle
BUNDLE_ID = 'test_class_pack'
BUNDLE_AVATARS = ['robo-bee', 'cool-bee']  # Ensure these slugs exist in catalog
TEACHER_USERNAME = 'teacher_beekey_test'
STUDENT_USERNAME = 'student_beekey_test'
PASSWORD = 'TestPass123!'


def ensure_user(username: str, role: str):
    user = User.query.filter_by(username=username).first()
    if user:
        # Ensure password matches expected (avoid stale hash issues)
        if not user.check_password(PASSWORD):
            user.password_hash = generate_password_hash(PASSWORD)
        return user
    user = User(username=username,
                display_name=f"{role.title()} User",
                email=f"{username}@example.com",
                role=role,
                password_hash=generate_password_hash(PASSWORD))
    if role == 'teacher':
        user.generate_teacher_key()
    db.session.add(user)
    db.session.commit()
    return user


def ensure_link(teacher: User, student: User):
    link = TeacherStudent.query.filter_by(teacher_key=teacher.teacher_key, student_id=student.id).first()
    if not link:
        link = TeacherStudent(teacher_key=teacher.teacher_key, teacher_user_id=teacher.id, student_id=student.id)
        db.session.add(link)
        db.session.commit()
    return link


def ensure_dynamic_bundle():
    dyn = DynamicBundle.query.filter_by(bundle_id=BUNDLE_ID).first()
    if not dyn:
        dyn = DynamicBundle(bundle_id=BUNDLE_ID, name='Test Class Pack', avatars=BUNDLE_AVATARS)
        db.session.add(dyn)
        db.session.commit()
    return dyn


def create_beekey(bundle_id: str):
    # Must run within app context; caller ensures this
    key_raw, key_norm = BundleKey.generate(bundle_id, prefix='BEEKEY')
    bk = BundleKey(key_raw=key_raw, key_norm=key_norm, bundle_id=bundle_id, max_uses=5, status='active')
    db.session.add(bk)
    db.session.commit()
    return {'key_raw': key_raw, 'key_norm': key_norm}


def main():
    with app.app_context():
        teacher = ensure_user(TEACHER_USERNAME, 'teacher')
        student = ensure_user(STUDENT_USERNAME, 'student')
        ensure_link(teacher, student)
        ensure_dynamic_bundle()
        bkey = create_beekey(BUNDLE_ID)
        # Persist student id before leaving context to avoid DetachedInstance issues
        student_id = student.id

    with app.test_client() as c:
        # Login teacher
        lr = c.post('/auth/login', json={'username': TEACHER_USERNAME, 'password': PASSWORD}, follow_redirects=False)
        if lr.status_code != 200 or not lr.is_json or not lr.get_json().get('success'):
            print('FAIL: Teacher login failed', lr.status_code, lr.get_json())
            sys.exit(1)

        # Redeem for student
        rr = c.post('/api/beekey/redeem-for-student', json={'beekey': bkey['key_raw'], 'student_id': student_id})
        if rr.status_code != 200:
            print('FAIL: Redemption endpoint status != 200', rr.status_code, rr.get_json())
            sys.exit(1)
        rdata = rr.get_json()
        if not rdata.get('success'):
            print('FAIL: Redemption success flag false', rdata)
            sys.exit(1)
        if rdata.get('unlocked_count') != len(BUNDLE_AVATARS):
            print('FAIL: unlocked_count mismatch', rdata)
            sys.exit(1)

        # Switch to student
        c.post('/auth/login', json={'username': STUDENT_USERNAME, 'password': PASSWORD})
        av_resp = c.get('/api/avatars?force=1')
        if av_resp.status_code != 200:
            print('FAIL: /api/avatars status != 200', av_resp.status_code)
            sys.exit(1)
        av_json = av_resp.get_json() or {}
        avatars = av_json.get('avatars', [])
        avatar_map = {a['id']: a for a in avatars}
        missing = [a for a in BUNDLE_AVATARS if a not in avatar_map]
        if missing:
            print('FAIL: Redeemed avatars missing from API response', missing)
            sys.exit(1)
        bad_reason = [a for a in BUNDLE_AVATARS if avatar_map[a].get('locked_reason') != 'teacher_unlocked']
        if bad_reason:
            print('FAIL: Incorrect locked_reason for', bad_reason, {a: avatar_map[a].get('locked_reason') for a in bad_reason})
            sys.exit(1)

        # Reload student to inspect preferences provenance
        with app.app_context():
            student_db = User.query.filter_by(id=student_id).first()
            prefs = (student_db.preferences or {})
            provenance = set(prefs.get('beekey_unlocked_avatars', []) or [])
            if not all(a in provenance for a in BUNDLE_AVATARS):
                print('FAIL: Provenance tagging missing avatars', provenance)
                sys.exit(1)

        print('PASS: BeeKey single student redemption test succeeded.')

if __name__ == '__main__':
    main()
