from __future__ import annotations

from pathlib import Path


def test_api_auth_status_endpoint_exists_and_returns_json(client):
    res = client.get('/api/auth/status')
    assert res.status_code == 200
    data = res.get_json() or {}
    assert 'authenticated' in data
    assert isinstance(data['authenticated'], bool)


def test_subscription_template_contains_server_auth_check():
    # Regression check: we should not rely solely on window.IS_REAL_AUTH.
    sub = Path('templates/subscription.html').read_text(encoding='utf-8')
    assert '/api/auth/status' in sub
