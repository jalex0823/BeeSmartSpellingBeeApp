import pytest
from AjaSpellBApp import app, db
from models import User

@pytest.fixture()
def client():
    with app.test_client() as c:
        yield c

def login(client, username, password):
    return client.post('/auth/login', data={'username': username, 'password': password}, follow_redirects=True)

@pytest.mark.parametrize('endpoint', ['/api/avatars'])
def test_guest_receives_only_mascot(client, endpoint):
    resp = client.get(f'{endpoint}?force=1')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get('user_authenticated') is False
    assert data.get('is_guest') is True
    assert data.get('guest_limited') is True
    avatars = data.get('avatars', [])
    assert len(avatars) == 1, f"Expected 1 avatar for guest, got {len(avatars)}"
    assert avatars[0]['id'] in ('honey-comb','honeycomb','mascot-bee')
    # Locked reason should be guest_mascot or absent; nothing else exposed
    assert avatars[0].get('locked_reason') in (None,'guest_mascot')

@pytest.mark.parametrize('endpoint', ['/api/avatars'])
def test_student_catalog_and_lock_reasons(client, endpoint):
    # Ensure student user exists (fallback create if not)
    with app.app_context():
        stu = User.query.filter(User.username.ilike('stud1')).first()
        assert stu is not None, "Test requires existing student user 'stud1'"
    login(client, 'stud1', 'Password123!')
    resp = client.get(f'{endpoint}?force=1')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get('user_authenticated') is True
    avatars = data.get('avatars', [])
    # Expect full catalog (>= 30; currently 40)
    assert len(avatars) >= 30
    # Validate mixture of unlocked and locked avatars
    locked = [a for a in avatars if a.get('is_locked')]
    unlocked = [a for a in avatars if not a.get('is_locked')]
    assert locked and unlocked, "Expected both locked and unlocked avatars for student"
    # Check locked_reason codes present for locked avatars
    for a in locked[:5]:  # sample few
        assert a.get('locked_reason') in {'not_enough_points','not_purchased','progress_required'}, f"Unexpected locked_reason {a.get('locked_reason')}" 

@pytest.mark.parametrize('endpoint', ['/api/avatars'])
def test_admin_all_unlocked(client, endpoint):
    # Ensure admin user exists
    with app.app_context():
        admin = User.query.filter(User.username.ilike('admin')).first()
        assert admin is not None, "Test requires existing admin user 'admin'"
    login(client, 'admin', 'Password123!')
    resp = client.get(f'{endpoint}?force=1')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data.get('user_authenticated') is True
    avatars = data.get('avatars', [])
    # All avatars should be unlocked for admin
    assert avatars, "No avatars returned for admin"
    locked = [a for a in avatars if a.get('is_locked')]
    assert not locked, f"Admin should have zero locked avatars, found {len(locked)}"
    for a in avatars[:5]:
        # locked_reason should be admin_unlocked or unlocked (fallback for free/misc)
        assert a.get('locked_reason') in {'admin_unlocked','unlocked','free'}, f"Unexpected locked_reason for admin: {a.get('locked_reason')}"
