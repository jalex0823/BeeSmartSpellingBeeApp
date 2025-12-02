import random, string, os, sys
# Ensure repository root is in sys.path so we can import AjaSpellBApp when executed from scripts/
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
import AjaSpellBApp as app_module

app = app_module.app
admin_key = getattr(app_module, 'ADMIN_REGISTRATION_KEY', None)
rand = ''.join(random.choices(string.ascii_lowercase+string.digits, k=6))

with app.test_client() as client:
    r = client.get('/api/avatars')
    print('GUEST STATUS', r.status_code)
    gd = r.get_json()
    print('GUEST BODY status:', gd.get('status'))
    av = gd.get('avatars') or []
    print('GUEST avatar count:', len(av))
    if av:
        print('GUEST first avatar id:', av[0].get('id'), 'locked?', av[0].get('is_locked'))

    student_user = f'student_{rand}'
    payload_student = {
        "username": student_user,
        "display_name": "Test Student",
        "password": "Passw0rd!",
        "email": f"{student_user}@example.com",
        "role": "student",
        "avatar_id": "mascot-bee"
    }
    r = client.post('/auth/register', json=payload_student)
    print('REGISTER STUDENT', r.status_code, (r.get_json() or {}).get('success'))

    r = client.get('/api/avatars')
    sd = r.get_json() or {}
    avatars = sd.get('avatars', [])
    locked = sum(1 for a in avatars if a.get('is_locked'))
    unlocked = sum(1 for a in avatars if not a.get('is_locked'))
    print('STUDENT STATUS', r.status_code, 'locked/unlocked:', locked, unlocked)

    client.get('/auth/logout')

    admin_user = f'admin_{rand}'
    payload_admin = {
        "username": admin_user,
        "display_name": "Admin",
        "password": "Passw0rd!",
        "email": f"{admin_user}@example.com",
        "role": "admin",
        "admin_key": admin_key,
        "avatar_id": "mascot-bee"
    }
    r = client.post('/auth/register', json=payload_admin)
    print('REGISTER ADMIN', r.status_code, (r.get_json() or {}).get('success'))

    r = client.get('/api/avatars')
    ad = r.get_json() or {}
    avatars = ad.get('avatars', [])
    locked = sum(1 for a in avatars if a.get('is_locked'))
    unlocked = sum(1 for a in avatars if not a.get('is_locked'))
    print('ADMIN STATUS', r.status_code, 'locked/unlocked:', locked, unlocked, 'all_unlocked:', locked == 0 and unlocked >= 1)
