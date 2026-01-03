import os
import sys
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from AjaSpellBApp import app


def run():
    client = app.test_client()

    # Import a small list (also initializes quiz state via server logic).
    words = "alpha\nbeta\ngamma"
    res = client.post("/api/wordbank/import-text", json={"text": words, "delimiter": None})
    assert res.status_code == 200, res.data
    print("Import:", res.get_json())

    # 1) Resume should NOT be offered before any progress.
    res = client.post("/api/quiz/resume")
    assert res.status_code == 200, res.data
    payload = res.get_json()
    print("Resume (no progress):", json.dumps(payload, indent=2))
    assert payload.get("in_progress") is False
    assert payload.get("resumed") is False

    # 2) Start quiz + earn points for first answer.
    res = client.post("/api/next")
    assert res.status_code == 200, res.data
    next_payload = res.get_json()
    print("Next 1:", json.dumps(next_payload, indent=2))
    first_word = next_payload.get("word")
    assert first_word, "Expected a word from /api/next"

    res = client.post(
        "/api/answer",
        json={"user_input": first_word, "method": "keyboard", "elapsed_ms": 1000},
    )
    assert res.status_code == 200, res.data
    ans1 = res.get_json()
    print("Answer 1:", json.dumps(ans1, indent=2))
    total1 = int((ans1.get("points") or {}).get("session_total") or 0)
    assert total1 > 0

    # 3) Now resume should be offered.
    res = client.post("/api/quiz/resume")
    assert res.status_code == 200, res.data
    payload = res.get_json()
    print("Resume (has progress):", json.dumps(payload, indent=2))
    assert payload.get("in_progress") is True
    assert payload.get("resumed") is True

    # 4) Resume action should NOT reset points/state.
    res = client.post("/api/quiz/start", json={"action": "resume"})
    assert res.status_code == 200, res.data
    start_payload = res.get_json()
    print("Quiz start(resume):", json.dumps(start_payload, indent=2))
    assert start_payload.get("resumed") is True

    # 5) Continue quiz, ensure points accumulate (not reset).
    res = client.post("/api/next")
    assert res.status_code == 200, res.data
    next_payload = res.get_json()
    print("Next 2:", json.dumps(next_payload, indent=2))
    second_word = next_payload.get("word")
    assert second_word

    res = client.post(
        "/api/answer",
        json={"user_input": second_word, "method": "keyboard", "elapsed_ms": 1200},
    )
    assert res.status_code == 200, res.data
    ans2 = res.get_json()
    print("Answer 2:", json.dumps(ans2, indent=2))
    total2 = int((ans2.get("points") or {}).get("session_total") or 0)
    assert total2 >= total1, f"Expected session_total to be >= {total1}, got {total2}"

    # 6) Finish the quiz quickly.
    completion_payload = None
    for _ in range(5):
        res = client.post("/api/next")
        assert res.status_code == 200, res.data
        p = res.get_json()
        if p.get("done"):
            print("Completion payload:", json.dumps(p, indent=2))
            completion_payload = p
            break
        w = p.get("word")
        if not w:
            continue
        res = client.post(
            "/api/answer",
            json={"user_input": w, "method": "keyboard", "elapsed_ms": 1500},
        )
        assert res.status_code == 200, res.data

    assert completion_payload is not None, "Did not reach quiz completion within expected steps"
    assert completion_payload.get("done") is True
    assert "summary" in completion_payload, f"Completion payload missing summary: {completion_payload.keys()}"

    # 7) "Report card" is the done=True summary payload the UI uses.
    summary = completion_payload["summary"]
    required_keys = [
        "total",
        "correct",
        "incorrect",
        "history",
        "session_points",
        "incorrect_words",
    ]
    for k in required_keys:
        assert k in summary, f"summary missing '{k}'"

    final_points = int(summary.get("session_points") or 0)
    assert final_points >= total2, f"Expected final session_points to be >= {total2}, got {final_points}"

    print("✅ Quiz start/resume/points/report smoke passed")


if __name__ == "__main__":
    run()
