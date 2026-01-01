# BeeSmart Spelling Bee App — Build 22 Changes (Dec 31, 2025)

This doc summarizes exactly what changed in **Build 22** so it can be shared with the team.

---

## Summary

Build 22 is a version-alignment and Xcode submission readiness update.

- App version is now **22** across backend, config, UI badge, and validation tests.
- Production/public URL fallback now defaults to **`https://beesmartspelling.app`** (prevents accidental localhost links).
- iOS wrapper now shows **Version 24.5 / Build 27** in Xcode (**MARKETING_VERSION**/**CURRENT_PROJECT_VERSION**).

> Note: “Build 22” in this document refers to the **web/backend app version alignment**. The iOS wrapper uses a separate Xcode Marketing Version / Build Number for App Store Connect submission.

---

## IAP Restore button fix (Jan 1, 2026)

- **Files:** `templates/unified_menu.html`, `templates/subscription.html`
- **Problem:** In the native wrapper, the Capacitor plugin exposes `restorePurchases()` (native export), while some web UI logic only attempted `window.BeeSmartIAP.restore()`.
- **Fix:** Restore now supports **both** `restore()` and `restorePurchases()` so tapping “Restore Purchases” always initiates the native restore flow when available (and then re-syncs owned products via `/api/iap/restore`).

---

## Backend (Flask)

### Version bump

- **File:** `AjaSpellBApp.py`
- **Change:** `APP_VERSION` updated from `"1.7"` → `"22"`
- **Impact:** `/health` now reports version `22`.

### Public base URL fallback hardened to production

- **File:** `AjaSpellBApp.py`
- **Change:** `_public_base_url()` fallback updated from `http://localhost:5000` → `https://beesmartspelling.app`
- **Why:** Prevents accidental localhost links in outbound emails/links if `APP_BASE_URL` isn’t set.

---

## Config

### Version alignment

- **File:** `config.py`
- **Change:** `APP_VERSION` updated from `'1.6'` → `'22'`

---

## Web UI

### Visible version badge updated

- **File:** `templates/unified_menu.html`
- **Change:** version badge content updated from `v1.6` → `v22`

### JS cache-buster/version string updated

- **File:** `templates/unified_menu.html`
- **Changes:**
  - `const V='v1.6-'+Date.now();` → `const V='v22-'+Date.now();`
  - `versionBadge.textContent = 'v1.6';` → `versionBadge.textContent = 'v22';`

---

## Tests / Validation

### Validation suite updated for Build 22

- **File:** `test_v15_complete_validation.py`
- **Changes:**
  - Docstring updated from “v1.6” → “v22”
  - Homepage UI check now expects `v22`
  - Health check expectation updated from `'1.7'` → `'22'`

---

## iOS / Xcode Wrapper

### Xcode Version/Build set to 24.5/25

- **File:** `mobile/ios/App/App.xcodeproj/project.pbxproj`
- **Changes (Debug + Release):**
  - `MARKETING_VERSION` updated from `22` → `24.5` *(Xcode “Version” field)*
  - `CURRENT_PROJECT_VERSION` updated from `22` → `27` *(Xcode “Build” field)*

### IAP (TestFlight/App Store Connect) — Capacitor plugin export fix

This was the root cause behind device probes showing `capacitor: true` but `BeeSmartIAP: false` in `window.Capacitor.Plugins`.

- **Files:**
  - `mobile/ios/App/App/BeeSmartIAPPlugin.swift`
  - `mobile/ios/App/App/BeeSmartIAPPlugin.m` *(new)*
  - `mobile/ios/App/App.xcodeproj/project.pbxproj`
- **Change:** Added an Objective-C Capacitor v5 `CAP_PLUGIN` export bridge so the native StoreKit2 plugin is visible to the web UI as:
  - `window.Capacitor.Plugins.BeeSmartIAP`
  - (and then wrapped by the web layer as `window.BeeSmartIAP`)
- **Why:** In Capacitor v5, the plugin must be exported via the Obj-C bridge macros **and** the bridge file must be compiled into the target.
- **Key verification in Xcode build logs:** you should see `CompileC ... BeeSmartIAPPlugin.m ... (in target 'App')`.
- **Breadcrumb (git):**
  - Commit that added/exported the bridge and ensured it’s in target sources: `43e57a6` — "iOS: export BeeSmartIAP Capacitor plugin"

---

## App Store Connect build — breadcrumbs (what to do next)

These are operational notes for producing a submission-ready build and confirming the IAP bridge is present.

### 1) Create an Archive (Release, device)

- Xcode: **Product → Archive** (scheme: `App`, configuration: Release)
- Expected: Archive succeeds and includes the `BeeSmartIAP` plugin export.

### 2) Distribute to App Store Connect

- Xcode Organizer: **Distribute App → App Store Connect → Upload**
- Versioning should show **Version 24.5 / Build 27** for the iOS wrapper.

### 3) After TestFlight install, run the on-device probe

Expected probe result after this fix:

- `window.Capacitor` exists
- `window.Capacitor.Plugins.BeeSmartIAP` exists
- Methods exist:
  - `purchase`
  - `restorePurchases`
  - `getOwnedProducts`

If the plugin still doesn’t appear:

- Confirm `BeeSmartIAPPlugin.m` is in **Build Phases → Compile Sources** for the `App` target.
- Confirm the build being tested is the new upload (not an older TestFlight build cached on device).

---

## DigitalOcean App Platform — Apple IAP env vars (required for real verification)

If TestFlight purchases/restore run but premium **doesn’t unlock**, check:

- `https://beesmartspelling.app/health/iap`

If it shows `verification_mode: "mock"` or `iap.apple.configured: false`, the production backend is missing Apple credentials.

### Where to add these

In DigitalOcean **App Platform → Settings → Environment Variables**, add these to the **web/service component that runs Flask** (the one serving `AjaSpellBApp.py`).

Make the private key a **Secret/Encrypted** env var.

### Env vars to add (copy/paste)

- `APPLE_ISSUER_ID` = `69a6de81-e6a6-47e3-e053-5b8c7c11a4d1`
- `APPLE_KEY_ID` = `4267TG524Q`
- `APPLE_APP_BUNDLE_ID` = `com.altech.beesmartspelling`

If your platform (like DigitalOcean App Platform) won’t accept multiline env vars, use the **single-line** option:

- `APPLE_PRIVATE_KEY_B64` = *(base64 of the full `.p8` PEM contents)*

Or, if multiline works for you:

- `APPLE_PRIVATE_KEY` = *(paste the full `.p8` contents including the BEGIN/END lines; keep newlines)*

#### `APPLE_PRIVATE_KEY` format example

Do **not** add quotes. Multiline is correct.

```text
-----BEGIN PRIVATE KEY-----
PASTE_YOUR_KEY_CONTENTS_HERE
-----END PRIVATE KEY-----
```

#### Generate `APPLE_PRIVATE_KEY_B64` (single line)

The repo includes a helper script:

- `scripts/encode_apple_p8_to_env_b64.py`

Run it locally with your downloaded `.p8`:

```bash
python3 scripts/encode_apple_p8_to_env_b64.py ~/Downloads/AuthKey_4267TG524Q.p8
```

Copy the output and paste it as the value of `APPLE_PRIVATE_KEY_B64` in App Platform.

### Deploy + verify

After saving env vars, **redeploy** the App Platform component.

Re-check `https://beesmartspelling.app/health/iap`:

- `iap.apple.configured` should be `true`
- it should no longer report missing `APPLE_ISSUER_ID` / `APPLE_KEY_ID` / `APPLE_APP_BUNDLE_ID` / `APPLE_PRIVATE_KEY`

---

## Docs

### Submission checklist updated

- **File:** `QUICK_START_XCODE_SUBMISSION.md`
- **Change:** Health endpoint checklist updated to reference v22 (and formatted as a code URL).

---

## Repo status

- Repo should have changes in:
  - `mobile/ios/App/App.xcodeproj/project.pbxproj`
  - `BUILD_22_CHANGES.md`

If you’ve committed these changes, this section should be updated to reflect a clean state.
