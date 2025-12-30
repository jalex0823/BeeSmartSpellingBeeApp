import os
import sys
import pathlib
import json

def run():
    # Configure permissive live-like mode (no real store calls required)
    os.environ['FLASK_ENV'] = 'testing'
    os.environ.setdefault('FAST_BOOT', '1')
    os.environ.setdefault('SKIP_AVATAR_STARTUP_SYNC', '1')
    os.environ['IAP_MOCK'] = '0'
    os.environ['IAP_VERIFICATION_MODE'] = 'live_permissive'
    os.environ['IAP_LIVE_ACCEPT_BASIC'] = '1'

    PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from AjaSpellBApp import app  # noqa: E402
    from models import db  # noqa: E402

    with app.app_context():
        db.create_all()

    client = app.test_client()

    # Register
    r = client.post('/auth/register', data=json.dumps({
        "username": "iap_live_user",
        "display_name": "IAP LiveUser",
        "password": "testpass",
        "email": "live_user@example.com",
        "role": "student",
        "avatar_id": "mascot-bee"
    }), content_type='application/json')
    if r.status_code != 200:
        # Allow re-running smoke tests against a persistent DB.
        try:
            body = r.get_json() or {}
        except Exception:
            body = {}
        if not (r.status_code == 400 and str(body.get('error', '')).lower().startswith('username already taken')):
            raise AssertionError(f"register failed: {r.status_code} {r.data}")

    # Login
    r = client.post('/auth/login', data=json.dumps({
        "username": "iap_live_user",
        "password": "testpass",
        "remember": False
    }), content_type='application/json')
    assert r.status_code == 200, f"login failed: {r.status_code} {r.data}"
    assert r.get_json().get('success') is True

    # Verify subscription (permissive)
    subscription_pid = os.environ.get('PRODUCT_SUBSCRIPTION_FULL_ID', 'com.beesmart.premium.monthly')
    verify_payload = {
        "product_id": subscription_pid,
        "transaction_id": "tx-demo-permissive",
        "payload": {"note": "permissive"}
    }
    r = client.post('/api/iap/verify/apple', data=json.dumps(verify_payload), content_type='application/json')
    assert r.status_code == 200, f"verify failed: {r.status_code} {r.data}"
    resp = r.get_json()
    assert resp.get('success') is True, resp
    ents = resp.get('entitlements') or {}
    assert ents.get('premium_member') is True, ents

    # Restore one avatar
    from avatar_skus import sku_for_slug  # noqa: E402
    restore_payload = {
        "platform": "apple",
        "product_ids": [os.environ.get('PRODUCT_AVATAR_SUPERBEE_ID', sku_for_slug('super-bee'))]
    }
    r = client.post('/api/iap/restore', data=json.dumps(restore_payload), content_type='application/json')
    assert r.status_code == 200, f"restore failed: {r.status_code} {r.data}"
    resp = r.get_json()
    assert resp.get('success') is True, resp
    applied = resp.get('applied') or []
    applied_pids = [a.get('product_id') for a in applied if isinstance(a, dict)]
    assert restore_payload['product_ids'][0] in applied_pids, {"applied": applied, "expected": restore_payload['product_ids'][0]}

    print("\n✅ IAP live_permissive test passed.")

if __name__ == '__main__':
    run()
