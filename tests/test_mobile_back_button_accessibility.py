from pathlib import Path


def test_base_has_safe_area_fixed_back_class():
    """Regression guard: keep a reusable safe-area aware fixed back-button helper."""
    base = Path("templates/base.html").read_text(encoding="utf-8")
    assert ".beesmart-fixed-back" in base
    assert ".beesmart-fixed-back-bottom-left" in base
    # iOS notch devices need safe-area support.
    assert "safe-area-inset-top" in base


def test_subscription_back_button_uses_fixed_back_class():
    """Subscription page has a fixed back button that must stay reachable on iPhone."""
    sub = Path("templates/subscription.html").read_text(encoding="utf-8")
    assert "class=\"back-button beesmart-fixed-back-bottom-left\"" in sub
