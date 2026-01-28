"""
Smoke tests for Apple Feb 2025 compliance (Developer Notes for Cursor).

Covers: kids copy removed, subscription/student gating, price+auto-renew on subscription screen.
Run: pytest tests/test_apple_feb2025_compliance_smoke.py -v
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_no_kids_child_visible_in_quiz():
    """Task 1.1: No 'Kids' or 'Kid-Safe' user-facing copy in quiz."""
    p = REPO_ROOT / "templates" / "quiz.html"
    txt = _read(p)
    assert "Kid-Safe Words" not in txt, "Use 'Filtered Words' (Apple Feb 2025)"
    assert "age-appropriate content" not in txt, "Use 'appropriate vocabulary' in tooltips"


def test_no_kids_child_visible_in_unified_menu():
    """Task 1.1: No 'Kid-Safe Content' in menu; use 'For All Ages' or 'Filtered Content'."""
    p = REPO_ROOT / "templates" / "unified_menu.html"
    txt = _read(p)
    assert "Kid-Safe Content" not in txt, "Use 'For All Ages' or 'Filtered Content' (Apple Feb 2025)"
    assert "age-appropriate content" not in txt or "appropriate vocabulary" in txt
    assert "For All Ages" in txt or "Filtered Content" in txt, "Badge should say 'For All Ages' or 'Filtered Content'"
    assert "for learners of all ages" in txt or "for all ages" in txt.lower(), "Subtext should mention all ages"


def test_terms_learners_not_children():
    """Task 1.1: Terms use 'learners' / 'people of all ages', not 'children and families' only."""
    p = REPO_ROOT / "templates" / "terms.html"
    txt = _read(p)
    assert "designed for learners and families" in txt or "people of all ages" in txt


def test_privacy_learners_not_children():
    """Task 1.1: Privacy uses 'learners and families', not kids-specific."""
    p = REPO_ROOT / "templates" / "privacy.html"
    txt = _read(p)
    assert "designed for learners and families" in txt
    assert "Families & Learners" in txt or "families" in txt.lower()


def test_subscription_has_price_and_autorenew():
    """Task 4.1: Subscription screen shows price and auto-renew (3.1.2)."""
    p = REPO_ROOT / "templates" / "subscription.html"
    txt = _read(p)
    assert "per month" in txt and ("$" in txt or "subscription_monthly_usd" in txt)
    assert "automatically renews unless canceled" in txt or "Subscription automatically renews" in txt
    assert "Payment will be charged to your Apple ID" in txt or "charged to your Apple ID" in txt


def test_subscription_student_blocked_ui():
    """Task 3.1: Subscription template has student_cannot_purchase block."""
    p = REPO_ROOT / "templates" / "subscription.html"
    txt = _read(p)
    assert "student_cannot_purchase" in txt
    assert "Subscriptions can only be managed by the account manager" in txt
    assert "disabled" in txt or "aria-disabled" in txt


def test_register_filtered_not_kidsafe():
    """Task 1.1: Register benefits say 'Filtered content', not 'Kid-safe'."""
    p = REPO_ROOT / "templates" / "auth" / "register.html"
    txt = _read(p)
    assert "Kid-safe content" not in txt and "Kid-safe" not in txt
    assert "Filtered content" in txt or "filtered" in txt.lower()


def test_help_avatar_lock_not_parental_controls():
    """Task 1.1: Help says 'Avatar Lock' / account managers, not 'Parental Controls' + teachers/parents."""
    p = REPO_ROOT / "templates" / "help.html"
    txt = _read(p)
    assert "Parental Controls" not in txt or "Avatar Lock" in txt
    assert "Account managers" in txt or "account manager" in txt
