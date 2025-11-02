# Android Studio Packaging Guide - BeeSmart Spelling Bee

## Prerequisites Checklist
✅ Android Studio installed (downloading now)
✅ Capacitor project structure exists (`mobile/` folder)
✅ Flask backend deployed on Railway
⬜ Android SDK installed (via Android Studio)
⬜ Release keystore generated
⬜ App signed and ready for Play Store

---

## Step 1: Complete Android Studio Setup

### After Download Completes:
1. **Run Android Studio installer** (likely in Downloads folder)
2. **Choose Custom Install** and ensure these are selected:
   - Android SDK
   - Android SDK Platform (API 33+)
   - Android SDK Build-Tools
   - Android Emulator (optional for testing)
   - Android SDK Platform-Tools
   - Android SDK Command-line Tools

3. **Set Environment Variables** (PowerShell as Admin):
```powershell
# Add to your system PATH
$androidHome = "C:\Users\jeff\AppData\Local\Android\Sdk"
[Environment]::SetEnvironmentVariable("ANDROID_HOME", $androidHome, "User")
$path = [Environment]::GetEnvironmentVariable("Path", "User")
$newPath = "$path;$androidHome\platform-tools;$androidHome\tools;$androidHome\tools\bin"
[Environment]::SetEnvironmentVariable("Path", $newPath, "User")

# Verify (restart PowerShell first)
adb --version
```

---

## Step 2: Open Your Project in Android Studio

### Option A: Via Command Line
```powershell
cd "c:\Users\jeff\Dropbox\BeeSmartSpellingBeeApp\mobile"
npm run cap:open:android
```

### Option B: Via Android Studio
1. Open Android Studio
2. **File → Open**
3. Navigate to: `c:\Users\jeff\Dropbox\BeeSmartSpellingBeeApp\mobile\android`
4. Click **OK** (Android Studio will recognize it as a Gradle project)

---

## Step 3: Configure Backend URL

Your app needs to connect to your Railway deployment:

**Edit:** `mobile/capacitor.config.ts`
```typescript
import { CapacitorConfig } from '@capacitor/core';

const config: CapacitorConfig = {
  appId: 'app.beesmartspelling',
  appName: 'BeeSmart Spelling Bee',
  webDir: 'dist',
  server: {
    // Point to your Railway deployment
    url: 'https://beesmartspelling.app',  // OR your Railway URL
    cleartext: false,
    androidScheme: 'https'
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: "#FFD700",
      showSpinner: false
    }
  }
};

export default config;
```

**Important:** Update `https://beesmartspelling.app` to your actual Railway deployment URL if different.

---

## Step 4: Sync Capacitor Project

```powershell
cd "c:\Users\jeff\Dropbox\BeeSmartSpellingBeeApp\mobile"

# Install dependencies if needed
npm install

# Sync web assets to Android project
npm run cap:sync
```

This copies your web app files into the Android project structure.

---

## Step 5: Generate Release Keystore

**CRITICAL:** You need a keystore to sign your app for the Play Store.

```powershell
cd "c:\Users\jeff\Dropbox\BeeSmartSpellingBeeApp\mobile\android"

# Generate keystore (one-time setup)
keytool -genkey -v -keystore upload-keystore.jks -keyalg RSA -keysize 2048 -validity 10000 -alias upload

# You'll be prompted for:
# - Keystore password (SAVE THIS!)
# - Key password (SAVE THIS!)
# - Your name/organization details
```

**SAVE THESE SECURELY:**
- Keystore file: `upload-keystore.jks`
- Alias: `upload`
- Passwords: Store in password manager

---

## Step 6: Configure Signing in Android Studio

1. In Android Studio, go to **Build → Generate Signed Bundle / APK**
2. Select **Android App Bundle** (recommended) or **APK**
3. Click **Next**
4. **Key store path:** Browse to your `upload-keystore.jks`
5. Enter your keystore password and key password
6. **Build Variants:** Select `release`
7. Check **V1 (Jar Signature)** and **V2 (Full APK Signature)**
8. Click **Finish**

### Alternative: Configure in Gradle

**Edit:** `mobile/android/app/build.gradle`

Add before `android {`:
```gradle
def keystorePropertiesFile = rootProject.file("keystore.properties")
def keystoreProperties = new Properties()
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}
```

Add inside `android { ... }` after `buildTypes {`:
```gradle
signingConfigs {
    release {
        keyAlias keystoreProperties['keyAlias']
        keyPassword keystoreProperties['keyPassword']
        storeFile file(keystoreProperties['storeFile'])
        storePassword keystoreProperties['storePassword']
    }
}
buildTypes {
    release {
        signingConfig signingConfigs.release
        minifyEnabled false
        proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
    }
}
```

**Create:** `mobile/android/keystore.properties` (ADD TO .gitignore!)
```properties
storePassword=YOUR_KEYSTORE_PASSWORD
keyPassword=YOUR_KEY_PASSWORD
keyAlias=upload
storeFile=upload-keystore.jks
```

---

## Step 7: Build Release AAB (Android App Bundle)

### In Android Studio:
1. **Build → Generate Signed Bundle / APK**
2. Select **Android App Bundle**
3. Follow signing prompts
4. Output: `mobile/android/app/release/app-release.aab`

### Via Command Line:
```powershell
cd "c:\Users\jeff\Dropbox\BeeSmartSpellingBeeApp\mobile\android"
.\gradlew bundleRelease
```

Output location: `app\build\outputs\bundle\release\app-release.aab`

---

## Step 8: Test Before Submitting

### Option A: Internal Testing (Recommended)
1. Upload AAB to Google Play Console → Internal Testing
2. Add test users
3. Install via Play Store link on real device

### Option B: Local APK Testing
Build APK instead of AAB:
```powershell
.\gradlew assembleRelease
```

Install on device:
```powershell
adb install app\build\outputs\apk\release\app-release.apk
```

---

## Step 9: Update Version for Play Store

**Edit:** `mobile/android/app/build.gradle`
```gradle
android {
    defaultConfig {
        versionCode 1        // Increment for each upload (1, 2, 3...)
        versionName "1.0.0"  // User-facing version
    }
}
```

**Important:** 
- `versionCode` must increase with each Play Store upload
- `versionName` is what users see (e.g., 1.0.0, 1.0.1, 1.1.0)

---

## Step 10: Prepare Play Console Assets

Before submitting, gather these assets:

### Required:
- **App Bundle (.aab)** ✅
- **App Icon:** 512×512 PNG (high-res)
- **Feature Graphic:** 1024×500 PNG
- **Screenshots:** 
  - Phone: At least 2 (max 8)
  - 7" Tablet: At least 2 (max 8)
  - 10" Tablet: At least 2 (max 8)

### Content:
- **Short Description:** Max 80 chars
- **Full Description:** Max 4000 chars
- **Privacy Policy URL:** Required for apps with user data
- **Contact Email**
- **Content Rating Questionnaire**

### Checklist Files:
- See `mobile/STORE_CHECKLIST.md` for complete details
- See `mobile/BRANDING.md` for asset specifications

---

## Step 11: Submit to Google Play Console

1. **Go to:** https://play.google.com/console
2. **Create Application** (if not already done)
3. **App Details:**
   - Name: BeeSmart Spelling Bee
   - Package: app.beesmartspelling
   - Category: Education
4. **Production → Create Release**
5. **Upload AAB:** Drag `app-release.aab`
6. **Release Notes:** Describe features
7. **Content Rating:** Complete questionnaire (kid-safe)
8. **Pricing:** Free or Paid
9. **Submit for Review**

---

## Troubleshooting

### "Android SDK not found"
```powershell
# Set ANDROID_HOME
$env:ANDROID_HOME = "C:\Users\jeff\AppData\Local\Android\Sdk"
```

### "Keystore not found"
Check path in `keystore.properties` is relative to `android/` folder:
```
storeFile=upload-keystore.jks  # Not ../upload-keystore.jks
```

### "Build failed: Duplicate resources"
Run clean build:
```powershell
.\gradlew clean
.\gradlew bundleRelease
```

### "Cleartext traffic not permitted"
Ensure `capacitor.config.ts` has:
```typescript
server: {
    androidScheme: 'https'
}
```

---

## Quick Reference Commands

```powershell
# Navigate to project
cd "c:\Users\jeff\Dropbox\BeeSmartSpellingBeeApp\mobile"

# Sync Capacitor
npm run cap:sync

# Open in Android Studio
npm run cap:open:android

# Build Release AAB
cd android
.\gradlew bundleRelease

# Build Release APK (testing)
.\gradlew assembleRelease

# Install on device
adb install app\build\outputs\apk\release\app-release.apk

# Check connected devices
adb devices
```

---

## Next Steps After Installation

1. ✅ Complete Android Studio installation
2. ✅ Open project in Android Studio
3. ✅ Generate keystore
4. ✅ Configure backend URL in `capacitor.config.ts`
5. ✅ Build signed AAB
6. ✅ Test on device/emulator
7. ✅ Prepare Play Store assets
8. ✅ Submit to Play Console

**Current Status:** Waiting for Android Studio installation to complete.

**When Ready:** Run `npm run cap:open:android` from the `mobile` folder!
