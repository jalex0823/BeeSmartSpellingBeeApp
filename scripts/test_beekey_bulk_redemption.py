"""Test script for /api/beekey/redeem-for-linked endpoint.
Run: python scripts/test_beekey_bulk_redemption.py

Validates bulk BeeKey redemption:
 1. Teacher login succeeds
 2. Two students linked via TeacherStudent
 3. Dynamic bundle created
 4. BeeKey created (max_uses sufficient)
 5. Bulk redemption unlocks avatars for all linked students
 6. Each student sees avatars with locked_reason == teacher_unlocked
 7. Provenance tagging (beekey_unlocked_avatars) includes all bundle avatars for each student
"""
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from AjaSpellBApp import app
from models import db, User, TeacherStudent, DynamicBundle, BundleKey
from werkzeug.security import generate_password_hash

BUNDLE_ID = 'test_bulk_class_pack'
BUNDLE_AVATARS = ['robo-bee', 'cool-bee']  # Keep small for speed
TEACHER_USERNAME = 'teacher_beekey_bulk'
STUDENT_USERNAMES = ['student_bulk_one', 'student_bulk_two']
PASSWORD = 'TestPass123!'


def ensure_user(username: str, role: str):
    user = User.query.filter_by(username=username).first()
    if user:
        if not user.check_password(PASSWORD):
            user.password_hash = generate_password_hash(PASSWORD)
        return user
    user = User(username=username,
                display_name=f"{role.title()} Bulk User",
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
        dyn = DynamicBundle(bundle_id=BUNDLE_ID, name='Test Bulk Class Pack', avatars=BUNDLE_AVATARS)
        db.session.add(dyn)
        db.session.commit()
    return dyn


def create_beekey(bundle_id: str):
    key_raw, key_norm = BundleKey.generate(bundle_id, prefix='BEEKEY')
    bk = BundleKey(key_raw=key_raw, key_norm=key_norm, bundle_id=bundle_id, max_uses=10, status='active')
    db.session.add(bk)
    db.session.commit()
    return {'key_raw': key_raw, 'key_norm': key_norm}


def main():
    with app.app_context():
        teacher = ensure_user(TEACHER_USERNAME, 'teacher')
        students = [ensure_user(u, 'student') for u in STUDENT_USERNAMES]
        for s in students:
            ensure_link(teacher, s)
        ensure_dynamic_bundle()
        bkey = create_beekey(BUNDLE_ID)
        student_ids = [s.id for s in students]

    with app.test_client() as c:
        # Login teacher
        lr = c.post('/auth/login', json={'username': TEACHER_USERNAME, 'password': PASSWORD}, follow_redirects=False)
        if lr.status_code != 200 or not lr.is_json or not lr.get_json().get('success'):
            print('FAIL: Teacher login failed', lr.status_code, lr.get_json())
            sys.exit(1)

        # Bulk redeem
        rr = c.post('/api/beekey/redeem-for-linked', json={'beekey': bkey['key_raw']})
        if rr.status_code != 200:
            print('FAIL: Bulk redemption status != 200', rr.status_code, rr.get_json())
            sys.exit(1)
        rdata = rr.get_json() or {}
        if not rdata.get('success'):
            print('FAIL: Bulk redemption success flag false', rdata)
            sys.exit(1)
        if rdata.get('avatars_count') != len(BUNDLE_AVATARS):
            print('FAIL: avatars_count mismatch', rdata)
            sys.exit(1)
        if rdata.get('users_unlocked') < len(student_ids):  # some may already have had avatars from prior runs
            print('FAIL: Not all students reported unlocked', rdata)
            sys.exit(1)

        # Verify each student
        for sid, username in zip(student_ids, STUDENT_USERNAMES):
            c.post('/auth/login', json={'username': username, 'password': PASSWORD})
            av_resp = c.get('/api/avatars?force=1')
            if av_resp.status_code != 200:
                print(f'FAIL: /api/avatars for {username} status != 200', av_resp.status_code)
                sys.exit(1)
            av_json = av_resp.get_json() or {}
            avatars = av_json.get('avatars', [])
            avatar_map = {a['id']: a for a in avatars}
            missing = [a for a in BUNDLE_AVATARS if a not in avatar_map]
            if missing:
                print(f'FAIL: Redeemed avatars missing for {username}', missing)
                sys.exit(1)
            bad_reason = [a for a in BUNDLE_AVATARS if avatar_map[a].get('locked_reason') != 'teacher_unlocked']
            if bad_reason:
                print(f'FAIL: Incorrect locked_reason for {username}', bad_reason, {a: avatar_map[a].get('locked_reason') for a in bad_reason})
                sys.exit(1)

            # Provenance
            with app.app_context():
                student_db = User.query.filter_by(id=sid).first()
                prefs = (student_db.preferences or {})
                provenance = set(prefs.get('beekey_unlocked_avatars', []) or [])
                if not all(a in provenance for a in BUNDLE_AVATARS):
                    print(f'FAIL: Provenance missing avatars for {username}', provenance)
                    sys.exit(1)

        print('PASS: Bulk BeeKey redemption test succeeded.')

if __name__ == '__main__':
    main()
