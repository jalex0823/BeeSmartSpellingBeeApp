import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from AjaSpellBApp import app

def run():
    client = app.test_client()

    # 1) Import simple text list via API
    words_text = "alpha\nbeta\ngamma\n"
    res = client.post('/api/wordbank/import-text', json={
        'text': words_text,
        'delimiter': None,
        'clear_first': True
    })
    assert res.status_code == 200, res.data
    print('Import-text response:', res.get_json())

    # 2) Verify wordbank count and loaded flag
    res = client.get('/api/wordbank/count')
    assert res.status_code == 200
    cnt = res.get_json()
    print('Wordbank Count:', json.dumps(cnt, indent=2))
    assert cnt.get('loaded') is True
    assert cnt.get('count') == 3

    # 3) Check session debug; quiz state should be initialized by the import-text endpoint
    res = client.get('/api/debug/session')
    dbg = res.get_json()
    print('Session Debug:', json.dumps(dbg, indent=2))
    assert dbg.get('wordbank_via_get') == 3
    assert 'quiz_state_v1' in dbg.get('session_keys', [])

    print('✅ Smoke test for wordbank import and quiz init passed')

if __name__ == '__main__':
    run()
