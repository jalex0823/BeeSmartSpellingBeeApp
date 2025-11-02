# BeeSmart Spelling Bee - Android Packaging Quick Reference

## 🚀 Quick Start (After Android Studio Installation)

### Step 1: Navigate to mobile folder
```powershell
cd "c:\Users\jeff\Dropbox\BeeSmartSpellingBeeApp\mobile"
```

### Step 2: Run the setup wizard
```powershell
.\quick-start.ps1
```

The wizard will guide you through:
1. Generating keystore
2. Configuring signing
3. Building release packages

---

## 📋 Manual Commands

### Generate Keystore (One-time setup)
```powershell
.\setup-keystore.ps1
```

### Configure Signing
```powershell
.\setup-signing.ps1
```

### Build Release AAB (Play Store)
```powershell
.\build-release.ps1
```

### Build Release APK (Testing)
```powershell
.\build-release.ps1 -BuildAPK
```

### Sync Capacitor
```powershell
npm run cap:sync
```

### Open Android Studio
```powershell
npm run cap:open:android
```

---

## ⚡ Build with Version Update

```powershell
# Update version and build
.\build-release.ps1 -VersionName "1.0.1" -VersionCode 2
```

---

## 🔧 Your Configuration

✅ **Backend URL:** https://beesmartspelling.app
✅ **App ID:** app.beesmartspelling
✅ **App Name:** BeeSmart Spelling Bee
✅ **Build System:** Capacitor + Android Studio
✅ **Signing:** Configured in build.gradle

---

## 📁 Important Files

- `capacitor.config.ts` - App configuration (backend URL)
- `android/app/build.gradle` - Build configuration (CONFIGURED ✅)
- `android/keystore.properties` - Signing credentials (create with setup-signing.ps1)
- `android/upload-keystore.jks` - Signing key (create with setup-keystore.ps1)

---

## 🎯 Next Steps

1. ✅ Android Studio installed
2. ⏳ Run: `.\quick-start.ps1` in the mobile folder
3. ⏳ Generate keystore
4. ⏳ Build release AAB
5. ⏳ Upload to Google Play Console

---

## 🆘 Need Help?

See full documentation: `ANDROID_PACKAGING_GUIDE.md`

## 🐝 Happy Building!
