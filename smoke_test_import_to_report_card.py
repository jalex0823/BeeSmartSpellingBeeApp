#!/usr/bin/env python3
"""Smoke test: import/upload -> quiz -> report card summary.

This exercises the same endpoints the UI uses:
- POST /api/upload (JSON)
- POST /api/quiz/start
- POST /api/next
- POST /api/answer
- POST /api/next (final) to fetch the report-card "summary" payload

Run with the Flask dev server already running locally.
"""

from __future__ import annotations

import sys
import time
from typing import Any, Dict, List

import requests
import io

# Ensure Windows console can handle Unicode (emojis, symbols) without crashing.
if sys.platform == "win32":
    try:
        if getattr(sys.stdout, "buffer", None) is not None and not getattr(sys.stdout, "closed", False):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        if getattr(sys.stderr, "buffer", None) is not None and not getattr(sys.stderr, "closed", False):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        # Best-effort only; never fail the smoke test due to console encoding tweaks.
        pass

BASE_URL = "http://127.0.0.1:5000"


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> int:
    s = requests.Session()

    words: List[Dict[str, str]] = [
        {"word": "rainbow", "sentence": "", "hint": ""},
        {"word": "butterfly", "sentence": "", "hint": ""},
        {"word": "adventure", "sentence": "", "hint": ""},
    ]

    print("1) Uploading words via /api/upload ...")
    r = s.post(
        f"{BASE_URL}/api/upload",
        json={"words": words},
        timeout=15,
    )
    _assert(r.status_code == 200, f"upload failed: {r.status_code} {r.text[:200]}")
    data = r.json()
    _assert(bool(data.get("ok")), f"upload not ok: {data}")
    _assert(int(data.get("count", 0)) == len(words), f"upload count mismatch: {data}")
    print(f"   ✅ uploaded {data.get('count')} words")

    print("2) Starting quiz via /api/quiz/start (start_new) ...")
    r = s.post(
        f"{BASE_URL}/api/quiz/start",
        json={"action": "start_new"},
        timeout=15,
    )
    _assert(r.status_code == 200, f"quiz/start failed: {r.status_code} {r.text[:200]}")
    start = r.json()
    _assert(start.get("status") == "success", f"quiz/start error: {start}")

    print("3) Running through quiz: /api/next -> /api/answer ...")
    seen = []

    # Answer first 2 correct, last 1 intentionally wrong.
    for i in range(len(words)):
        nxt = s.post(f"{BASE_URL}/api/next", timeout=15)
        _assert(nxt.status_code == 200, f"next failed: {nxt.status_code} {nxt.text[:200]}")
        payload = nxt.json()
        _assert(payload.get("done") is False, f"unexpected done early: {payload}")
        _assert("word" in payload, f"/api/next missing word field: {payload.keys()}")

        word = payload["word"]
        seen.append(word)

        user_input = word if i < len(words) - 1 else "definitelywrong"
        ans = s.post(
            f"{BASE_URL}/api/answer",
            json={"user_input": user_input, "method": "smoke", "elapsed_ms": 1200},
            timeout=15,
        )
        _assert(ans.status_code == 200, f"answer failed: {ans.status_code} {ans.text[:200]}")
        a = ans.json()
        _assert("correct" in a, f"/api/answer missing 'correct': {a}")
        print(f"   Q{i+1}: word='{word}' input='{user_input}' -> correct={a.get('correct')}")

        # Small pause to mimic real flow (and to keep logs readable)
        time.sleep(0.05)

    print("4) Fetching report-card summary via final /api/next ...")
    final = s.post(f"{BASE_URL}/api/next", timeout=15)
    _assert(final.status_code == 200, f"final next failed: {final.status_code} {final.text[:200]}")
    final_payload: Dict[str, Any] = final.json()

    _assert(final_payload.get("done") is True, f"expected done=True: {final_payload}")
    _assert("summary" in final_payload, f"missing summary: {final_payload.keys()}")

    summary = final_payload["summary"]
    required_keys = [
        "total",
        "correct",
        "incorrect",
        "history",
        "session_points",
        "incorrect_words",
    ]
    for k in required_keys:
        _assert(k in summary, f"summary missing '{k}'")

    total = summary.get("total")
    correct = summary.get("correct")
    incorrect = summary.get("incorrect")

    print("   ✅ report-card summary received")
    print(f"      total={total} correct={correct} incorrect={incorrect}")
    print(f"      history_len={len(summary.get('history') or [])}")
    print(f"      incorrect_words={len(summary.get('incorrect_words') or [])}")

    _assert(int(total) == len(words), f"summary.total mismatch: {total} vs {len(words)}")
    _assert(int(correct) + int(incorrect) == len(words), "correct+incorrect must equal total")

    print("\n✅ SMOKE PASS: import → quiz → report card")
    print(f"   Words encountered (server order): {seen}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"\n❌ SMOKE FAIL: {e}")
        return_code = 1
        raise SystemExit(return_code)
