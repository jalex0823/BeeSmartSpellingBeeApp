"""
Smoke tests: syntax errors (templates + app), full app routes, and wireframe layout.

Run: pytest tests/test_smoke_syntax_and_app.py -v
"""

from pathlib import Path
import re

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ─── Template syntax (Jinja render) ─────────────────────────────────────────

@pytest.fixture(scope="module")
def app():
    import AjaSpellBApp
    AjaSpellBApp.app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        PROPAGATE_EXCEPTIONS=True,
    )
    return AjaSpellBApp.app


@pytest.fixture(scope="module")
def client(app):
    with app.test_client() as c:
        with app.app_context():
            yield c


def test_app_imports_without_error():
    """App module imports and Flask app exists."""
    import AjaSpellBApp
    assert AjaSpellBApp.app is not None


def test_key_templates_render(app):
    """Key templates render without Jinja/syntax errors (need request context for url_for)."""
    with app.test_request_context("/"):
        from flask import render_template
        render_template("base.html")
        render_template("auth/login.html")
        render_template("auth/register.html")
        render_template("subscription.html", user_authenticated=False, current_user=None,
                        student_cannot_purchase=False, subscription_monthly_usd=3.99,
                        subscription_trial_days=0, subscription_product_ids={},
                        iap_monthly_only=False)
        render_template("help.html")
        render_template("terms.html")
        render_template("privacy.html")


def test_home_route_returns_ok(client):
    """GET / or /app returns 200 or expected redirect."""
    r = client.get("/")
    assert r.status_code in (200, 302)
    r2 = client.get("/app")
    assert r2.status_code in (200, 302)


def test_auth_routes_respond(client):
    """Auth routes respond (200 or 302)."""
    assert client.get("/auth/login").status_code in (200, 302)
    assert client.get("/auth/register").status_code in (200, 302)


def test_subscription_help_terms_privacy_respond(client):
    """Subscription, help, terms, privacy respond."""
    assert client.get("/subscription").status_code in (200, 302)
    assert client.get("/help").status_code in (200, 302)
    assert client.get("/terms").status_code == 200
    assert client.get("/privacy").status_code == 200


def test_api_health_or_equivalent(client):
    """At least one API or status endpoint responds."""
    # Common endpoints that indicate app is wired
    r = client.get("/api/auth/status") if hasattr(client, "get") else None
    if r is not None:
        assert r.status_code in (200, 401, 302)


# ─── Wireframe layout (unified_menu): structure and spacing ───────────────────

def test_unified_menu_has_wireframe_layout_classes():
    """Unified menu has wireframe layout classes: stats 2×2, main actions 2×2, refresh pill, what now."""
    menu = REPO_ROOT / "templates" / "unified_menu.html"
    txt = _read(menu)
    assert "home-stats-row" in txt
    assert "home-refresh-stats-wrap" in txt
    assert "home-main-actions" in txt
    assert "home-btn-quiz" in txt
    assert "home-btn-dashboard" in txt
    assert "home-btn-settings" in txt
    assert "home-btn-signout" in txt
    assert "home-what-now-wrap" in txt


def test_unified_menu_mobile_css_has_equal_sizing():
    """Mobile (<=480px) CSS uses 2×2 grid, equal gap (12–16px), button height 56px."""
    menu = REPO_ROOT / "templates" / "unified_menu.html"
    txt = _read(menu)
    assert "grid-template-columns: 1fr 1fr" in txt or "grid-template-columns:1fr 1fr" in txt.replace(" ", "")
    assert "home-stats-row" in txt and "home-main-actions" in txt
    # Gap 12px or 16px
    assert re.search(r"gap:\s*1[26]px", txt), "Expected gap 12px or 16px for equal spacing"
    # Button height 56px on mobile
    assert "56px" in txt


def test_unified_menu_has_wireframe_button_labels():
    """Main action labels match wireframe: Start Quiz, Dashboard, Settings, Sign Out; About; Refresh Stats."""
    menu = REPO_ROOT / "templates" / "unified_menu.html"
    txt = _read(menu)
    assert "Dashboard" in txt
    assert "Settings" in txt
    assert "Sign Out" in txt
    assert "Start Quiz" in txt, "Wireframe: main action row 1 left is 'Start Quiz'"
    assert "About" in txt
    assert "Refresh stats" in txt or "Refresh Stats" in txt


def test_unified_menu_main_actions_visual_order():
    """Mobile order: Start Quiz (1), Dashboard (2), Settings (3), Sign Out (4)."""
    menu = REPO_ROOT / "templates" / "unified_menu.html"
    txt = _read(menu)
    assert "home-main-actions .home-btn-quiz { order: 1" in txt or "home-btn-quiz { order: 1" in txt
    assert "home-btn-dashboard { order: 2" in txt or "home-btn-dashboard { order: 2" in txt
    assert "home-btn-settings { order: 3" in txt
    assert "home-btn-signout { order: 4" in txt


def test_about_modal_exists_and_has_content():
    """About modal exists with title and short copy."""
    menu = REPO_ROOT / "templates" / "unified_menu.html"
    txt = _read(menu)
    assert "aboutModalOverlay" in txt
    assert "aboutModalTitle" in txt
    assert "About BeeSmart" in txt
    assert "aboutModalCloseBtn" in txt
    assert "Spelling practice" in txt or "spelling" in txt
