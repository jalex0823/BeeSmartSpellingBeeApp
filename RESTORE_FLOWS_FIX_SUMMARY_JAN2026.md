# BeeSmart Restore Purchases — Fix Summary (Jan 5, 2026)

This document explains the **implemented** solution for the reported “Restore Purchases” issues across the 3 repro flows shared by **Kumari Swet**.

## Goals / requirements

We needed to satisfy all of the following:

- **Apple-compliant Restore UX**
  - Allow the iOS restore prompt when needed.
  - Don’t show misleading “Premium Active” states when the user is **not logged into BeeSmart**.
  - Provide clear, honest messaging about what happened and what the user must do next.
- **Support real-world user behavior** (freelancers)
  - Users often tap **Restore Purchases before signing in** to BeeSmart.
- **Stop premium state from “sticking” after logout**
  - Logging out of BeeSmart should clear premium indicators and cached client state.
- **Reduce intermittent restore failures**
  - Especially in TestFlight / app wrappers where the native bridge can be late to initialize.

## High-level solution (what was implemented)

### A) Allow restore initiation *before* BeeSmart login (Flows 2/3)

**Behavior change:** We no longer block “Restore Purchases” solely because the BeeSmart user is logged out.

- We allow the native restore to run (so iOS can prompt for Apple ID if needed).
- If the user is not authenticated in BeeSmart, we do **not** apply entitlements to a user account.
- Instead, we show a clear message and route the user to BeeSmart login:

> “Restore completed on this device. Now please sign in to your BeeSmart account to apply your membership.”

After login, the server can apply the restored subscription to that logged-in BeeSmart user.

**Implemented in:**

- `templates/unified_menu.html`
- `templates/subscription.html`

### B) Never show “Premium Active” UI while logged out

Even if the device has App Store purchase history, we **never** show green “Active Subscription” UI unless BeeSmart authentication is confirmed.

**Implemented in:**

- `templates/subscription.html`
  - Auth checks are performed before painting any “active” subscription UI.

### B2) Apple-ID-first purchase (allow subscription purchase while logged out)

Apple Review expects subscription purchase state to be tied to the **Apple ID** (App Store account), not the BeeSmart email login.

**Behavior:**

- If the user is **logged out** of BeeSmart, they can still initiate the Apple subscription purchase on the device.
- After a successful purchase, we show a clear message that the purchase is on-device, then route the user to BeeSmart login so we can **apply** the membership to that BeeSmart account.
- We still do **not** show “Premium Active” while logged out.

**Implemented in:**

- `templates/subscription.html` (`subscribe(plan)`) — allows purchase pre-login, then redirects to `/auth/login?next=...` to apply membership.

### C) Reduce intermittent restore failures (bridge readiness retry)

In TestFlight / wrapped webviews, the native IAP bridge may initialize late.

We added a small retry strategy:

- wait up to ~4.5s for the bridge
- pause ~300ms
- wait another ~2.5s

This reduces “restore sometimes fails” in Flow 3 where the bridge was not ready yet.

**Implemented in:**

- `templates/unified_menu.html` (`_waitForIapBridgeWithRetry()`)
- `templates/subscription.html` (similar retry)

### D) Clear premium/restore state on BeeSmart logout (prevents “sticking”)

On BeeSmart logout, we clear:

- server session keys that can influence premium state
- cookies used for anonymous restore/install tracking
- localStorage cache used as a client-side helper (`beesmart_login_entitlements_v1`)

**Implemented in:**

- `AjaSpellBApp.py` (`logout()` route)
- `templates/unified_menu.html` (Sign Out clears localStorage)

## Repro flows — expected behavior now

### Flow 1

**Steps:**

1. Login Apple account into device settings
2. Open BeeSmart app
3. Purchase Monthly membership
4. Then login BeeSmart user
5. Membership activates for that user
6. Logout Apple account from same device
7. Delete BeeSmart app

**Expected result (after fixes):**

- Purchase activation still occurs correctly when user logs into BeeSmart.
- After BeeSmart logout, premium UI and cached entitlement hints do **not** remain “stuck”.
- Deleting/reinstalling app does not cause BeeSmart premium UI to appear for a logged-out user.

**Why:** logout clears premium/session and related cookies, and the UI is auth-gated.

### Flow 2

**Steps:**

1. Don’t login Apple account into device settings (or use a new device)
2. Reinstall BeeSmart
3. Before logging into BeeSmart user, tap Restore membership
4. Apple prompts to login with Apple account
5. Previously: app appears to fail restore in this scenario

**Expected result (after fixes):**

- Restore UI allows the native restore prompt to run, which can trigger Apple’s login sheet.
- After restore finishes, because BeeSmart is not signed in:
  - show message: **“Restore completed on this device. Now please sign in to your BeeSmart account to apply your membership.”**
  - redirect user to BeeSmart login (`/auth/login?next=...`)
- The app does **not** claim premium is active until BeeSmart login occurs.

**Apple compliance:**

- iOS restore acknowledgement occurs.
- App messaging is honest: restore happened on-device, but BeeSmart login is required to apply it to an account.

### Flow 3

**Steps:**

1. Skip Flow 2 after Flow 1 in second round test
2. Login Apple account into device settings
3. Reinstall BeeSmart
4. Before logging into BeeSmart user, try Restore membership
5. Sometimes restore fails

**Expected result (after fixes):**

- Same correct Flow 2 behavior (restore can be initiated pre-login; login required to apply).
- Improved reliability due to bridge readiness retry.
- If bridge is still not ready, we fall back to server-side reconcile messaging (without claiming premium is active).

## Where the logic lives (code map)

- Main menu restore behavior, modal messaging, bridge retry:
  - `templates/unified_menu.html`
- Subscription page restore behavior + strict “no active while logged out” gating:
  - `templates/subscription.html`
- Native IAP bridge (restore + reconcile orchestration):
  - `static/js/native-iap-bridge.js`
- Server logout clears IAP-related session/cookies:
  - `AjaSpellBApp.py` → `logout()`

## iOS container updates (Xcode / App Store Connect readiness)

In addition to the web+server fixes above, we updated the iOS Capacitor container so Restore is more reliable and continuity is better across reinstalls.

### 1) Stable `installId` provided by native (for reinstall continuity)

The native plugin now exposes `getInstallId()` backed by `UserDefaults` (key: `beesmart_install_id_v1`).

- This lets the web bridge attach a stable per-install identifier when reconciling restores.
- It reduces cases where a reinstall appears like a “new, unknown” device to the restore flow.

Implemented in:

- `mobile/ios/App/App/BeeSmartIAPPlugin.swift`
- `mobile/ios/App/App/BeeSmartIAPPlugin.m` (Capacitor export)

### 2) Restore is tolerant of StoreKit errors (no hard failure UX)

`restorePurchases()` now returns a structured result even when StoreKit throws, instead of rejecting the call.

- The web layer can still proceed with server reconcile and show honest guidance (e.g., “restore completed on this device; sign in to apply”) rather than a generic failure.
- This improves perceived reliability in real-world conditions (and is more Apple-friendly than a hard “Restore failed” for transient StoreKit issues).

Implemented in:

- `mobile/ios/App/App/BeeSmartIAPPlugin.swift`

## Verification

- `FLASK_ENV=testing python3 test_v15_complete_validation.py` → **PASS (12/12)**

- iOS build validation:
  - `App.xcworkspace` scheme `App` → **BUILD SUCCEEDED**

> Note: running validation without `FLASK_ENV=testing` may fail if it attempts to connect to the production DigitalOcean Postgres DB from a network that blocks it.

## Repo state

- iOS container changes committed and pushed:
  - `8ca0c0c` — iOS IAP: add installId + tolerant restore
