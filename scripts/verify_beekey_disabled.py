"""Regression check: BeeKey/key-redemption must be disabled by default.

This repo has teacher/desktop-only key redemption endpoints. For App Store
compliance we want those endpoints *hidden* unless explicitly enabled.

Expected default behavior (ALLOW_KEY_REDEMPTION != '1'):
- /api/bundles/redeem returns 404
- /api/beekey/redeem-for-linked returns 404

Usage:
  python3 scripts/verify_beekey_disabled.py --base-url http://127.0.0.1:5051

Exits non-zero on failure.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def _get_status(url: str) -> int:
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return int(resp.status)
    except urllib.error.HTTPError as e:
        return int(e.code)


def _post_json(url: str, payload: dict) -> int:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return int(resp.status)
    except urllib.error.HTTPError as e:
        return int(e.code)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://127.0.0.1:5000")
    args = ap.parse_args()

    base = args.base_url.rstrip("/")
    strict_404 = os.environ.get('APP_STORE_BUILD', '0').strip() == '1'

    # Quick reachability check so failures are actionable.
    health = _get_status(base + "/health")
    if health < 200 or health >= 500:
        print(f"FAIL: server not reachable/healthy at {base} (GET /health -> {health})")
        return 2

    cases = [
        ("/api/bundles/redeem", {"key": "TEST"}),
        ("/api/beekey/redeem-for-linked", {"beekey": "TEST"}),
    ]

    failures = 0
    for path, payload in cases:
        status = _post_json(base + path, payload)
        # If APP_STORE_BUILD=1, we require a hard 404 (endpoint hidden).
        if strict_404:
            allowed = (404,)
        else:
            # Otherwise, either 404 (hidden) or 403 (explicitly forbidden) are acceptable
            # signals that BeeKey/key redemption is disabled for this build.
            allowed = (404, 403)

        if status not in allowed:
            failures += 1
            exp = "404" if strict_404 else "404/403"
            print(f"FAIL: {path} expected {exp} (disabled), got {status}")
        else:
            print(f"PASS: {path} returned {status} (disabled)")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
