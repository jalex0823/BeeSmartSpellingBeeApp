# Apple Premium Subscription Purchase Flow – E2E Smoke Test

**Goal:** Verify full Apple purchase flow works end-to-end (Sandbox).

**Product ID:** `com.beesmart.premium.monthly`

---

## Smoke Test Checklist (run on fresh install / sandbox user)

### 1. Fresh state
- [ ] No previous entitlement cached (fresh install or clear local storage).
- [ ] App shows Premium locked state (locked tiles, Upgrade visible).

### 2. Open Premium page
- [ ] Navigate to Premium (tap Premium tile or Upgrade button).
- [ ] Premium page loads.
- [ ] Correct product ID displayed: **com.beesmart.premium.monthly**.

### 3. Purchase
- [ ] Tap Subscribe.
- [ ] Apple purchase sheet appears.
- [ ] Complete purchase using Sandbox tester.
- [ ] Success callback triggers.
- [ ] Entitlement stored (local + server if applicable).

### 4. Post-purchase UI
- [ ] Premium page shows “Active” (or equivalent).
- [ ] Locked Premium tiles now open normally (no upsell).
- [ ] Premium badge/indicator updates immediately (no relaunch required).

### 5. Restore purchases
- [ ] Reinstall app / clear local storage.
- [ ] Tap Restore Purchases.
- [ ] Premium re-unlocks.

---

## Required debug output (must be visible in logs)

| Phase            | Log message |
|------------------|-------------|
| Store init       | `IAP: store initialized` |
| Product fetched  | `IAP: product fetched id=com.beesmart.premium.monthly` |
| Purchase started | `IAP: purchase started` |
| Purchase success | `IAP: purchase success transaction=<id>` |
| Entitlement      | `IAP: entitlement active` |
| Restore started  | `IAP: restore started` |
| Restore success  | `IAP: restore success entitlement active` |

---

## Acceptance criteria

- Purchase works in Sandbox without loops or crashes.
- Entitlement unlocks within 2 seconds after purchase success.
- Restore works after reinstall.

---

## Premium navigation instrumentation (Premium tiles → Premium page)

When tapping Premium tile or Upgrade:

- `PremiumNav: from=<source> -> premium page`
- `PremiumNav: success`
- On failure: `PremiumNav: failure error=<err>` and modal: “Unable to open Premium page. Please try again.”

**Sources:** tile name / feature name (e.g. `BeeSmart Premium`, `upgrade_button`).

---

## Quiz keyboard integration (when using custom keyboard)

- **Do not** mount the keyboard on `DOMContentLoaded`.
- **Mount** when the countdown timer enters RUNNING state (e.g. in `startCountdownTimer()` / `beginRound()`).
- **Unmount** (or disable) when the round ends / game over.
- Use `spacerTargetEl` so the quiz main container gets `padding-bottom` equal to keyboard height + 12px; clear on unmount.
- Intro: add class `quiz-keyboard-enter` on mount (slide up + fade in, 200–300ms). Exit: add `quiz-keyboard-exit` before unmount (slide down + fade out, 150–250ms).
