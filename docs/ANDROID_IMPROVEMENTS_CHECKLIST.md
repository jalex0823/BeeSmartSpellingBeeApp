# BeeSmart Spelling – Android Improvements Checklist

This checklist maps the **BeeSmart Spelling Android Improvements** requirements to the repo. Use it to verify releases and onboarding.

---

## 1. Gradle – variables.gradle (Android ≤ 13)

**Requirement:** Update `ext { }` in all Android variables.gradle files for supporting Android ≤ 13.

**Status:** Done in all three locations.

| File | Status |
|------|--------|
| `android/variables.gradle` | Updated |
| `mobile/android/variables.gradle` | Updated |
| `mobile-wrapper/android/variables.gradle` | Updated |

**Spec (all three files):**

```gradle
ext {
  buildToolsVersion = "34.0.0"
  minSdkVersion = 22
  compileSdkVersion = 36
  targetSdkVersion = 35
  androidxActivityVersion = '1.7.0'
  androidxAppCompatVersion = '1.6.1'
  androidxCoordinatorLayoutVersion = '1.2.0'
  androidxCoreVersion = '1.10.0'
  androidxFragmentVersion = '1.5.6'
  coreSplashScreenVersion = '1.0.0'
  androidxWebkitVersion = '1.6.1'
  junitVersion = '4.13.2'
  androidxJunitVersion = '1.1.5'
  androidxEspressoCoreVersion = '3.5.1'
  cordovaAndroidVersion = '10.1.1'
}
```

If you add a new Android module, add a `variables.gradle` (or shared `ext` block) using the same values.

---

## 2. Python + Google Play Auto-Renewal Subscriptions

**Requirement:** Backend must verify and manage Google Play subscriptions; never trust the app alone.

| Item | Status | Where in repo |
|------|--------|----------------|
| User buys in app → app gets purchaseToken + productId | Done | Native Android billing + `native-iap-bridge.js` |
| App sends token → Python backend | Done | `POST /api/android/subscription/verify` |
| Python verifies with Google Play Developer API | Done | `iap_verification.py` → `verify_google_purchase()` |
| Backend confirms payment, stores expiry, enables premium | Done | `AjaSpellBApp.py` verify route + `PurchaseRecord` + user flags |
| Use expiryTimeMillis, autoRenewing, paymentState, cancelReason | Done | Read from API response; returned in verify JSON |
| Real-time developer notifications (RTDN) | Done | `POST /api/android/rtdn` (Pub/Sub push) |
| Database: user_id, product_id, purchase_token, status (expiry) | Done | `PurchaseRecord` model; expiry on User + in raw_payload |
| Security: never trust app; verify token/package/product server-side | Done | All verification in Python; package/product from config/env |

**Config:** `config/android.json` (packageName, subscriptionProductIds, featureFlags).

**Setup guide:** `docs/ANDROID_PLAYSTORE_SUBSCRIPTIONS.md` (Play Console, service account, env vars, verify + RTDN).

---

## 3. Google Play vs Apple IAP

**Requirement:** Android uses only Google Play Billing; iOS uses only Apple IAP.

| Item | Status |
|------|--------|
| Android app uses Google Play Billing only | Done (no Apple IAP on Android) |
| iOS app uses Apple IAP only | Unchanged |
| Android product IDs (e.g. premium_monthly) separate from Apple | Done in `config/android.json` and subscription UI |

---

## 4. Setup Auto-Renew Subscription in Play Console

**Requirement:** Create and publish subscription in Google Play Console.

**Status:** Documented; must be done in Play Console (not in repo).

See **`docs/ANDROID_PLAYSTORE_SUBSCRIPTIONS.md`** for:

- Create subscription (Monetize → Products → Subscriptions)
- Set pricing / trials
- Activate and publish (e.g. internal test track)
- Link service account (Setup → API access)

---

## 5. Signed AAB & Gradle build

**Requirement:** Build a signed Android App Bundle (AAB) for Play Store upload; Gradle must run (Java 21–compatible).

| Item | Status | Where |
|------|--------|--------|
| variables.gradle (Android ≤ 13) | Done | All three: `android/`, `mobile/android/`, `mobile-wrapper/android/` |
| Gradle wrapper (Java 21 compatible) | Done | `mobile/android/gradle/wrapper/gradle-wrapper.properties` → Gradle 8.10+ |
| Keystore + keystore.properties | Done | `mobile/android/upload-keystore.jks`, `keystore.properties` (gitignored) |
| Release signing in build | Done | `mobile/android/app/build.gradle` uses signingConfigs.release when keystore present |
| Signed AAB output | Done | `mobile/android/app/build/outputs/bundle/release/app-release.aab` |

**To build signed AAB again:** From `mobile/android`, set `JAVA_HOME` to your JDK (e.g. Android Studio JBR), then run `.\gradlew.bat bundleRelease`. Or use `mobile/build-aab.ps1` after signing is configured.

**Important:** If the home screen shows "Web page not available" / localhost, run `npx cap sync android` from `mobile/` before building. The app loads from `https://beesmartspelling.app` via Capacitor's `server.url`; that config is copied into the built app only during sync. See `docs/PRODUCTION_URL_AND_ICONS.md`.

---

## Quick reference – key files

| Purpose | File(s) |
|---------|--------|
| Gradle versions (Android ≤ 13) | `android/variables.gradle`, `mobile/android/variables.gradle`, `mobile-wrapper/android/variables.gradle` |
| Android app config | `config/android.json` |
| Google Play verification (Python) | `iap_verification.py` (`verify_google_purchase`) |
| Verify endpoint | `AjaSpellBApp.py`: `/api/android/subscription/verify` |
| RTDN webhook | `AjaSpellBApp.py`: `/api/android/rtdn` |
| Purchase records | `models.py`: `PurchaseRecord` |
| Subscription + Play copy (UI) | `templates/subscription.html` |
| Play Store setup + env vars | `docs/ANDROID_PLAYSTORE_SUBSCRIPTIONS.md` |
| Signed AAB build | `mobile/android/` → `gradlew bundleRelease`; output: `app/build/outputs/bundle/release/app-release.aab` |
| Keystore (do not commit) | `mobile/android/upload-keystore.jks`, `keystore.properties` |
