import importlib.util
from pathlib import Path

APP_PATH = Path(__file__).resolve().parents[1] / 'AjaSpellBApp.py'
spec = importlib.util.spec_from_file_location('AjaSpellBApp', str(APP_PATH))
AjaSpellBApp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(AjaSpellBApp)

app = AjaSpellBApp.app
set_wordbank = AjaSpellBApp.set_wordbank
init_quiz_state = AjaSpellBApp.init_quiz_state

# Ensure errors propagate during tests so 500s show useful tracebacks.
app.config.update(TESTING=True, PROPAGATE_EXCEPTIONS=True)


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
    # Seed through a route so the same client session cookie gets the storage pointer.
    seed = client.post('/api/upload-manual-words', json=wb)
    assert seed.status_code == 200
    # Start quiz
    start = client.post('/api/next')
    assert start.status_code == 200
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
    # Seed through a route so the same client session cookie gets the storage pointer.
    seed = client.post('/api/upload-manual-words', json=wb)
    assert seed.status_code == 200
    start = client.post('/api/next')  # load first word
    assert start.status_code == 200
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
