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

    # TEACHER
    teacher_user = f'teacher_{rand}'
    payload_teacher = {
        "username": teacher_user,
        "display_name": "Teacher",
        "password": "Passw0rd!",
        "email": f"{teacher_user}@example.com",
        "role": "teacher",
        "avatar_id": "mascot-bee"
    }
    r = client.post('/auth/register', json=payload_teacher)
    print('REGISTER TEACHER', r.status_code, (r.get_json() or {}).get('success'))
    # Avatars API for teacher
    r = client.get('/api/avatars')
    td = r.get_json() or {}
    t_avatars = td.get('avatars', [])
    t_locked = sum(1 for a in t_avatars if a.get('is_locked'))
    t_unlocked = sum(1 for a in t_avatars if not a.get('is_locked'))
    print('TEACHER STATUS', r.status_code, 'locked/unlocked:', t_locked, t_unlocked)
    # Teacher dashboard access
    r = client.get('/teacher/dashboard')
    print('TEACHER DASHBOARD', r.status_code)

    client.get('/auth/logout')

    # PARENT
    parent_user = f'parent_{rand}'
    payload_parent = {
        "username": parent_user,
        "display_name": "Parent",
        "password": "Passw0rd!",
        "email": f"{parent_user}@example.com",
        "role": "parent",
        "avatar_id": "mascot-bee"
    }
    r = client.post('/auth/register', json=payload_parent)
    print('REGISTER PARENT', r.status_code, (r.get_json() or {}).get('success'))
    # Avatars API for parent
    r = client.get('/api/avatars')
    pd = r.get_json() or {}
    p_avatars = pd.get('avatars', [])
    p_locked = sum(1 for a in p_avatars if a.get('is_locked'))
    p_unlocked = sum(1 for a in p_avatars if not a.get('is_locked'))
    print('PARENT STATUS', r.status_code, 'locked/unlocked:', p_locked, p_unlocked)
    # Parent dashboard access
    r = client.get('/parent/dashboard')
    print('PARENT DASHBOARD', r.status_code)

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
