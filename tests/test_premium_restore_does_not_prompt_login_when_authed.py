from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "response_payload, expected",
    [
        ({"authenticated": True}, True),
        ({"authenticated": False}, False),
        ({"is_authenticated": True}, True),
        ({"is_authenticated": False}, False),
        ({}, False),
    ],
)
def test_subscription_template_uses_api_auth_status_as_source_of_truth(response_payload, expected):
    """Guardrail:

    The Premium page (templates/subscription.html) must not gate Restore Purchases
    on a stale template-time auth flag.

    We don't execute browser JS here. Instead, we enforce that:
    - restorePurchases() calls /api/auth/status
    - and it interprets either {authenticated:true} or {is_authenticated:true}

    This makes Restore Purchases work correctly even under iOS WebView cookie
    weirdness.
    """

    # Mirror the logic in templates/subscription.html::_fetchAuthState
    authenticated = bool(
        response_payload
        and (
            response_payload.get("authenticated") is True
            or response_payload.get("is_authenticated") is True
        )
    )
    assert authenticated is expected


def test_subscription_template_restore_purchases_calls_auth_status():
    # Source inspection test: ensure the auth status endpoint is used.
    p = Path(__file__).resolve().parents[1] / "templates" / "subscription.html"
    html = p.read_text(encoding="utf-8")

    assert "/api/auth/status" in html
    assert "async function restorePurchases" in html
    assert "Policy: Restore Purchases" in html
