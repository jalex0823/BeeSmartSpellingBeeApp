# Native Sandbox Restore Validation Runbook (iOS + Android)

This runbook validates the **real** “Restore Purchases” flow in the native wrapper (StoreKit / Play Billing), end-to-end:

Native Store → `BeeSmartIAP.getOwnedProducts()` → `POST /api/iap/restore` → server applies entitlements → UI reflects restored state.

> Note: On the web (Safari/Chrome) there is no native purchase history API. Restore testing must be done in a TestFlight/internal build (iOS) or internal testing track build (Android).

---

## What “success” looks like ✅

- Tapping **Restore Purchases** shows a success confirmation.
- Premium content is unlocked if a subscription is owned.
- Previously purchased avatars/bundles appear **unlocked** in the avatar picker.
- Server returns HTTP 200 from `/api/iap/restore` with:
  - `success: true`
  - `restore_id` (short id for traceability)
  - `entitlements` summary including restored items

---

## Pre-reqs

### Common

- You have a BeeSmart account (email/username) and can log in.
- The build is pointed at the correct backend (staging/prod) and can authenticate.
- The device has network access.

### iOS (TestFlight)

- Sandbox tester Apple ID configured (Settings → App Store → Sandbox Account) as required for your test setup.
- TestFlight build installed.

### Android (Internal testing)

- Test account opted into the internal testing track.
- Google Play account on device is the tester account.

Additional Play Console setup (common gotchas):

- **License testing:** In Google Play Console → Settings → Developer account → **License testing**, add the tester Gmail(s).
- **Test products must be active:** Ensure your in-app products/subscriptions are **Active** (or otherwise eligible for testing in your console state).
- **Install must come from Play:** For Play Billing purchase history to resolve correctly, install the build via the **Play Store internal testing track** (not via local APK sideload).
- **Correct account:** The device’s Play Store must be signed into the **same Google account** that is (a) a license tester and (b) used to purchase.

---

## Test matrix (recommended)

Run all that applies:

1. **Subscription restore** (monthly premium)
2. **Avatar SKU restore** (buy one paid avatar)
3. **Bundle restore** (buy one bundle pack)
4. **Mixed restore** (subscription + bundle + avatar)

---

## Steps (end-to-end)

### A) Establish ownership (one-time)

1. Install the app build.
2. Log in to your BeeSmart account.
3. Purchase **one** item in each category you want to validate (subscription/avatar/bundle).
4. Confirm the item is unlocked immediately after purchase.

### B) Validate restore after reinstall

1. Delete the app from the device.
2. Reinstall the same build from TestFlight / Internal testing.
3. Log in to the same BeeSmart account.
4. From the home/menu screen, tap **Restore Purchases**.

Expected:

- A success message appears.
- If a `restore_id` is shown, copy it (helps with log lookup).

### C) Validate UI effects

1. Open the avatar picker.
2. Confirm previously owned avatars are unlocked.
3. Confirm bundles are marked owned (or the avatars inside are unlocked).
4. Confirm premium-only features reflect subscription ownership.

---

## Troubleshooting 🔧

### “Restore Purchases is available in the BeeSmart mobile app build.”

- You’re not running inside the native wrapper, or the bridge is not injected.
- Confirm you’re in a TestFlight/internal build (not mobile Safari).

### Restore shows “No previous purchases were found” but you *did* buy

- Confirm you’re using the same Apple ID / Google account used to purchase.
- Confirm the purchase completed (not pending).
- Confirm the native bridge returns owned products.

### Restore fails with an error message

- Grab the `restore_id` if present.
- Check backend logs for `IAP restore start restore_id=...`.

### Entitlements don’t show up in UI after a successful restore

- Force-refresh the avatar picker (navigate away and back).
- Check `/api/avatars` and `/api/bundles` responses for `is_owned` changes.
- If needed, log out/in and retry restore.

---

## Developer notes (implementation expectations)

- Client calls:
  - `BeeSmartIAP.getOwnedProducts()` → array of SKUs (strings) or objects.
  - Client normalizes/filters/dedupes before calling server.
- Server endpoint:
  - `POST /api/iap/restore` with `{ platform, product_ids }`
  - Server normalizes product ids (strings or objects), applies entitlements idempotently, logs `restore_id`.

---

## What to capture for a validation record

- Build version / commit
- Platform (iOS/Android) + device model/OS version
- Account used (username only; no password)
- Purchases owned (SKUs)
- Restore result message + `restore_id`
- Screenshot/video of:
  - Restore confirmation
  - Avatar picker showing unlocked items
  - Premium feature unlocked
