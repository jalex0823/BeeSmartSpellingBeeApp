"""Simple API smoke test using Flask test client to avoid external server dependency.

Handles both legacy list payload and current dict payload with `avatars` key.
"""
from AjaSpellBApp import app

with app.test_client() as c:
    r = c.get('/api/avatars')
    print(f'API Status: {r.status_code}')
    if r.status_code != 200:
        print('Body:', r.data[:200])
        raise SystemExit(1)
    data = r.get_json(silent=True)
    if isinstance(data, list):
        avatars = data
    elif isinstance(data, dict):
        avatars = data.get('avatars', [])
    else:
        print('Unexpected payload type')
        raise SystemExit(1)
    print(f'Total: {len(avatars)}')

    obj = [a for a in avatars if a.get('obj_file', '').endswith('.obj')]
    glb = [a for a in avatars if a.get('obj_file', '').endswith('.glb') or a.get('model_type') == 'glb']

    print(f'OBJ: {len(obj)}, GLB: {len(glb)}')

    if glb:
        first = glb[0]
        print(f'\nFirst GLB: {first.get("name","?")}')
        urls = first.get('urls', {}) or {}
        print(f'  URL: {urls.get("model_obj","n/a")}')
        print(f'  Thumbnail: {urls.get("thumbnail","n/a")}')
