#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smoke Test for Speed Round: setup -> start -> quiz flow

Run while the Flask app is running. Uses BEE_BASE (default http://localhost:5051).

Usage:
    python smoke_test_speed_round.py

Requirements: Logged-in premium user session (set BEE_COOKIE or run after manual login).
Without auth: setup/quiz pages load; POST /api/speed-round/start returns 401/403.
"""
from __future__ import annotations

import os
import sys
import requests

BASE_URL = os.environ.get("BEE_BASE", "http://localhost:5051")
SESSION = requests.Session()
SESSION.headers.update({"Content-Type": "application/json"})


def test_setup_page():
    """GET /speed-round/setup - should return 200"""
    r = SESSION.get(f"{BASE_URL}/speed-round/setup", timeout=15)
    ok = r.status_code == 200 and "Speed Round" in r.text
    print(f"  [SETUP] GET /speed-round/setup -> {r.status_code} {'OK' if ok else 'FAIL'}")
    return ok


def test_start_api():
    """POST /api/speed-round/start - returns 302 redirect to quiz (success) or 401/403 (auth required)"""
    payload = {
        "time_per_word": 15,
        "difficulty": "grade_3_4",
        "word_count": 5,
        "word_source": "auto",
    }
    r = SESSION.post(f"{BASE_URL}/api/speed-round/start", json=payload, allow_redirects=True)
    # Success: 302 redirect to /speed-round/quiz, then 200 from quiz page
    if r.status_code == 200 and "/speed-round/quiz" in r.url:
        print(f"  [START] POST /api/speed-round/start -> 302 -> quiz OK (url={r.url[:60]}...)")
        return True
    if r.status_code in (401, 403):
        try:
            data = r.json()
            err = data.get("error", "?")
            print(f"  [START] POST /api/speed-round/start -> {r.status_code} ({err}) - auth/premium required")
        except Exception:
            print(f"  [START] POST /api/speed-round/start -> {r.status_code} - auth/premium required")
        return False  # Not a bug, just needs login
    print(f"  [START] POST /api/speed-round/start -> {r.status_code} url={r.url} (unexpected)")
    return False


def test_quiz_direct():
    """GET /speed-round/quiz without session - should redirect to setup or subscription"""
    r = SESSION.get(f"{BASE_URL}/speed-round/quiz", allow_redirects=False, timeout=15)
    # Without session: redirect to setup or subscription
    ok = r.status_code in (302, 307) or (r.status_code == 200 and "Speed Round" in r.text)
    dest = r.headers.get("Location", "?") if r.status_code in (302, 307) else r.url
    print(f"  [QUIZ]  GET /speed-round/quiz -> {r.status_code} -> {dest[:50] if dest else 'N/A'}")
    return ok


def main():
    print("=" * 60)
    print("Speed Round Smoke Test")
    print(f"Base URL: {BASE_URL}")
    print("=" * 60)

    try:
        health = SESSION.get(f"{BASE_URL}/health", timeout=5)
        if health.status_code != 200:
            print(f"FAIL: Health check returned {health.status_code}")
            return 1
    except Exception as e:
        print(f"FAIL: Cannot reach {BASE_URL}/health - {e}")
        print("  Make sure the app is running (e.g. python AjaSpellBApp.py)")
        return 1

    print("Health OK\n")

    results = []
    results.append(("Setup page", test_setup_page()))
    results.append(("Start API (setup->quiz flow)", test_start_api()))
    results.append(("Quiz direct (redirect behavior)", test_quiz_direct()))

    print()
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    for name, ok in results:
        status = "PASS" if ok else "FAIL"
        print(f"  {status}: {name}")
    print()
    print(f"Results: {passed}/{total} passed")

    if passed == total:
        print("Speed round smoke test PASSED")
        return 0
    if not results[1][1] and passed == 2:
        print("Note: Start API failed - log in as premium user to test full flow.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
