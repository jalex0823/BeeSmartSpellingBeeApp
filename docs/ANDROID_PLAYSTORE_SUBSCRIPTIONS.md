## Android Play Store subscriptions (BeeSmart)

This repo now supports **server-verified Google Play subscriptions** without changing iOS/App Store behavior.

### 1) Play Console (non-code checklist)

- Create subscriptions in **Play Console → Monetize → Products → Subscriptions**
  - Create your monthly (and optional yearly) subscription(s).
  - Example product id used by the Android web UI in this repo: `premium_monthly`
  - Set pricing / trials.
- Ensure products are **activated/published** (in at least an internal test track).

### 2) Google API access (service account)

- In Google Cloud:
  - Create/select project
  - Enable **Google Play Android Developer API**
  - Create a **service account** and download the JSON key
- In Play Console:
  - **Setup → API access**
  - Link the same Google Cloud project
  - Grant the service account access (typically “View financial data” is NOT required for subscription verification; you need Android Publisher access).

### 3) Server configuration (Railway / prod environment variables)

Set:

- `GOOGLE_PLAY_PACKAGE_NAME`
  - Must match Android `applicationId` (e.g. `com.beesmart.spelling`)
- `GOOGLE_PLAY_SERVICE_ACCOUNT_PATH`
  - Path to the JSON key on the server filesystem
  - Alternative: `GOOGLE_PLAY_SERVICE_ACCOUNT` as a JSON string (not recommended for large keys)

Optional:

- `GOOGLE_PUBSUB_PUSH_TOKEN`
  - Shared secret used by Pub/Sub push to protect the RTDN webhook

### 4) Verification endpoint (purchase-time)

The Android native wrapper should send `productId + purchaseToken` to the backend:

- `POST /api/android/subscription/verify`
  - Request JSON:
    - `productId`
    - `purchaseToken`
  - Response JSON includes:
    - `isActive`
    - `expiryTimeMillis`
    - `autoRenewing`
    - `paymentState`
    - `cancelReason`

Notes:
- Endpoint requires the user to be signed in (subscriptions are account-based).
- Verification uses Google Play Developer API server-side. The app should never unlock premium purely locally.

### 5) RTDN (recommended) for renew/cancel/expire updates

Configure Pub/Sub push to:

- `POST /api/android/rtdn?token=<GOOGLE_PUBSUB_PUSH_TOKEN>`

This endpoint:
- decodes Pub/Sub push payload
- extracts `subscriptionId` + `purchaseToken`
- re-verifies with Google
- updates `PurchaseRecord` and (best-effort) the user’s premium flag

### 6) Android-only config layer (repo)

Android-specific values are stored in:

- `config/android.json`

This is intentionally separate so Android release work does not change iOS/App Store config.

