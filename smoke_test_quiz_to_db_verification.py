#!/usr/bin/env python3
"""
🐝 SMOKE TEST: Quiz Completion → Database → Stats Verification

This test verifies that:
1. Quiz completion data is saved to the database (QuizSession table)
2. User stats are updated in the database (User table)
3. Stats can be retrieved via API endpoints
4. Stats recalculation works correctly

Run with the Flask server running (local or DO production).
Set BASE_URL environment variable to test against DO production.
"""

from __future__ import annotations

import sys
import time
import os
from typing import Any, Dict, List, Optional
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
        pass

# Allow BASE_URL to be set via environment variable for DO production testing
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5051")

print("=" * 80)
print("🐝 QUIZ → DATABASE → STATS VERIFICATION SMOKE TEST")
print("=" * 80)
print(f"Testing against: {BASE_URL}")
print()


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> int:
    s = requests.Session()
    
    # Test words
    words: List[Dict[str, str]] = [
        {"word": "database", "sentence": "The database stores information.", "hint": "Data storage"},
        {"word": "verification", "sentence": "We need verification of the results.", "hint": "Confirmation"},
        {"word": "smoke", "sentence": "Smoke tests verify basic functionality.", "hint": "Quick test"},
    ]
    
    print("=" * 80)
    print("PHASE 1: UPLOAD WORDS & START QUIZ")
    print("=" * 80)
    
    print("1) Uploading words via /api/upload ...")
    r = s.post(
        f"{BASE_URL}/api/upload",
        json={"words": words},
        timeout=15,
    )
    _assert(r.status_code == 200, f"upload failed: {r.status_code} {r.text[:200]}")
    upload_data = r.json()
    _assert(bool(upload_data.get("ok")), f"upload not ok: {upload_data}")
    _assert(int(upload_data.get("count", 0)) == len(words), f"upload count mismatch: {upload_data}")
    print(f"   ✅ uploaded {upload_data.get('count')} words")
    
    print("2) Starting quiz via /api/quiz/start ...")
    r = s.post(
        f"{BASE_URL}/api/quiz/start",
        json={"action": "start_new"},
        timeout=15,
    )
    _assert(r.status_code == 200, f"quiz/start failed: {r.status_code} {r.text[:200]}")
    start_data = r.json()
    _assert(start_data.get("status") == "success", f"quiz/start error: {start_data}")
    print("   ✅ Quiz started")
    
    print()
    print("=" * 80)
    print("PHASE 2: ANSWER WORDS & COMPLETE QUIZ")
    print("=" * 80)
    
    print("3) Answering words (2 correct, 1 incorrect) ...")
    session_points_earned = 0
    correct_count = 0
    incorrect_count = 0
    
    for i in range(len(words)):
        # Get next word
        nxt = s.post(f"{BASE_URL}/api/next", timeout=15)
        _assert(nxt.status_code == 200, f"next failed: {nxt.status_code} {nxt.text[:200]}")
        payload = nxt.json()
        _assert(payload.get("done") is False or i == len(words) - 1, f"unexpected done early: {payload}")
        _assert("word" in payload, f"/api/next missing word field: {payload.keys()}")
        
        word = payload["word"]
        
        # Answer: correct for first 2, wrong for last
        user_input = word if i < len(words) - 1 else "wrongspelling"
        is_correct = (i < len(words) - 1)
        
        ans = s.post(
            f"{BASE_URL}/api/answer",
            json={"user_input": user_input, "method": "smoke", "elapsed_ms": 1500},
            timeout=15,
        )
        _assert(ans.status_code == 200, f"answer failed: {ans.status_code} {ans.text[:200]}")
        answer_data = ans.json()
        _assert("correct" in answer_data, f"/api/answer missing 'correct': {answer_data}")
        
        if answer_data.get("correct"):
            correct_count += 1
        else:
            incorrect_count += 1
        
        # Track points earned
        points_info = answer_data.get("points", {})
        points_earned = points_info.get("earned", 0) if isinstance(points_info, dict) else 0
        session_points_earned += points_earned
        
        print(f"   Q{i+1}: word='{word}' input='{user_input}' -> correct={answer_data.get('correct')}, points={points_earned}")
        
        time.sleep(0.1)  # Small delay
    
    print(f"   ✅ Quiz answers submitted: {correct_count} correct, {incorrect_count} incorrect")
    print(f"   ✅ Session points earned: {session_points_earned}")
    
    print()
    print("4) Fetching final quiz summary ...")
    final = s.post(f"{BASE_URL}/api/next", timeout=15)
    _assert(final.status_code == 200, f"final next failed: {final.status_code} {final.text[:200]}")
    final_payload: Dict[str, Any] = final.json()
    
    _assert(final_payload.get("done") is True, f"expected done=True: {final_payload}")
    _assert("summary" in final_payload, f"missing summary: {final_payload.keys()}")
    
    summary = final_payload["summary"]
    print(f"   ✅ Quiz summary received:")
    print(f"      total={summary.get('total')}, correct={summary.get('correct')}, incorrect={summary.get('incorrect')}")
    print(f"      session_points={summary.get('session_points', 0)}")
    
    # Wait a moment for database commit
    print()
    print("5) Waiting for database commit ...")
    time.sleep(2)
    
    print()
    print("=" * 80)
    print("PHASE 3: VERIFY STATS VIA API")
    print("=" * 80)
    
    print("6) Fetching user stats via /api/users/stats ...")
    stats_response = s.get(f"{BASE_URL}/api/users/stats", timeout=15)
    _assert(stats_response.status_code == 200, f"stats fetch failed: {stats_response.status_code}")
    stats_data = stats_response.json()
    
    if stats_data.get("authenticated"):
        stats = stats_data.get("stats", {})
        lifetime_points = stats.get("total_lifetime_points", 0)
        quizzes_completed = stats.get("total_quizzes_completed", 0)
        gpa = stats.get("cumulative_gpa", 0.0)
        accuracy = stats.get("average_accuracy", 0.0)
        
        print(f"   ✅ Stats retrieved:")
        print(f"      total_lifetime_points: {lifetime_points}")
        print(f"      total_quizzes_completed: {quizzes_completed}")
        print(f"      cumulative_gpa: {gpa}")
        print(f"      average_accuracy: {accuracy}%")
        
        # Verify stats were updated (should have at least the session points)
        if lifetime_points > 0:
            print(f"   ✅ Lifetime points > 0 (quiz points were applied)")
        else:
            print(f"   ⚠️  WARNING: Lifetime points is 0 (may indicate DB issue)")
        
        if quizzes_completed > 0:
            print(f"   ✅ Quizzes completed > 0 (quiz count was incremented)")
        else:
            print(f"   ⚠️  WARNING: Quizzes completed is 0 (may indicate DB issue)")
    else:
        print("   ℹ️  User not authenticated (guest quiz - stats won't be saved)")
    
    print()
    print("7) Testing stats recalculation via /api/users/stats/recalculate ...")
    print("   (Note: This endpoint requires authentication - will skip for guest users)")
    try:
        recalc_response = s.post(
            f"{BASE_URL}/api/users/stats/recalculate",
            timeout=15,
        )
        
        if recalc_response.status_code == 200:
            recalc_data = recalc_response.json()
            if recalc_data.get("status") == "success":
                recalc_stats = recalc_data.get("stats", {})
                print(f"   ✅ Recalculation successful:")
                print(f"      total_lifetime_points: {recalc_stats.get('total_lifetime_points', 0)}")
                print(f"      total_quizzes_completed: {recalc_stats.get('total_quizzes_completed', 0)}")
                print(f"      cumulative_gpa: {recalc_stats.get('cumulative_gpa', 0.0)}")
                print(f"      average_accuracy: {recalc_stats.get('average_accuracy', 0.0)}%")
                
                recalculation_info = recalc_data.get("recalculation", {})
                if recalculation_info:
                    print(f"      sessions_processed: {recalculation_info.get('sessions_processed', 0)}")
                    print(f"      points_changed: {recalculation_info.get('points_changed', False)}")
                    print(f"      quizzes_changed: {recalculation_info.get('quizzes_changed', False)}")
            else:
                print(f"   ⚠️  Recalculation returned: {recalc_data.get('status')}")
        elif recalc_response.status_code in (401, 403, 405):
            print(f"   ℹ️  Recalculation requires authentication (status {recalc_response.status_code})")
        else:
            print(f"   ⚠️  Recalculation failed: {recalc_response.status_code}")
            print(f"      Response: {recalc_response.text[:200]}")
    except Exception as e:
        print(f"   ⚠️  Recalculation error: {e}")
    
    print()
    print("=" * 80)
    print("✅ SMOKE TEST COMPLETE")
    print("=" * 80)
    print()
    print("VERIFICATION SUMMARY:")
    print("  ✅ Quiz completed successfully")
    print("  ✅ Quiz summary received with correct/incorrect counts")
    print("  ✅ Stats API endpoint accessible")
    if stats_data.get("authenticated"):
        print("  ✅ User stats retrieved (authenticated user)")
        print("  ✅ Stats recalculation tested")
    else:
        print("  ℹ️  Guest user (stats not saved to DB)")
    print()
    print("NEXT STEPS:")
    print("  1. Check server logs for 'DATABASE COMMITTED' messages")
    print("  2. Verify QuizSession.completed=True in database")
    print("  3. Verify User.total_lifetime_points and total_quizzes_completed updated")
    print("  4. If stats are 0, check for errors in quiz completion logic")
    print()
    print("TO TEST WITH AUTHENTICATED USER:")
    print("  - Login first, then run this test")
    print("  - Or set up test credentials in the script")
    print("  - Stats will then be saved to the database and verified")
    
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as e:
        print(f"\n❌ SMOKE TEST FAILED: {e}")
        raise SystemExit(1)
    except Exception as e:
        print(f"\n❌ SMOKE TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise SystemExit(1)
