# BeeSmart App — Freelancer Test Checklist (Apple Feb 2025 Compliance)

Use this checklist to verify app behavior, UI copy, and role permissions after the Apple Feb 2025 compliance work. Run on a **fresh install or Sandbox** build (TestFlight or local) after the backend has cleared subscription data for the test accounts.

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
- [ ] **Build:** Latest app build with Feb 2025 compliance changes installed (TestFlight or dev build).
- [ ] **Accounts:** At least one **Student**, one **Teacher**, and one **Parent** (or Admin) test account available.

---

## 0. Pre-Work — Data Reset (Task 0.1)

| # | Check | Expected | Pass? |
|---|--------|----------|-------|
| 0.1 | Log in as each of the 5 test emails above. | Each user is **non-subscribed** (no Premium). | ☐ |
| 0.2 | For each, open **Premium / Subscription** and confirm status. | Status says “Premium not active” or “Premium is not active yet” (no cached premium). | ☐ |
| 0.3 | As a **non-student** test user, tap **Restore Purchases** on the subscription screen. | Restore runs; if no prior purchase, message like “No purchases found” — **no crash, no infinite loading**. | ☐ |
| 0.4 | After restore (with clean data), re-open app. | User remains non-subscribed (clean state). | ☐ |

**Acceptance:** Users re-enter as non-subscribed, no cached premium, Restore works from a clean state.

---

## 1. Kids / Child Copy Removed (Task 1.1)

**Rule:** No visible copy implies the app is “for children.” No “Kids,” “Child,” “For children,” “Student (kid implied),” or COPPA-style phrasing in **user-facing** UI (tooltips, onboarding, empty states, help).

| # | Screen / Area | What to check | Expected | Pass? |
|---|----------------|----------------|----------|-------|
| 1.1 | **Main menu (home)** | Badge/label near Terms or premium area. | Says **“Filtered Content”** (not “Kid-Safe Content”). | ☐ |
| 1.2 | **Main menu** | Tooltip/title on that badge or word-filter hint. | Refers to **“appropriate vocabulary”** or “filtered” (not “age-appropriate content” or “kid-safe”). | ☐ |
| 1.3 | **Quiz screen** | Badge/label for word filtering (e.g. bottom or corner). | Says **“Filtered Words”** (not “Kid-Safe Words”). | ☐ |
| 1.4 | **Quiz screen** | Tooltip/title on that badge. | **“appropriate vocabulary”** or “filtered” (not “age-appropriate content”). | ☐ |
| 1.5 | **Terms of Use** | Opening or eligibility paragraph. | **“designed for learners and families”** and **“people of all ages”** (not “children and families” only). | ☐ |
| 1.6 | **Privacy Policy** | Main intro and “Families” section. | **“designed for learners and families”**; section heading **“Families & Learners”** (or similar); **no** “for children” / “COPPA” in user-facing bullets. | ☐ |
| 1.7 | **Registration / Sign-up** | Benefits or feature bullets. | **“Filtered content with automated word filtering”** (not “Kid-safe content”). | ☐ |
| 1.8 | **Help / FAQ** | Avatar or controls section. | **“Avatar Lock”** and **“Account managers”** (not “Parental Controls” / “Teachers and parents can lock student avatars”). | ☐ |

**Acceptance:** No visible copy implies the app is for children; app behavior matches a General Audience / non–Kids Category description.

---

## 2. “Parent & Teacher Approved” Replaced (Task 2.1)

**Rule:** Any in-app “features” or “why BeeSmart” blurb must be role-agnostic and age-neutral. Same copy can apply to all users.

| # | Location | What to check | Expected | Pass? |
|---|----------|----------------|----------|-------|
| 2.1 | **App Store listing** (if you can change it) | “Parent & Teacher Approved” block and bullets. | **Removed.** Replaced with bullets like: Ad-free learning, Structured skill progression, Progress tracking, Clean interface, Filtered vocabulary. | ☐ |
| 2.2 | **In-app “About” or “Features” or onboarding** (if any) | Any “PARENT & TEACHER APPROVED” or “Safe, ad-free / Educational / Age-appropriate / Easy to use / Track progress” block. | **Removed or rewritten** so it does **not** reference parent, teacher, child, student, or supervision. | ☐ |
| 2.3 | **Any upsell or premium pitch** | Bullets or short description. | No “parent/teacher approved” or “for kids/children”; focus on **features** (ad-free, progress, structure, etc.). | ☐ |

**Acceptance:** Copy does not segregate by role; same description can apply to all users; safe for General Audience.

---

## 3. Role Permissions — Student Restricted (Task 3.1)

**Rule:** Student role cannot initiate purchases, manage subscriptions, access external links/communication, share personal info, or change account/billing. Only Parent/Teacher (or Admin) can manage subscriptions.

### 3A. Student account

| # | Action | Expected | Pass? |
|---|--------|----------|-------|
| 3.1 | Log in as **Student**. Open **Premium / Subscription** (from menu or profile). | Subscription screen **does not** allow purchase or restore: message **“Subscriptions can only be managed by the account manager”**; **Subscribe** and **Restore** are **disabled** (grayed / not tappable). | ☐ |
| 3.2 | As Student, try to open any **external link** (e.g. “Terms,” “Privacy,” “Contact”) if your build restricts those for students. | Per product spec: either links are hidden or students see a blocked state / explanation (no unrestricted external browsing from student context). | ☐ |
| 3.3 | As Student, use **core learning only**: start a quiz, view progress, use word lists. | All **allowed**: core learning, content, read-only progress work. | ☐ |

### 3B. Parent / Teacher account

| # | Action | Expected | Pass? |
|---|--------|----------|-------|
| 3.4 | Log in as **Teacher** or **Parent**. Open **Premium / Subscription**. | Subscribe and Restore are **enabled**; user can initiate purchase and restore. | ☐ |
| 3.5 | As Teacher/Parent, tap **Restore Purchases**. | Restore runs (e.g. “No purchases found” or success); no crash. | ☐ |

### 3C. Backend / API (if you have access)

| # | Check | Expected | Pass? |
|---|--------|----------|-------|
| 3.6 | Call **Restore** (or equivalent) with a **Student** token and subscription product IDs. | Server **does not** apply subscription; response includes something like `student_subscription_blocked: true` and message that only the account manager can manage subscriptions. | ☐ |

**Acceptance:** Student cannot spend money or trigger IAP; reviewer cannot get a working IAP flow from a student account; no unrestricted external browsing from student context.

---

## 4. Subscription & Auto-Renew (Task 4.1 — Guideline 3.1.2)

**Rule:** Price and billing are clear; trial (if any) does not overshadow the recurring price; auto-renew is stated on the subscription screen, near the CTA.

| # | What to check | Expected | Pass? |
|---|----------------|----------|-------|
| 4.1 | **Subscription screen — primary price** | **“$3.99 per month”** (or your live price) is the **largest** price text. | ☐ |
| 4.2 | **Billing cadence** | Line like **“Auto-renewable subscription”** or **“Monthly”** is visible directly under or next to the price. | ☐ |
| 4.3 | **Auto-renew statement** | Words to the effect: **“Subscription automatically renews unless canceled at least 24 hours before the end of the current period.”** appear **on the same screen**, not only in a separate modal. | ☐ |
| 4.4 | **Disclosure placement** | **“Payment will be charged to your Apple ID account”** and **“You can manage or cancel in Apple ID settings”** appear **on the subscription screen**, **before** the Subscribe button. | ☐ |
| 4.5 | **If you offer a free trial** | Trial line says e.g. **“Free trial for N days, then $3.99 per month”**; **font/size is not larger** than the main price. | ☐ |
| 4.6 | **Subscribe button** | Label is clear, e.g. **“Subscribe for $3.99/month.”** | ☐ |
| 4.7 | **Restore** | **“Restore Purchases”** is **directly under** the Subscribe button. | ☐ |
| 4.8 | **App Store Connect** | Subscription metadata (price, trial, product name) **matches** what the app shows. | ☐ |

**Acceptance:** No ambiguity about billing; price is at least as prominent as trial; matches App Store Connect.

---

## 5. Final validation (Cursor checklist — your confirmation)

Before sign-off, confirm:

| # | Check | Pass? |
|---|--------|-------|
| 5.1 | No “kids / child / parent / teacher” **segregating** language in user-facing copy (internal role names in backend/admin are OK). | ☐ |
| 5.2 | **Student** role cannot purchase or restore subscription (UI disabled + server blocks application of subscription for students). | ☐ |
| 5.3 | **Student** cannot browse externally in a way that violates the spec (if you enforce “no external browsing from student context”). | ☐ |
| 5.4 | Subscription screen clearly states **price** and **auto-renew** on the same screen, near the CTA. | ☐ |
| 5.5 | Sandbox/test accounts have been **reset** (subscription data cleared) and re-tested. | ☐ |
| 5.6 | App behavior and claims **match** the App Store description (including any new role-agnostic “features” copy). | ☐ |

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

```bash
pytest tests/test_apple_feb2025_compliance_smoke.py tests/test_restore_does_not_log_out.py tests/test_premium_restore_does_not_prompt_login_when_authed.py tests/test_ui_polish_smoke.py -v
```

These cover: kids copy removed in key templates, subscription price/auto-renew/student block in template, restore flow and timing. Full role and IAP behavior still need **manual** checks with Student vs Parent/Teacher accounts on a real build.
