import os
import sys

import pytest


@pytest.fixture(scope="module")
def app_and_client():
    # Ensure repo root is importable when running from tests/
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    # Import the Flask app object from the main app module.
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


def _collect_unlocked(avatars_payload):
    assert avatars_payload["status"] == "success"
    avatars = avatars_payload["avatars"]
    # API returns `is_locked` (True/False) rather than `unlocked`.
    unlocked = [a for a in avatars if not bool(a.get("is_locked"))]
    return avatars, unlocked


def test_api_avatars_guest_is_mostly_locked(app_and_client, monkeypatch):
    """Guests should be locked down, with mascot as the only default."""
    app, client = app_and_client

    # Simulate logged-out.
    from flask_login import utils as flask_login_utils

    monkeypatch.setattr(
        flask_login_utils,
        "_get_user",
        lambda: type("Anon", (), {"is_authenticated": False})(),
        raising=True,
    )

    resp = client.get("/api/avatars")
    assert resp.status_code == 200
    payload = resp.get_json()
    avatars, unlocked = _collect_unlocked(payload)

    # Guest should see the catalog but only a very small subset unlocked.
    assert len(avatars) >= 39
    # Product rule: guests don't have avatar picker access; mascot is the default.
    unlocked_ids = {a.get("id") for a in unlocked}
    assert "mascot-bee" in unlocked_ids
    # Fail closed: allow only mascot by default. If we ever intentionally unlock
    # something else for guests (e.g., App Review mode), loosen this assertion.
    assert unlocked_ids.issubset({"mascot-bee"})


def test_api_avatars_registered_default_free_only(app_and_client, monkeypatch):
    """Registered non-premium should have exactly the 5 default_free avatars unlocked."""
    app, client = app_and_client

    class User:
        is_authenticated = True
        id = 123
        role = "student"
        honey_points = 0
        premium_member = False
        purchased_avatars = []
        purchased_bundles = []

    from flask_login import utils as flask_login_utils

    monkeypatch.setattr(flask_login_utils, "_get_user", lambda: User(), raising=True)

    resp = client.get("/api/avatars")
    assert resp.status_code == 200
    payload = resp.get_json()
    avatars, unlocked = _collect_unlocked(payload)

    # Validate unlocked count.
    # Note: the app can also unlock a special "mascot" avatar for all signed-in users
    # (tier often shows as `mascot_free`), so we assert at least the 5 registration
    # freebies, not necessarily exactly 5 total unlocked.
    assert len(unlocked) >= 5

    # Validate unlocked set matches catalog `tier == default_free`.
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from avatar_catalog import AVATAR_CATALOG

    expected_ids = sorted([a["id"] for a in AVATAR_CATALOG if str(a.get("tier", "")).lower() == "default_free"])
    unlocked_ids = sorted([a.get("id") for a in unlocked])
    assert set(expected_ids).issubset(set(unlocked_ids))


def test_api_avatars_admin_all_unlocked(app_and_client, monkeypatch):
    """Admin should have all avatars unlocked."""
    app, client = app_and_client

    class Admin:
        is_authenticated = True
        id = 999
        role = "admin"
        honey_points = 0
        premium_member = True
        purchased_avatars = []
        purchased_bundles = []

    from flask_login import utils as flask_login_utils

    monkeypatch.setattr(flask_login_utils, "_get_user", lambda: Admin(), raising=True)

    resp = client.get("/api/avatars")
    assert resp.status_code == 200
    payload = resp.get_json()
    avatars, unlocked = _collect_unlocked(payload)

    assert len(avatars) >= 39
    assert len(unlocked) == len(avatars)


@pytest.mark.parametrize("path", ["/avatar-picker"])
def test_guest_cannot_access_avatar_picker_routes(app_and_client, monkeypatch, path):
    """Guests should be redirected away from authenticated-only picker UIs to register/login."""
    app, client = app_and_client

    # Simulate logged-out guest.
    from flask_login import utils as flask_login_utils

    monkeypatch.setattr(
        flask_login_utils,
        "_get_user",
        lambda: type("Anon", (), {"is_authenticated": False})(),
        raising=True,
    )

    resp = client.get(path, follow_redirects=False)
    assert resp.status_code in (301, 302, 303, 307, 308)
    location = resp.headers.get("Location", "")

    # Accept either register or login redirect targets (implementation may vary).
    assert ("/auth/register" in location) or ("/auth/login" in location)


def test_guest_can_browse_honeycomb_picker(app_and_client, monkeypatch):
    """Guests may browse the honeycomb picker for IAP discoverability (Apple requirement)."""
    _app, client = app_and_client

    # Simulate logged-out guest.
    from flask_login import utils as flask_login_utils

    monkeypatch.setattr(
        flask_login_utils,
        "_get_user",
        lambda: type("Anon", (), {"is_authenticated": False})(),
        raising=True,
    )

    resp = client.get("/honeycomb-picker", follow_redirects=False)
    assert resp.status_code == 200
