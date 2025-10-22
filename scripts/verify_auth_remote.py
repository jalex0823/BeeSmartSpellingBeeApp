#!/usr/bin/env python3
"""
Verify BeeSmart auth endpoints on a live deployment.
Steps:
 - GET /health
 - GET /auth/register and /auth/login (200)
 - POST /auth/register with a unique username
 - Confirm we can access /auth/dashboard (auto-login after registration)

Usage:
  Set BASE_URL env var to your deployment URL (no trailing slash).
  Example (PowerShell):
    $env:BASE_URL = 'https://beesmartspellingbee.up.railway.app'
    python scripts/verify_auth_remote.py
"""

import os
import time
import json
import sys
import requests


def main() -> int:
    base = os.environ.get("BASE_URL", "http://127.0.0.1:5000").rstrip("/")
    print(f"\n🐝 Verifying BeeSmart at: {base}")
    sess = requests.Session()

    # Health check
    try:
        r = sess.get(f"{base}/health", timeout=10)
        print(f"/health -> {r.status_code}")
        if r.ok:
            try:
                print("  ", r.json())
            except Exception:
                pass
        else:
            print("❌ Health check failed")
            return 2
    except Exception as e:
        print(f"❌ Health request error: {e}")
        return 2

    # Pages
    for ep in ("/auth/register", "/auth/login"):
        try:
            r = sess.get(f"{base}{ep}", timeout=10)
            print(f"{ep} -> {r.status_code}")
            if r.status_code != 200:
                print(f"❌ Unexpected status for {ep}")
                return 2
        except Exception as e:
            print(f"❌ Request error for {ep}: {e}")
            return 2

    # Register a unique user
    uname = f"railway_check_{int(time.time())}"
    payload = {
        "username": uname,
        "display_name": "Railway Check",
        "password": "test123",
        "email": f"{uname}@example.com",
        "grade_level": "5"
    }
    try:
        r = sess.post(f"{base}/auth/register", json=payload, timeout=20)
        print(f"POST /auth/register -> {r.status_code}")
        if not r.ok:
            print("❌ Registration failed:", r.text[:300])
            return 3
        data = r.json()
        print("  response:", json.dumps({k: data.get(k) for k in ("success", "message", "redirect")}, indent=2))
        if not data.get("success"):
            print("❌ Registration reported unsuccessful")
            return 3
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return 3

    # Verify dashboard access (session cookie should be set after auto-login)
    try:
        r = sess.get(f"{base}/auth/dashboard", timeout=15)
        print(f"/auth/dashboard -> {r.status_code}")
        if r.status_code != 200:
            print("❌ Dashboard not accessible after registration")
            return 4
    except Exception as e:
        print(f"❌ Dashboard request error: {e}")
        return 4

    print("\n✅ Live auth verification PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
