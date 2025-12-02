"""
Quick smoke test for /api/avatars endpoint.
Runs in-process using Flask test client without starting a server.
"""
from __future__ import annotations

import json

try:
    import AjaSpellBApp as app_module
except Exception as e:
    print(f"Failed to import app module: {e}")
    raise

app = getattr(app_module, 'app', None)
if app is None:
    raise RuntimeError('Flask app not found in AjaSpellBApp')

with app.test_client() as client:
    # Guest request
    r = client.get('/api/avatars')
    print('Status:', r.status_code)
    try:
        data = r.get_json()
    except Exception:
        data = json.loads(r.data.decode('utf-8', errors='ignore'))
    print('Keys:', list(data.keys()) if isinstance(data, dict) else type(data))
    if isinstance(data, dict):
        avatars = data.get('avatars') or []
        print('Avatar count:', len(avatars))
        sample = avatars[0] if avatars else {}
        print('Sample avatar:', json.dumps(sample, indent=2)[:400])
