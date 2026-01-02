import os
import sys
import pathlib
import json
import uuid
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
from avatar_skus import sku_for_slug  # noqa: E402
from bundle_skus import bundle_sku_for_id  # noqa: E402
from avatar_bundles import BUNDLE_CATALOG  # noqa: E402


def run():
    print("== IAP endpoint sanity test (mock mode) ==")
    with app.app_context():
        db.create_all()

    client = app.test_client()

    # Keep the test idempotent even when using a persistent local DB.
    _nonce = uuid.uuid4().hex[:8]
    _username = f"iap_tester_{_nonce}"
    _email = f"iap_tester_{_nonce}@example.com"

    # 1) Register a user
    reg_payload = {
        "username": _username,
        "display_name": "IAP Tester",
        "password": "testpass",
        "email": _email,
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
        "username": _username,
        "password": "testpass",
        "remember": False
    }
    r = client.post('/auth/login', data=json.dumps(login_payload), content_type='application/json')
    assert r.status_code == 200, f"login failed: {r.status_code} {r.data}"
    resp = r.get_json()
    assert resp.get('success') is True, resp
    print("- Logged in user")

    # 3) Restore an avatar product id (non-premium path)
    restore_payload = {
        "platform": "apple",
        # Use canonical store SKU form (prefix + hyphenated slug)
        "product_ids": [sku_for_slug('super-bee')]
    }
    r = client.post('/api/iap/restore', data=json.dumps(restore_payload), content_type='application/json')
    assert r.status_code == 200, f"restore failed: {r.status_code} {r.data}"
    resp = r.get_json()
    assert resp.get('success') is True, resp
    ents = resp.get('entitlements') or {}
    assert ents.get('premium_member') is False, ents
    # The entitlement summary has evolved; accept either explicit purchases or
    # broader unlock lists as proof the restore applied.
    purchased = ents.get('purchased_avatars') or []
    unlocked = ents.get('unlocked_avatars') or []
    assert ('super-bee' in purchased) or ('super-bee' in unlocked), ents
    print("- Restored avatar unlock (mock)")

    # 4) Restore a bundle product id (non-premium path)
    bundle_id = None
    try:
        bundle_id = next(iter((BUNDLE_CATALOG or {}).keys()))
    except Exception:
        bundle_id = None
    assert bundle_id, f"No bundles available in BUNDLE_CATALOG: {BUNDLE_CATALOG}"
    bundle_sku = bundle_sku_for_id(bundle_id)
    restore_payload = {
        "platform": "apple",
        "product_ids": [bundle_sku]
    }
    r = client.post('/api/iap/restore', data=json.dumps(restore_payload), content_type='application/json')
    assert r.status_code == 200, f"restore bundle failed: {r.status_code} {r.data}"
    resp = r.get_json()
    assert resp.get('success') is True, resp
    ents = resp.get('entitlements') or {}
    purchased_bundles = ents.get('purchased_bundles') or []
    unlocked_bundles = ents.get('unlocked_bundles') or []
    assert (bundle_id in purchased_bundles) or (bundle_id in unlocked_bundles), ents
    print(f"- Restored bundle unlock (mock): {bundle_id}")

    # 5) Verify full unlock in mock mode (premium path)
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

    print("\n✅ IAP endpoints sanity test passed.")


if __name__ == '__main__':
    run()
