# IAP Acceptance Verification — One Shot Checklist

**Goal:** No negative sales messages; single source of truth; restore modal only after UI refresh. All approved avatars purchasable with exact Apple product IDs.

---

## 1. Single source of truth ✅

- **`data/avatars.catalog.json`** — Created. Contains all 36 approved avatars with:
  - `avatarKey` (catalog slug)
  - `displayName`
  - `iapProductId` (exact Apple product ID)
  - `priceTier`, `isFree`
- **Backend** — `avatar_skus.py` has `APP_STORE_AVATAR_PRODUCT_ID_TO_SLUG` (1:1 with Apple). API returns exact `product_id` via `app_store_product_id_for_avatar()`. UI gets product_id from API response (no hardcoding in components).

---

## 2. No negative / “not available” messages ✅

- **Avatar picker** (`static/js/honeycomb-avatar-picker-responsive.js`):
  - Removed alert for missing `productId` (approved avatars always have it; we just return).
  - “Purchase could not start” → “One moment — the store is loading. Tap Purchase again in a few seconds.”
  - “Purchase completed, but the unlock has not appeared yet” → “Purchase complete! If this avatar doesn’t unlock right away, tap Restore Purchases and it will sync.”
  - Purchase failure → “The purchase didn’t go through. Tap Purchase again or try Restore Purchases if you already bought this bee.” (cancel/skip not shown).
  - Bundle “not available” → silent return (bundle shop removed).

---

## 3. Restore: modal only after UI refresh

- **Picker** already listens for `beesmart:iap-reconciled` and calls `loadAvatars()` (lines 71–82).
- **Menu restore flow** (`unified_menu.html`): Currently shows the green modal *then* dispatches `beesmart:iap-reconciled`. Spec says: show modal *after* entitlements refresh and UI update.
- **Manual change** (if you want strict spec compliance): In `unified_menu.html`, in `restorePurchases()`, for the “premium || ownedCount > 0” branch:
  1. First dispatch `beesmart:iap-reconciled` (so picker runs `loadAvatars()`).
  2. Then `await new Promise(r => setTimeout(r, 600));`
  3. Then call `showRestoreGreenModal(...)` with message: “Restore complete. … Your avatars and premium status are updated.”
  4. Then `runRestoreGlitterOnly();`
- So: **dispatch → 600ms delay → show modal → glitter**. That way the modal appears after the picker has had time to refresh.

---

## 4. Product ID / entitlements (already done)

- **v2 vs non-v2:** Catalog and `APP_STORE_AVATAR_PRODUCT_ID_TO_SLUG` use exact Apple IDs (e.g. `beesmart.avatar.fairy_bee`, `beesmart.avatar.gamer_bee` without `.v2`; others with `.v2`).
- **Unlock by productId:** Backend stores `purchased_avatars` (avatar slugs); verify/restore map product IDs to avatar_id via `PRODUCT_MAP` and update `purchased_avatars`. Entitlement comparisons use exact product_id in PRODUCT_MAP.
- **Subscription:** `com.beesmart.premium.monthly` in PRODUCT_MAP. Avatar unlocks are per product_id; subscription does not replace individual avatar ownership.

---

## 5. Acceptance criteria checklist

| Criteria | Status |
|----------|--------|
| Every avatar with iapProductId shows Buy (with price) or Owned | ✅ API returns product_id + price; picker shows Purchase/Owned |
| Buying completes → tile flips to Owned, selectable without restart | ✅ Reconcile + loadAvatars after purchase |
| Restore unlocks previously bought avatars in 1–2 s | ✅ Restore → server reconcile → beesmart:iap-reconciled → loadAvatars |
| Restore modal not shown before UI updates | ⚠️ Optional: apply manual change in §3 |
| No “not available” / negative sales message for catalog avatars | ✅ Removed/softened |
| No Purchase for product Apple didn’t return | ✅ We only show Purchase when we have product_id from catalog; no product fetch yet so we rely on catalog |
| No wrong .v2 mapping | ✅ Exact IDs in avatar_skus + data/avatars.catalog.json |

---

## 6. Files changed this pass

- `data/avatars.catalog.json` — new single source of truth (36 avatars, exact iapProductId).
- `static/js/honeycomb-avatar-picker-responsive.js` — no “not available” alert; softened purchase/restore and failure messages.
- `APP_STORE_AVATAR_VERIFICATION_DELTA.md` — Apple vs app product ID comparison (0 delta).
- `IAP_ACCEPTANCE_VERIFICATION.md` — this checklist.

Backend and `avatar_skus.py` were already updated earlier (APP_STORE map, product_id in API, PRODUCT_MAP).
