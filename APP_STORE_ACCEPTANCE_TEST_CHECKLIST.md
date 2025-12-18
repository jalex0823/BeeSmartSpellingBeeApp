# BeeSmart Spelling Bee App — App Store Acceptance Test Checklist (iOS)

**Last updated:** 2025-12-18  
**Goal:** Verify the iOS build matches repo-documented behavior and passes App Store review expectations (stability, privacy, purchases, accessibility).

> Notes
> - Some items are **console/config checks** (App Store Connect, Railway). They can’t be proven by code alone.
> - If a requirement is documented but you can’t find an implementation in code, this checklist flags it as a **gap to verify**.

---

## 0) Test setup prerequisites

- [ ] **Use the reviewer demo accounts** in the release build:
  - Student: `student_demo` / `REVIEW-ONLY`
  - Teacher: `teacher_demo` / `REVIEW-ONLY`
  - Sources: `store/ReviewerNotes.md`, `store/AppStoreListing.md`, `APP_WHITEPAPER_v2.2.md`, `IAP_DEVELOPER_GUIDE.md`

- [ ] **Confirm password reset dev peek is OFF in production**
  - Dev-only endpoint must be disabled unless explicitly enabled for test:
    - `GET /dev/peek-reset-token?identifier=...` only when `ALLOW_DEV_RESET_PEEK=1`
  - Sources: `README.md`, `docs/mobile-readiness-checklist.md`

- [ ] **Know which IAP mode you’re running**
  - Mock mode: accepts purchases for test flows.
  - Live mode: Apple receipt validation / error handling must be correct.
  - Sources: `IAP_DEVELOPER_GUIDE.md`, `NATIVE_IAP_BRIDGE.md`, `/health/iap` in `AjaSpellBApp.py`

---

## 1) Word‑Bank Upload & Quiz Functions

### 1.1 Multiple upload formats

- [ ] Upload a **small** word list:
  - `.txt` (one word per line)
  - `.csv` (word column)
  - Expected: words parsed, deduped, stored, and quiz can start.

- [ ] Upload a **large** word list (hundreds+ words):
  - Expected: progress UI stays responsive; quiz works; no 500 errors.

- [ ] Upload **DOCX** and **PDF** word lists:
  - Expected: accepted and parsed; invalid PDFs rejected with a user-friendly error.

- [ ] Upload an **image** (OCR path):
  - Expected: if OCR is available, words extracted; if unavailable, fail gracefully with a helpful message.

- [ ] Upload an **invalid file** (empty, unsupported extension, corrupted):
  - Expected: no crash; user-friendly error; app remains usable.

**Sources (UI + server):**
- Upload tiles + supported formats messaging: `templates/unified_menu.html`
- Upload API & parsing: `AjaSpellBApp.py` (`/api/upload`)
- OCR gating guidance: `docs/mobile-readiness-checklist.md`, `FULL_FEATURES_ENABLED.md`

### 1.2 Interactive quiz flows

- [ ] Start a quiz from a freshly uploaded list.
- [ ] Verify keyboard input works (mobile + external keyboard on iPad).
- [ ] Verify hints/definitions do **not** reveal the spelling.
- [ ] Verify progress tracking, streaks, scoring, and end-of-quiz report card.

**Sources:**
- Quiz UI + hint panels + accessibility attributes: `templates/quiz.html`
- Quiz endpoints: `AjaSpellBApp.py` (`/api/next`, `/api/answer`, `/api/clear`, `/api/wordbank`)
- Session + wordbank storage pattern: `.github/copilot-instructions.md`

### 1.3 Retry choice flow (wrong answer → user chooses)

- [ ] Spell a word wrong (first attempt):
  - Expected: two buttons appear — **“✅ Retry”** and **“❌ Show Answer”**
  - Expected: **10-second countdown** is visible
  - Expected: **answer is NOT shown** during the choice window

- [ ] Tap **Retry** within 10 seconds:
  - Expected: choice buttons disappear
  - Expected: input enabled and focused
  - Expected: **20-second retry window** appears
  - Expected: **no answer shown** during retry window

- [ ] Submit a second wrong attempt:
  - Expected: “no more retries” behavior + appropriate messaging/logs

- [ ] Let the 10-second choice countdown expire:
  - Expected: auto-selects Show Answer (per implementation docs)

**Sources:**
- Retry feature docs: `RETRY_CHOICE_FLOW_IMPLEMENTATION.md`, `RETRY_FIX_FINAL_SUMMARY.md`, `READY_FOR_TESTING.md`
- Manual test guides: `TEST_RETRY_FLOW_MANUAL.md`, `QUICK_TEST_GUIDE.md`, `TEST_STEPS_RETRY_FIX.txt`
- Implementation variants: `templates/quiz2t.html`, `templates/quiz_buzz.html`, `templates/quiz.html`
- Optional automated UI test: `test_retry_choice_flow.py`

### 1.4 Saved word lists

- [ ] As a logged-in user, save the current wordbank as a named saved list.
- [ ] View saved lists and load one into the current session.
- [ ] Verify saved-list counts/badges update and the correct list loads.
- [ ] Verify guest users cannot access saved lists (locked tile / prompt).

**Sources:**
- Saved lists tile + modal logic: `templates/unified_menu.html`
- Saved lists API visibility in diagnostics: `full_diagnostic.py` (mentions `/api/saved-lists`)

### 1.5 Session-based statistics

- [ ] As a guest, verify session stats reset on reload/clear.
- [ ] As a logged-in user, verify progress persists across sessions where intended.

**Sources:**
- Session/wordbank patterns and keys: `.github/copilot-instructions.md`
- Mastery/stat tracking hardening: `models.py` (`WordMastery.update_stats()`)

---

## 2) Word Pronunciation & Hints

### 2.1 Kid-friendly dictionary & phonetic hints

- [ ] Use “Show Definition” and verify:
  - Definition shown is kid-friendly
  - The target word is blanked (no answer leak)
  - Example sentence, similar words, and phonetic hint behave as designed

**Sources:**
- Dictionary filtering and kid-friendly transforms: `dictionary_api.py`
- Quiz display formatting + blanking safeguards: `templates/quiz.html`

### 2.2 Audio pronunciation

- [ ] Tap “Pronounce Word” and verify audio plays.
- [ ] Toggle mute and ensure pronounce respects user settings.
- [ ] Verify behavior under iOS constraints (audio must be user-initiated).

**Sources:**
- Quiz pronounce workflow: `templates/quiz.html`
- Menu dictionary pronounce button (Web Speech): `templates/unified_menu.html`
- Pronounce endpoint behavior: `AjaSpellBApp.py` (`/api/pronounce`)

### 2.3 Hint usage rules

- [ ] Confirm hint usage does not apply unintended penalties.
- [ ] Confirm hint availability is limited as intended (once per word, if that’s the rule).

**Sources:**
- Quiz logic: `templates/quiz.html`

---

## 3) User Accounts, Authentication & Password Reset

### 3.1 Registration & login

- [ ] Create accounts for student/teacher/parent (if roles exist in UI).
- [ ] Validate required fields and error messages.
- [ ] Verify flows work on:
  - Safari iOS (WKWebView wrapper)
  - Chrome/Edge mobile

**Sources:**
- Registration template (includes BeeKey field): `templates/auth/register.html`
- Login + forgot-password panel: `templates/auth/login.html`

### 3.2 Password reset flow

- [ ] Trigger forgot-password:
  - Expected: generic response (no user enumeration)
  - Expected: rate limiting works (429 after repeated attempts)

- [ ] Complete reset using email link/token:
  - Expected: tokens expire; invalid tokens rejected

- [ ] In dev/testing only: verify dev peek endpoint works when enabled.

**Sources:**
- Implementation + env toggles + rate limiting notes: `README.md`
- Email template: `templates/emails/reset.html`
- Reset page: `templates/auth/reset.html`
- Reset E2E / test: `test_password_reset_flow.py`
- SMTP guidance: `SMTP_SETUP_HOSTINGER.md`

### 3.3 Rate limiting (in-memory vs Redis)

- [ ] Validate rate limiting without Redis.
- [ ] Validate rate limiting with Redis configured.

**Sources:**
- Redis-backed rate limiting notes: `README.md`

### 3.4 Parental gate (external links / purchases)

- [ ] Attempt to open external links from the app.
- [ ] Attempt to initiate purchase flows.
- [ ] Expected: a parental gate appears (passcode / acknowledgement), per product docs.

**Important:** The repo documentation references parental gate behavior, but a quick code search did **not** find a concrete parental-gate implementation function. Treat this as a high-priority verification item.

**Sources (requirement):**
- `compliance/Accessibility_COPPA_Checklist.md`
- `APP_WHITEPAPER_v2.2.md` (parental gate references)

---

## 4) 3D Avatars & Menu UI

### 4.1 Avatar selection & display

- [ ] Guest users: verify rotating carousel appears.
- [ ] Logged-in users: verify only their selected avatar is shown.
- [ ] Verify avatar click triggers theme-specific effect and optional sound.
- [ ] Verify reduced-motion behavior disables/simplifies animations.

**Sources:**
- Guest carousel + user avatar loader + reduced-motion checks: `templates/unified_menu.html`
- Avatar catalog (source of truth): `avatar_catalog.py` and sync docs `AVATAR_CATALOG_SYNC_COMPLETE_NOV13.md`

### 4.2 Avatar purchasing/earning & Honey Points

- [ ] Earn honey points in quiz and verify totals update.
- [ ] Verify unlock thresholds and entitlement persistence.

**Sources:**
- Honey points system doc: `HONEY_POINTS_SYSTEM.md`
- Quiz UI honey points animations: `templates/quiz.html`

### 4.3 BeeKey registration field

- [ ] On registration, enter a valid BeeKey pack code.
  - Expected: avatars unlock; success message shown.
- [ ] Enter an invalid/expired/exhausted code.
  - Expected: clear error; registration can continue.

**Sources:**
- Registration BeeKey field: `templates/auth/register.html`
- BeeKey docs: `BEEKEY_QUICK_REFERENCE.md`, `BUNDLE_KEY_REDEMPTION_TECHNICAL_GUIDE.md`, `BEEKEY_INFO_AND_PACKS.md`
- BeeKey redeem endpoints: `AjaSpellBApp.py` (BeeKey/bundle routes)

### 4.4 Admin dashboard BeeKey request button

- [ ] Verify “Request BeeKey Pack” appears in admin UI.
- [ ] Verify it links to `https://beesmartspelling.app/contact`.
- [ ] Verify no JS errors; no in-dashboard key generation is exposed.

**Sources:**
- BeeKey updates summary: `BEEKEY_UPDATES_COMPLETE.md`, `BEEKEY_ADMIN_REGISTRATION_UPDATE.md`

### 4.5 3D bees on landing page

- [ ] Verify 3D bees render smoothly when WebGL is supported.
- [ ] Verify fallback to CSS/2D when WebGL isn’t available.
- [ ] Verify reduced-motion disables animation.
- [ ] Verify responsive bee count (desktop vs mobile) and wrap-around behavior.

**Sources:**
- 3D bee test guide: `TESTING_3D_BEES.md`
- 3D bee/WebGL checks: `templates/unified_menu.html`

---

## 5) In‑App Purchases (IAP) & Entitlements

### 5.1 Subscription purchase & restore

- [ ] Signed-in user triggers native purchase via `window.BeeSmartIAP.purchase(SKU)`.
- [ ] App POSTs to `/api/iap/verify/apple` and receives entitlements.
- [ ] Verify `premium_member` is applied and persists after restart.

- [ ] Restore flow:
  - call `getOwnedProducts()` and POST `/api/iap/restore`
  - verify idempotent behavior (no duplicates)

**Sources:**
- Server contract and product mapping: `IAP_DEVELOPER_GUIDE.md`
- Client bridge contract: `NATIVE_IAP_BRIDGE.md`
- UI bridge usage: `templates/unified_menu.html`
- Test scripts: `scripts/test_iap_endpoints.py`, `scripts/test_iap_live_permissive.py`

### 5.2 Avatar purchases

- [ ] Purchase individual avatars:
  - Expected: product ID maps to correct avatar
  - Expected: display names end with “Avatar” (Apple requirement)

**Sources:**
- Apple compliance naming rule and avatar constraints: `AVATAR_APPLE_COMPLIANCE_COMPLETE.md`, `AVATAR_CATALOG_SYNC_COMPLETE_NOV13.md`, `avatar_catalog.py`
- SKU/entitlement mapping: `avatar_skus.py`, `IAP_DEVELOPER_GUIDE.md`

### 5.3 Avatar bundle purchases & BeeKey redemption

- [ ] Redeem a BeeKey pack and verify bundled avatars unlock.
- [ ] Verify server entitlements reflect the unlocks.

**Sources:**
- Bundle/BeeKey docs: `BUNDLE_KEY_REDEMPTION_TECHNICAL_GUIDE.md`, `BEEKEY_INFO_AND_PACKS.md`
- Implementation: `AjaSpellBApp.py`

### 5.4 IAP sandbox & error handling

- [ ] Mock mode:
  - Expected: verification endpoints accept purchases for testing.

- [ ] Live-like negative tests:
  - Invalid token/receipt → appropriate error
  - Missing product_id → 400
  - Unsupported platform → 400

**Sources:**
- `IAP_DEVELOPER_GUIDE.md`, `scripts/test_iap_live_permissive.py`

### 5.5 Restore across devices

- [ ] Sign in on a second device, run restore.
- [ ] Expected: entitlements reapply without duplicate charges.

**Sources:**
- `IAP_DEVELOPER_GUIDE.md`, `NATIVE_IAP_BRIDGE.md`

### 5.6 App Store Connect product configuration

- [ ] Confirm all required IAP products exist and are “Cleared for Sale”.
- [ ] Confirm product IDs match the backend’s accepted mapping.
- [ ] Confirm price tiers and screenshots are correct (opaque 640×920 where required).

**Sources (repo guidance):**
- `mobile/STORE_CHECKLIST.md`, `mobile/README.md`, `mobile/IOS_PACKAGING.md`
- Avatar catalog + SKU mapping: `avatar_catalog.py`, `avatar_skus.py`

---

## 6) Accessibility & User Experience

- [ ] High-contrast UI and large, tappable buttons (iPhone size).
- [ ] VoiceOver navigation:
  - logical reading order
  - meaningful labels
  - no trap focus

- [ ] Reduce Motion:
  - 3D bees & confetti/visual effects disabled/simplified

- [ ] Orientation + viewport:
  - portrait/landscape don’t break layouts

- [ ] Touch + external keyboard (iPad):
  - typing answers
  - Enter submits

**Sources:**
- Accessibility/COPPA checklist: `compliance/Accessibility_COPPA_Checklist.md`
- Reduced-motion code paths: `templates/unified_menu.html`, `templates/quiz.html`

---

## 7) Performance & Stability

- [ ] Health endpoint:
  - `/health` returns a version string
  - `/health/iap` returns IAP status info

- [ ] Production-like server run:
  - no uncaught exceptions in typical flows
  - stable memory/CPU under repeated quiz sessions

- [ ] Network failure handling:
  - drop internet → user-friendly error
  - dictionary API throttling (429) → graceful fallback

- [ ] Logs:
  - helpful for debugging
  - no sensitive data leakage

**Sources:**
- Health endpoints: `AjaSpellBApp.py` (`/health`, `/health/iap`)
- Ops checklist references: `APP_WHITEPAPER_v2.2.md`

---

## 8) Compliance, Data Safety & Privacy

- [ ] Privacy policy and terms accessible in-app:
  - `/privacy` and `/terms` load and match store URLs

- [ ] Verify minimal data collection and no third-party trackers.

- [ ] Data deletion request flow:
  - user can request deletion
  - request is processed and confirmed

- [ ] HTTPS + cookie security:
  - cookies set Secure / appropriate SameSite
  - sessions invalidated on logout

**Sources:**
- Privacy template: `templates/privacy.html`
- Store URL guidance: `store/URLs_README.md`, `mobile/STORE_CHECKLIST.md`, `ops/DomainAndSSL.md`
- Mobile compliance guidance: `mobile/README.md`, `docs/mobile-readiness-checklist.md`

---

## 9) Teacher/Admin Tools

- [ ] Teacher workflows:
  - create/manage class word lists
  - assign lists to students
  - students can access assigned lists

- [ ] Bundle/BeeKey management:
  - generate, redeem, revoke, usage limits
  - verify audit fields captured (ip_address, user_agent, timestamp)

**Sources:**
- Teacher workflow docs: `GROUPS_TEACHER_WORKFLOW.md`
- Bundle/BeeKey technical guide: `BUNDLE_KEY_REDEMPTION_TECHNICAL_GUIDE.md`
- Bundle implementation: `models.py`, `AjaSpellBApp.py`

---

## 10) Launch Checklist (Pre‑submission)

- [ ] Final IAP configuration:
  - all products exist and are cleared
  - product IDs match mapping

- [ ] Screenshots & metadata match the current whitepaper.

- [ ] Age rating questionnaire complete and appropriate.

- [ ] Localization:
  - verify U.S. English strings
  - confirm any translations are complete

- [ ] Demo accounts confirmed functional in release build.

- [ ] Production deployment health endpoints reachable (Railway):
  - `/health`
  - `/health/iap`

**Sources:**
- Store packaging checklist: `mobile/IOS_PACKAGING.md`, `mobile/STORE_CHECKLIST.md`, `store/AppStoreListing.md`
- Whitepaper: `APP_WHITEPAPER_v2.2.md`

---

## Optional: Automated checks already in repo

These scripts can reduce manual effort; run them against a local server or test environment.

- IAP sanity (mock): `scripts/test_iap_endpoints.py`
- IAP live-like permissive: `scripts/test_iap_live_permissive.py`
- Password reset: `test_password_reset_flow.py`
- Retry-choice UI: `test_retry_choice_flow.py`
- Quiz flow smoke: `final_test_complete.py`
