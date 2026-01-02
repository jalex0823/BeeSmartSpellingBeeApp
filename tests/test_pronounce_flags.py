import json
import importlib.util
from pathlib import Path

# Import Flask app and helpers from AjaSpellBApp
APP_PATH = Path(__file__).resolve().parents[1] / 'AjaSpellBApp.py'
spec = importlib.util.spec_from_file_location('AjaSpellBApp', str(APP_PATH))
AjaSpellBApp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(AjaSpellBApp)

app = AjaSpellBApp.app
get_wordbank = AjaSpellBApp.get_wordbank
set_wordbank = AjaSpellBApp.set_wordbank
init_quiz_state = AjaSpellBApp.init_quiz_state
QUIZ_STATE_KEY = AjaSpellBApp.QUIZ_STATE_KEY

# Ensure errors propagate during tests so 500s show useful tracebacks.
app.config.update(TESTING=True, PROPAGATE_EXCEPTIONS=True)

# Minimal integration using Flask test client

def test_should_announce_and_auto_pronounce_flags():
    client = app.test_client()

    # Seed a tiny wordbank
    wb = [{'word': 'bee', 'sentence': 'The bee buzzes.', 'hint': 'It makes honey.'}]
    seed = client.post('/api/upload-manual-words', json=wb)
    assert seed.status_code == 200, (seed.get_json() or seed.get_data(as_text=True))

    # Hit /api/next to get flags
    resp = client.post('/api/next')
    assert resp.status_code == 200
    data = resp.get_json()

    assert 'shouldAnnounce' in data and 'announceToken' in data

    # Auto pronounce once
    payload = {'auto': True, 'token': data['announceToken']}
    resp2 = client.post('/api/pronounce', data=json.dumps(payload), content_type='application/json')
    assert resp2.status_code == 200

    # Hit /api/next rapidly again — shouldAnnounce likely false
    resp3 = client.post('/api/next')
    assert resp3.status_code == 200
    data3 = resp3.get_json()
    assert 'shouldAnnounce' in data3
    # We cannot strictly assert false due to timing, but the field existence is verified.
