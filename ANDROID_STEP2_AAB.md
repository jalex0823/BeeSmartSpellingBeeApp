# Step 2 — Generate the Android App Bundle (AAB)

**Google Play does not accept IPA (iOS) or raw APK for production.** You must upload an **Android App Bundle (.aab)**.

---

## First-time setup (do once)

### 1. Install Node.js (required for sync)

npm/npx are needed to sync web assets into Android. Install Node.js LTS:

- **Option A (winget):**  
  `winget install OpenJS.NodeJS.LTS --accept-package-agreements`
- **Option B:** Download from https://nodejs.org/ and run the installer.

**Then close and reopen PowerShell** so `npm` and `npx` are in PATH.

### 2. Allow running PowerShell scripts (one-time)

If you see *"running scripts is disabled on this system"*:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Confirm with **Y**. (This allows your own scripts; still restricts unsigned downloads.)

### 3. Java (JDK 17)

The `build-aab.ps1` script can find or install Java via winget. If you prefer to set it yourself:

```powershell
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.17.10-hotspot"
$env:Path = "$env:JAVA_HOME\bin;" + $env:Path
```

---

## Why AAB only

| Format | Use |
|--------|-----|
| **AAB (Android App Bundle)** | ✅ **Required** for Play Console production (and recommended for internal/closed testing). |
| APK | ❌ Not accepted for new production releases. Use only for local install/testing. |
| IPA | ❌ iOS format; not used by Google Play. |

---

## Prerequisites

- **JDK 17** (or 11+) — Android Gradle Plugin 8.x uses JDK 17.
- **Android SDK** — Installed via Android Studio or command-line tools; `ANDROID_HOME` set.
- **Release keystore** (recommended) — For signed AAB. If missing, build still produces an AAB but it may need to be signed before upload (Play can sign for you in some cases; see Play Console).

---

## Generate the AAB (run on your machine)

**You need locally:** JDK 17+, Node.js (for sync), and scripts allowed (see First-time setup above).

### Quick build (all-in-one script)

From **PowerShell** (after first-time setup):

```powershell
cd "c:\Users\Jeff\OneDrive\Documents\GitHub\BeeSmartSpellingBeeApp\mobile"
npm run build
npx cap sync android
.\build-aab.ps1
```

If you get *"running scripts is disabled"*, run this once:  
`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`  
Or run the script with:  
`powershell -ExecutionPolicy Bypass -File .\build-aab.ps1`

### 1. Sync web assets (required once)

Only if you changed web content. From **repo root** in a terminal where **Node/npx** are in PATH:

```powershell
cd "c:\Users\Jeff\OneDrive\Documents\GitHub\BeeSmartSpellingBeeApp\mobile"
npm run build
npx cap sync android
```

(If your app loads from `server.url` only, you can skip this and go to step 2.)

### 2. Build the App Bundle

In a terminal where **Java** is in PATH (or `JAVA_HOME` is set), run:

**Windows (PowerShell or CMD):**

```powershell
cd "c:\Users\Jeff\OneDrive\Documents\GitHub\BeeSmartSpellingBeeApp\mobile\android"
.\gradlew.bat bundleRelease
```

**macOS/Linux:**

```bash
cd "path/to/BeeSmartSpellingBeeApp/mobile/android"
./gradlew bundleRelease
```

If you see **"JAVA_HOME is not set"**, install JDK 17 and set it, for example:

```powershell
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.x-hotspot"   # adjust path
$env:Path = "$env:JAVA_HOME\bin;$env:Path"
```

Then run `.\gradlew.bat bundleRelease` again.

### 3. Output location

The AAB is written to:

```
mobile\android\app\build\outputs\bundle\release\app-release.aab
```

Use **this file** when uploading to Google Play Console (Production or Internal testing).

---

## Optional: signed AAB

If you have a release keystore configured:

1. **`mobile/android/keystore.properties`** (do not commit; add to `.gitignore`):

   ```properties
   storePassword=***
   keyPassword=***
   keyAlias=upload
   storeFile=upload-keystore.jks
   ```

2. **`mobile/android/upload-keystore.jks`** — Your keystore file (do not commit).

With these in place, `bundleRelease` produces a **signed** AAB. If they are missing, the AAB is unsigned; Play Console may still accept it and use Play App Signing.

---

## Verify

- File exists: `mobile\android\app\build\outputs\bundle\release\app-release.aab`
- Size is reasonable (e.g. a few dozen MB for a web-view app).
- Upload to Play Console → **Release** → **Create new release** → upload `app-release.aab`.

---

## Related

- **ANDROID_READY_CURSOR.md** — Step 1: confirm Android-ready in Cursor.
- **ANDROID_PACKAGING_GUIDE.md** — Full build, signing, and submit steps.
- **GOOGLE_PLAY_ANDROID_FILES.md** — Version and package reference.
