# Android IAP & Subscriptions – Verification for Testing

This document verifies that IAP and subscription options for Android are set up and ready for testing.

---

## ✅ What’s Already Configured

### 1. Native Android Plugin (`BeeSmartIAPPlugin.java`)
- **Location:** `mobile/android/app/src/main/java/com/beesmart/spellingbee/BeeSmartIAPPlugin.java`
- **Plugin name:** `BeeSmartIAP` (registered in `MainActivity.java`)
- **Methods:**
  - `purchase(productId)` – Launches Google Play billing flow (SUBS first, fallback to INAPP for avatars)
  - `restorePurchases()` – Returns success; reconciliation uses `getOwnedProducts()`
  - `getOwnedProducts()` – Queries Play Billing for subscriptions + in-app purchases
  - `getProductDetails(productId)` – Fetches price/info from Play Store
  - `getInstallId()` – Stable device ID for restore/reinstall continuity
- **Billing library:** `com.android.billingclient:billing:6.1.0` (Google Play Billing v5+)

### 2. Config (`config/android.json`)
```json
{
  "packageName": "com.beesmart.spellingbee",
  "subscriptionProductIds": { "monthly": "premium_monthly" },
  "featureFlags": { "useGooglePlayBilling": true }
}
```

### 3. Product IDs (`store/GOOGLE_PLAY_PRODUCT_IDS.md`)
- **Subscription:** `premium_monthly` (BeeSmart Premium Monthly)
- **Avatars:** 36 one-time products, format `beesmart.avatar.<slug>.v3` (e.g. `beesmart.avatar.firefighter_bee.v3`)

### 4. Web Layer (`native-iap-bridge.js`)
- Platform detection: `Capacitor.getPlatform() === 'android'` → `platform: 'google'`
- Subscription purchases: Server verification via `/api/android/subscription/verify` with `purchaseToken`
- Avatar purchases: Verification via `/api/iap/verify` with platform `google`
- Restore flow: `restorePurchases()` → `reconcileFromNative()` → `getOwnedProducts()` → server verify → apply entitlements

### 5. Backend (Flask)
- **Subscription verify:** `/api/android/subscription/verify` (POST: `productId`, `purchaseToken`)
- **General IAP verify:** `/api/iap/verify` – routes to `verify_google_purchase()` when platform is `google`
- **Avatar API:** `/api/avatars?platform=android` returns Google Play product IDs for locked avatars

### 6. UI
- **Subscription page:** Platform-aware copy (Google Play vs App Store), Restore Purchases, purchase flow
- **Avatar picker:** Uses product IDs from API; purchase flow calls `BeeSmartIAP.purchase(productId)`
- **Unified menu:** Restore Purchases button, platform-aware messaging

---

## ⚠️ Required for Testing to Work

### Google Play Console (you must do)

1. **Create products**
   - **Subscription:** Monetize → Products → Subscriptions → Create `premium_monthly`
   - **Avatars:** Monetize → Products → In-app products → Create each `beesmart.avatar.<slug>.v3` (see `GOOGLE_PLAY_PRODUCT_IDS.md`)

2. **License testing**
   - Settings → Developer account → **License testing**
   - Add tester Gmail addresses

3. **Internal testing track**
   - Release → Testing → Internal testing
   - Install must come from Play Store (not sideloaded APK) for billing to work

4. **App must be published**
   - At least to Internal testing
   - Products must be **Active**

### Backend (server/deployment)

Set these environment variables for **server-side verification**:

| Variable | Purpose |
|----------|---------|
| `GOOGLE_PLAY_PACKAGE_NAME` | `com.beesmart.spellingbee` |
| `GOOGLE_PLAY_SERVICE_ACCOUNT` | JSON string of service account credentials |
| **OR** `GOOGLE_PLAY_SERVICE_ACCOUNT_PATH` | Path to service account JSON file |

**Service account setup:**
1. Google Cloud Console → APIs & Services → Credentials → Create Service Account
2. Grant role: **Google Play Android Developer**
3. Create JSON key, download
4. Put JSON in env var or file path

Without these, subscriptions will **not** be verified server-side and premium may not unlock correctly.

---

## Testing Checklist

### Before testing
- [ ] Products created in Google Play Console (subscription + avatars you plan to test)
- [ ] Products **Active**
- [ ] License testers added
- [ ] App on Internal testing track
- [ ] Backend env vars set (`GOOGLE_PLAY_PACKAGE_NAME`, `GOOGLE_PLAY_SERVICE_ACCOUNT` or path)
- [ ] Device signed into same Google account as license tester

### Subscription flow
1. [ ] Open app → Subscription page
2. [ ] Tap Subscribe → Google Play purchase sheet appears
3. [ ] Complete purchase (use test card if prompted)
4. [ ] Premium unlocks (Speed Round, etc.)
5. [ ] Tap Restore Purchases → Success, premium still active

### Avatar flow
1. [ ] Open Avatar picker
2. [ ] Tap locked avatar → Purchase option
3. [ ] Complete purchase → Avatar unlocks
4. [ ] Restore Purchases → Avatar still unlocked after reinstall

### Restore after reinstall
1. [ ] Delete app
2. [ ] Reinstall from Play Store (Internal testing)
3. [ ] Log in
4. [ ] Tap Restore Purchases → Previous purchases restored

---

## Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Native plugin | ✅ Ready | `BeeSmartIAPPlugin` with purchase, restore, getOwnedProducts |
| Config | ✅ Ready | `premium_monthly`, `useGooglePlayBilling: true` |
| Product IDs | ✅ Documented | `GOOGLE_PLAY_PRODUCT_IDS.md` |
| Web bridge | ✅ Ready | Platform detection, server verification |
| Backend verify | ✅ Ready | `iap_verification.verify_google_purchase()` |
| Google Play products | ⚠️ You create | In Play Console |
| Backend env vars | ⚠️ You set | `GOOGLE_PLAY_PACKAGE_NAME`, service account |
| Test install source | ⚠️ Required | Install from Play Store Internal testing |

**Bottom line:** The app code is ready for Android IAP testing. Success depends on creating products in Google Play Console, configuring the service account for verification, and installing from the Internal testing track.
