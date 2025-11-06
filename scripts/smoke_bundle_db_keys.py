#!/usr/bin/env python3
"""Smoke test for DB-managed bundle keys.
Requires an admin account credentials via USERNAME/PASSWORD env vars.

Usage:
  BASE_URL=http://localhost:5050 USERNAME=admin PASSWORD=SECRET python scripts/smoke_bundle_db_keys.py
"""
import os, sys, json
try:
    import requests
except Exception:
    print("Install requests: pip install requests")
    sys.exit(2)

BASE_URL = os.getenv('BASE_URL','http://localhost:5050').rstrip('/')
USER = os.getenv('USERNAME','admin')
PASS = os.getenv('PASSWORD','ADMIN-PASS')
BUNDLE_ID = os.getenv('BUNDLE_ID','classroom_starter_pack')

s = requests.Session()
print(f"➡️ Base: {BASE_URL}")
print("🔐 Logging in (admin)...")
resp = s.post(f"{BASE_URL}/auth/login", json={"username": USER, "password": PASS})
try: data = resp.json()
except: data = {'raw': resp.text}
if not resp.ok or not data.get('success'):
    print('❌ Login failed', resp.status_code, data)
    sys.exit(1)
print('✅ Logged in')

print('🎁 Creating bundle key...')
resp = s.post(f"{BASE_URL}/api/admin/bundle-keys", json={"bundle_id": BUNDLE_ID, "max_uses": 1, "expires_days": 0})
try: create_body = resp.json()
except: create_body = {'raw': resp.text}
if not resp.ok or not create_body.get('success'):
    print('❌ Create failed', resp.status_code, create_body)
    sys.exit(1)
key_raw = create_body['bundle_key']['key_raw']
print('✅ Created key:', key_raw)

print('🔓 Redeeming key...')
resp = s.post(f"{BASE_URL}/api/bundles/redeem", json={"key": key_raw})
try: redeem_body = resp.json()
except: redeem_body = {'raw': resp.text}
if not resp.ok or not redeem_body.get('success'):
    print('❌ Redemption failed', resp.status_code, redeem_body)
    sys.exit(1)
print('✅ Redemption success:', json.dumps({
    'bundle_id': redeem_body.get('bundle_id'),
    'source': redeem_body.get('source'),
    'unlocked_count': redeem_body.get('unlocked_count'),
}, indent=2))

print('🔁 Attempting second redemption (should be exhausted)...')
resp = s.post(f"{BASE_URL}/api/bundles/redeem", json={"key": key_raw})
try: second = resp.json()
except: second = {'raw': resp.text}
print('➡️ Second redemption response:', second)
print('Done.')
