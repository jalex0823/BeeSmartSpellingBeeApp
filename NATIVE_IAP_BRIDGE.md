# BeeSmart Native IAP Bridge

A minimal, platform-agnostic JS interface for native wrappers (iOS/Android) to integrate In‑App Purchases with BeeSmart’s server-side verification and entitlements.

This complements IAP_DEVELOPER_GUIDE.md (server) by specifying the client bridge.

## TL;DR
- Web renders SKU in `window.SUBSCRIPTION_SKU` and, if available, uses `window.BeeSmartIAP` to purchase and then `POST /api/iap/verify/<platform>`.
- Web also calls `/api/iap/restore` once per day if `getOwnedProducts()` exists.
- Server owns entitlements and is idempotent. Mock mode is supported in dev.

## JS Bridge Contract (window.BeeSmartIAP)

Implement this object in your native WebView (WKWebView / Android WebView) before page load or inject on DOMContentLoaded.

Required properties/methods:
- `platform: 'apple' | 'google' | 'web'`
- `async getOwnedProducts(): Promise<string[]>`
  - Returns an array of product IDs (SKUs) the user currently owns (active subscriptions and non-consumables).
- `async purchase(productId: string): Promise<PurchaseResult>`
  - Triggers native purchase flow and resolves with transaction details for server verification.

PurchaseResult shape (flexible, server maps fields):
```
{
  // Either name your fields exactly as below, or provide them in `payload`.
  transaction_id?: string;      // App Store transactionId or Play purchase order id
  transactionId?: string;       // alias
  purchase_token?: string;      // Google Play purchase token
  purchaseToken?: string;       // alias
  payload?: any;                // raw receipt / signed JWS / additional data
}
```

Tip: It’s okay to return only `payload` with the raw receipt. The server preserves it in `PurchaseRecord.raw_payload`.

## Web → Native → Server Flow

1) User clicks “Start Free Trial / Subscribe” and is already logged in
- Website checks for `window.BeeSmartIAP.purchase` and `window.SUBSCRIPTION_SKU`.
- Calls `purchase(SKU)`.
- POSTs the result to `/api/iap/verify/<platform>` with JSON body:
```
{
  "product_id": "...",
  "transaction_id": "...",
  "purchase_token": "...",
  "payload": { /* raw receipt or full object */ }
}
```
- Server verifies (mock in dev), applies entitlements idempotently, and returns `entitlements` in response.

2) Restore (once per day)
- If `getOwnedProducts()` exists, web calls it and POSTs to `/api/iap/restore` with `{ platform, product_ids }`.
- Server applies entitlements accordingly and logs a `PurchaseRecord` (status: verified via restore).

## Apple (StoreKit) mapping

- `platform = 'apple'`
- `getOwnedProducts()`
  - For subscriptions, query current entitlements via StoreKit 2 and map active product IDs.
- `purchase(SKU)`
  - Present StoreKit purchase flow.
  - Return `payload` that includes the App Store receipt container or signed JWS, and optionally `transactionId`.

Server-side (future live mode):
- Validate receipt/JWS via App Store Server API.
- Check subscription status (active/expired, grace) and respond accordingly.

## Google Play Billing mapping

- `platform = 'google'`
- `getOwnedProducts()`
  - Query purchases (subs + inapp) and map active product IDs.
- `purchase(SKU)`
  - Launch BillingClient flow.
  - Return `{ purchaseToken, payload: original Google JSON, transactionId? }`.

Server-side (future live mode):
- Use Play Developer API to verify purchase token and subscription state.

## Environment and SKU

- Subscription SKU comes from `PRODUCT_SUBSCRIPTION_FULL_ID` (default `beesmart.sub.full_monthly`).
- Exposed to pages as `window.SUBSCRIPTION_SKU`.

## Server endpoints

- `POST /api/iap/verify/<platform>` (auth required)
  - Body: `{ product_id, transaction_id?, purchase_token?, payload? }`
  - Response: `{ success, entitlements }`
- `POST /api/iap/restore` (auth required)
  - Body: `{ platform, product_ids: string[] }`
  - Response: `{ success, applied, entitlements }`

See `IAP_DEVELOPER_GUIDE.md` for product mapping and environment variables.

## Dev & Mocking

- `IAP_MOCK=1` enables server mock verification. Client can pass any shape; server will accept and apply mapping.
- Use `scripts/test_iap_endpoints.py` to sanity-check flows locally.

## Minimal Native Stubs (pseudo)

Apple (Swift, StoreKit 2):
```
window.BeeSmartIAP = {
  platform: 'apple',
  async getOwnedProducts() {
    // query current entitlements, return product IDs
    return ownedProductIds;
  },
  async purchase(productId) {
    // present StoreKit flow, await result
    return {
      transactionId: result.id,
      payload: { jws: result.signedPayload }
    };
  }
};
```

Android (Kotlin, Play Billing):
```
window.BeeSmartIAP = {
  platform: 'google',
  async getOwnedProducts() { return ownedSkus; },
  async purchase(productId) {
    // launch BillingClient flow
    return {
      purchaseToken: details.purchaseToken,
      payload: details
    };
  }
};
```

## UX Guidance

- If the user isn’t signed in, let the web page navigate to the registration screen. Verification requires an authenticated session.
- After registration, the web page will optionally prompt to start a subscription if a native bridge is present; otherwise, the daily restore covers users who purchased externally.
