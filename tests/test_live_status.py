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
    set_wordbank(wb, is_user_upload=True)
    init_quiz_state()
    # Start quiz
    client.post('/api/next')
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
    set_wordbank(wb, is_user_upload=True)
    init_quiz_state()
    client.post('/api/next')  # load first word
    ans = client.post('/api/answer', json={"user_input": "alpha", "method": "keyboard", "elapsed_ms": 1500})
    assert ans.status_code == 200
    ans_data = ans.get_json()
    assert ans_data['correct'] is True
    status = client.get('/api/live-status')
    live = status.get_json()
    assert live['index'] == 2
    assert live['correct'] == 1
    assert live['incorrect'] == 0
    assert live['session_points'] >= 100
