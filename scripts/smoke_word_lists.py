"""Smoke test for the /word-lists page and saved-lists API gating.

This is intentionally lightweight (no Playwright/Selenium) so it can run in CI
or locally without a browser.

Contract:
- GET /word-lists should return 200 and include expected title text.
- GET /api/saved-lists while logged out should return 401 with auth_required.

Usage:
  python3 scripts/smoke_word_lists.py --base-url http://localhost:5051

Exit codes:
  0 OK
  2 HTTP/connection failure
  3 Unexpected response/content
"""

from __future__ import annotations

import argparse
import sys

import requests


def fail(msg: str, code: int = 3) -> "NoReturn":
    print(f"SMOKE FAIL: {msg}")
    raise SystemExit(code)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:5000")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    s = requests.Session()

    # Fast preflight so a down server yields a clear, actionable message.
    try:
        health = s.get(f"{base_url}/health", timeout=2)
        print(f"Preflight: GET /health -> {health.status_code}")
    except Exception as e:
        print(
            "SMOKE FAIL: server not reachable. Make sure the app is running, then re-run. "
            f"Details: {e}"
        )
        return 2

    try:
        r = s.get(f"{base_url}/word-lists", timeout=5)
    except Exception as e:
        print(f"SMOKE FAIL: cannot reach /word-lists: {e}")
        return 2

    if r.status_code != 200:
        fail(f"/word-lists status {r.status_code}")

    body = r.text
    if "My Word Lists" not in body and "Word Lists" not in body:
        fail("/word-lists missing expected title text")

    try:
        r2 = s.get(f"{base_url}/api/saved-lists", timeout=5)
    except Exception as e:
        print(f"SMOKE FAIL: cannot reach /api/saved-lists: {e}")
        return 2

    # Logged-out contract: should be unauthorized.
    if r2.status_code != 401:
        fail(f"/api/saved-lists expected 401 while logged out, got {r2.status_code}")

    try:
        j = r2.json()
    except Exception:
        fail("/api/saved-lists did not return JSON")

    if not (j.get("auth_required") or j.get("error") == "auth_required"):
        fail(f"/api/saved-lists JSON missing auth_required flags: keys={sorted(j.keys())}")

    print("SMOKE OK: /word-lists reachable; /api/saved-lists gated with 401 when logged out")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
