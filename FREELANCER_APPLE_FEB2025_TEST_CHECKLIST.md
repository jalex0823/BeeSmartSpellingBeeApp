# BeeSmart App — Freelancer Test Checklist (Apple Feb 2025 + Submission 1.1)

Use this checklist to verify app behavior, UI copy, and role permissions after the Apple Feb 2025 compliance work and **Submission 1.1** changes. Run on a **fresh install or Sandbox** build (TestFlight or local) after the backend has cleared subscription data for the test accounts.

---

## Pre-requisites

- [ ] **Backend:** Subscription data cleared for these 5 test accounts (run on your backend/env):
  - `skumar@tinfoxconsulting.com`
  - `skumar+11@tinfoxconsulting.com`
  - `skumar+22@tinfoxconsulting.com`
  - `satya_785@yahoo.co.in`
  - `skumar+01@tinfoxconsulting.com`
  - Command (where `DATABASE_URL` points to that env):  
    `python scripts/clear_subscription_data_for_users.py`
- [ ] **Build:** Latest app build with **Feb 2025 + Submission 1.1** changes installed (TestFlight or dev build).
- [ ] **Accounts:** At least one **Student**, one **Teacher**, and one **Parent** (or Admin) test account available.

**References for testers:**

- **Clearing subscription data:** Full steps, dry run, and confirmation for QA → `SUBSCRIPTION_STATUS_AND_CLEAR.md`
- **Compliance + Submission 1.1 summary:** → `APPLE_FEB2025_COMPLIANCE.md` (including section 5: one subscription → all 3 roles, WWDC 2025 Session 299)

---

## Submission 1.1 — New checks (run these first)

These reflect the latest changes requested prior to submission.

### 1.1 Trial as message only (no trial buttons/links)

| # | What to check | Expected | Pass? |
|---|----------------|----------|-------|
| S1.1 | **Main menu — guest / not signed in** | Any register or “start” CTA. | **No** “Start X-day Free Trial” **button or link**. CTA says **“Register”** (or “Start now”). | ☐ |
| S1.2 | **Same area** | Text below or near the register CTA. | **Message only** (not a button): e.g. “A 7‑day introductory offer is included in the subscription. Then $X.XX/month. Auto‑renews unless canceled.” | ☐ |
| S1.3 | **Subscription screen** (as Parent/Teacher) | Trial wording. | Trial (if any) is **text/message** on the page, not a separate **trial button**. Primary CTA is “Subscribe for $X.XX/month.” | ☐ |

**Acceptance:** Trial is communicated as **message only**; 7-day introductory plan is included in subscription; no trial as a link or button.

---

### 1.2 No “Guest User” button

| # | What to check | Expected | Pass? |
|---|----------------|----------|-------|
| S1.4 | **Main menu — not signed in** | Sign In / Register area. | **No** “Or continue as guest” and **no** “Guest User” button. Users enter the app as guest **automatically** (no CTA to “be a guest”). | ☐ |
| S1.5 | **Quick Guide** (if visible when not signed in) | Bullets. | **No** line like “**Guest:** Try the app without registering…”. Only **Sign In** and **Register** are mentioned. | ☐ |

**Acceptance:** Guest entry is implicit; no guest button or link anywhere in the app.

---

### 1.3 No “For All Ages” button

| # | What to check | Expected | Pass? |
|---|----------------|----------|-------|
| S1.6 | **Main menu** (left column or near Terms) | Any badge/button that says “For All Ages”. | **Removed.** There is **no** “For All Ages” **button or badge** on the menu. | ☐ |
| S1.7 | **Same area** | General safety/vocabulary message. | Optional: plain text like “All words are filtered for appropriate vocabulary — for learners of all ages” is OK (no button). | ☐ |

**Acceptance:** “For All Ages” as a **button** is removed per screenshot 3.

---

### 2.1–2.2 Student: Subscription, Help, and Support hidden

| # | What to check | Expected | Pass? |
|---|----------------|----------|-------|
| S2.1 | Log in as **Student**. Look at **main menu**. | Subscription / Premium entry. | **No** “Upgrade to Premium” / subscription **button** or link visible. | ☐ |
| S2.2 | As **Student**, same menu. | Restore Purchases. | **No** “Restore Purchases” button visible. | ☐ |
| S2.3 | As **Student**, same menu. | Help / support area. | **No** “Quick Help”, “User Guide”, “Admin Guide” links visible. | ☐ |
| S2.4 | As **Student**, type or open **/subscription** (or /premium) in browser. | Result. | **Redirected to /app** (main app). Student does **not** see the subscription page. | ☐ |
| S2.5 | As **Student**, open **/help** or **/support**. | Result. | **Redirected to /app**. Student does **not** see Help or Support (or email) page. | ☐ |
| S2.6 | Log in as **Parent** or **Teacher**. Main menu. | Subscription, Restore, Help. | **Subscription** button, **Restore Purchases**, and **Quick Help** / User Guide (and Support if linked) **are visible**. | ☐ |

**Acceptance:** Student role does not see subscription, Restore, Help, or support (including email); direct URLs redirect to app. Parent/Teacher see full controls.

---

### 2.3 Student controlled by Parent/Teacher (code → Student, buttons hidden)

| # | What to check | Expected | Pass? |
|---|----------------|----------|-------|
| S2.7 | Apply **student/linking code** (from Parent/Teacher account) so the test user becomes **Student**. | Role and UI. | Account is **Student**; **all** of S2.1–S2.5 hold: no subscription button, no Restore, no Help, no support; direct /subscription, /help, /support redirect to /app. | ☐ |

**Acceptance:** After code is applied, Student role is active and all “necessary buttons” (subscription, Help, support) are hidden.

---

### 2.4 Subscription-per-device (product clarification)

| # | What to check | Expected | Pass? |
|---|----------------|----------|-------|
| S2.8 | **Confirm with product owner** | One Apple ID subscription on one device → Parent, Teacher, and Student on that device all have premium. | Documented in `APPLE_FEB2025_COMPLIANCE.md` section 5. **Confirm** whether this is **intentional** (family/device sharing) or should be **per-account only**. See WWDC 2025 Session 299 for reference. | ☐ |

**Acceptance:** Product decision is recorded; no test failure — clarification item only.

---

## 0. Pre-Work — Data Reset (Task 0.1)

| # | Check | Expected | Pass? |
|---|--------|----------|-------|
| 0.1 | Log in as each of the 5 test emails above. | Each user is **non-subscribed** (no Premium). | ☐ |
| 0.2 | For each, open **Premium / Subscription** (as Parent/Teacher) and confirm status. | Status says “Premium not active” or “Premium is not active yet” (no cached premium). | ☐ |
| 0.3 | As a **non-student** test user, tap **Restore Purchases** on the subscription screen. | Restore runs; if no prior purchase, message like “No purchases found” — **no crash, no infinite loading**. | ☐ |
| 0.4 | After restore (with clean data), re-open app. | User remains non-subscribed (clean state). | ☐ |

**Acceptance:** Users re-enter as non-subscribed, no cached premium, Restore works from a clean state.

---

## 1. Kids / Child Copy Removed (Task 1.1)

**Rule:** No visible copy implies the app is “for children.” No “Kids,” “Child,” “For children,” or COPPA-style phrasing in **user-facing** UI.

| # | Screen / Area | What to check | Expected | Pass? |
|---|----------------|----------------|----------|-------|
| 1.1 | **Main menu (home)** | Any badge/label near Terms or content. | **No** “Kid-Safe Content” badge. (Submission 1.1: “For All Ages” **button** also removed.) | ☐ |
| 1.2 | **Main menu** | Tooltip or word-filter hint. | **“appropriate vocabulary”** or “filtered” (not “age-appropriate content” or “kid-safe”). | ☐ |
| 1.3 | **Quiz screen** | Badge/label for word filtering. | **“Filtered Words”** (not “Kid-Safe Words”). | ☐ |
| 1.4 | **Quiz screen** | Tooltip on that badge. | **“appropriate vocabulary”** or “filtered” (not “age-appropriate content”). | ☐ |
| 1.5 | **Terms of Use** | Opening or eligibility. | **“designed for learners and families”** and **“people of all ages”** (not “children and families” only). | ☐ |
| 1.6 | **Privacy Policy** | Intro and “Families” section. | **“designed for learners and families”**; **“Families & Learners”** (or similar); no “for children”/“COPPA” in user-facing bullets. | ☐ |
| 1.7 | **Registration / Sign-up** | Benefits or feature bullets. | **“Filtered content with automated word filtering”** (not “Kid-safe content”). | ☐ |
| 1.8 | **Help / FAQ** (as Parent/Teacher) | Avatar or controls section. | **“Avatar Lock”** and **“Account managers”** (not “Parental Controls” / “Teachers and parents can lock student avatars”). | ☐ |

**Acceptance:** No visible copy implies the app is for children; General Audience / non–Kids Category.

---

## 2. “Parent & Teacher Approved” Replaced (Task 2.1)

**Rule:** In-app “features” or “why BeeSmart” copy is role-agnostic and age-neutral.

| # | Location | What to check | Expected | Pass? |
|---|----------|----------------|----------|-------|
| 2.1 | **App Store listing** (if editable) | “Parent & Teacher Approved” block. | **Removed.** Replaced with bullets like: Ad-free learning, Structured progression, Progress tracking, Clean interface, Filtered vocabulary. | ☐ |
| 2.2 | **In-app About / Features** (if any) | Any “PARENT & TEACHER APPROVED” or role-specific block. | **Removed or rewritten** so it does **not** reference parent, teacher, child, student, or supervision. | ☐ |

**Acceptance:** Copy does not segregate by role; same description can apply to all users.

---

## 3. Role Permissions — Student Restricted (Task 3.1 + Submission 1.1)

**Rule:** Student cannot initiate purchases, manage subscriptions, or access Help/support. Only Parent/Teacher (or Admin) can. Submission 1.1: subscription button, Restore, Help, and support are **hidden** for Student and **redirect** when opening those URLs.

### 3A. Student account

| # | Action | Expected | Pass? |
|---|--------|----------|-------|
| 3.1 | Log in as **Student**. Check main menu. | **No** subscription button, **no** Restore Purchases, **no** Quick Help / User Guide / Admin Guide. | ☐ |
| 3.2 | As Student, open **/subscription** or **/help** or **/support** (e.g. bookmark or URL). | **Redirected to /app**; does **not** see subscription, Help, or support page. | ☐ |
| 3.3 | As Student, use **core learning only**: start a quiz, view progress, word lists. | All **allowed**: core learning, content, read-only progress work. | ☐ |

### 3B. Parent / Teacher account

| # | Action | Expected | Pass? |
|---|--------|----------|-------|
| 3.4 | Log in as **Teacher** or **Parent**. Open **Premium / Subscription**. | Subscribe and Restore are **enabled**; user can initiate purchase and restore. | ☐ |
| 3.5 | As Teacher/Parent, tap **Restore Purchases** (menu or subscription page). | Restore runs (e.g. “No purchases found” or success); no crash. | ☐ |
| 3.6 | As Teacher/Parent, open **Help**, **User Guide**, **Support**. | All **visible** and reachable. | ☐ |

### 3C. Backend / API (if you have access)

| # | Check | Expected | Pass? |
|---|--------|----------|-------|
| 3.7 | Call **Restore** (or equivalent) with a **Student** token and subscription product IDs. | Server **does not** apply subscription; response includes e.g. `student_subscription_blocked: true` and message that only the account manager can manage subscriptions. | ☐ |

**Acceptance:** Student cannot spend money, trigger IAP, or access Help/support; Parent/Teacher can.

---

## 4. Subscription & Auto-Renew (Task 4.1 — Guideline 3.1.2)

**Rule:** Price and billing are clear; trial (if any) is message only; auto-renew is stated on the subscription screen.

| # | What to check | Expected | Pass? |
|---|----------------|----------|-------|
| 4.1 | **Subscription screen** (as Parent/Teacher) — primary price | **“$3.99 per month”** (or your live price) is the **largest** price text. | ☐ |
| 4.2 | **Billing cadence** | Line like **“Auto-renewable subscription”** visible near the price. | ☐ |
| 4.3 | **Auto-renew statement** | **“Subscription automatically renews unless canceled at least 24 hours before the end of the current period.”** on the **same screen**. | ☐ |
| 4.4 | **Disclosure** | **“Payment will be charged to your Apple ID account”** and **“You can manage or cancel in Apple ID settings”** on the subscription screen, **before** the Subscribe button. | ☐ |
| 4.5 | **Trial** (if offered) | Trial is **message/text** (e.g. “Free trial for N days, then $3.99 per month”); **not** a separate trial button. | ☐ |
| 4.6 | **Subscribe button** | Label is clear, e.g. **“Subscribe for $3.99/month.”** | ☐ |
| 4.7 | **Restore** | **“Restore Purchases”** directly under the Subscribe button. | ☐ |
| 4.8 | **App Store Connect** | Subscription metadata (price, trial, product name) **matches** what the app shows. | ☐ |

**Acceptance:** No ambiguity about billing; price at least as prominent as trial; matches App Store Connect.

---

## 5. Final validation

Before sign-off, confirm:

| # | Check | Pass? |
|---|--------|-------|
| 5.1 | No “kids / child / parent / teacher” **segregating** language in user-facing copy (internal role names OK). | ☐ |
| 5.2 | **Trial** is **message only**; no trial **buttons or links** (Submission 1.1). | ☐ |
| 5.3 | **No** “Guest User” or “Or continue as guest” **button** anywhere (Submission 1.1). | ☐ |
| 5.4 | **No** “For All Ages” **button** on the menu (Submission 1.1). | ☐ |
| 5.5 | **Student** does not see subscription, Restore, Help, or support; direct URLs redirect to /app (Submission 1.1). | ☐ |
| 5.6 | **Student** role cannot purchase or restore (UI hidden + server blocks). | ☐ |
| 5.7 | Subscription screen clearly states **price** and **auto-renew** on the same screen, near the CTA. | ☐ |
| 5.8 | Sandbox/test accounts **reset** (subscription data cleared) and re-tested. | ☐ |
| 5.9 | App behavior and claims **match** the App Store description (including role-agnostic “features” copy). | ☐ |

---

## Quick reference — Test accounts (subscription reset)

These 5 accounts should be cleared of subscription/entitlement data before running Task 0 and subscription tests:

- `skumar@tinfoxconsulting.com`
- `skumar+11@tinfoxconsulting.com`
- `skumar+22@tinfoxconsulting.com`
- `satya_785@yahoo.co.in`
- `skumar+01@tinfoxconsulting.com`

**Clear script:** `python scripts/clear_subscription_data_for_users.py` (run where `DATABASE_URL` is set for the target environment).

---

## Automated smoke tests (for devs)

From repo root:

**Syntax + full app + wireframe layout:**
```bash
pytest tests/test_smoke_syntax_and_app.py -v
```
Covers: app import, key template render (no Jinja/syntax errors), home/auth/subscription/help/terms/privacy routes, wireframe layout (stats 2×2, main actions 2×2, equal gap 16px, button height 56px, Start Quiz | Dashboard | Settings | Sign Out, What Now? modal).

**Compliance + restore + UI polish:**
```bash
pytest tests/test_apple_feb2025_compliance_smoke.py tests/test_restore_does_not_log_out.py tests/test_premium_restore_does_not_prompt_login_when_authed.py tests/test_ui_polish_smoke.py -v
```

These cover: kids copy removed in key templates, subscription price/auto-renew/student block in template, restore flow and timing. **Submission 1.1** (trial message only, no guest button, no “For All Ages” button, student hidden subscription/Help/support) and full role behavior still need **manual** checks with Student vs Parent/Teacher accounts on a real build.
