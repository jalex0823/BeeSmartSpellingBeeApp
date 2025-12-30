#!/usr/bin/env python3
"""Local StoreKit readiness verification.

Contract
- Assumes BeeSmart Flask app is already running locally.
- Verifies 4 things:
  1) /health returns 200 JSON
  2) /subscription renders $3.99 (and not $3.33)
  3) /api/avatars?dev_full=1 returns full catalog + includes product_id fields
  4) Product IDs include the expected .v2 SKUs for Fairy Bee and Gamer Bee

Notes
- To enable full catalog as a guest for testing, set:
    ALLOW_DEV_FULL_AVATARS=1
  and call /api/avatars?dev_full=1
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request


def _get(url: str, timeout_s: float = 8.0) -> tuple[int, str, dict[str, str]]:
    req = urllib.request.Request(url, headers={"Accept": "application/json,text/html"})
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            headers = {k.lower(): v for k, v in resp.headers.items()}
            return resp.status, body, headers
    except Exception as e:
        raise RuntimeError(f"GET failed: {url}: {e}")


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> int:
    base = os.getenv("BEESMART_BASE_URL", "http://127.0.0.1:5051").rstrip("/")

    # 1) health
    status, body, _ = _get(f"{base}/health")
    _assert(status == 200, f"/health status {status}")
    try:
        health = json.loads(body)
    except Exception:
        raise AssertionError(f"/health did not return JSON. Body: {body[:200]}")
    _assert("version" in health, f"/health missing version: {health}")

    # 2) subscription pricing
    status, html, _ = _get(f"{base}/subscription")
    _assert(status == 200, f"/subscription status {status}")
    _assert("3.33" not in html, "Found 3.33 on /subscription (should be 3.99 only)")
    _assert(re.search(r"\$\s*3\.99|3\.99", html), "Did not find 3.99 on /subscription")

    # 3) avatars full catalog for StoreKit
    status, body, _ = _get(f"{base}/api/avatars?dev_full=1")
    _assert(status == 200, f"/api/avatars?dev_full=1 status {status}")
    data = json.loads(body)
    avatars = data.get("avatars") if isinstance(data, dict) else None
    _assert(isinstance(avatars, list), "avatars payload missing list")
    _assert(len(avatars) >= 30, f"Expected full catalog (~39). Got {len(avatars)}")

    product_ids: list[str] = []
    for a in avatars:
        if not isinstance(a, dict):
            continue
        pid = a.get("product_id")
        if pid:
            product_ids.append(str(pid))

    _assert(len(product_ids) >= 10, f"Expected many product_ids for paid avatars. Got {len(product_ids)}")
    _assert(any(pid.endswith(".v2") for pid in product_ids), "No .v2 product IDs found in avatar payload")

    # 4) specific required SKUs
    _assert(
        "beesmart.avatar.fairy_bee.v2" in product_ids,
        "Missing beesmart.avatar.fairy_bee.v2 in /api/avatars payload",
    )
    _assert(
        "beesmart.avatar.gamer_bee.v2" in product_ids,
        "Missing beesmart.avatar.gamer_bee.v2 in /api/avatars payload",
    )

    print("PASS: StoreKit local readiness checks succeeded")
    print(f"  base: {base}")
    print(f"  avatars: {len(avatars)}")
    print(f"  product_ids: {len(product_ids)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"FAIL: {e}")
        raise SystemExit(1)
