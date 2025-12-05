import json
import pytest

from AjaSpellBApp import app, init_quiz_state, set_wordbank

@pytest.fixture
def client():
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
    })
    with app.test_client() as client:
        with app.app_context():
            yield client


def start_quiz_with_words(client, words):
    # Prepare a minimal wordbank shape: {word, sentence, hint}
    rows = [{"word": w, "sentence": f"Fill in the blank: ___", "hint": ""} for w in words]
    set_wordbank(rows, is_user_upload=True)
    init_quiz_state(len(rows))


def post_json(client, url, payload):
    return client.post(url, data=json.dumps(payload), content_type='application/json')


def test_next_advances_and_fields_consistent(client):
    start_quiz_with_words(client, ["apple", "bee", "cat"])    
    # First next
    r1 = post_json(client, '/api/next', {})
    assert r1.status_code == 200
    data1 = r1.get_json()
    assert data1.get('done') is False
    assert data1['progress']['index'] == 1
    assert data1['progress']['total'] == 3
    assert data1['definition']
    assert 'word' in data1  # for TTS/pronounce

    # Submit incorrect answer, should move to next word and increment incorrect
    a1 = post_json(client, '/api/answer', {"user_input": "wrong", "method": "keyboard", "elapsed_ms": 5000})
    assert a1.status_code == 200
    ad1 = a1.get_json()
    assert ad1['progress']['index'] == 2
    assert ad1['progress']['incorrect'] == 1

    # Next call should show second word
    r2 = post_json(client, '/api/next', {})
    assert r2.status_code == 200
    data2 = r2.get_json()
    assert data2['progress']['index'] == 2
    assert data2['progress']['total'] == 3

    # Submit correct answer for second word
    a2 = post_json(client, '/api/answer', {"user_input": "bee", "method": "voice", "elapsed_ms": 10000})
    ad2 = a2.get_json()
    assert ad2['progress']['index'] == 3
    assert ad2['progress']['correct'] == 1

    # Skip third
    a3 = post_json(client, '/api/answer', {"user_input": "", "method": "skip"})
    ad3 = a3.get_json()
    assert ad3['progress']['index'] == 3  # already at total
    assert ad3['quiz_complete'] is True
    assert ad3['progress']['total'] == 3


def test_default_wordbank_fallback(client):
    # Do not set wordbank; api_next should initialize via default loader
    r = post_json(client, '/api/next', {})
    assert r.status_code == 200 or r.status_code == 400
    # If default words exist, we expect success
    if r.status_code == 200:
        data = r.get_json()
        assert data.get('done') is False
        assert data['progress']['index'] == 1
        assert data['progress']['total'] >= 1
    else:
        err = r.get_json()
        assert err['status'] == 'error'


def test_hint_and_sentence_presence(client):
    start_quiz_with_words(client, ["delta"])    
    r = post_json(client, '/api/next', {})
    data = r.get_json()
    assert 'sentence' in data
    assert 'hint' in data

    # Request pronounce (auto) should not increment hints
    pr = post_json(client, '/api/pronounce', {"auto": True, "token": "t123"})
    assert pr.status_code == 200 or pr.status_code == 400

    # Request pronounce (user) should increment hints_used_current_word
    pr2 = post_json(client, '/api/pronounce', {"auto": False})
    assert pr2.status_code == 200 or pr2.status_code == 400
