# Google Play – Android Files Reference

Quick reference for **which files to update** when preparing a release for Google Play (Play Console). Android package files live in **`mobile/android/`**.

## Files to update per release

| File | What to update | Notes |
|------|----------------|--------|
| **`mobile/android/app/build.gradle`** | `versionCode`, `versionName` | **Required every upload.** `versionCode` must increase; `versionName` is user-facing (e.g. 5.0, 5.1). |
| **`mobile/android/app/src/main/res/values/strings.xml`** | `app_name`, `title_activity_main` | Optional; only if changing display name. |
| **`mobile/capacitor.config.ts`** | `appId`, `server.url` | Only when changing app id or backend URL. |

## Version and package (source of truth)

**Location:** `mobile/android/app/build.gradle`

- **versionCode** – Integer; must be **greater** than the last uploaded build (e.g. 5 → 6).
- **versionName** – String shown to users (e.g. `"5.0"`, `"5.1"`, `"6.0"`).
- **applicationId** – Package name for Play Console (do not change after first publish). Current: **`com.beesmart.spelling`**.

**Note:** `mobile/STORE_CHECKLIST.md` lists Android Application ID as `app.beesmartspelling`. The **actual** value used by the app is in `build.gradle`: **`com.beesmart.spelling`**. Use the value from `build.gradle` when creating or matching the app in Play Console.

## Optional metadata

- **AndroidManifest.xml** – `mobile/android/app/src/main/AndroidManifest.xml`  
  Uses `@string/app_name` and permissions; no version fields. Edit only for permissions or manifest entries.
- **App name on device** – `mobile/android/app/src/main/res/values/strings.xml` → `app_name`, `title_activity_main`.

## Build and artifact

- **Output AAB:** `mobile/android/app/build/outputs/bundle/release/app-release.aab`  
  Upload this file to Play Console.
- **Signing:** Uses `mobile/android/keystore.properties` and `mobile/android/upload-keystore.jks` when present (see **ANDROID_PACKAGING_GUIDE.md**).

## Related docs

- **ANDROID_PACKAGING_GUIDE.md** – Full build, signing, and submit steps.
- **mobile/STORE_CHECKLIST.md** – Store listing, assets, compliance.
- **mobile/BRANDING.md** – Icons and graphics.
- **store/Release_*.md**, **store/PlayStoreListing.md** – Release checklists and listing copy.
