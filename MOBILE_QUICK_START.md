# 📱 BeeSmart Mobile App - Quick Start

## Overview
This directory contains the Capacitor wrapper that packages the BeeSmart Flask web app into native iOS and Android apps for distribution on App Store and Google Play.

## 🚀 One-Command Setup

```powershell
# Run the automated setup script
.\setup_mobile_wrapper.ps1
```

This will:
- ✅ Check Node.js and npm installation
- ✅ Install Capacitor CLI
- ✅ Create mobile-wrapper directory
- ✅ Configure Capacitor for both platforms
- ✅ Install iOS and Android platforms
- ✅ Sync all assets and configurations

## 📦 Manual Setup (Alternative)

If you prefer manual setup:

```powershell
# 1. Install Capacitor CLI
npm install -g @capacitor/cli

# 2. Create and configure project
cd mobile-wrapper
npm install @capacitor/core @capacitor/cli
npm install @capacitor/ios @capacitor/android

# 3. Add platforms
npx cap add ios
npx cap add android

# 4. Sync
npx cap sync
```

## 🎨 Generate App Assets

```powershell
# Generate all icons and splash screens
python generate_mobile_assets.py

# Or specify custom base images
python generate_mobile_assets.py "path/to/icon.png" "path/to/splash.png"
```

This generates:
- 📱 iOS: 16 icon sizes + 6 splash screen sizes
- 🤖 Android: 5 icon densities + 10 splash screen variants

## 🍎 iOS Development

### Open in Xcode
```powershell
cd mobile-wrapper
npm run open:ios
```

### Configure Signing
1. In Xcode, select **App** target
2. Go to **Signing & Capabilities**
3. Import certificates:
   - Double-click `ios_distribution.cer` to add to Keychain
   - Import `BeeSmartAppStoreProfile.mobileprovision`
4. Select your team and provisioning profile

### Build for App Store
1. **Product** → **Archive**
2. **Distribute App** → **App Store Connect**
3. Upload `.ipa` file

## 🤖 Android Development

### Open in Android Studio
```powershell
cd mobile-wrapper
npm run open:android
```

### Configure Signing
1. **Build** → **Generate Signed Bundle/APK**
2. Create keystore:
   - Keystore path: `beesmart-release.keystore`
   - Alias: `beesmart`
   - Password: [secure password]
3. Select build variant: **release**

### Build for Play Store
1. Generate **Android App Bundle (AAB)**
2. Upload to Google Play Console

## 🔧 Configuration

### capacitor.config.json
```json
{
  "appId": "com.beesmart.spellingbee",
  "appName": "BeeSmart Spelling Bee",
  "server": {
    "url": "https://beesmart.up.railway.app"
  }
}
```

### Change Production URL
If you move hosting from Railway:
```powershell
cd mobile-wrapper
# Edit capacitor.config.json and update server.url
npx cap sync
```

## 📱 Testing

### iOS Simulator
```powershell
npx cap run ios
```

### Android Emulator
```powershell
npx cap run android
```

### Device Testing
- **iOS**: Use TestFlight for beta testing
- **Android**: Use Internal Testing track in Play Console

## 🐛 Troubleshooting

### "cleartext HTTP traffic not permitted"
✅ Ensure `server.url` uses `https://` in `capacitor.config.json`

### 3D avatars won't load
✅ Add CORS headers in Flask:
```python
from flask_cors import CORS
CORS(app, resources={r"/static/*": {"origins": ["capacitor://localhost"]}})
```

### iOS signing fails
✅ Trust certificate in Keychain Access:
1. Open Keychain Access
2. Find certificate → Right-click → Get Info
3. Trust → Always Trust
4. Restart Xcode

### Android build fails
✅ Clean and rebuild:
```powershell
cd mobile-wrapper/android
./gradlew clean
npx cap sync android
```

## 📚 Documentation

- **Full Guide**: See `MOBILE_WRAPPER_GUIDE.md` for detailed instructions
- **Capacitor Docs**: https://capacitorjs.com/docs
- **iOS Guidelines**: https://developer.apple.com/design/human-interface-guidelines/
- **Android Guidelines**: https://m3.material.io/

## 🎯 Deployment Checklist

### iOS App Store
- [ ] Apple Developer account ($99/year)
- [ ] App Store Connect listing
- [ ] Privacy policy URL
- [ ] Screenshots (6.5" iPhone, 12.9" iPad)
- [ ] App icon (1024x1024, no alpha)
- [ ] Submit for review

### Google Play Store
- [ ] Google Play Console account ($25 one-time)
- [ ] Play Store listing
- [ ] Privacy policy URL
- [ ] Screenshots + feature graphic
- [ ] App icon (512x512)
- [ ] Submit for review

## 📦 NPM Scripts

```powershell
# Sync changes to platforms
npm run sync

# Open in IDE
npm run open:ios
npm run open:android

# Build for specific platform
npm run build:ios
npm run build:android
```

## 🚀 Next Steps

1. ✅ Run `setup_mobile_wrapper.ps1`
2. ✅ Generate assets with `generate_mobile_assets.py`
3. ✅ Test in simulators/emulators
4. ✅ Configure signing certificates
5. ✅ Build and archive
6. ✅ Submit to stores

**Estimated timeline**: 3-4 weeks from setup to live in stores

---

Need help? Check `MOBILE_WRAPPER_GUIDE.md` for comprehensive documentation.
