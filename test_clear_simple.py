"""Test /api/clear endpoint using Flask test client rather than external HTTP.

The endpoint requires a confirmation payload; first send empty data (expect 400/403), then valid confirmation.
"""
from AjaSpellBApp import app

with app.test_client() as c:
    print("Testing /api/clear without confirmation...")
    r = c.post('/api/clear', json={})
    if r.status_code in (400, 403):
        print(f"✅ Expected rejection status={r.status_code}")
    else:
        print(f"❌ Unexpected status without confirmation: {r.status_code}")
        print('Body:', r.data[:200])

    print("\nTesting /api/clear with confirmation...")
    r2 = c.post('/api/clear', json={"confirmed": True})
    if r2.status_code == 200:
        resp = r2.get_json(silent=True) or {}
        print(f"✅ Success: cleared_count={resp.get('cleared_count','?')}")
    else:
        print(f"❌ Error status: {r2.status_code}")
        print('Body:', r2.data[:200])