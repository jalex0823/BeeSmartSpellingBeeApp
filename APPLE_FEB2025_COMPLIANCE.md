# Apple Feb 2025 Compliance – BeeSmart

Summary of changes for updated Apple guidelines: role permissions, Kids Category alignment, and subscription disclosure (Guideline 3.1.2).

---

## Submission 1.1 (latest changes)

- **1.1 Trial as message only:** Removed trial **buttons/links** ("Start X-day Free Trial"). Trial is now **message only**: "A 7‑day introductory offer is included in the subscription." Register button says "Register" (no trial CTA). Subscription page already showed trial as text.
- **1.2 Guest User button removed:** Removed "Or continue as guest" and the Quick Guide line "Guest: Try the app without registering…". Users enter as guest automatically (no CTA). Backend guest sessions unchanged.
- **1.3 "For All Ages" button removed:** Removed the "For All Ages" badge from the menu (per screenshot 3). Safety message "for learners of all ages" remains as text.
- **2.1–2.2 Student access:** Subscription button, Restore Purchases button, Quick Help, User Guide, Admin Guide, and Support are **hidden for Student role** in the menu. Backend: `/help`, `/support`, `/guide`, `/admin-guide`, `/subscription` **redirect Students to /app**.
- **2.3 Student controlled by Parent/Teacher:** Code feature unchanged; after applying code, Student role is active and all subscription/Help/support UI is hidden (above).
- **2.4 Subscription-per-device:** Documented in section 5 below; WWDC 2025 Session 299 reference added. Product decision (intentional vs per-account) remains with stakeholder.

---

## 0. Pre-Work: Data Reset for Testing

**Task 0.1 — Clear subscription state (backend)**

- **Script:** `scripts/clear_subscription_data_for_users.py`
- **Default emails:** skumar@tinfoxconsulting.com, skumar+11@tinfoxconsulting.com, skumar+22@tinfoxconsulting.com, satya_785@yahoo.co.in, skumar+01@tinfoxconsulting.com
- **Run on backend:** `python scripts/clear_subscription_data_for_users.py` (with `DATABASE_URL` set for that environment).
- **Dry run:** `CLEAR_SUB_DRY_RUN=1 python scripts/clear_subscription_data_for_users.py`

---

## 1. Kids-Related Copy Removed/Neutralized

**Task 1.1 — Audit & remove kids-specific UI copy**

- **quiz.html:** "Kid-Safe Words" → "Filtered Words"; tooltip "age-appropriate content" → "appropriate vocabulary".
- **unified_menu.html:** "Kid-Safe Content" → "Filtered Content"; tooltip "age-appropriate content" → "appropriate vocabulary".
- **terms.html:** "designed for children and families" → "designed for learners and families… people of all ages".
- **privacy.html:** "designed for children and families" → "designed for learners and families"; "Children & Families" / COPPA phrasing → "Families & Learners" and privacy-practices wording only.
- **auth/register.html:** "Kid-safe content with automated filtering" → "Filtered content with automated word filtering".
- **help.html:** "Parental Controls: Teachers and parents can lock student avatars…" → "Avatar Lock: Account managers can lock avatar choices for linked accounts…".

Backend role names (student, teacher, parent, admin) stay internal; no kid-specific language in user-facing UI.

---

## 2. “Parent & Teacher Approved”–Style Copy

**Task 2.1 — Role-agnostic replacement**

Where you had (or would add) a “PARENT & TEACHER APPROVED” block with bullets like “Safe, ad-free experience”, “Educational content focused”, “Age-appropriate design”, etc., use role-agnostic, age-neutral copy instead.

**Do not:** Segregate by parent/teacher/child/student; imply approval or supervision hierarchy.

**Do:** Focus on features and experience.

**Example replacement (direction only, adjust tone as needed):**

- Ad-free learning experience  
- Structured skill progression  
- Progress tracking and insights  
- Clean, distraction-free interface  
- Content filtered for appropriate vocabulary  

Use this style in App Store description, in-app “About” or “Features” sections, and any place that previously said “Parent & Teacher Approved” or similar.

---

## 3. Role Permissions (Student Restrictions)

**Task 3.1 — Enforce student-role limits (backend + UI)**

**Student role (restricted):**

- Must **not** be able to: initiate purchases, manage subscriptions, access external links/communication, share personal info, change account or billing settings.
- Allowed: core learning, content consumption, read-only progress.

**Parent/Teacher (and admin):** Only roles that can initiate purchases and manage subscriptions.

**Implementation:**

- **Backend (`AjaSpellBApp.py`):**
  - **`/api/iap/restore`:** If the authenticated user’s role is `student`, subscription-like product IDs are not applied. Response includes `student_subscription_blocked: true` and message: "Subscriptions can only be managed by the account manager."
  - **`/subscription` and `/premium`:** `subscription_page()` passes `student_cannot_purchase=True` when `current_user.role == 'student'`.
- **UI (`subscription.html`):** When `student_cannot_purchase` is true, the subscription screen shows the message “Subscriptions can only be managed by the account manager…” and the Subscribe and Restore buttons are disabled.

Students can open the subscription page but cannot complete purchase or restore subscription entitlements.

---

## 4. Subscription & Auto-Renew (Guideline 3.1.2)

**Task 4.1 — Price and auto-renew clarity**

**Current subscription screen (`/subscription`, `subscription.html`):**

- **Primary:** “$3.99 per month” (largest).
- **Secondary:** “Auto-renewable subscription”.
- **Trial (if `SUBSCRIPTION_TRIAL_DAYS` > 0):** “Free trial for N days, then $3.99 per month” in smaller type so price remains most prominent.
- **Disclosure (same screen, before purchase button):**
  - “Payment will be charged to your Apple ID account.”
  - “Subscription automatically renews unless canceled at least 24 hours before the end of the current period.”
  - “You can manage or cancel your subscription in your Apple ID settings.”
- **CTA:** “Subscribe for $3.99/month”.
- **Restore:** “Restore Purchases” directly under the subscribe button.

Ensure App Store Connect (e.g. 7-day trial, price, product name) matches this and `SUBSCRIPTION_TRIAL_DAYS` where used.

---

## 5. One subscription → all roles on same device (product clarification)

**Observed behavior:** One Apple ID subscription on one iOS device gives Parent, Teacher, and Student accounts on that device full premium access (same subscription plan for all three roles).

**Technical note:** Premium is stored per user (`users.premium_member`). If the iOS app or restore flow applies the same Apple ID receipt to every BeeSmart account that restores on that device, each of those accounts gets `premium_member = True`—which explains “same subscription for all 3 roles” on the same device.

**Product decision (for stakeholder):**

- **Option A — Intentional (family/device sharing):** One subscription per device or per Apple ID is the intended model; all roles on that device sharing the same Apple ID (or device-level restore) are meant to have premium. No code change needed; document as intended.
- **Option B — Per-account only:** Only the account that completed the purchase (or a designated “account manager” role) should have premium; other roles on the same device should not get premium from that one purchase. That would require backend/iOS changes (e.g. only apply entitlement to the purchasing user or to Parent/Teacher when restored by them, not to Student when restored on same device).

Until the product owner confirms, treat current behavior as **as-is** and document that the “disconnect” (one subscription → all roles) is a known behavior and a product clarification item, not a bug.

**Reference:** [WWDC 2025 — Session 299](https://developer.apple.com/videos/play/wwdc2025/299/) (subscription and in-app purchase guidance).

---

## Final Validation Checklist

Before marking complete:

- [ ] No “kids / child / parent / teacher” segregating language in user-facing copy.
- [ ] Student role cannot purchase or restore subscription (server + UI).
- [ ] Subscription screen clearly shows price and auto-renew wording.
- [ ] Sandbox accounts reset and re-tested with `clear_subscription_data_for_users.py`.
- [ ] App behavior matches App Store description (including any “Parent & Teacher Approved” replacement text above).
