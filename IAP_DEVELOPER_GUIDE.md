# In‑App Purchases (IAP) – Developer Guide

## Overview
 - Native wrappers (iOS/Android) should provide a thin JS bridge for purchase/restore.
 - See also: `NATIVE_IAP_BRIDGE.md` for the client-side JS bridge contract (window.BeeSmartIAP) and examples.

 ## Client Integration (Web + Native)
 
 - Pages expose the subscription SKU to JS via `window.SUBSCRIPTION_SKU`.
 - If `window.BeeSmartIAP.purchase` exists and the user is signed-in, the web UI can trigger the native purchase and then call `POST /api/iap/verify/<platform>`.
 - Daily restore: if `window.BeeSmartIAP.getOwnedProducts` exists, the web UI calls it and POSTs `/api/iap/restore`.
 - For quick manual testing without a native wrapper, append `?iap_mock=1` to the homepage URL. This enables a JS mock of `window.BeeSmartIAP` (does not override a real native implementation). Use `?iap_owned=1` with it to simulate an active subscription for restore.
 ## Environment Variables
 
 - `PRODUCT_SUBSCRIPTION_FULL_ID`: SKU for monthly subscription (default `beesmart.sub.full_monthly`). Exposed to JS as `window.SUBSCRIPTION_SKU`.

## Enabling Live Verification

By default, the server runs in mock mode (accepts all) for fast local development.

Modes (env):
- `IAP_MOCK=1` → always accept (default locally)
- `IAP_VERIFICATION_MODE=live_strict` → require real store verification (recommended for production)
- `IAP_VERIFICATION_MODE=live_permissive` → accept on basic checks if store calls fail/missing (useful for bring-up)
- `IAP_LIVE_ACCEPT_BASIC=1` → allow acceptance on preflight checks even if API credentials aren’t configured

Apple required env when doing live checks:
- `APPLE_ISSUER_ID`, `APPLE_KEY_ID`, `APPLE_PRIVATE_KEY` or `APPLE_PRIVATE_KEY_PATH`
- `APPLE_APP_BUNDLE_ID`
- `APPLE_ENV` (Sandbox | Production)

Google required env when doing live checks:
- `GOOGLE_PLAY_PACKAGE_NAME`
- `GOOGLE_PLAY_SERVICE_ACCOUNT` (JSON string) or `GOOGLE_PLAY_SERVICE_ACCOUNT_PATH`

Optional dependencies for live verification:
- `pyjwt`, `cryptography`, `requests` (Apple)
- `google-auth`, `google-api-python-client` (Google)

Install (example):
```
pip install pyjwt cryptography requests google-auth google-api-python-client
```

Implementation notes:
- Live helpers live in `iap_verification.py`; the app will import and use them when not in mock mode.
- In `live_permissive` mode, the server may accept purchases that pass basic preflight even if API calls aren’t possible. Use only for bring-up.
# In‑App Purchases (IAP) — Backend Guide

This document explains how BeeSmart’s backend verifies purchases from Apple App Store and Google Play Billing, how product IDs map to user entitlements, and how clients (iOS/Android/Web) should integrate.

Status: Server endpoints and entitlement mapping are implemented with a safe mock verification mode for development. Live Apple/Google verification hooks are stubbed and can be enabled in a later step.


## Why this exists

- Keep the server authoritative over entitlements
- Enable App Store/Play Billing compliance with verifiable receipts/tokens
- Support “restore purchases” across devices


## Endpoints

All endpoints require the user to be logged in (session cookie). Responses are JSON.

- Verify purchase
  - POST `/api/iap/verify/<platform>` where `<platform>` is `apple`, `google`, or `web`
  - Body:
    - `product_id` (string, required)
    - `transaction_id` (string, optional)
    - `purchase_token` (string, optional — Google)
    - `payload` (object, optional — raw receipt/token blob or client metadata)
  - Behavior:
    - Logs a `PurchaseRecord` with `status=pending`
    - Verifies with store (mock mode passes; live validation TODO)
    - Applies entitlements idempotently
    - Updates `PurchaseRecord` to `verified` or `failed`
  - 200 Response:
    - `{ success: true, record_id, entitlements }`
  - 4xx Response:
    - `{ success: false, error, record_id? }`

- Restore purchases
  - POST `/api/iap/restore`
  - Body:
    - `product_ids` (array of strings, required): list of owned SKUs gathered by the native client
    - `platform` (string, optional: `apple`|`google`|`web`; default `apple`)
  - Behavior:
    - Applies entitlements for each product idempotently
    - Logs `PurchaseRecord` rows with `status=verified` and `{ restore: true }`
  - 200 Response:
    - `{ success: true, applied: [...], entitlements }`


## Entitlements

Entitlements are applied server-side and are idempotent (safe to call multiple times):

- `premium_member: true` for full unlock products
- `purchased_avatars: ["<avatar-id>", ...]` for avatar unlocks
- `purchased_bundles: ["<bundle-id>", ...]` with bundled avatar unlocks

The entitlements summary returned by both endpoints includes:
- `premium_member` (boolean)
- `purchased_avatars` (array)
- `purchased_bundles` (array)
- `unlocked_avatars` (array): convenience view that includes free + purchased + earned-by-points avatars


## Product → Entitlement mapping

Defined in `AjaSpellBApp.py` as `PRODUCT_MAP` and overridable via env vars. Defaults:

- Full unlock (premium)
  - `PRODUCT_FULL_UNLOCK_ID` (default: `beesmart.full_unlock`) → `premium_member=true`
  - `PRODUCT_SUBSCRIPTION_FULL_ID` (default: `beesmart.sub.full_monthly`) → `premium_member=true` (subscription)
- Individual avatars
  - `PRODUCT_AVATAR_SUPERBEE_ID` (default: `beesmart.avatar.superbee`) → unlock `superbee`
  - `PRODUCT_AVATAR_QUEEN_ID` (default: `beesmart.avatar.queen`) → unlock `queen-bee`
  - `PRODUCT_AVATAR_KNIGHT_ID` (default: `beesmart.avatar.knight`) → unlock `knight-bee`
  - `PRODUCT_AVATAR_ROCKER_ID` (default: `beesmart.avatar.rocker`) → unlock `rocker-bee`
- Bundle example
  - `PRODUCT_BUNDLE_TOP_ID` (default: `beesmart.bundle.top`) → unlocks `superbee`, `queen-bee`, `knight-bee`, `rocker-bee`

Add new SKUs by extending `PRODUCT_MAP` or setting env vars in your deployment.


## Verification modes

- Mock mode (default): `IAP_MOCK=1`
  - Skips live Apple/Google calls and treats verification as successful
  - Use for local/dev to exercise UI and entitlement flows
- Live mode: set `IAP_MOCK=0` and implement credentials
  - Apple: App Store Server API — generate a signed JWT and call transaction APIs
  - Google: Play Developer API — service account JSON + `purchases.products.get` (+ acknowledge)
  - Subscriptions: verify active status/expiry server-side (periodic checks or webhooks)

The current code stubs return errors in live mode until credentials and client code are supplied.


## Client integration notes

- iOS (StoreKit):
  1) Complete purchase with StoreKit 2
  2) Obtain transaction/receipt info
  3) POST to `/api/iap/verify/apple` with `{ product_id, transaction_id, payload: { ...store receipt... } }`
  4) On app re-install or device change, gather owned products locally then call `/api/iap/restore`
  5) Free trials and auto-renew are configured in App Store Connect (Intro Offers/Promos). The server copy is controlled by env vars but the store is the source of truth.

- Android (Play Billing):
  1) Complete purchase via BillingClient
  2) Get `purchaseToken` + `productId`
  3) POST to `/api/iap/verify/google` with `{ product_id, purchase_token, payload: { original JSONPurchase } }`
  4) On app re-install, gather owned SKUs and call `/api/iap/restore`
  5) For subscriptions, ensure your client renewals are reflected by periodically restoring or by backend reconciliation.
  6) Configure free trials/intro pricing in Play Console. Server copy uses env vars for messaging; store governs billing behavior.

- Web: Use `platform=web` only for server-managed products (Stripe/Square etc. not covered here). Web products can still map to the same entitlements.


## Data model

- `PurchaseRecord`
  - `user_id`, `platform` (apple|google|web)
  - `product_id`, `status` (pending|verified|failed|refunded)
  - `transaction_id`, `purchase_token`
  - `raw_payload` (JSON)
  - `purchased_at`, `updated_at`

Records are appended for traceability. Entitlements live on the `User` record (`premium_member`, `purchased_avatars`, `purchased_bundles`).


## Error handling

Common error responses:
- 400 `Unsupported platform` — path segment not in `apple|google|web`
- 400 `Missing product_id` — request body missing `product_id`
- 400 `apple_verification_not_configured`/`google_verification_not_configured` — live mode without creds
- 500 `db_commit_failed: <details>` — database write error

`PurchaseRecord.status` will be `failed` on store verification failure.


## Security

- Endpoints require a logged-in session; requests are scoped to `current_user`
- Server is the source of truth for entitlements — never trust only the client
- Store tokens/receipts are stored minimally under `raw_payload` for audit


## Try it locally (mock mode)

With the app running and you logged in, mock mode lets you test the flow end-to-end. Example products:
- Full unlock: `beesmart.full_unlock`
- Avatar: `beesmart.avatar.superbee`

Example request (JSON):
```json
{
  "product_id": "beesmart.full_unlock",
  "transaction_id": "test-tx-12345",
  "payload": { "dev": true }
}
```

Send to `/api/iap/verify/apple` or `/api/iap/verify/google` — both succeed in mock mode.

To restore, POST to `/api/iap/restore` with:
```json
{
  "platform": "apple",
  "product_ids": ["beesmart.full_unlock", "beesmart.avatar.superbee"]
}
```


## Roadmap to production verification

- Apple App Store Server API
  - Generate JWT with private key (ES256), include issuer and bundle identifiers
  - Query transaction history / status; handle revocations and refunds
  - Distinguish sandbox vs production endpoints

- Google Play Billing
  - Service account JSON (least privilege)
  - `purchases.products.get` (non-consumables) or `purchases.subscriptions.get`
  - Acknowledge purchases and handle refunds/revocations via webhooks or scheduled checks

- Admin/ops
  - Optional webhooks or cron jobs to reconcile revocations/refunds with entitlements
  - Audit views on `PurchaseRecord`


## Environment variables

- `IAP_MOCK` — `1` (default) enables mock verification; set to `0` for live
- `PRODUCT_FULL_UNLOCK_ID` — overrides full unlock SKU
- `PRODUCT_AVATAR_SUPERBEE_ID`, `PRODUCT_AVATAR_QUEEN_ID`, `PRODUCT_AVATAR_KNIGHT_ID`, `PRODUCT_AVATAR_ROCKER_ID`
- `PRODUCT_BUNDLE_TOP_ID` — overrides bundle SKU

Additional live verification secrets (to be added when enabling live mode):
- Apple: issuer ID, key ID, private key, bundle ID
- Google: service account JSON, package name


## Troubleshooting

- 401 Unauthorized: ensure you’re logged in; endpoints require auth
- 400 errors: check payload shape — must include `product_id`; platform must be valid
- No entitlement changes: check product ID matches `PRODUCT_MAP` or env overrides
- DB errors: confirm the `purchase_records` table exists — the app’s `create_all()` will auto-create locally


## Related files

- `AjaSpellBApp.py` — endpoints and mapping
- `models.py` — `PurchaseRecord` and `User` fields for entitlements
- `avatar_catalog.py` — IDs for catalog avatars (e.g., `superbee`, `queen-bee`, `knight-bee`, `rocker-bee`)
