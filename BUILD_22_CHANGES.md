# BeeSmart Spelling Bee App — Build 22 Changes (Dec 31, 2025)

This doc summarizes exactly what changed in **Build 22** so it can be shared with the team.

---

## Summary

Build 22 is a version-alignment and Xcode submission readiness update.

- App version is now **22** across backend, config, UI badge, and validation tests.
- Production/public URL fallback now defaults to **`https://beesmartspelling.app`** (prevents accidental localhost links).
- iOS wrapper now shows **Version 22 / Build 22** in Xcode (**MARKETING_VERSION**/**CURRENT_PROJECT_VERSION**).

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

### Xcode Version/Build set to 22/22

- **File:** `mobile/ios/App/App.xcodeproj/project.pbxproj`
- **Changes (Debug + Release):**
  - `MARKETING_VERSION` updated from `20` → `22` *(Xcode “Version” field)*
  - `CURRENT_PROJECT_VERSION` updated from `21` → `22` *(Xcode “Build” field)*

---

## Docs

### Submission checklist updated

- **File:** `QUICK_START_XCODE_SUBMISSION.md`
- **Change:** Health endpoint checklist updated to reference v22 (and formatted as a code URL).

---

## Repo status

- Repo is clean (no uncommitted changes).
