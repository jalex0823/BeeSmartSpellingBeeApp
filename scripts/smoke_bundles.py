#!/usr/bin/env python3
"""
Quick smoke test for bundle-key redemption.

- Starts with an existing server running (e.g., PORT=5050)
- Logs in using demo teacher account
- Redeems a dev key from avatar_bundles.py

Usage:
  BASE_URL=http://localhost:5050 KEY=BEE-CLASS-STARTER-1 ./scripts/smoke_bundles.py
"""
import os
import sys
import json

try:
    import requests
except Exception:
    print("ERROR: This script requires the 'requests' package. Install with: pip install requests")
    sys.exit(2)

BASE_URL = os.getenv("BASE_URL", "http://localhost:5050").rstrip("/")
USERNAME = os.getenv("USERNAME", "teacher_demo")
PASSWORD = os.getenv("PASSWORD", "REVIEW-ONLY")
KEY = os.getenv("KEY", "BEE-CLASS-STARTER-1")

s = requests.Session()

print(f"➡️  Target: {BASE_URL}")

# 1) Login
login_url = f"{BASE_URL}/auth/login"
print("🔐 Logging in as demo teacher...")
resp = s.post(login_url, json={"username": USERNAME, "password": PASSWORD})
try:
    data = resp.json()
except Exception:
    data = {"raw": resp.text}

if not resp.ok or not data or not data.get("success"):
    print(f"❌ Login failed: status={resp.status_code}, body={data}")
    sys.exit(1)
print("✅ Logged in")

# 2) Redeem bundle key
redeem_url = f"{BASE_URL}/api/bundles/redeem"
print(f"🎁 Redeeming key: {KEY}")
resp = s.post(redeem_url, json={"key": KEY})
try:
    body = resp.json()
except Exception:
    body = {"raw": resp.text}

if resp.ok and body.get("success"):
    ent = body.get("entitlements", {})
    print("✅ Redemption success")
    print(json.dumps({
        "bundle_id": body.get("bundle_id"),
        "unlocked_count": body.get("unlocked_count"),
        "purchased_bundles": ent.get("purchased_bundles"),
        "purchased_avatars": ent.get("purchased_avatars"),
    }, indent=2))
    sys.exit(0)
else:
    print(f"❌ Redemption failed: status={resp.status_code}, body={body}")
    sys.exit(1)
