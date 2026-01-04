from pathlib import Path


def test_restore_login_redirect_includes_next_param_subscription():
    """Smooth UX: if someone taps Restore while signed out, send them to login and back here."""
    sub = Path("templates/subscription.html").read_text(encoding="utf-8")
    assert "/auth/login?next=" in sub


def test_restore_login_redirect_includes_next_param_menu():
    """Smooth UX: same behavior from the unified menu flow."""
    menu = Path("templates/unified_menu.html").read_text(encoding="utf-8")
    assert "/auth/login?next=" in menu
