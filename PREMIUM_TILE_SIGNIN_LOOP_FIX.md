# Premium Tile Sign-In Loop Fix (Jan 2026)

## Problem

Purchase premium account and unlocking of tiles was stuck in a **sign-in loop** for authenticated (but non-premium) users across account types (Teacher, Parent, Student):

1. User is **already signed in** (parent/teacher/student, non-premium).
2. User taps a premium tile (Extract Image, Saved Lists, Speed Round) → sees "Premium Required".
3. Modal showed **"Sign In to Unlock"** with only a **Sign In** button.
4. User taps Sign In → goes to `/auth/login` → already logged in so redirects back to app.
5. User taps premium tile again → same modal → Sign In again → **loop**.

## Root Cause

- **TILE_UNLOCK_FIX.md** (Nov 2025) fixed `window.IS_AUTH` so tiles unlock correctly for *authenticated* users for *auth-gated* features.
- For **premium-gated** tiles, when `window.IS_AUTH` is true but `window.IS_PREMIUM` is false, the code correctly called `showLockedFeature('BeeSmart Premium')`.
- **Bug:** `showLockedFeature()` always showed the same modal: "Sign in to unlock" and a **Sign In** button, even when the user was already signed in. So authenticated non-premium users were sent to login → redirect back → repeat.

## Fix (Applied Globally for All Account Types)

### 1. `templates/unified_menu.html`

- **showLockedFeature(featureName, options)**  
  - Added optional second argument `options.requirePremium`.
  - When **not authenticated:** show "Sign in to unlock" and button to `/auth/login?next=/subscription`.
  - When **authenticated but not premium** (`options.requirePremium === true`): show "Subscribe to BeeSmart Premium to unlock this feature and more!" and button to **/subscription** (no sign-in loop).

- **Tile click handler**  
  - When `requiresPremium && !window.IS_PREMIUM`, call  
    `showLockedFeature('BeeSmart Premium', { requirePremium: true })`  
  so the modal shows **Subscribe to Premium** → `/subscription` instead of Sign In.

### 2. `AjaSpellBApp.py` – `/minimal` route

- **Before:** Rendered `unified_menu.html` with only `timestamp` → missing `is_premium`, `subscription_product_id`, etc. → tiles could show wrong lock state for any account type.
- **After:** Pass same auth/subscription context as `home_root_direct()`: `registration_billing_mode`, `subscription_product_id`, `is_premium`, `avatar_product_ids`.  
  Ensures **Teacher, Parent, Student** all get correct `window.IS_AUTH` and `window.IS_PREMIUM` when hitting `/minimal`.

## Verification (All 3 Account Types)

- **Student (non-premium):** Tap premium tile → modal "Subscribe to Premium" → /subscription → (students are redirected to app_home by design; no loop).
- **Parent/Teacher (non-premium):** Tap premium tile → modal "Subscribe to Premium" → /subscription → can complete purchase; no sign-in loop.
- **Guest:** Tap premium tile → modal "Sign In to Unlock" → /auth/login?next=/subscription → correct.

## Premium Apple-to-App Pipeline (Same as Avatar Purchase)

To ensure premium applies immediately after purchase (like avatar purchase), the subscription page now calls **`/api/iap/verify/<platform>`** with the purchase result payload right after a successful StoreKit purchase:

1. **Subscription page:** After `BeeSmartIAP.purchase(productId)` returns (not cancelled, not pending), the page:
   - Builds a verify body: `product_id`, `transaction_id`, `purchase_token`, `payload` (same shape as avatar picker).
   - POSTs to `/api/iap/verify/apple` (or `android` from `BeeSmartIAP.platform`).
   - Server runs `_apply_entitlement(user, product_id)` → sets `user.premium_member = True` and commits (same as IAP_ENTITLEMENTS_FIX for avatars).
2. **Then** the existing reconcile + restore flow runs as backup.

This matches the avatar purchase pipeline: **verify first** (apply entitlement + commit), **then reconcile** (refresh owned list). Without the verify call, premium relied only on reconcile (getOwnedProducts + restore); if getOwnedProducts was delayed, premium could fail to apply until Restore was tapped.

**Files:** `templates/subscription.html` — after purchase success, added `/api/iap/verify/<platform>` call before reconcile.

---

## Smoke Test: Purchase Process (App → Apple Store)

Use this checklist when running smoke on the purchase flow (aligned with existing .md runbooks):

1. **From app (TestFlight/sandbox)**  
   - [ ] Log in as **Parent** or **Teacher** (non-premium).  
   - [ ] Tap a premium tile (e.g. Extract Image, Saved Lists, Speed Round).  
   - [ ] **Expected:** Modal "Subscribe to Premium" with button to subscription page (no "Sign In" loop).  
   - [ ] Tap "Subscribe to Premium" → land on `/subscription`.  
   - [ ] Complete sandbox subscription purchase.  
   - [ ] **Expected:** Premium unlocks; tiles no longer show "Premium Required" for that user.

2. **Restore / sign-in**  
   - [ ] Follow **RESTORE_FLOWS_FIX_SUMMARY_JAN2026.md** and **store/NATIVE_SANDBOX_RESTORE_RUNBOOK.md**.  
   - [ ] Restore Purchases works without forcing a sign-in loop.  
   - [ ] After BeeSmart login, premium state applies correctly.

3. **Student**  
   - [ ] Log in as **Student**.  
   - [ ] Tap premium tile → modal "Subscribe to Premium" → go to `/subscription`.  
   - [ ] **Expected:** Redirect to app home (students cannot purchase; no loop).

4. **Guest**  
   - [ ] Not logged in; tap premium tile → "Sign In to Unlock" → /auth/login?next=/subscription.  
   - [ ] After login, can navigate to subscription as expected.

## Related Docs

- **TILE_UNLOCK_FIX.md** – `window.IS_AUTH` / tile unlock for authenticated users.  
- **RESTORE_FLOWS_FIX_SUMMARY_JAN2026.md** – Restore purchases and login flow.  
- **store/NATIVE_SANDBOX_RESTORE_RUNBOOK.md** – End-to-end restore in native wrapper.  
- **TESTFLIGHT_SANDBOX_TESTING_CHECKLIST.md** – IAP and purchase flow tests.

## Files Changed

- `templates/unified_menu.html` – `showLockedFeature(..., options)` and tile handler `requirePremium: true`.  
- `AjaSpellBApp.py` – `/minimal` route passes full auth/subscription context.
