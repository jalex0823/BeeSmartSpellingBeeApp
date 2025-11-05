import os
import sys
import pathlib
import json
from pprint import pprint

# Configure testing environment
os.environ['FLASK_ENV'] = 'testing'
os.environ['IAP_MOCK'] = '1'

# Ensure project root on sys.path
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from AjaSpellBApp import app  # noqa: E402
from models import db  # noqa: E402


def run():
    print("== IAP endpoint sanity test (mock mode) ==")
    with app.app_context():
        db.create_all()

    client = app.test_client()

    # 1) Register a user
    reg_payload = {
        "username": "iap_tester",
        "display_name": "IAP Tester",
        "password": "testpass",
        "email": "iap_tester@example.com",
        "role": "student",
        "avatar_id": "mascot-bee"
    }
    r = client.post('/auth/register', data=json.dumps(reg_payload), content_type='application/json')
    assert r.status_code == 200, f"register failed: {r.status_code} {r.data}"
    resp = r.get_json()
    assert resp.get('success') is True, resp
    print("- Registered user")

    # 2) Login explicitly (session cookie should already be set, but be explicit)
    login_payload = {
        "username": "iap_tester",
        "password": "testpass",
        "remember": False
    }
    r = client.post('/auth/login', data=json.dumps(login_payload), content_type='application/json')
    assert r.status_code == 200, f"login failed: {r.status_code} {r.data}"
    resp = r.get_json()
    assert resp.get('success') is True, resp
    print("- Logged in user")

    # 3) Verify full unlock in mock mode
    verify_payload = {
        "product_id": os.environ.get('PRODUCT_FULL_UNLOCK_ID', 'beesmart.full_unlock'),
        "transaction_id": "tx-mock-123",
        "payload": {"sandbox": True}
    }
    r = client.post('/api/iap/verify/apple', data=json.dumps(verify_payload), content_type='application/json')
    assert r.status_code == 200, f"verify failed: {r.status_code} {r.data}"
    resp = r.get_json()
    assert resp.get('success') is True, resp
    ents = resp.get('entitlements') or {}
    assert ents.get('premium_member') is True, ents
    print("- Verified premium unlock (mock)")

    # 4) Restore an avatar product id
    restore_payload = {
        "platform": "apple",
        "product_ids": [os.environ.get('PRODUCT_AVATAR_SUPERBEE_ID', 'beesmart.avatar.superbee')]
    }
    r = client.post('/api/iap/restore', data=json.dumps(restore_payload), content_type='application/json')
    assert r.status_code == 200, f"restore failed: {r.status_code} {r.data}"
    resp = r.get_json()
    assert resp.get('success') is True, resp
    ents = resp.get('entitlements') or {}
    purchased = ents.get('purchased_avatars') or []
    assert 'superbee' in purchased, ents
    print("- Restored avatar unlock (mock)")

    print("\n✅ IAP endpoints sanity test passed.")


if __name__ == '__main__':
    run()
