# Avatar IAP Implementation Summary

This document summarizes how avatar purchases and entitlements are implemented so that **all avatars are purchasable without issues or false positives**.

## 1. Single source of truth: `data/avatars.catalog.json`

- **File:** `data/avatars.catalog.json`
- **Fields per avatar:** `avatarKey`, `displayName`, `iapProductId`, `priceTier` (optional), `isFree`
- **Product IDs** match App Store Connect exactly (including `.v2` where applicable; e.g. `beesmart.avatar.fairy_bee` and `beesmart.avatar.gamer_bee` have no `.v2`).
- **Backend:** `avatar_skus.py` loads this file at import and builds `APP_STORE_AVATAR_PRODUCT_ID_TO_SLUG` from it. The `/api/avatars` response uses `app_store_product_id_for_avatar(avatar_id)` so every avatar tile gets the correct `product_id`.
- **UI:** Does **not** hardcode product IDs. The avatar picker uses `avatar.product_id` from the API only; no fallback construction (e.g. no `beesmart.avatar.<slug>.v2`) to avoid mismatches.

## 2. Entitlements and unlock rule

- **Stored by product ID → avatar slug:** Restore/purchase returns product IDs (e.g. `beesmart.avatar.franken_bee.v2`). Backend maps via `PRODUCT_MAP` to `avatar_id` (e.g. `franken-bee`) and appends to `user.purchased_avatars`.
- **Unlock rule:** An avatar is unlocked if:
  - **isFree** (default_free / mascot_free), OR
  - **iapProductId** is in **ownedProductIds** (i.e. avatar slug is in `purchased_avatars`), OR
  - **activeSubscription** and avatar is in the premium set (`tier == 'premium'` or `is_premium_included`).
- **Normalized comparison:** Slug comparison is normalized (lowercase, strip, `_` → `-`) in `avatar_catalog.check_avatar_unlocked` and in `_is_avatar_unlocked_for_user` so restores that store `franken-bee` match catalog id `franken-bee` regardless of casing.

## 3. Subscription vs non-consumable

- **Subscription** (`com.beesmart.premium.monthly`): Unlocks premium features and, in this implementation, **all premium-tier avatars** (subscription unlocks the “premium avatar set”).
- **Non-consumable avatar purchases** still unlock individually; a user can own avatars without a subscription.
- Backend: `_is_avatar_unlocked_for_user` and `check_avatar_unlocked(..., has_premium_subscription=...)` both implement “premium member → premium avatars unlocked.”

## 4. Restore flow and UI refresh

- When the user taps **Restore Purchases:**
  1. Native restore runs (e.g. `AppStore.sync()`).
  2. Client calls `/api/iap/restore` with owned product IDs; server applies entitlements and updates `purchased_avatars`.
  3. Client dispatches `beesmart:iap-reconciled`; **then** after a short delay (600 ms menu, 400 ms subscription page) the success modal is shown.
- **Avatar picker:** Listens for `beesmart:iap-reconciled` and schedules `loadAvatars()` (350 ms) so the grid is refreshed with updated `purchased_avatars` / lock state **before** the user sees “Restore complete.” No “Restored purchases…” modal before UI update.

## 5. Root causes addressed

- **Product ID mismatch (.v2):** Catalog and backend use exact App Store IDs; no assumption that all IDs end with `.v2`. UI does not build product IDs from slugs.
- **Unlock by name vs product ID:** Entitlements are applied by **product ID**; backend maps to **avatar slug** and stores slugs in `purchased_avatars`. Unlock checks use normalized slug comparison.
- **Restore uses cache:** After restore, client re-syncs with server via `/api/iap/restore` and then refreshes avatar list, so UI always reflects current entitlements.
- **Stale UI state:** `beesmart:iap-reconciled` triggers a refresh of the avatar list; lock state is derived from the latest API response (`is_locked`, `purchased_avatars`).

## 6. Acceptance criteria (done)

- Every avatar with an `iapProductId` in the catalog shows a **Buy** button with price (from API) or **Owned** if already purchased.
- Buying an avatar completes purchase and the tile flips to Owned/Unlocked after refresh (and optionally after “Restore Purchases” if needed).
- **Restore Purchases** unlocks previously bought avatars within 1–2 seconds; the success modal appears only after the UI has been updated.
- No avatar tile shows **Purchase** for a product the backend does not return (product_id comes from catalog-backed API only).
- No duplicate or incorrect mapping between tiles and product IDs; catalog and `avatar_skus` are the single source of truth.
