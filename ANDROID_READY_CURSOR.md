# Step 1 — Confirm Your App Is Android-Ready (Cursor)

Before touching Google Play, ensure the project targets Android correctly. Use this in Cursor when preparing for release.

---

## Cursor instruction (copy-paste)

```
Prepare the project for Android (Google Play) release.

- Ensure Android build target is enabled.
- Use Android App Bundle (AAB), not APK, for Play Console uploads.
- Verify all platform-specific configs: package name, permissions, icons.
- Keep feature parity with iOS release.
```

---

## Key Android requirements (verified in this project)

| Requirement | Status | Location |
|-------------|--------|----------|
| **Package name** (reverse domain, immutable) | ✅ `com.beesmart.spellingbee` | `mobile/android/app/build.gradle` → `applicationId`; `mobile/capacitor.config.ts` → `appId`; `config/android.json` → `packageName` |
| **Target SDK** | ✅ Android 14 (API 34) | `mobile/android/variables.gradle` → `targetSdkVersion` |
| **Compile SDK** | ✅ 34 | `mobile/android/variables.gradle` → `compileSdkVersion` |
| **64-bit support** | ✅ Default (no abiFilters excluding arm64-v8a) | AGP includes 64-bit; no override in `app/build.gradle` |
| **No debug in release** | ✅ `debuggable false` in release | `mobile/android/app/build.gradle` → `buildTypes.release` |
| **AAB output** | ✅ Use `bundleRelease` | `cd mobile/android` then `.\gradlew bundleRelease` → `app/build/outputs/bundle/release/app-release.aab` |
| **Icons** | ✅ mipmap-hdpi … xxxhdpi | `mobile/android/app/src/main/res/` |
| **Permissions** | ✅ INTERNET, BILLING | `mobile/android/app/src/main/AndroidManifest.xml` |

---

## Build commands (reference)

- **AAB (for Play Console):**  
  `cd mobile/android` → `.\gradlew bundleRelease`  
  Output: `app\build\outputs\bundle\release\app-release.aab`

- **APK (local/testing only):**  
  `.\gradlew assembleRelease`  
  Output: `app\build\outputs\apk\release\app-release.apk`

---

## Related docs

- **ANDROID_STEP2_AAB.md** — Step 2: Generate the Android App Bundle (AAB); Google does not accept IPA or APK for production.
- **GOOGLE_PLAY_ANDROID_FILES.md** — Which files to update per release (versionCode, versionName).
- **ANDROID_PACKAGING_GUIDE.md** — Full build, signing, and submit steps.
