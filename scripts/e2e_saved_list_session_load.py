import json
import os
import sys

# Ensure project root is on sys.path for module imports
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from AjaSpellBApp import app


def run():
    client = app.test_client()
    # Create a list with load_into_session=true
    payload = {
        "name": "E2E Test List",
        "description": "automated test",
        "words": [
            {"word": "apple"},
            {"word": "bee"},
            {"word": "school"}
        ],
        "load_into_session": True
    }
    res = client.post("/api/saved-lists", json=payload)
    assert res.status_code in (200,201), res.data
    data = res.get_json()
    assert data.get("ok") is True
    list_obj = data.get("list")
    assert list_obj and list_obj.get("word_count") == 3

    # Debug session state
    res = client.get("/api/debug/session")
    assert res.status_code == 200
    dbg = res.get_json()
    print("Session Debug:", json.dumps(dbg, indent=2))
    assert dbg.get("wordbank_via_get") == 3

    # Verify quiz state initialized
    res = client.get("/api/wordbank/count")
    assert res.status_code == 200
    cnt = res.get_json()
    print("Wordbank Count:", json.dumps(cnt, indent=2))
    assert cnt.get("loaded") is True
    assert cnt.get("count") == 3

    print("✅ E2E saved list → session load passed")


if __name__ == "__main__":
    run()
