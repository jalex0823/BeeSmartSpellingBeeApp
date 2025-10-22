import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from AjaSpellBApp import app

def test_reset_page_renders():
    client = app.test_client()
    resp = client.get('/auth/reset?token=abc')
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert 'Reset your password' in html


def test_reset_post_generic_response():
    client = app.test_client()
    resp = client.post('/auth/reset', json={'token': 'abc', 'password': 'short'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data and data.get('success') is True
    assert 'password has been updated' in (data.get('message') or '')
