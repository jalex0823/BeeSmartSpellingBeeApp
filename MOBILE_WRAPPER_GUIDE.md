# 📱 BeeSmart Spelling Bee - Mobile App Wrapper Guide

## Overview
This guide walks through wrapping the Flask-based BeeSmart app for iOS App Store and Google Play Store using Capacitor.

**Current Status:**
- ✅ Flask app hosted on Railway with HTTPS
- ✅ Responsive design with mobile-first CSS
- ✅ iOS provisioning profile and certificate available
- 🔄 Ready for mobile wrapper implementation

---

## 🧱 Phase 1: Pre-Flight Checklist

### ✅ App Requirements (Already Met)
- [x] **HTTPS enabled**: Railway provides SSL by default
- [x] **Responsive design**: BeeSmart.css with mobile viewport meta tags
- [x] **Stable hosting**: Railway deployment with health checks
- [x] **iOS credentials**: 
  - `ios_distribution.cer` (certificate)
  - `BeeSmartAppStoreProfile.mobileprovision` (provisioning profile)

### 📋 Additional Preparations Needed
- [ ] Verify app works offline (or add graceful offline handler)
- [ ] Add mobile-specific splash screens (1170x2532, 1284x2778, etc.)
- [ ] Create app icons (1024x1024 base, auto-generate others)
- [ ] Test touch interactions (avatar picker, quiz buttons)
- [ ] Optimize 3D avatar loading for mobile networks

---

## 🧰 Phase 2: Install Capacitor

### Step 1: Install Node.js and Capacitor CLI
```powershell
# Check if Node.js is installed
node --version
npm --version

# Install Capacitor CLI globally
npm install -g @capacitor/cli

# Verify installation
cap --version
```

### Step 2: Initialize Capacitor Project
```powershell
# Create a new directory for the mobile wrapper
cd "C:\Users\jeff\Dropbox\BeeSmartSpellingBeeApp"
mkdir mobile-wrapper
cd mobile-wrapper

# Initialize Capacitor project
npm init @capacitor/app

# Follow prompts:
# - App name: BeeSmart Spelling Bee
# - App ID: com.beesmart.spellingbee
# - Web directory: www (we'll configure this)
```

---

## 🍎 Phase 3: iOS Configuration

### Step 1: Install iOS Platform
```powershell
cd mobile-wrapper
npm install @capacitor/ios
npx cap add ios
```

### Step 2: Configure capacitor.config.json
Create/edit `capacitor.config.json`:
```json
{
  "appId": "com.beesmart.spellingbee",
  "appName": "BeeSmart Spelling Bee",
  "webDir": "www",
  "bundledWebRuntime": false,
  "server": {
    "url": "https://beesmart.up.railway.app",
    "cleartext": false,
    "allowNavigation": [
      "beesmart.up.railway.app",
      "*.railway.app"
    ]
  },
  "ios": {
    "contentInset": "automatic",
    "scheme": "BeeSmart"
  },
  "plugins": {
    "SplashScreen": {
      "launchShowDuration": 2000,
      "backgroundColor": "#FFD700",
      "androidScaleType": "CENTER_CROP",
      "showSpinner": true,
      "spinnerColor": "#000000"
    }
  }
}
```

### Step 3: Add iOS Assets

#### App Icon (1024x1024)
Create from existing bee logo:
```powershell
# Place app icon at:
# mobile-wrapper/ios/App/App/Assets.xcassets/AppIcon.appiconset/icon-1024.png
```

#### Splash Screen
```powershell
# Create splash screens (iOS requires multiple sizes):
# - 1170x2532 (iPhone 13/14/15 Pro Max)
# - 1284x2778 (iPhone 14 Pro Max)
# - 2048x2732 (iPad Pro 12.9")
# Place in: mobile-wrapper/ios/App/App/Assets.xcassets/Splash.imageset/
```

### Step 4: Configure Xcode Project
```powershell
# Open project in Xcode
npx cap open ios
```

**In Xcode:**
1. **Select Target** → "App"
2. **General Tab**:
   - Display Name: `BeeSmart Spelling Bee`
   - Bundle Identifier: `com.beesmart.spellingbee`
   - Version: `1.0`
   - Build: `1`

3. **Signing & Capabilities**:
   - Team: Select your Apple Developer team
   - Provisioning Profile: Import `BeeSmartAppStoreProfile.mobileprovision`
   - Certificate: Import `ios_distribution.cer` to Keychain

4. **Info.plist Settings**:
   - Add: `NSCameraUsageDescription` → "BeeSmart needs camera access for image-based word list uploads"
   - Add: `NSMicrophoneUsageDescription` → "BeeSmart needs microphone access for voice spelling"
   - Add: `NSPhotoLibraryUsageDescription` → "BeeSmart needs photo library access to upload word lists"

### Step 5: Build for App Store
```powershell
# Archive in Xcode:
# Product → Archive
# Then: Distribute App → App Store Connect
# Upload the .ipa file
```

---

## 🤖 Phase 4: Android Configuration

### Step 1: Install Android Platform
```powershell
cd mobile-wrapper
npm install @capacitor/android
npx cap add android
```

### Step 2: Configure Android Manifest
Edit `mobile-wrapper/android/app/src/main/AndroidManifest.xml`:
```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <application
        android:label="BeeSmart Spelling Bee"
        android:icon="@mipmap/ic_launcher"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:theme="@style/AppTheme"
        android:usesCleartextTraffic="false">
        
        <activity
            android:name=".MainActivity"
            android:configChanges="orientation|keyboardHidden|keyboard|screenSize|locale|smallestScreenSize|screenLayout|uiMode"
            android:label="@string/title_activity_main"
            android:theme="@style/AppTheme.NoActionBarLaunch"
            android:launchMode="singleTask"
            android:exported="true">
            
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
    
    <!-- Permissions -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
</manifest>
```

### Step 3: Add Android Assets

#### App Icon
```powershell
# Generate adaptive icons using Android Asset Studio
# Place in: mobile-wrapper/android/app/src/main/res/mipmap-*/ic_launcher.png
# Sizes: mdpi (48x48), hdpi (72x72), xhdpi (96x96), xxhdpi (144x144), xxxhdpi (192x192)
```

#### Splash Screen
Edit `mobile-wrapper/android/app/src/main/res/drawable/splash.png`

### Step 4: Build with Android Studio
```powershell
# Open project in Android Studio
npx cap open android
```

**In Android Studio:**
1. **Build → Generate Signed Bundle/APK**
2. Select: **Android App Bundle (AAB)** for Play Store
3. Create or select keystore:
   - Keystore path: `beesmart-release.keystore`
   - Alias: `beesmart`
   - Password: [secure password]

4. **Build Variants**: Select `release`
5. **Generate AAB** → Upload to Google Play Console

---

## 🔌 Phase 5: Add Native Features (Optional)

### Camera Plugin (for OCR word list uploads)
```powershell
npm install @capacitor/camera
npx cap sync
```

**Update app code:**
```javascript
import { Camera, CameraResultType } from '@capacitor/camera';

async function captureWordList() {
  const image = await Camera.getPhoto({
    quality: 90,
    allowEditing: true,
    resultType: CameraResultType.DataUrl
  });
  
  // Send to Flask /api/upload endpoint
  const response = await fetch('/api/upload', {
    method: 'POST',
    body: JSON.stringify({ image: image.dataUrl }),
    headers: { 'Content-Type': 'application/json' }
  });
}
```

### Push Notifications (for quiz reminders)
```powershell
npm install @capacitor/push-notifications
npx cap sync
```

### Voice Recognition (for spelling answers)
```powershell
npm install @capacitor-community/speech-recognition
npx cap sync
```

---

## 🧠 Phase 6: Best Practices & Optimization

### 1. Offline Handling
Add service worker for offline fallback:
```javascript
// static/js/offline-handler.js
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js').then(registration => {
    console.log('✅ Service Worker registered');
  });
}

// Show friendly message when offline
window.addEventListener('offline', () => {
  document.body.insertAdjacentHTML('beforeend', `
    <div id="offline-banner" style="position:fixed;top:0;left:0;right:0;background:#ff6b6b;color:white;padding:10px;text-align:center;z-index:9999;">
      🐝 No internet connection. Quiz progress will sync when online.
    </div>
  `);
});

window.addEventListener('online', () => {
  const banner = document.getElementById('offline-banner');
  if (banner) banner.remove();
});
```

### 2. Mobile Performance
```python
# AjaSpellBApp.py - Add mobile detection
from flask import request

@app.before_request
def detect_mobile():
    user_agent = request.headers.get('User-Agent', '').lower()
    request.is_mobile = any(x in user_agent for x in ['mobile', 'android', 'iphone', 'capacitor'])
    
    # Optimize 3D models for mobile
    if request.is_mobile and 'avatar' in request.path:
        # Serve lower-poly GLB files or reduce texture quality
        pass
```

### 3. Deep Linking
Enable direct links to quiz/avatars:
```json
// capacitor.config.json
{
  "plugins": {
    "App": {
      "appUrlOpen": {
        "ios": ["beesmart"],
        "android": ["beesmart"]
      }
    }
  }
}
```

### 4. App Store Optimization (ASO)

#### iOS App Store Connect
- **App Name**: BeeSmart Spelling Bee
- **Subtitle**: Fun Spelling Practice for Kids
- **Keywords**: spelling, education, kids, bee, quiz, learning, vocabulary
- **Description**:
  ```
  🐝 Make spelling fun with BeeSmart!
  
  • Upload custom word lists (CSV, TXT, images)
  • Interactive quiz with voice support
  • 27 unique bee avatars to unlock
  • Track progress with streaks and badges
  • Safe, ad-free experience for kids
  
  Perfect for:
  - Elementary school students
  - Homeschool families
  - Spelling bee preparation
  - ESL learners
  ```

#### Google Play Console
- **Short Description** (80 chars): "🐝 Fun spelling practice for kids with custom word lists & 3D bee avatars"
- **Full Description**: Same as iOS
- **Category**: Education → Educational
- **Content Rating**: Everyone

---

## 📦 Phase 7: Deployment Checklist

### iOS App Store
- [ ] Apple Developer account ($99/year)
- [ ] App Store Connect listing created
- [ ] Privacy policy URL (host on Railway)
- [ ] Screenshots (6.5" iPhone, 12.9" iPad)
- [ ] App preview video (optional, 15-30 seconds)
- [ ] App icon without alpha channel (1024x1024)
- [ ] TestFlight beta testing (optional)
- [ ] Submit for review

### Google Play Store
- [ ] Google Play Console account ($25 one-time)
- [ ] Play Store listing created
- [ ] Privacy policy URL
- [ ] Screenshots (phone + tablet)
- [ ] Feature graphic (1024x500)
- [ ] App icon (512x512)
- [ ] Content rating questionnaire completed
- [ ] Internal testing track (optional)
- [ ] Submit for review

---

## 🚀 Quick Start Commands

```powershell
# Step 1: Create wrapper project
cd "C:\Users\jeff\Dropbox\BeeSmartSpellingBeeApp"
mkdir mobile-wrapper
cd mobile-wrapper
npm init @capacitor/app

# Step 2: Configure for hosted app
# Edit capacitor.config.json (set server.url to Railway URL)

# Step 3: Add platforms
npm install @capacitor/ios @capacitor/android
npx cap add ios
npx cap add android

# Step 4: Sync and open
npx cap sync
npx cap open ios      # Opens Xcode
npx cap open android  # Opens Android Studio

# Step 5: Build and deploy
# iOS: Xcode → Product → Archive → Distribute
# Android: Android Studio → Build → Generate Signed Bundle
```

---

## 🐛 Common Issues & Solutions

### Issue: "cleartext HTTP traffic not permitted"
**Solution**: Ensure `server.url` uses `https://` in capacitor.config.json

### Issue: Avatar 3D models won't load in WebView
**Solution**: Add CORS headers in Flask:
```python
from flask_cors import CORS
CORS(app, resources={r"/static/*": {"origins": ["capacitor://localhost"]}})
```

### Issue: iOS certificate signing fails
**Solution**: 
1. Import certificate to Keychain Access
2. Trust certificate: Right-click → Get Info → Trust → Always Trust
3. Restart Xcode

### Issue: Android build fails with "AAPT2 error"
**Solution**: Clean build and sync:
```powershell
cd mobile-wrapper/android
./gradlew clean
npx cap sync android
```

---

## 📞 Support Resources

- **Capacitor Docs**: https://capacitorjs.com/docs
- **iOS Human Interface Guidelines**: https://developer.apple.com/design/human-interface-guidelines/
- **Android Material Design**: https://m3.material.io/
- **App Store Review Guidelines**: https://developer.apple.com/app-store/review/guidelines/
- **Google Play Policies**: https://play.google.com/about/developer-content-policy/

---

## 🎯 Next Steps

1. **Test locally**: Run on iOS simulator and Android emulator
2. **Beta testing**: Use TestFlight (iOS) and Internal Testing (Android)
3. **Gather feedback**: Get users to test avatar picker, quiz flow, OCR upload
4. **Iterate**: Fix bugs, optimize performance
5. **Launch**: Submit to both stores!

**Estimated Timeline:**
- Setup & configuration: 2-3 days
- Asset creation (icons, splash): 1 day
- Testing & debugging: 3-5 days
- Store submission & review: 1-2 weeks (Apple), 1-3 days (Google)

**Total**: ~3-4 weeks from start to live in stores 🚀
