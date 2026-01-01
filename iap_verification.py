"""
Live IAP verification helpers for Apple App Store Server API and Google Play Developer API.

This module is optional: if dependencies or environment variables are missing, helpers return a clear
error that upstream code can convert into a user-facing message or a 4xx.

Environment (Apple):
- APPLE_ISSUER_ID
- APPLE_KEY_ID
- APPLE_PRIVATE_KEY (PEM) or APPLE_PRIVATE_KEY_PATH
- APPLE_APP_BUNDLE_ID
- APPLE_ENV: Sandbox | Production (defaults to Production)

Environment (Google):
- GOOGLE_PLAY_PACKAGE_NAME
- GOOGLE_PLAY_SERVICE_ACCOUNT (JSON string) or GOOGLE_PLAY_SERVICE_ACCOUNT_PATH

Optional:
- IAP_VERIFICATION_MODE: mock | live_strict | live_permissive
- IAP_LIVE_ACCEPT_BASIC=1: accept basic checks without calling stores (dev convenience)

Dependencies (optional, install when enabling live verification):
- requests
- pyjwt
- cryptography
- google-auth
- google-api-python-client
"""
from __future__ import annotations

from typing import Tuple, Dict, Any
import os
import json
import base64


def _load_private_key() -> str | None:
    # Preferred for platforms that can't save multiline secrets reliably:
    # a single-line base64 encoding of the full PEM contents.
    b64 = os.getenv('APPLE_PRIVATE_KEY_B64')
    if b64:
        try:
            # Support common DO/CI paste variants (whitespace/newlines).
            cleaned = ''.join(b64.split())
            decoded = base64.b64decode(cleaned).decode('utf-8')
            return decoded
        except Exception:
            return None

    key = os.getenv('APPLE_PRIVATE_KEY')
    if key:
        return key
    path = os.getenv('APPLE_PRIVATE_KEY_PATH')
    if path and os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None
    return None


def verify_apple_purchase(data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """Verify Apple purchase using App Store Server API (Get Transaction Info).
    Expects: data = { product_id, transaction_id?, payload? }
    Returns (ok, status, details)
    """
    product_id = (data or {}).get('product_id')
    payload = (data or {}).get('payload') or {}
    transaction_id = (data or {}).get('transaction_id') or payload.get('transactionId')

    if not product_id:
        return False, 'apple_missing_product_id', {}
    if not transaction_id and not payload:
        return False, 'apple_missing_transaction', {}

    issuer_id = os.getenv('APPLE_ISSUER_ID')
    key_id = os.getenv('APPLE_KEY_ID')
    bundle_id = os.getenv('APPLE_APP_BUNDLE_ID')
    private_key_pem = _load_private_key()
    if not (issuer_id and key_id and bundle_id and private_key_pem):
        return False, 'apple_config_missing', {'need': ['APPLE_ISSUER_ID','APPLE_KEY_ID','APPLE_APP_BUNDLE_ID','APPLE_PRIVATE_KEY or APPLE_PRIVATE_KEY_B64 or APPLE_PRIVATE_KEY_PATH']}

    # Build developer token (JWT ES256)
    try:
        import jwt  # pyjwt
        from datetime import datetime, timedelta, timezone
        headers = { 'alg': 'ES256', 'kid': key_id, 'typ': 'JWT' }
        now = datetime.now(timezone.utc)
        claims = {
            'iss': issuer_id,
            'iat': int(now.timestamp()),
            'exp': int((now + timedelta(minutes=30)).timestamp()),
            'aud': 'appstoreconnect-v1',
            'bid': bundle_id,
        }
        developer_token = jwt.encode(claims, private_key_pem, algorithm='ES256', headers=headers)
    except Exception as e:
        return False, f'apple_token_build_failed: {e}', {}

    # Call Get Transaction Info: GET /inApps/v1/transactions/{transactionId}
    try:
        import requests
        base = 'https://api.storekit.itunes.apple.com'  # Production; use sandbox base if APPLE_ENV=Sandbox
        if (os.getenv('APPLE_ENV') or '').lower().startswith('sandbox'):
            base = 'https://api.storekit-sandbox.itunes.apple.com'
        url = f"{base}/inApps/v1/transactions/{transaction_id}"
        r = requests.get(url, headers={'Authorization': f'Bearer {developer_token}'}, timeout=10)
        if r.status_code == 200:
            info = r.json()
            # Minimal sanity: check bundle id and product id match
            # The field names may vary; we attempt best-effort mapping
            ok_bundle = True
            try:
                ok_bundle = (info.get('bundleId') == bundle_id) or (info.get('appAppleId') is not None)
            except Exception:
                ok_bundle = True
            ok_product = True
            try:
                ok_product = (info.get('productId') == product_id) or (product_id in json.dumps(info))
            except Exception:
                ok_product = True
            if ok_bundle and ok_product:
                return True, 'apple_verified', {'transaction': info}
            return False, 'apple_mismatch', {'transaction': info}
        return False, f'apple_http_{r.status_code}', {'body': _safe_json(r)}
    except Exception as e:
        return False, f'apple_request_failed: {e}', {}


def verify_google_purchase(data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """Verify Google purchase using Google Play Developer API.
    Expects: data = { product_id, purchase_token, payload? }
    Returns (ok, status, details)
    """
    product_id = (data or {}).get('product_id')
    purchase_token = (data or {}).get('purchase_token') or ((data or {}).get('payload') or {}).get('purchaseToken')
    if not product_id:
        return False, 'google_missing_product_id', {}
    if not purchase_token:
        return False, 'google_missing_purchase_token', {}

    package_name = os.getenv('GOOGLE_PLAY_PACKAGE_NAME')
    svc_json = os.getenv('GOOGLE_PLAY_SERVICE_ACCOUNT')
    svc_path = os.getenv('GOOGLE_PLAY_SERVICE_ACCOUNT_PATH')
    if not package_name:
        return False, 'google_config_missing', {'need': ['GOOGLE_PLAY_PACKAGE_NAME','GOOGLE_PLAY_SERVICE_ACCOUNT or PATH']}

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        SCOPES = ['https://www.googleapis.com/auth/androidpublisher']
        if svc_json:
            info = json.loads(svc_json)
            creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
        elif svc_path:
            creds = service_account.Credentials.from_service_account_file(svc_path, scopes=SCOPES)
        else:
            return False, 'google_service_account_missing', {}
        service = build('androidpublisher', 'v3', credentials=creds, cache_discovery=False)

        # Heuristic: subscriptions vs inapp
        is_subscription = bool(os.getenv('PRODUCT_SUBSCRIPTION_FULL_ID') == product_id or _is_product_subscription_like(product_id))
        if is_subscription:
            # purchases.subscriptions.get
            req = service.purchases().subscriptions().get(packageName=package_name, subscriptionId=product_id, token=purchase_token)
            resp = req.execute()
            # Basic validity check
            acknowledged = resp.get('acknowledgementState') == 1 or resp.get('cancelReason') in (None, 0)
            return (True, 'google_verified', {'subscription': resp}) if acknowledged else (False, 'google_not_acknowledged', {'subscription': resp})
        else:
            # purchases.products.get
            req = service.purchases().products().get(packageName=package_name, productId=product_id, token=purchase_token)
            resp = req.execute()
            purchase_state = resp.get('purchaseState')  # 0 purchased
            consumed = resp.get('consumptionState')
            if purchase_state == 0:
                return True, 'google_verified', {'product': resp}
            return False, 'google_purchase_not_complete', {'product': resp}
    except Exception as e:
        return False, f'google_request_failed: {e}', {}


def _is_product_subscription_like(sku: str | None) -> bool:
    if not sku:
        return False
    s = sku.lower()
    return any(k in s for k in ('sub', 'monthly', 'yearly', 'subscription'))


def _safe_json(r) -> Any:
    try:
        return r.json()
    except Exception:
        try:
            return {'text': r.text[:500]}
        except Exception:
            return {'raw': 'unavailable'}
