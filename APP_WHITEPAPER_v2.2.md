# BeeSmart Spelling Bee — Comprehensive App Whitepaper (v2.2)

Prepared by Altech Computer Services, LLC  
<https://beesmartspelling.app>  
Effective Date: November 5, 2025

## Contents

1. App Identity & Positioning  
2. iOS App Store Metadata  
3. Google Play Listing Metadata  
4. Features, Accessibility & UX Notes  
5. Monetization Model & Tier Structure  
6. Compliance, Data Safety & Privacy Notes  
7. Privacy Policy (Summary)  
8. Terms of Use (Summary)  
9. Reviewer Notes & Test Access  
10. Localization Plan  
11. Next Steps & Launch Checklist  
12. Technical Appendix (IAP + Avatars)

---

## 1. App Identity & Positioning

App name: BeeSmart Spelling Bee  
Subtitle: Fun spelling practice for kids  
Tagline: Learn, hear, and master words—your way.

BeeSmart Spelling Bee helps kids master spelling and vocabulary with kid‑friendly definitions, phonetic hints, and keyboard answers. Learners can upload word lists from CSV, TXT, DOCX, PDF, or images (OCR) and practice in a playful, ad‑free environment. A delightful 3D avatar system motivates progress; guests see a rotating avatar carousel, while registered users see their chosen avatar.

### Target Audience

- Primary: Elementary and middle school students (ages 6–13)  
- Secondary: Parents and teachers who curate word lists

### Categories

- iOS: Education (Primary). Kids (6–8 or 9–11)  
- Google Play: Education > Learning

### Unique Value

- Multi‑format uploads (CSV/TXT/DOCX/PDF/images via OCR)  
- Built‑in kid‑friendly dictionary and phonetic spelling  
- Keyboard answers; hints without revealing the word  
- Session-based progress tracking  
- Motivating 3D avatars (GLB/OBJ) with guest carousel vs registered avatar  
- Privacy‑first, ad‑free design

---

## 2. iOS App Store Metadata

App name: BeeSmart Spelling Bee  
Subtitle: Fun spelling practice for kids

Promotional text: Build confidence with friendly definitions, phonetic hints, and feedback. Upload word lists from files or photos and practice in kid‑safe, ad‑free sessions.

Long Description:  
BeeSmart Spelling Bee makes spelling practice simple and fun. Upload files (CSV/TXT/DOCX/PDF) or worksheet photos using built‑in OCR. Each word includes a kid‑friendly definition, example, and optional phonetic spelling. Kids answer via keyboard, ask for hints, and track streaks. 3D avatars add motivation: guests see a carousel; registered users see their chosen avatar.

Highlights:

- Multi‑format uploads (CSV, TXT, DOCX, PDF, OCR)  
- Kid‑friendly definitions and phonetics  
- Keyboard input (voice planned)  
- Streak tracking and progress feedback  
- 3D avatars with guest carousel vs registered avatar  
- Ad‑free and privacy‑focused  
- In‑app purchases: monthly subscription (free trial/intro offers) and optional avatar unlocks

Keywords: spelling, kids, vocabulary, phonics, education, quiz, practice, classroom, teacher, OCR, worksheet, avatars

In‑App Purchases (disclosure): Monthly subscription with free trial/intro pricing; optional non‑consumable avatar unlocks and bundles; restore supported.

---

## 3. Google Play Listing Metadata

Short description: Master spelling with kid‑friendly definitions, phonetic hints, and easy list uploads.

Full Description:  
BeeSmart Spelling Bee helps kids build spelling skills with friendly definitions and hints. Import lists from CSV/TXT/DOCX/PDF or photos (OCR). Kids practice by typing answers, track streaks, and build confidence. 3D avatars motivate progress. Subscriptions unlock premium access; avatars can be earned with points or purchased.

Features:

- Import word lists from files or photos  
- Kid‑friendly dictionary  
- Keyboard answers  
- Progress tracking and streaks  
- 3D avatars (guest carousel vs registered avatar)  
- Ad‑free and secure  
- In‑app purchases: subscription + optional avatar unlocks (restore supported)

Category: Education > Learning  
Data collected: Uploaded word lists (User content)  
Diagnostics: Optional crash logs  
Encryption: HTTPS in transit  
Data deletion: Users or parents can request deletion

---

## 4. Features, Accessibility & UX Notes

- High‑contrast visuals and large buttons  
- Kid‑friendly UI with clear typography  
- Keyboard‑only input (voice planned)  
- Parental gate for purchases or external links  
- Accessibility: designed to work with VoiceOver/TalkBack  
- Safari/macOS stability: quiz timer decoupled from TTS (onend) to avoid stalls  
- Improved iOS/macOS TTS defaults (clearer female voice)  
- Home screen avatar unification: guests see only the carousel; registered users see only their selected avatar  
- Loading & diagnostics show the unified avatar mode in real time  
- Vertical shimmer removed on home (prevents mobile whiteouts); body overlays and pseudo‑elements disabled under home‑no‑shimmer guard
- Guest carousel polish: increased spacing between items and smooth, reduced‑motion‑respecting transitions  
- Registered avatar display standardized to the high‑quality carousel container (240×180) for consistent 3D fidelity  
- Guest carousel refinement: eased crossfade between avatars with subtle lift/float easing and a thin honey‑gold podium/base beneath each model for visual grounding  
- Registered avatars: restored per‑avatar “Click Here” themed animations (e.g., Al Bee → science effects), adapted for online use with graceful fallbacks; audio optional and non‑blocking  
- Quiz celebrations: on correct answers, trigger persona‑themed overlays with confetti and a short, non‑blocking sound stinger; respects reduced‑motion, in‑app mute, and includes a user toggle

---

## 5. Monetization Model & Tier Structure

Primary: Subscription‑first with free trial/intro options.  
Secondary: Earn‑or‑buy avatar unlocks (non‑consumables) and optional bundles.

- Subscription (monthly)  
  - Product ID (env): `PRODUCT_SUBSCRIPTION_FULL_ID` (default `beesmart.premium.monthly`)  
  - Free trial days and intro pricing configured in store; surfaced in app for messaging  
  - Grants premium membership (full access)  

- Avatars (non‑consumable)  
  - Deterministic SKUs: `com.beesmart.avatar.<avatar-slug>` (override with `AVATAR_SKU_PREFIX`)  
  - Earn with Honey Points or purchase; bundles available  
  - CSV for store setup: `store/avatar_skus.csv`

Example unlock guidelines (subject to catalog pricing):

- 12–30k Honey Points or $0.99–$2.99 per avatar depending on tier  
- Free defaults for registered users: Cool Bee, Builder Bee, Brother Bee, Detective Bee  

Restore: Supported via native bridges; server applies entitlements idempotently.

Teacher/Parent bundle keys (distribution)

- Purpose: allow schools/families to unlock curated avatar bundles without going through the stores (e.g., classroom packs, family packs)
- Redemption: authenticated users redeem a one‑time key in the Parent/Teacher dashboards; server applies entitlements idempotently
- Storage: development keys live in `avatar_bundles.py`; production should store keys server‑side (DB or KMS/secret env) with usage tracking (issued, redeemed_by, redeemed_at, expiry)
- Security: keys are normalized and never embedded in the client; server is the source of truth for entitlements
- UX: success message lists unlocked avatars and updates avatar picker immediately

---

## 6. Compliance, Data Safety & Privacy Notes

- COPPA and GDPR mindful  
- No third‑party ads or data sales  
- HTTPS encryption and secure storage  
- Parental gates for purchases and external links  
- Optional teacher/parent accounts (email/username only)  
- Data deletion available via request  
- Storekit/Play Billing compliance via server‑side verification stubs (enable live mode with credentials)

---

## 7. Privacy Policy (Summary)

BeeSmart Spelling Bee collects only minimal data necessary to deliver functionality. We do not show third‑party ads or sell personal information. Uploaded word lists and quiz performance are stored securely and can be deleted. Parents may request data deletion via <privacy@beesmartspelling.app>.

Full policy: <https://beesmartspelling.app/privacy>

---

## 8. Terms of Use (Summary)

BeeSmart Spelling Bee is licensed for personal, educational, or classroom use. Accounts for teachers/parents may be required for advanced features. By using the app, you agree to the Privacy Policy and Terms of Use. The application is governed under Texas law.

Full terms: <https://beesmartspelling.app/terms>

---

## 9. Reviewer Notes & Test Access

Test Accounts  

- Student: `student_demo` / Password: `REVIEW-ONLY`  
- Teacher: `teacher_demo` / Password: `REVIEW-ONLY`

Test Steps  

1) Upload a sample list (e.g., `50Words_kidfriendly.txt`)  
2) Start a quiz and answer with keyboard input  
3) Request a hint and verify kid‑friendly definition without revealing the word  
4) Try OCR upload using a worksheet photo  
5) Verify health endpoints: `/health` and `/health/iap`  
6) Native IAP (mock/permissive): purchase and restore subscription and one avatar SKU  
7) Home UI polish: as a guest, observe increased spacing plus fluid crossfades (subtle lift-in/float-out) and the honey‑gold podium under each avatar; as a registered user, confirm the avatar renders in the same 240×180 container and triggers a theme‑specific animation on click (e.g., Al Bee → science equations/sparks)

IAP Review Aids  

- Subscription SKU (env): `PRODUCT_SUBSCRIPTION_FULL_ID` (default `beesmart.premium.monthly`; legacy `beesmart.sub.full_monthly` supported)  
- Avatar SKUs: see `store/avatar_skus.csv` (prefix `com.beesmart.avatar`)  
- Server endpoints:  
  - Verify: `POST /api/iap/verify/<platform>` (apple|google|web)  
  - Restore: `POST /api/iap/restore`  
  - Bundle redeem: `POST /api/bundles/redeem` (auth required)
- Modes:  
  - `IAP_MOCK=1` → accept all (dev)  
  - `IAP_VERIFICATION_MODE=live_strict` → real store validation  
  - `IAP_VERIFICATION_MODE=live_permissive` + `IAP_LIVE_ACCEPT_BASIC=1` → bring‑up  
- Native bridge contract: `NATIVE_IAP_BRIDGE.md`

Security/Reset (dev‑only utilities)  

- Password reset test helpers and a dev peek endpoint can be enabled for E2E only; disabled in production by default.

Bundle‑key redemption (dashboard)

- Sign in as a Teacher account (`teacher_demo` above)  
- Open the Teacher Dashboard and locate “Redeem Avatar Bundle Key”  
- Use any development key defined in `avatar_bundles.py` under `REDEEMABLE_KEYS` (dev only) and press Redeem  
- Confirm success messaging, and verify avatars from the redeemed bundle are unlocked in the avatar picker  
- Note: in production, keys are stored server‑side and may be single‑use with expiry/limits

---

## 10. Localization Plan

- Phase 1: en‑US  
- Phase 2: es‑US, en‑GB (localized text, descriptions, and screenshots)  
- Future: bilingual definitions with teacher‑curated wordbanks

---

## 11. Next Steps & Launch Checklist

- Finalize privacy and terms pages  
- Verify reviewer demo accounts  
- Test iOS and Android builds (signing, IAP flows, restores)  
- Add/confirm parental gate verification  
- Submit to App Store and Play Console  
- Enable data deletion link in app  
- Begin localization for Spanish/UK English  
- Confirm Apple/Google IAP credentials for live verification  
- Generate/update `store/avatar_skus.csv` when catalog changes  
- CI smoke: periodically check `/health` and `/health/iap`

Bundle keys: operations & QA  

- Add admin UI and backend to generate/revoke bundle keys, set limits/expiry, and track consumption  
- Migrate dev keys to DB‑backed storage with audit logs (issued_by, redeemed_by, timestamps, IP)  
- Add automated tests for `/api/bundles/redeem` covering valid, invalid, expired, and idempotent redemption  
- Enhance dashboard UX to list which avatars were unlocked after redemption

---

## 12. Technical Appendix (IAP + Avatars)

- PRODUCT_MAP includes:  
  - Premium: `beesmart.full_unlock`, `beesmart.premium.monthly` (legacy: `beesmart.sub.full_monthly`)  
  - Avatars: auto‑added from `avatar_skus.build_product_entitlements()`  
- Entitlements:  
  - Premium → `premium_member=true`  
  - Avatar purchase → adds to `User.purchased_avatars`  
  - Bundle → adds to `User.purchased_bundles` and unlocks included avatars  
  - Bundle keys (teacher/parent distribution) → POST `/api/bundles/redeem` (auth required) applies a pre-defined bundle idempotently. UI: Parent/Teacher dashboards provide a "Redeem Avatar Bundle Key" field.
  - Dynamic BeeKeys (admin-generated 4‑packs) → Admins create on-demand bundles (`POST /api/admin/bee-keys/generate`) producing a unique bundle with 4 avatars + tracked key; redemptions audited (IP + user-agent).
  
  Endpoint details (bundle key redemption)
  - Method: `POST /api/bundles/redeem` (auth required)
  - Request JSON:

    ```json
    { "key": "YOUR-BUNDLE-KEY-HERE" }
    ```

  - Success (200):

    ```json
    {
      "ok": true,
      "bundle_id": "classroom_starter_pack",
      "unlocked_avatars": ["cool-bee", "builder-bee", "brother-bee"],
      "purchased_bundles": ["classroom_starter_pack", "family_fun_pack"],
      "purchased_avatars": ["cool-bee", "builder-bee", "brother-bee", "detective-bee"]
    }
    ```

  - Error (400/404 examples):

    ```json
    { "ok": false, "error": "invalid_key" }
    ```

    ```json
    { "ok": false, "error": "bundle_not_found" }
    ```

  - Notes: keys are normalized server‑side; redemption is idempotent; production deployments should back keys with a database and audit logs
  - Dynamic BeeKeys: generated bundles (prefix `beekey_`) are resolved from database if not in static catalog; each redemption creates a trace row for compliance/analytics
- Frontend exposure:  
  - `window.SUBSCRIPTION_SKU` for subscription  
  - `window.AVATAR_SKUS` map for per‑avatar products  
- Asset sanity: avatar assets under `static/assets/avatars/` (OBJ) and `static/assets/avatars/glb_files/` (GLB). Use the VS Code task “Avatar: Asset Consistency (localhost)” to run `test_avatar_assets.py`.
- Docs: `IAP_DEVELOPER_GUIDE.md`, `NATIVE_IAP_BRIDGE.md`
