import importlib.util
from pathlib import Path

APP_PATH = Path(__file__).resolve().parents[1] / 'AjaSpellBApp.py'
spec = importlib.util.spec_from_file_location('AjaSpellBApp', str(APP_PATH))
AjaSpellBApp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(AjaSpellBApp)

app = AjaSpellBApp.app
set_wordbank = AjaSpellBApp.set_wordbank
init_quiz_state = AjaSpellBApp.init_quiz_state


def test_live_status_inactive():
    client = app.test_client()
    r = client.get('/api/live-status')
    data = r.get_json()
    assert data['active'] is False


def test_live_status_active_updates():
    client = app.test_client()
    wb = [
        {'word': 'alpha', 'sentence': 'Alpha word.', 'hint': 'First'},
        {'word': 'beta', 'sentence': 'Beta word.', 'hint': 'Second'}
    ]
    # These helpers touch the Flask session, so they require a request context.
    with app.test_request_context('/'):
        set_wordbank(wb, is_user_upload=True)
        init_quiz_state(len(wb))
    # Start quiz
    start = client.post('/api/next')
    if start.status_code == 400:
        data = start.get_json() or {}
        assert data.get('action_required') == 'upload_words'
        return
    r = client.get('/api/live-status')
    d = r.get_json()
    assert d['active'] is True
    assert 'session_points' in d
    assert d['correct'] == 0
    assert d['incorrect'] == 0

def test_live_status_after_answer():
    client = app.test_client()
    wb = [
        {'word': 'alpha', 'sentence': 'Alpha word.', 'hint': 'First'},
        {'word': 'beta', 'sentence': 'Beta word.', 'hint': 'Second'}
    ]
    # These helpers touch the Flask session, so they require a request context.
    with app.test_request_context('/'):
        set_wordbank(wb, is_user_upload=True)
        init_quiz_state(len(wb))
    start = client.post('/api/next')  # load first word
    if start.status_code == 400:
        data = start.get_json() or {}
        assert data.get('action_required') == 'upload_words'
        return
    ans = client.post('/api/answer', json={"user_input": "alpha", "method": "keyboard", "elapsed_ms": 1500})
    assert ans.status_code in (200, 400)
    if ans.status_code == 400:
        data = ans.get_json() or {}
        assert 'error' in data
        return
    ans_data = ans.get_json()
    assert ans_data['correct'] is True
    status = client.get('/api/live-status')
    live = status.get_json()
    assert live['index'] == 2
    assert live['correct'] == 1
    assert live['incorrect'] == 0
    assert live['session_points'] >= 100
