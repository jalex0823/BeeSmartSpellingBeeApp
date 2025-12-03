import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from AjaSpellBApp import app

def run():
    client = app.test_client()

    # Load a small list to initialize wordbank and quiz state
    res = client.post('/api/wordbank/import-text', json={'text': 'alpha\nbeta\ngamma', 'delimiter': None})
    assert res.status_code == 200, res.data
    print('Import:', res.get_json())

    # Check quiz state presence
    res = client.get('/api/quiz/state')
    assert res.status_code == 200, res.data
    state_payload = res.get_json()
    print('State:', json.dumps(state_payload, indent=2))
    assert state_payload.get('has_state') is True
    assert state_payload.get('total_words') == 3

    # Resume should detect existing state and not reinitialize
    res = client.post('/api/quiz/resume')
    assert res.status_code == 200, res.data
    resume_payload = res.get_json()
    print('Resume:', json.dumps(resume_payload, indent=2))
    assert resume_payload.get('resumed') is True

    print('✅ Quiz resume test passed')

if __name__ == '__main__':
    run()
