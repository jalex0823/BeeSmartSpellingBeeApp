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
    """Charge a Google Pay payment token via Stripe (or swap in another gateway).

    TODO checklist before going live:
      1. pip install stripe  (add stripe to requirements.txt)
      2. Set STRIPE_SECRET_KEY=sk_live_... on Railway / your host
      3. Set GOOGLE_PAY_GATEWAY=stripe
      4. Set GOOGLE_PAY_GATEWAY_MERCHANT_ID=acct_XXXX  (your Stripe account ID)
      5. In GooglePayPlugin.java replace GATEWAY/GATEWAY_MERCHANT_ID with real values
      6. Switch WALLET_ENVIRONMENT to ENVIRONMENT_PRODUCTION in GooglePayPlugin.java
      7. Get your Google Pay Business Profile approved at pay.google.com/business/console

    Args:
        payment_token: Token from Google Pay PaymentData → paymentMethodData
                       → tokenizationData → token
        amount:        Charge amount string (e.g. "3.99")
        currency:      ISO 4217 code (default "USD")

    Returns:
        dict: { ok: bool, transaction_id: str|None, error: str|None }
    """
    if not payment_token:
        return {"ok": False, "transaction_id": None, "error": "No payment token provided"}

    stripe_secret = os.environ.get("STRIPE_SECRET_KEY", "").strip()

    # ── Stripe (active when STRIPE_SECRET_KEY is set) ─────────────────────────
    if GATEWAY == "stripe" and stripe_secret:
        try:
            import stripe as _stripe  # pip install stripe
            _stripe.api_key = stripe_secret

            # Convert amount string to integer cents (Stripe requires cents)
            amount_cents = int(round(float(amount) * 100))

            # Create a PaymentMethod from the Google Pay token, then confirm a PaymentIntent.
            # Stripe treats Google Pay tokens as card tokens directly.
            payment_method = _stripe.PaymentMethod.create(
                type="card",
                card={"token": payment_token},
            )

            intent = _stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency.lower(),
                payment_method=payment_method.id,
                confirm=True,
                automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
            )

            if intent.status in ("succeeded", "requires_capture"):
                logger.info("Stripe PaymentIntent succeeded id=%s", intent.id)
                return {"ok": True, "transaction_id": intent.id, "error": None}
            else:
                return {
                    "ok": False,
                    "transaction_id": intent.id,
                    "error": f"PaymentIntent status: {intent.status}",
                }
        except Exception as exc:
            logger.error("Stripe charge failed: %s", exc)
            return {"ok": False, "transaction_id": None, "error": str(exc)}

    # ── Braintree (active when GATEWAY=braintree and BT env vars are set) ─────
    if GATEWAY == "braintree":
        bt_merchant = os.environ.get("BRAINTREE_MERCHANT_ID", "").strip()
        bt_public   = os.environ.get("BRAINTREE_PUBLIC_KEY", "").strip()
        bt_private  = os.environ.get("BRAINTREE_PRIVATE_KEY", "").strip()
        if bt_merchant and bt_public and bt_private:
            try:
                import braintree as _bt  # pip install braintree
                gateway = _bt.BraintreeGateway(
                    _bt.Configuration(
                        environment=_bt.Environment.Production,
                        merchant_id=bt_merchant,
                        public_key=bt_public,
                        private_key=bt_private,
                    )
                )
                result = gateway.transaction.sale({
                    "amount": amount,
                    "payment_method_nonce": payment_token,
                    "options": {"submit_for_settlement": True},
                })
                if result.is_success:
                    logger.info("Braintree transaction succeeded id=%s", result.transaction.id)
                    return {"ok": True, "transaction_id": result.transaction.id, "error": None}
                else:
                    return {
                        "ok": False,
                        "transaction_id": None,
                        "error": str(result.message),
                    }
            except Exception as exc:
                logger.error("Braintree charge failed: %s", exc)
                return {"ok": False, "transaction_id": None, "error": str(exc)}

    # ── Fallback stub (no gateway configured yet) ─────────────────────────────
    logger.warning(
        "payment_bridge: gateway not configured (GATEWAY=%s). "
        "Set STRIPE_SECRET_KEY + GOOGLE_PAY_GATEWAY=stripe to enable real charges.",
        GATEWAY,
    )
    return {
        "ok": False,
        "transaction_id": None,
        "error": (
            "Payment gateway not configured. "
            "Set STRIPE_SECRET_KEY and GOOGLE_PAY_GATEWAY=stripe on your server."
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
