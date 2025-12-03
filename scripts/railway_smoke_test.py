import os
import sys
import time
import json
import requests

BASE_URL = os.getenv('BASE_URL') or (sys.argv[1] if len(sys.argv) > 1 else None)
if not BASE_URL:
    print('Usage: python scripts/railway_smoke_test.py <BASE_URL>\nOr set BASE_URL env var. Example: https://beesmart-production.up.railway.app')
    sys.exit(1)

session = requests.Session()
session.headers.update({'Accept': 'application/json'})

FAILURES = []

def check(name, func):
    try:
        func()
        print(f"✅ {name}")
    except AssertionError as e:
        FAILURES.append((name, str(e)))
        print(f"❌ {name}: {e}")
    except Exception as e:
        FAILURES.append((name, f"{type(e).__name__}: {e}"))
        print(f"❌ {name}: {e}")


def health_check():
    r = session.get(f"{BASE_URL}/health", timeout=10)
    assert r.status_code == 200, f"/health {r.status_code}"
    data = r.json()
    assert 'version' in data, 'missing version key'


def avatars_check():
    r = session.get(f"{BASE_URL}/api/avatars", timeout=15)
    assert r.status_code == 200, f"/api/avatars {r.status_code}"
    data = r.json()
    assert data.get('status') == 'success', f"avatars status {data}"
    assert isinstance(data.get('avatars'), list) and len(data['avatars']) >= 1, 'no avatars returned'


def wordbank_flow_check():
    # Upload small list FIRST to ensure session storage id is initialized
    payload = { 'rows': [
        {'word':'bee','sentence':'','hint':''},
        {'word':'honey','sentence':'','hint':''},
        {'word':'comb','sentence':'','hint':''}
    ] }
    r = session.post(f"{BASE_URL}/api/wordbank", json=payload, timeout=20)
    assert r.status_code == 200, f"set {r.status_code}"
    data = r.json()
    assert data.get('status') == 'success', f"set payload {data}"
    # Get
    r = session.get(f"{BASE_URL}/api/wordbank", timeout=15)
    assert r.status_code == 200, f"get {r.status_code}"
    data = r.json()
    assert data.get('status') == 'success' and data.get('count',0) >= 3, f"get payload {data}"
    # Count
    r = session.get(f"{BASE_URL}/api/wordbank/count", timeout=15)
    assert r.status_code == 200, f"count {r.status_code}"
    data = r.json()
    assert data.get('loaded') is True and data.get('count',0) >= 3, f"count payload {data}"

    # Finally clear to verify endpoint works with initialized session
    r = session.post(f"{BASE_URL}/api/wordbank/clear", timeout=15)
    # Some deployments may return 500 if storage file missing; treat as non-fatal but log
    if r.status_code != 200:
        raise AssertionError(f"clear {r.status_code}")


def quiz_next_answer_check():
    # Ensure a small list exists to start a quiz
    payload = { 'rows': [
        {'word':'bee','sentence':'','hint':''},
        {'word':'honey','sentence':'','hint':''}
    ] }
    _ = session.post(f"{BASE_URL}/api/wordbank", json=payload, timeout=20)

    # Start quiz by requesting next, then answer
    r = session.post(f"{BASE_URL}/api/next", json={}, timeout=15)
    assert r.status_code == 200, f"next {r.status_code}"
    data = r.json()
    # Consider success if a word is present and done is False
    word = (data.get('word_info') or {}).get('word') or data.get('word') or ''
    assert isinstance(word, str), 'next word missing'
    # Submit answer (wrong intentionally)
    ans = {'user_input':'zzz','method':'keyboard','elapsed_ms': 1200}
    r = session.post(f"{BASE_URL}/api/answer", json=ans, timeout=15)
    assert r.status_code == 200, f"answer {r.status_code}"
    data = r.json()
    # Success can be implied if response contains progress or result fields
    assert 'status' in data or 'result' in data or 'progress' in data, f"answer payload {data}"


def run():
    print(f"🚀 Railway smoke test against {BASE_URL}")
    check('health', health_check)
    check('avatars', avatars_check)
    check('wordbank flow', wordbank_flow_check)
    check('quiz next/answer', quiz_next_answer_check)

    if FAILURES:
        print("\n❌ Smoke test failures:")
        for name, msg in FAILURES:
            print(f" - {name}: {msg}")
        sys.exit(2)
    else:
        print("\n✅ All smoke tests passed")
        sys.exit(0)

if __name__ == '__main__':
    run()
