import os
import sys

import pytest


@pytest.fixture(scope="module")
def app_and_client():
    # Ensure repo root is importable when running from tests/
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    import AjaSpellBApp as appmod

    app = getattr(appmod, "app", None)
    assert app is not None, "Expected Flask app to be exposed as AjaSpellBApp.app"

    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SECRET_KEY="test-secret",
    )

    with app.test_client() as client:
        yield app, client


@pytest.fixture()
def authed_client(app_and_client, monkeypatch):
    """Flask test client with an authenticated (non-premium) user patched in."""
    _app, client = app_and_client

    class User:
        is_authenticated = True
        id = 123
        username = "test-student"
        role = "student"
        honey_points = 0
        premium_member = False
        purchased_avatars = []
        purchased_bundles = []

    from flask_login import utils as flask_login_utils

    monkeypatch.setattr(flask_login_utils, "_get_user", lambda: User(), raising=True)
    return client


def test_picker_pages_never_upsell_for_authed_user(authed_client):
    """Authenticated users must be able to open picker pages.

    Production rule:
      - Any registered user (student/admin/etc) can access the picker UI.
      - Only avatar tiles are locked/unlocked; the user is never redirected to premium/upsell.
    """

    # These endpoints should not redirect to any premium/upsell page.
    for path in ("/avatar-picker", "/honeycomb-picker", "/honeycomb-picker-old"):
        resp = authed_client.get(path, follow_redirects=False)
        assert resp.status_code == 200, f"Expected 200 for {path}, got {resp.status_code}"
        body = (resp.get_data(as_text=True) or "").lower()
        assert "join the hive" not in body
        assert "subscription" not in body


def test_api_avatars_registered_user_has_mixed_lock_states(authed_client):
    """A registered non-premium user should get the full catalog with lock states.

    We don't assert the exact 5 free IDs here (catalog can evolve), but we do
 assert the key behavior:
      - Some avatars are unlocked (the default free set)
      - Some avatars are locked (premium/earn_or_buy)
    """
    resp = authed_client.get("/api/avatars")
    assert resp.status_code == 200
    payload = resp.get_json() or {}
    assert payload.get("status") == "success"
    avatars = payload.get("avatars") or []
    assert isinstance(avatars, list)
    assert len(avatars) >= 5

    # API returns `is_locked` (True/False) rather than `unlocked`.
    unlocked = [a for a in avatars if not bool(a.get("is_locked"))]
    locked = [a for a in avatars if bool(a.get("is_locked"))]
    assert len(unlocked) >= 1
    assert len(locked) >= 1
