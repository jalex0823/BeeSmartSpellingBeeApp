#!/usr/bin/env python3
"""
BeeSmart — Battles API smoke test

This script exercises the Battles endpoints against a running local server.
It will:
  - GET /health
  - GET /api/battles/live
  - POST /api/battles/create (public, allow_guests)
  - POST /api/battles/<code>/join (as guest name)
  - GET /api/battles/<code>

Usage:
  python scripts/smoke_battles.py            # default http://localhost:5000
  BASE_URL=http://127.0.0.1:5000 python scripts/smoke_battles.py

Exit codes:
  0 on success, non-zero on failure
"""
import os
import sys
import json
import time
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    print("This script requires the 'requests' package. Install with: pip install requests", file=sys.stderr)
    sys.exit(2)

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")
SESSION = requests.Session()

def p(step, data=None):
    print(f"\n=== {step} ===")
    if data is not None:
        if isinstance(data, (dict, list)):
            print(json.dumps(data, indent=2, sort_keys=True))
        else:
            print(str(data))

def req(method, path, **kwargs):
    url = urljoin(BASE_URL.rstrip('/') + '/', path.lstrip('/'))
    resp = SESSION.request(method.upper(), url, timeout=8, **kwargs)
    return resp

def main():
    try:
        # Health check
        r = req('GET', '/health')
        p('GET /health', {'status': r.status_code, 'json': r.json() if r.headers.get('content-type','').startswith('application/json') else r.text})
        r.raise_for_status()

        # List live battles
        r = req('GET', '/api/battles/live')
        live = []
        try:
            live = r.json()
        except Exception:
            pass
        p('GET /api/battles/live', {'status': r.status_code, 'count': len(live) if isinstance(live, list) else 'n/a'})
        r.raise_for_status()

        # Create a new battle (public, allow guests)
        payload = {"wordset_name": "Smoke Test Set", "mode": "standard", "max_players": 8, "is_public": True, "allow_guests": True}
        r = req('POST', '/api/battles/create', json=payload)
        data = r.json()
        p('POST /api/battles/create', data)
        r.raise_for_status()
        if not data.get('ok') or 'battle' not in data or 'code' not in data['battle']:
            print('Battle creation did not return expected payload', file=sys.stderr)
            return 3
        code = data['battle']['code']

        # Join the newly created battle as a guest
        r = req('POST', f'/api/battles/{code}/join', json={"name": "GuestTester"})
        join_data = r.json()
        p(f'POST /api/battles/{code}/join', join_data)
        r.raise_for_status()
        if not join_data.get('ok'):
            print('Join failed', file=sys.stderr)
            return 4

        # Fetch battle info
        time.sleep(0.2)
        r = req('GET', f'/api/battles/{code}')
        info = r.json()
        p(f'GET /api/battles/{code}', info)
        r.raise_for_status()
        print("\n✅ Battles smoke test completed successfully.")
        return 0
    except requests.RequestException as e:
        print(f"HTTP error: {e}", file=sys.stderr)
        return 5
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 6

if __name__ == '__main__':
    sys.exit(main())
