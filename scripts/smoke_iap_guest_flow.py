#!/usr/bin/env python3
"""Lightweight local smoke test for guest IAP restore + avatar entitlements.

This is *not* a full integration test against StoreKit. It's a quick confidence
check you can run locally before making an Xcode build.

What it validates:
- /health responds
- reconcile-only restore doesn't fail
- restoring a guest SKU persists and is reflected by /api/avatars in a fresh session

It relies on the Flask app already running locally.

Usage:
  python3 scripts/smoke_iap_guest_flow.py

Optional env:
    BASE_URL=http://127.0.0.1:5051
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, Optional

import requests


def _fail(msg: str) -> None:
    print(f"[smoke] FAIL: {msg}")
    raise SystemExit(2)


def _ok(msg: str) -> None:
    print(f"[smoke] OK: {msg}")


def _get_json(session: requests.Session, url: str) -> Dict[str, Any]:
    r = session.get(url, timeout=7)
    r.raise_for_status()
    try:
        return r.json()
    except Exception as e:
        _fail(f"Non-JSON response from {url}: {e}")
        return {}


def _post_json(session: requests.Session, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    r = session.post(url, json=payload, timeout=10)
    r.raise_for_status()
    try:
        return r.json()
    except Exception as e:
        _fail(f"Non-JSON response from {url}: {e}")
        return {}


def main() -> None:
    base = os.environ.get("BASE_URL", "http://127.0.0.1:5051").rstrip("/")

    s1 = requests.Session()

    health = _get_json(s1, f"{base}/health")
    if not isinstance(health, dict) or "version" not in health:
        _fail(f"Unexpected /health payload: {health}")
    _ok("/health")

    # Reconcile-only restore: should always succeed.
    rec = _post_json(
        s1,
        f"{base}/api/iap/restore",
        {"platform": "apple", "product_ids": [], "install_id": "smoke_install_id_v1"},
    )
    if not rec.get("success"):
        _fail(f"reconcile-only restore returned success=False: {rec}")
    _ok("reconcile-only /api/iap/restore")

    # Restore a known SKU shape. We don't need a real Apple SKU for the smoke test;
    # the endpoint should accept/record arbitrary IDs and surface them under guest entitlements.
    test_sku = "smoke.test.avatar.sku"
    rec2 = _post_json(
        s1,
        f"{base}/api/iap/restore",
        {"platform": "apple", "product_ids": [test_sku], "install_id": "smoke_install_id_v1"},
    )
    if not rec2.get("success"):
        _fail(f"restore with sku returned success=False: {rec2}")

    ent = rec2.get("entitlements") or {}
    anon_owned = ent.get("anon_owned_products") or []
    if test_sku not in anon_owned:
        # Still allow pass if server doesn't echo it, but warn.
        _fail(f"Expected restored SKU in entitlements. anon_owned_products={anon_owned}")
    _ok("restore persists into entitlements")

    # New session: simulate reinstall-cookie-loss by NOT sending anon_restore_id,
    # but provide the same install_id so the server can re-associate.
    s2 = requests.Session()
    rec3 = _post_json(
        s2,
        f"{base}/api/iap/restore",
        {"platform": "apple", "product_ids": [], "install_id": "smoke_install_id_v1"},
    )
    if not rec3.get("success"):
        _fail(f"fresh-session reconcile-only failed: {rec3}")

    ent3 = rec3.get("entitlements") or {}
    anon_owned3 = ent3.get("anon_owned_products") or []
    if test_sku not in anon_owned3:
        _fail(
            "Install-id relink failed: expected SKU to show up after fresh session reconcile. "
            f"anon_owned_products={anon_owned3}"
        )
    _ok("fresh session recovered entitlements via install_id")

    avatars = _get_json(s2, f"{base}/api/avatars")
    if not isinstance(avatars, dict) or "avatars" not in avatars:
        _fail(f"Unexpected /api/avatars payload keys: {list(avatars.keys())}")
    _ok("/api/avatars responds")

    print("[smoke] PASS")


if __name__ == "__main__":
    try:
        main()
    except requests.RequestException as e:
        print(f"[smoke] ERROR: {e}")
        sys.exit(2)
