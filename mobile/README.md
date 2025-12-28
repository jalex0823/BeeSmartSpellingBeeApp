# Mobile Wrapping – BeeSmart Spelling App

This folder contains everything needed to package the BeeSmart Spelling Bee Flask app for the Google Play Store using Capacitor.

## 🚀 Quick Start

**After Android Studio installation completes:**

```powershell
cd "c:\Users\jeff\Dropbox\BeeSmartSpellingBeeApp\mobile"
.\quick-start.ps1
```

The interactive wizard guides you through:
1. Keystore generation
2. Signing configuration
3. Building release packages

See **STATUS.txt** for current setup status.

---

## 📋 Documentation Files

- **STATUS.txt** - Current setup status and next steps
- **QUICK_REFERENCE.md** - Command cheat sheet
- **SETUP_COMPLETE.md** - Detailed configuration summary
- **ANDROID_PACKAGING_GUIDE.md** (in parent folder) - Complete guide
- **STORE_CHECKLIST.md** - Play Store submission checklist
- **BRANDING.md** - Asset requirements

---

## 🎯 Configuration

- **App Name:** BeeSmart Spelling Bee
- **App ID:** app.beesmartspelling
- **Version:** 1.0.0 (versionCode 1)
- **Approach:** Capacitor WebView wrapper bundling web assets (no remote hosting)

---

## ⚡ Automation Scripts

All scripts are ready to use:

### `quick-start.ps1` - Interactive Setup Wizard
Complete packaging workflow with menu system.

### `setup-keystore.ps1` - Keystore Generation
One-time setup to create Android signing key.

### `setup-signing.ps1` - Configure Signing
One-time setup to configure release signing.

### `build-release.ps1` - Automated Build
Build release AAB or APK with optional version updates.

**Examples:**
```powershell
# Build Play Store AAB
.\build-release.ps1

# Build test APK
.\build-release.ps1 -BuildAPK

# Build with version update
.\build-release.ps1 -VersionName "1.0.1" -VersionCode 2
```

---

## 🏗️ Architecture

### Web App (Flask/Python)
- Flask backend (this repo)
- Full web UI with PWA support

### Mobile App (Capacitor)
- Native Android wrapper
- WebView loads bundled web assets
- Native integrations: Camera, Microphone, StatusBar
- Splash screen and app icons
- Play Store ready

---

## 📁 Project Structure

```
mobile/
├── android/              # Android Studio project
│   ├── app/
│   │   └── build.gradle  # Build config (signing configured ✅)
│   ├── .gitignore        # Updated ✅
│   ├── upload-keystore.jks        # Created by setup-keystore.ps1
│   └── keystore.properties        # Created by setup-signing.ps1
├── capacitor.config.ts   # App config (configured ✅)
├── package.json          # Dependencies
├── quick-start.ps1       # Interactive wizard ✅
├── setup-keystore.ps1    # Keystore generator ✅
├── setup-signing.ps1     # Signing config ✅
├── build-release.ps1     # Build automation ✅
├── STATUS.txt            # Current status
├── QUICK_REFERENCE.md    # Commands
├── SETUP_COMPLETE.md     # Configuration details
├── STORE_CHECKLIST.md    # Submission checklist
└── README.md            # This file
```

---

## 🔐 Security

### Protected Files (in .gitignore)
- `android/upload-keystore.jks` - Signing key
- `android/keystore.properties` - Credentials
- Any `.keystore` files

### Safe to Commit
- All PowerShell scripts
- Configuration files
- Documentation

---

## Prerequisites

- ✅ Node.js 18+ (installed)
- ✅ Capacitor configured
- ⏳ Android Studio + Android SDK (downloading)
- ⏳ Java JDK (for keytool)
- ⏳ Google Play Console account

---

## Manual Setup Steps (if not using quick-start.ps1)

```bash
npm init -y
npm i -D @capacitor/cli @capacitor/core
npx cap init "BeeSmart Spelling Bee" app.beesmartspelling --web-dir=dist
```

You can keep `web-dir=dist` even though we use a different folder for bundled assets in this repo—Capacitor requires a folder.

2) Use the bundled-assets Capacitor configuration

Edit `capacitor.config.ts` (created here for you). Ensure you **do not** set `server.url`:

```ts
server: {
  // No remote hosting or external server URL.
  // The app loads the bundled assets from webDir.
  cleartext: false,
}
```

3) Add platforms

```bash
npx cap add ios
npx cap add android
```

4) Permissions & entitlements
- iOS (Info.plist):
  - NSCameraUsageDescription = "Allow taking a photo to upload spelling words."
  - NSMicrophoneUsageDescription = "Enable voice spelling input."
  - NSPhotoLibraryAddUsageDescription / NSPhotoLibraryUsageDescription if saving/choosing photos.
- Android (AndroidManifest.xml):
  - <uses-permission android:name="android.permission.CAMERA" />
  - <uses-permission android:name="android.permission.RECORD_AUDIO" />
  - Add READ_MEDIA_IMAGES (API 33+) or READ_EXTERNAL_STORAGE (<33) if needed.

5) Handle external links
Make sure links to external sites open in the system browser. You can use a simple JS handler in your web app to `target="_blank"` or handle via Capacitor’s Browser plugin.

6) Build

```bash
npx cap sync
npx cap open ios
npx cap open android
```

Then build and run from Xcode/Android Studio.

7) Store listing checklist
- App Icon (1024×1024 PNG, no transparency)
- Screenshots (phone + tablet)
- Short & full description
- Privacy policy URL: https://beesmartspelling.app/privacy
- Support URL: https://beesmartspelling.app/support
- Terms of Use: https://beesmartspelling.app/terms
- Age rating questionnaire (COPPA friendly)
- Category: Education
- Sign-in demo account if needed for review

8) Policy considerations
- Kids content: ensure COPPA compliance, no third‑party tracking.
- Microphone/Camera: ask for permission only when used.
- Account deletion path (if accounts exist) documented and implemented.

9) Optional: Deep Links / Universal Links
- If you need `beesmartspelling.app` links to open the app, configure:
  - iOS: Associated Domains (`applinks:beesmartspelling.app`)
  - Android: Asset Links + intent filter for your domain

10) Optional: Publish as a PWA
- Your PWA can be installable directly in Chrome/Edge and on Android. The manifest and service worker are already added.

## Next steps
- [ ] Install Node deps and run `npx cap init`
- [ ] Add platforms and set permissions
- [ ] Test camera/microphone flows inside the wrapper
- [ ] Prepare store metadata and assets
- [ ] Submit internal testing builds (TestFlight/Closed Testing)
