"""
payment_bridge.py — Server-side helper for Google Pay token verification.

Flow:
  1. Android GooglePayPlugin.java receives the Google Pay token from the payment sheet.
  2. The Capacitor JS layer (native-iap-bridge.js) POSTs the token to /api/android/subscription/verify.
  3. That Flask route calls verify_google_pay_token() from this module (optional direct-token path).

For subscriptions the existing /api/android/subscription/verify route already handles
Google Play Billing purchaseToken verification via iap_verification.py.

This module adds a complementary path for one-time Google Pay payments (e.g., future
consumable purchases or direct card payments processed by your payment gateway).
"""

import os
import json
import logging

logger = logging.getLogger(__name__)


# ── Gateway configuration ─────────────────────────────────────────────────────
# These must match the GATEWAY / GATEWAY_MERCHANT_ID constants in GooglePayPlugin.java.
# Set via environment variables — never hard-code production credentials in source.

GATEWAY = os.environ.get("GOOGLE_PAY_GATEWAY", "example")
GATEWAY_MERCHANT_ID = os.environ.get("GOOGLE_PAY_GATEWAY_MERCHANT_ID", "exampleMerchantId")


def verify_google_pay_token(payment_token: str, amount: str, currency: str = "USD") -> dict:
    """Verify / charge a Google Pay payment token with your payment gateway.

    This is a stub that must be replaced with a real gateway SDK call
    (e.g., Stripe, Braintree, Adyen) before going to production.

    Args:
        payment_token: The token string from PaymentData.toJson() → paymentMethodData
                       → tokenizationData → token
        amount:        Charge amount as a string (e.g. "3.99")
        currency:      ISO 4217 currency code (default "USD")

    Returns:
        dict with keys:
            ok (bool)       — True if charge succeeded
            transaction_id  — Gateway transaction ID (str or None)
            error           — Error message if ok is False (str or None)
    """
    if not payment_token:
        return {"ok": False, "transaction_id": None, "error": "No payment token provided"}

    # ── STUB: replace with your real gateway SDK call ─────────────────────────
    # Example for Stripe:
    #   import stripe
    #   stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
    #   charge = stripe.PaymentIntent.create(
    #       amount=int(float(amount) * 100),   # Stripe uses cents
    #       currency=currency.lower(),
    #       payment_method_data={
    #           "type": "card",
    #           "card": {"token": payment_token},
    #       },
    #       confirm=True,
    #   )
    #   return {"ok": True, "transaction_id": charge.id, "error": None}
    # ─────────────────────────────────────────────────────────────────────────

    logger.warning(
        "payment_bridge.verify_google_pay_token called with STUB gateway '%s'. "
        "Replace with real gateway integration before production.",
        GATEWAY,
    )
    return {
        "ok": False,
        "transaction_id": None,
        "error": (
            "Gateway not configured. Set GOOGLE_PAY_GATEWAY and "
            "GOOGLE_PAY_GATEWAY_MERCHANT_ID env vars and implement "
            "the real gateway call in payment_bridge.py."
        ),
    }


def extract_token_from_payment_json(payment_json_str: str) -> str | None:
    """Pull the gateway token out of the raw Google Pay PaymentData JSON.

    Args:
        payment_json_str: JSON string from PaymentData.toJson() (passed up from Java)

    Returns:
        The token string, or None if extraction fails.
    """
    try:
        obj = json.loads(payment_json_str)
        token = (
            obj
            .get("paymentMethodData", {})
            .get("tokenizationData", {})
            .get("token")
        )
        return str(token).strip() if token else None
    except Exception as exc:
        logger.error("extract_token_from_payment_json failed: %s", exc)
        return None
