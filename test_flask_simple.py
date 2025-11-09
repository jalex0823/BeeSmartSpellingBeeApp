"""Simple sanity check using the app's built-in /health endpoint via test client.

Avoids binding to port 5000 (which may already be in use during CI/dev).
"""
from AjaSpellBApp import app

with app.test_client() as c:
    r = c.get('/health')
    print('Status:', r.status_code)
    try:
        print('JSON:', r.get_json())
    except Exception:
        print('Body:', r.data[:200])
    if r.status_code != 200:
        raise SystemExit(1)
