# Freelancer Android Fixes

Summary of fixes for issues reported in freelancer screenshots.

---

## 1. Home screen not loading ("Web page not available" / localhost)

**Symptom:** App shows "The web page at http://localhost/ could not be loaded because: net::ERR_CLEARTEXT_NOT_PERMITTED"

**Cause:** The app was built without running `npx cap sync android`. Capacitor copies the production URL (`https://beesmartspelling.app`) into the Android app only during sync. Without it, the app uses the dev default (localhost).

**Fix:**
```bash
cd mobile
npx cap sync android
```
Then rebuild: `.\build-aab.ps1` or `gradlew bundleRelease` from `mobile/android/`.

If using **mobile-wrapper** project:
```bash
cd mobile-wrapper
npx cap sync android
```

---

## 2. Android splash screen should match iOS

**Symptom:** Android splash doesn't match iOS (yellow background + BeeSmart logo in laurel wreath).

**Fix:** Splash screens are generated from `static/BeeSmartCrestLogo1.png` (same as iOS). Run:
```bash
python generate_android_splash.py
```
This updates all three Android projects: `android/`, `mobile/android/`, `mobile-wrapper/android/`.

Then rebuild the app.

---

## 3. Android app icon

**Status:** Done. Uses BeeSmart Spelling Bee logo from `static/BeeSmart_AppIcon_512.png`.

To refresh icons after updating the source:
```bash
python scripts/generate_android_icons_from_source.py
```
