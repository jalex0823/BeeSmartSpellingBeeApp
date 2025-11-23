"""End-to-end quiz flow test using public API endpoints.

Flow exercised:
1. POST /api/upload-manual-words to seed a small custom word list (avoids direct session helpers).
2. Loop: /api/next to fetch each quiz word, then /api/answer to submit correct spelling.
3. After final answer, /api/next returns completion summary we validate.

This mirrors real user interaction and ensures request/session lifecycle integrity.
"""
from AjaSpellBApp import app, get_quiz_state, get_wordbank

SEED_WORDS = ["apple", "bee", "honey"]

with app.test_client() as c:
    # 1. Seed words via manual upload endpoint
    upload_resp = c.post('/api/upload-manual-words', json={"words": SEED_WORDS})
    assert upload_resp.status_code == 200, f"Upload failed status={upload_resp.status_code} body={upload_resp.data[:200]}"
    upload_json = upload_resp.get_json() or {}
    assert upload_json.get('ok') is True, f"Upload response not ok: {upload_json}"
    assert upload_json.get('count') == len(SEED_WORDS), "Uploaded word count mismatch"

    # Verify quiz state & wordbank populated
    state = get_quiz_state()
    wb = get_wordbank()
    assert state is not None, "Quiz state missing after upload"
    assert wb and len(wb) == len(SEED_WORDS), f"Wordbank size mismatch: expected {len(SEED_WORDS)} got {len(wb) if wb else 0}"

    answered = 0
    correct = 0

    # 2. Iterate through words
    for _ in range(len(SEED_WORDS)):
        nxt = c.post('/api/next', json={})
        assert nxt.status_code == 200, f"/api/next status={nxt.status_code}"
        nxt_json = nxt.get_json() or {}
        assert nxt_json.get('done') is False, f"Unexpected completion early: {nxt_json}"
        current_word = nxt_json.get('word')
        assert current_word, f"Missing word in next payload: {nxt_json}"

        ans = c.post('/api/answer', json={
            "user_input": current_word,
            "method": "keyboard",
            "elapsed_ms": 500
        })
        assert ans.status_code == 200, f"/api/answer status={ans.status_code}"
        ans_json = ans.get_json() or {}
        assert 'correct' in ans_json, f"Answer payload missing correctness flag: {ans_json}"
        if ans_json.get('correct'):
            correct += 1
        answered += 1

    # 3. Final call should yield summary
    final = c.post('/api/next', json={})
    assert final.status_code == 200, f"Final /api/next status={final.status_code}"
    final_json = final.get_json() or {}
    assert final_json.get('done') is True, f"Quiz not marked done: {final_json}"
    summary = final_json.get('summary') or {}
    assert summary.get('total') == len(SEED_WORDS), f"Summary total mismatch: {summary}"
    assert summary.get('correct') == correct == len(SEED_WORDS), f"Correct count mismatch: {summary}"
    assert summary.get('incorrect') == 0, f"Unexpected incorrect tally: {summary}"

    print("Quiz flow test passed ✅", summary)
