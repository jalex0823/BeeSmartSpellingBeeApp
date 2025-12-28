# BeeSmart Spelling — Pre‑Release / Store Compliance & Stability Pass (Jeffery)

**Owner:** Jeffery Alexander  
**Status:** Pre‑Release / Store Compliance & Stability Pass  
**Last updated:** 2025-12-28

This is the in-repo tracker for the items you listed (1–9), plus App Store submission gating items that must be verified in App Store Connect.

## Legend

- [ ] Not done
- [x] Done / verified
- [~] Partially done / needs follow-up verification
- [C] **Needs App Store Connect verification** (cannot be proven from repo alone)
- [R] **Repo-verified** (proven by code/templates/docs in this repo)

---

## 1) App Store Compliance (High Priority)

### 1.1 Must‑verify in App Store Connect (submission blockers)

- [x] [C] Terms of Use (EULA) link set in App Store metadata (Guideline 3.1.2)
  - Evidence: `APP_STORE_CONNECT_CHECKLIST_DEC2025.md` section 7 marked complete.
- [~] [C] Apple Standard EULA vs Custom EULA selection confirmed
  - Connect check: App Store Connect → App Information → **License Agreement**.
  - Acceptance: written note (or screenshot) of which selection is active + exact URL.
- [x] [C] IAP metadata updated to avoid price text in the description
  - Evidence: `APP_STORE_CONNECT_CHECKLIST_DEC2025.md` IAP “no price text” items marked complete.
- [~] [C] Subscription disclosure text confirmed (required language)
  - Must include: auto‑renewal, billing frequency, cancellation instructions.
  - Connect check: App Store Connect → Subscriptions → each subscription → **Subscription Information**.
- [ ] [C] Metadata character limits validated
  - Acceptance: no validation warnings; key fields fit constraints.

### 1.2 Repo‑verifiable compliance implementations

- [x] [R] “Restore Purchases” UX exists in live pages
  - Evidence: `templates/subscription.html` contains a Restore Purchases control calling `window.BeeSmartIAP.restore()`.
  - Evidence: `templates/unified_menu.html` includes restore flow using `window.BeeSmartIAP.getOwnedProducts()` and posts to `/api/iap/restore`.
- [x] [R] Restore endpoint exists on the server
  - Evidence: `AjaSpellBApp.py` → `@app.route('/api/iap/restore', methods=['POST'])` (`api_iap_restore`).
- [x] [R] Guest restore supported (no login required)
  - Evidence: `AjaSpellBApp.py` `api_iap_restore()` stores guest entitlements using `anon_restore_id` cookie + `session['anon_owned_products']`.

### 1.3 App‑review / “Jeffery tagged” gating

- [x] [R] Key redemption kill‑switch for App Store builds
  - Evidence: `AjaSpellBApp.py` `/api/bundles/redeem` returns 404 when `APP_STORE_BUILD=1`.
- [x] [R] Key redemption disabled by default unless explicitly enabled
  - Evidence: `AjaSpellBApp.py` checks `ALLOW_KEY_REDEMPTION != '1'` and returns 404.
- [x] [R] Review Mode toggle exists (repo implementation + docs)
  - Evidence: `AjaSpellBApp.py` uses env `APP_REVIEW_MODE` and supports `/?review=1` session toggle (found during repo verification pass).
  - Evidence: reviewer/demo notes exist in multiple docs (see reviewer notes / checklist files).
- [ ] [C] Confirm review build env vars are set correctly
  - Required for review build: `APP_STORE_BUILD=1` (to hide redemption) and `APP_REVIEW_MODE=1` (if review toggle is expected).

---

## 2) Avatar & UI Issues

- [ ] Fix registered user avatar carousel not unlocking correct avatars.
  - Acceptance: owned/unlocked avatars match entitlements (IAP + honey points + bundles) for a known test account.
- [ ] Ensure guest users default correctly to **Mascot Bee** avatar.
  - Acceptance: fresh session loads mascot consistently.
- [ ] Re-center registered avatar on Main Menu card.
- [ ] Increase avatar container and avatar size for better visual balance.
- [ ] Add persona-based idle animations per avatar.
- [ ] Implement optional adjacent background animations tied to avatar persona.

---

## 3) Quiz & Word Bank Functionality

- [ ] Resolve bulk word import failure.
- [ ] Fix random word quiz not loading.
- [ ] Normalize spelling input for accurate scoring.
- [ ] Ensure word bank clearing functions correctly between sessions.
- [ ] Validate external vs internal word bank source selection.

---

## 4) Audio & Pronunciation

- [ ] Remove announcer echoing the word to spell.
- [ ] Add toggle options:
  - [ ] English-only pronunciation
  - [ ] Korean-only pronunciation
  - [ ] English + Korean
- [ ] Disable device spell-check during spelling input.
- [ ] Balance audio levels across announcer, effects, and feedback sounds.

---

## 5) UI/UX Improvements

- [ ] Auto-center modal dialogs on open to reduce scrolling.
- [ ] Change dropdown selection font color to black for readability.
- [ ] Match header color dynamically to selected belt/grade theme.
- [ ] Remove glow effects from logo where distracting.
- [ ] Add themed background card behind main menu pills.

---

## 6) Stability & Error Handling

- [ ] Resolve JavaScript console errors:
  - [ ] `MorphController` class not found
  - [ ] Service worker response conversion failure
  - [ ] Unexpected string / unexpected end of input
- [ ] Harden API endpoint `/api/save-partial-progress` (400 errors).
- [ ] Add defensive checks for script load order dependencies.

---

## 7) Reporting & Progress Tracking

- [ ] Validate report card generation:
  - [ ] Buzz points
  - [ ] Grade point accuracy
  - [ ] Completion metrics
- [ ] Ensure partial progress saves correctly and resumes cleanly.
- [ ] Confirm end-of-quiz summary accuracy.

---

## 8) Final QA & Release Prep

- [ ] Smoke test: Import → quiz → score → report card flow
- [ ] Test on:
  - [ ] Desktop (Chrome)
  - [ ] Desktop (Safari)
  - [ ] Desktop (Edge)
  - [ ] Mobile viewport responsiveness
- [ ] Verify no blocker issues remain prior to App Store resubmission.

---

## 9) Documentation & Developer Notes

- [ ] Consolidate all fixes into final developer update notes.
- [ ] Prepare brief internal release notes for version submission.
- [ ] Archive resolved issues for post-launch backlog reference.

---

## App Store Connect verification checklist (copy/paste for final pass)

- [C] App Information
  - [C] License Agreement (Standard vs Custom) matches intended EULA
  - [C] Support URL, marketing URL, privacy policy URL are correct
- [C] App Review Information
  - [C] Contact info is complete and reachable
  - [C] “Notes” include reviewer path (review mode toggle, demo creds, restore purchases)
  - [C] If login exists: reviewer account works; if not needed: note that clearly
- [C] App Privacy
  - [C] Nutrition labels match actual data collection (kids app scrutiny)
- [C] Age Rating + Kids Category
  - [C] Age rating questionnaire matches “kids” expectations
  - [C] If marked “Made for Kids” / Kids Category: compliance items satisfied
- [C] Pricing and Availability
  - [C] Territory/pricing schedule correct
  - [C] Any launch date / phased release settings correct
- [C] Subscriptions / IAP
  - [C] All IAP products are in “Ready for Submission” (or approved) state
  - [C] Subscription group configured correctly
  - [C] Subscription text has required disclosure language
  - [C] No price text embedded in descriptions/marketing text
  - [C] Localizations reviewed (names/descriptions) for each locale
  - [C] Review notes include how to restore purchases + reviewer flow
  - [C] Screenshots readable (no tiny text)
  - [C] Any “Sign in required” messaging does not block restore
- [C] Screenshots / Previews
  - [C] 6.7" + 6.1" (or required set) uploaded, correct ordering, legible text
  - [C] No UI shows pricing text that conflicts with IAP policy
- [C] Export Compliance
  - [C] Export compliance answered correctly (encryption use)

