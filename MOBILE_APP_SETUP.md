# 📱 BeeSmart Mobile App Setup Guide

Complete guide to package BeeSmart Spelling App into iOS and Android mobile apps using Capacitor.

## 🎯 Overview

This guide helps you wrap your Railway-hosted BeeSmart web app (`https://beesmart.up.railway.app`) into native mobile apps for iOS (App Store) and Android (Play Store).

## 📋 Prerequisites

### Required Software
- **Node.js** 16+ and npm ([Download](https://nodejs.org/))
- **Xcode** 14+ (macOS only, for iOS) ([Download](https://developer.apple.com/xcode/))
- **Android Studio** 2021+ (for Android) ([Download](https://developer.android.com/studio))
- **CocoaPods** (iOS dependency manager): `sudo gem install cocoapods`

### Required Accounts
- **Apple Developer Account** ($99/year) for App Store
- **Google Play Console** ($25 one-time) for Play Store

---

## 🚀 Quick Start (Step-by-Step)

### 1. Create Mobile App Project

```powershell
# Create project directory
mkdir beesmart-mobile
cd beesmart-mobile

# Initialize npm project
npm init -y

# Install Capacitor
npm install @capacitor/core @capacitor/cli

# Initialize Capacitor
npx cap init "BeeSmart Spelling" "com.beesmart.app" --web-dir=www
```

**Configuration Prompts:**
- **App name**: `BeeSmart Spelling`
- **App ID**: `com.beesmart.app` (reverse domain, unique identifier)
- **Web directory**: `www` (where your web app files live)

### 2. Create Web App Wrapper

Create `www/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="format-detection" content="telephone=no">
    <meta name="msapplication-tap-highlight" content="no">
    
    <title>BeeSmart Spelling</title>
    
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html, body { height: 100%; overflow: hidden; }
        
        #splash {
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            transition: opacity 0.5s ease;
        }
        
        #splash.hidden { opacity: 0; pointer-events: none; }
        
        #splash img {
            width: 200px;
            height: 200px;
            animation: bounce 1s infinite;
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }
        
        #splash h1 {
            color: white;
            font-family: 'Arial Black', sans-serif;
            margin-top: 20px;
            font-size: 28px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        #app-frame {
            width: 100%;
            height: 100%;
            border: none;
            display: block;
        }
    </style>
</head>
<body>
    <!-- Splash Screen -->
    <div id="splash">
        <img src="https://beesmart.up.railway.app/static/assets/avatars/CoolBee/CoolBee.png" 
             alt="BeeSmart Logo" 
             onerror="this.style.display='none'">
        <h1>🐝 BeeSmart</h1>
        <p style="color: white; margin-top: 10px;">Loading...</p>
    </div>
    
    <!-- Main App (Railway hosted web app) -->
    <iframe id="app-frame" 
            src="https://beesmart.up.railway.app" 
            sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-modals"
            allowfullscreen>
    </iframe>
    
    <script>
        // Hide splash screen after app loads
        const iframe = document.getElementById('app-frame');
        const splash = document.getElementById('splash');
        
        iframe.onload = () => {
            setTimeout(() => {
                splash.classList.add('hidden');
            }, 1000);
        };
        
        // Timeout fallback in case iframe doesn't load
        setTimeout(() => {
            splash.classList.add('hidden');
        }, 5000);
    </script>
</body>
</html>
```

### 3. Add Mobile Platforms

```powershell
# Install platform packages
npm install @capacitor/ios @capacitor/android

# Add iOS platform
npx cap add ios

# Add Android platform
npx cap add android

# Sync web assets to native projects
npx cap sync
```

### 4. Configure App Icons and Splash Screens

#### iOS Icons (Required sizes)
Place in `ios/App/App/Assets.xcassets/AppIcon.appiconset/`:
- `1024x1024` - App Store icon
- `180x180` - iPhone icon
- `120x120` - iPhone icon (2x)
- `167x167` - iPad Pro icon

#### Android Icons
Place in `android/app/src/main/res/`:
- `mipmap-mdpi/ic_launcher.png` - 48x48
- `mipmap-hdpi/ic_launcher.png` - 72x72
- `mipmap-xhdpi/ic_launcher.png` - 96x96
- `mipmap-xxhdpi/ic_launcher.png` - 144x144
- `mipmap-xxxhdpi/ic_launcher.png` - 192x192

**Tip:** Use [appicon.co](https://appicon.co/) to generate all icon sizes from one 1024x1024 image.

### 5. Build and Test

#### iOS (macOS only)
```powershell
# Open in Xcode
npx cap open ios

# In Xcode:
# 1. Select your signing team (Xcode > Preferences > Accounts)
# 2. Select target device (iPhone simulator or real device)
# 3. Click ▶️ Run button
```

#### Android
```powershell
# Open in Android Studio
npx cap open android

# In Android Studio:
# 1. Wait for Gradle sync to complete
# 2. Select emulator or connected device
# 3. Click ▶️ Run button
```

---

## 🎨 Advanced Features

### A. Enable Native Features

Install Capacitor plugins for native device features:

```powershell
# Camera (for OCR word list uploads)
npm install @capacitor/camera

# Microphone (for voice spelling input)
npm install @capacitor/microphone

# Notifications (for study reminders)
npm install @capacitor/push-notifications

# Haptics (for tactile feedback)
npm install @capacitor/haptics

# Update native projects
npx cap sync
```

### B. Offline Support with Service Worker

Create `www/service-worker.js`:

```javascript
const CACHE_NAME = 'beesmart-v1';
const OFFLINE_URL = 'https://beesmart.up.railway.app';

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll([OFFLINE_URL]);
        })
    );
});

self.addEventListener('fetch', (event) => {
    if (event.request.mode === 'navigate') {
        event.respondWith(
            fetch(event.request).catch(() => {
                return caches.match(OFFLINE_URL);
            })
        );
    }
});
```

Register in `index.html`:
```javascript
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/service-worker.js');
}
```

### C. Deep Linking (Open specific app sections from URLs)

Edit `capacitor.config.json`:
```json
{
  "appId": "com.beesmart.app",
  "appName": "BeeSmart Spelling",
  "webDir": "www",
  "server": {
    "url": "https://beesmart.up.railway.app",
    "cleartext": true
  },
  "plugins": {
    "SplashScreen": {
      "launchShowDuration": 2000,
      "backgroundColor": "#FFA500",
      "androidScaleType": "CENTER_CROP",
      "showSpinner": false
    }
  }
}
```

---

## 📦 Production Build & Deployment

### iOS - TestFlight & App Store

1. **Archive Build (Xcode)**
   ```
   Product > Archive
   ```

2. **Upload to App Store Connect**
   - Window > Organizer > Archives
   - Select archive > Distribute App
   - Choose "App Store Connect"
   - Follow upload wizard

3. **TestFlight (Beta Testing)**
   - Log into [App Store Connect](https://appstoreconnect.apple.com)
   - Select your app > TestFlight tab
   - Add external testers
   - Submit for beta review

4. **App Store Release**
   - Complete app metadata (description, screenshots, keywords)
   - Submit for App Store review (1-3 days)
   - Release when approved

### Android - Play Store

1. **Generate Signed APK/Bundle**
   ```powershell
   # In Android Studio:
   Build > Generate Signed Bundle / APK
   ```

2. **Create Signing Key**
   ```powershell
   keytool -genkey -v -keystore beesmart-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias beesmart
   ```

3. **Upload to Play Console**
   - Log into [Google Play Console](https://play.google.com/console)
   - Create new app
   - Upload AAB file (Android App Bundle)
   - Complete store listing (description, screenshots, category)

4. **Release Tracks**
   - **Internal Testing**: Small group (instant)
   - **Closed Testing**: Larger group (hours)
   - **Open Testing**: Public beta (hours)
   - **Production**: Full release (review 1-3 days)

---

## 🔧 Maintenance & Updates

### Update Web Content (No App Update Needed)
Since your app loads from Railway, most changes to your web app (UI, features, bug fixes) deploy automatically without requiring new app store submissions!

### When to Submit App Updates
Only needed for:
- ✅ Native plugin changes
- ✅ App icon/name changes
- ✅ Capacitor version upgrades
- ✅ New native permissions

### Update Process
```powershell
# Update web content
npx cap sync

# Rebuild iOS
npx cap open ios
# (Xcode: Archive > Upload)

# Rebuild Android
npx cap open android
# (Android Studio: Generate Signed Bundle)
```

---

## 📊 Analytics & Monitoring

### Option 1: Google Analytics
```html
<!-- Add to www/index.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### Option 2: Firebase (Recommended for Mobile)
```powershell
npm install @capacitor-firebase/analytics
npx cap sync
```

---

## 🐛 Troubleshooting

### Issue: White screen on launch
**Solution:** Check `www/index.html` exists and iframe URL is correct

### Issue: iOS build fails
**Solution:** 
```powershell
cd ios/App
pod install
cd ../..
npx cap sync ios
```

### Issue: Android gradle sync fails
**Solution:** Update `android/build.gradle`:
```gradle
buildscript {
    ext.kotlin_version = '1.9.0'
    dependencies {
        classpath 'com.android.tools.build:gradle:8.0.2'
    }
}
```

### Issue: App loads slowly
**Solution:** Implement service worker caching (see Advanced Features section)

---

## 📚 Resources

- [Capacitor Docs](https://capacitorjs.com/docs)
- [iOS Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Android Material Design](https://material.io/design)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [Google Play Policy Center](https://play.google.com/about/developer-content-policy/)

---

## ✅ Deployment Checklist

- [ ] Test on iOS Simulator
- [ ] Test on physical iPhone
- [ ] Test on Android Emulator
- [ ] Test on physical Android device
- [ ] Test offline behavior
- [ ] Test deep linking
- [ ] Generate all icon sizes
- [ ] Create splash screens
- [ ] Write app store descriptions (English + other languages)
- [ ] Capture screenshots (all device sizes)
- [ ] Set privacy policy URL
- [ ] Set support URL
- [ ] Configure age rating
- [ ] Test in-app purchases (if applicable)
- [ ] Submit for TestFlight beta
- [ ] Gather beta tester feedback
- [ ] Submit to App Store review
- [ ] Submit to Play Store review

---

## 🎉 Success!

Once approved, your app will be available:
- 🍎 **iOS**: `https://apps.apple.com/app/beesmart-spelling/YOUR_APP_ID`
- 🤖 **Android**: `https://play.google.com/store/apps/details?id=com.beesmart.app`

---

**Questions?** Open an issue or contact support at support@beesmartspelling.app
