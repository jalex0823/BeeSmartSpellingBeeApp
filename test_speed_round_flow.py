"""Minimal validation script for Speed Round multi-word progression and word list switching.
Run while the Flask app is running on localhost:5000.

Usage (PowerShell):
    python test_speed_round_flow.py

It will:
1. (Optional) Load a saved list if an ID/UUID is provided via env SPEED_LIST_ID.
2. Start a speed round (auto difficulty grade_3_4, 8 words).
3. Loop: fetch next word, submit a fake answer (first letter correct else random), until complete.
4. Print progression, ensuring index increments.
5. Start a second speed round using 'uploaded' source (if wordbank present) to confirm list switching.
"""
from __future__ import annotations
import os, random, time, json, requests

BASE_URL = os.environ.get("BEE_BASE", "http://127.0.0.1:5051")
SESSION = requests.Session()
SESSION.headers.update({"Content-Type": "application/json"})


def maybe_load_saved_list():
    list_id = os.environ.get("SPEED_LIST_ID")
    if not list_id:
        print("[LOAD] Skipping saved list load (no SPEED_LIST_ID env set)")
        return
    payload = {"id": list_id}
    r = SESSION.post(f"{BASE_URL}/api/saved-lists/load", json=payload)
    print(f"[LOAD] /api/saved-lists/load status={r.status_code} body={r.text[:200]}")


def start_round(source="auto", word_count=8):
    payload = {
        "time_per_word": 15,
        "difficulty": "grade_3_4",
        "word_count": word_count,
        "word_source": source
    }
    r = SESSION.post(f"{BASE_URL}/api/speed-round/start", json=payload, allow_redirects=True)
    print(f"[START] source={source} status={r.status_code} url={r.url[:70]}...")
    if r.status_code >= 400:
        r.raise_for_status()
    # Success: API returns 302 redirect to /speed-round/quiz; session follows and gets 200
    if "/speed-round/quiz" in r.url:
        return
    try:
        data = r.json()
        if data.get("error") in ("auth_required", "premium_required"):
            raise RuntimeError(f"Speed round requires auth+premium: {data.get('error')}")
    except ValueError:
        pass
    raise RuntimeError(f"Expected redirect to quiz, got status={r.status_code} url={r.url}")


def get_next():
    r = SESSION.get(f"{BASE_URL}/api/speed-round/next")
    if r.status_code != 200:
        print(f"[NEXT] Non-200: {r.status_code} {r.text[:200]}")
    return r


def answer_word(word: str, streak: int):
    # naive pseudo-answer: if streak < 2 return first char only (likely wrong), else full word (likely correct)
    guess = word if streak >= 2 else word[:1]
    payload = {
        "user_input": guess,
        "elapsed_ms": random.randint(500, 4000),
        "skipped": False
    }
    r = SESSION.post(f"{BASE_URL}/api/speed-round/answer", json=payload)
    if r.status_code != 200:
        print(f"[ANSWER] Non-200: {r.status_code} {r.text[:200]}")
    return r


def run_flow(source="auto"):
    start_round(source=source)
    progression = []
    while True:
        nr = get_next()
        if nr.status_code != 200:
            print("[FLOW] Aborting due to next error")
            break
        data = nr.json()
        if data.get("complete"):
            print("[FLOW] Round complete signaled by /next")
            break
        word = data.get("word")
        idx = data.get("current_index")
        remaining = data.get("remaining")
        print(f"[NEXT] idx={idx} remaining={remaining} word={word}")
        ar = answer_word(word, streak=data.get("current_streak", 0))
        ad = ar.json()
        print(f"    [ANSWER] correct={ad.get('is_correct')} streak={ad.get('current_streak')} pts={ad.get('points_earned')} next_index={ad.get('next_index')} rem={ad.get('remaining')} complete={ad.get('complete')}")
        progression.append({"idx": idx, "complete": ad.get("complete"), "next": ad.get("next_index")})
        if ad.get("complete"):
            print("[FLOW] Completion detected after answer")
            break
    # Summarize index increments
    indices = [p["idx"] for p in progression]
    print(f"[SUMMARY] Indices visited: {indices}")
    if indices and indices != sorted(indices):
        print("[WARN] Indices not monotonic ascending!")
    else:
        print("[OK] Indices progressed ascending.")


def main():
    maybe_load_saved_list()
    print("\n=== First Speed Round (auto) ===")
    run_flow(source="auto")
    # Try uploaded source if available
    print("\n=== Second Speed Round (uploaded) ===")
    run_flow(source="uploaded")

if __name__ == "__main__":
    main()
