# Subscription Logic Status & Clearing User Data (Jan 2026)

## Current state

- **Restore and premium application**  
  `/api/iap/restore` and `_apply_entitlement()` use `users.premium_member` and (where present) subscription product IDs. No subscription DB columns are required for restore to set premium.

- **Subscription page**  
  `/subscription` and `/premium` pass `subscription_monthly_usd`, `subscription_trial_days`, and `subscription_product_ids` to the template. Primary price ($3.99/month), “Auto-renewable subscription,” optional trial line, disclosure, and Restore are implemented per Apple 2.3.2 / 3.1.2.

- **Disabled on purpose (until migration)**  
  - `POST /api/validate-receipt` → **503** with `migration_needed: true`.  
  - `POST /apple-webhook` → **200** with `migration_needed: true` (no DB updates).  

  Receipt validation and webhook logic stay disabled until subscription columns exist. If the iOS app calls `/api/validate-receipt`, it will get 503 until you run the migration and re-enable the view.

## Confirmation for QA (Kumari) — clearing subscription data

**Is it valid per app business concept?** Yes. Clearing subscription data for these test users is valid and aligned with the app’s business: it resets their premium state in the backend so the same Sandbox/accounts can be reused for purchase and restore testing. It does not affect real paying users.

**How to run:** Use the script and options below. Run it on the backend (e.g. Digital Ocean) where `DATABASE_URL` points at that environment. Dry run first with `CLEAR_SUB_DRY_RUN=1` to confirm the five users without writing.

**“One subscription → all 3 roles” on same device:** This is documented in `APPLE_FEB2025_COMPLIANCE.md` (section 5). Current behavior (one Apple ID subscription on one device giving Parent, Teacher, and Student full access on that device) is **as-is** until the product owner confirms whether it’s intentional (family/device sharing) or should be limited to the purchasing account only.

---

## Clearing subscription data for specific users

Kumari requested clearing subscription data for these accounts (e.g. for re-testing purchase/restore):

- skumar@tinfoxconsulting.com  
- skumar+11@tinfoxconsulting.com  
- skumar+22@tinfoxconsulting.com  
- satya_785@yahoo.co.in  
- skumar+01@tinfoxconsulting.com  

**Script:** `scripts/clear_subscription_data_for_users.py`

**What it does**

- Sets `users.premium_member = False` for each given user.
- If subscription columns exist (after `migrate_subscription_fields`), clears `subscription_type`, `subscription_status`, `subscription_expires_at`, etc., and sets `subscription_status = 'none'`.
- Deletes `PurchaseRecord` rows for subscription product IDs for those users.

**How to run**

1. **Against your backend (e.g. Digital Ocean)**  
   Run where `DATABASE_URL` (or your app’s DB env) points at that backend:

   ```bash
   python scripts/clear_subscription_data_for_users.py
   ```

   Uses the five emails above by default.

2. **Dry run (no DB writes)**  
   ```bash
   CLEAR_SUB_DRY_RUN=1 python scripts/clear_subscription_data_for_users.py
   ```

3. **Other emails**  
   ```bash
   CLEAR_SUB_EMAILS="a@b.com,c@d.com" python scripts/clear_subscription_data_for_users.py
   ```

## If you see “subscription logic” or “boat load of errors”

1. **503 from `/api/validate-receipt`**  
   Expected while receipt validation is disabled. Options:  
   - Keep it disabled and rely on Restore + `premium_member` (current behavior), or  
   - Run `scripts/migrate_subscription_fields.py` on the DB, then re-enable the validate-receipt view and Apple webhook in `AjaSpellBApp.py`.

2. **Template / JS errors on `/subscription`**  
   The subscription template is fed `subscription_monthly_usd`, `subscription_trial_days`, and `subscription_product_ids` in both the success and exception paths of `subscription_page()`. If something still errors, the stack trace will point to the missing or wrong variable.

3. **Tests**  
   Restore and subscription UI are covered by:
   - `tests/test_restore_does_not_log_out.py`
   - `tests/test_ui_polish_smoke.py` (restore modals / timing)
   - `tests/test_premium_restore_does_not_prompt_login_when_authed.py`  
   All should pass; run them after any subscription changes.

## Apple 3.1.2 (subscription/trial clarity)

The in-app subscription screen is aligned with “billed amount most prominent”:

- Primary: “$X.XX per month” (largest).
- Secondary: “Auto-renewable subscription.”
- Trial (if `SUBSCRIPTION_TRIAL_DAYS` > 0): “Free trial for N days, then $X.XX per month” in smaller type.
- Required legal text appears on the same screen, before the purchase button.
- “Restore Purchases” is directly under the subscribe button.

Ensure App Store Connect (e.g. 7-day trial) matches what you set in `SUBSCRIPTION_TRIAL_DAYS` and in any copy that mentions trial length.
