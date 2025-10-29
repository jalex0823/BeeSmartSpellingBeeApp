# 🐝 BeeSmart Spelling - Capacitor Mobile Setup Guide

## Quick Start (5 Minutes)

### 1. Install Dependencies
```powershell
# Install Node packages
npm install

# Verify Capacitor CLI
npx cap --version
```

### 2. Initialize Capacitor (First Time Only)
```powershell
# This creates the base config (already done via capacitor.config.json)
# Just sync to verify
npx cap sync
```

### 3. Add iOS Platform
```powershell
# Add iOS (requires macOS + Xcode)
npm run cap:add:ios

# Open in Xcode
npm run cap:open:ios
```

### 4. Add Android Platform
```powershell
# Add Android (requires Android Studio)
npm run cap:add:android

# Open in Android Studio
npm run cap:open:android
```

---

## Configuration Details

### Server URL
**Current**: `https://beesmartspellingbeeapp-production.up.railway.app`

Update `capacitor.config.json` if your Railway URL changes:
```json
{
  "server": {
    "url": "https://YOUR-RAILWAY-APP.railway.app"
  }
}
```

### App Identifiers
- **App ID**: `com.beesmart.spelling`
- **App Name**: BeeSmart Spelling
- **Bundle Version**: 1.0.0

---

## Required Code Changes

### 1. Add Capacitor Detection Helper
Create `static/js/capacitor-helper.js`:

```javascript
// Capacitor environment detection
const CapHelper = {
  isNative: () => {
    return window.Capacitor && window.Capacitor.isNativePlatform();
  },
  
  isPlatform: (platform) => {
    return window.Capacitor && window.Capacitor.getPlatform() === platform;
  },
  
  getApiBase: () => {
    // Use relative URLs when running in native app (proxies to server.url)
    return CapHelper.isNative() ? '' : '';
  }
};

// Log platform info
if (CapHelper.isNative()) {
  console.log('🐝 Running on:', window.Capacitor.getPlatform());
} else {
  console.log('🌐 Running in browser');
}
```

### 2. Update API Calls (Optional - for offline support)
Your current API calls work as-is! Capacitor proxies them to Railway.

For offline caching, wrap fetch calls:
```javascript
// Before
fetch('/api/avatars')

// After (same, but with offline fallback)
fetch('/api/avatars')
  .catch(err => {
    // Load from local cache if offline
    if (CapHelper.isNative()) {
      return Filesystem.readFile({ path: 'avatars-cache.json' });
    }
    throw err;
  });
```

---

## Native Features Integration

### Camera for OCR Uploads
Add to your upload page:

```javascript
import { Camera, CameraResultType } from '@capacitor/camera';

async function takePictureForWordList() {
  if (!CapHelper.isNative()) {
    // Use existing file input
    document.getElementById('fileInput').click();
    return;
  }
  
  try {
    const image = await Camera.getPhoto({
      quality: 90,
      allowEditing: false,
      resultType: CameraResultType.DataUrl
    });
    
    // Send to your existing /api/upload endpoint
    const formData = new FormData();
    const blob = await fetch(image.dataUrl).then(r => r.blob());
    formData.append('file', blob, 'camera-image.jpg');
    
    fetch('/api/upload', {
      method: 'POST',
      body: formData
    });
  } catch (error) {
    console.error('Camera error:', error);
  }
}
```

### Text-to-Speech for Pronunciation
```javascript
import { TextToSpeech } from '@capacitor/text-to-speech';

async function pronounceWord(word) {
  if (CapHelper.isNative()) {
    await TextToSpeech.speak({
      text: word,
      lang: 'en-US',
      rate: 0.8, // Slower for kids
      pitch: 1.1,
      volume: 1.0
    });
  } else {
    // Use existing /api/pronounce endpoint
    fetch('/api/pronounce', { method: 'POST', body: JSON.stringify({ word }) });
  }
}
```

### Local Storage for Offline Word Lists
```javascript
import { Filesystem, Directory } from '@capacitor/filesystem';

async function cacheWordList(wordlist) {
  if (!CapHelper.isNative()) return;
  
  await Filesystem.writeFile({
    path: 'wordlist-cache.json',
    data: JSON.stringify(wordlist),
    directory: Directory.Data
  });
}

async function loadCachedWordList() {
  if (!CapHelper.isNative()) return null;
  
  try {
    const file = await Filesystem.readFile({
      path: 'wordlist-cache.json',
      directory: Directory.Data
    });
    return JSON.parse(file.data);
  } catch {
    return null;
  }
}
```

---

## iOS Setup (macOS Required)

### 1. Prerequisites
- macOS 12+ (Monterey or later)
- Xcode 14+ (free from App Store)
- Apple Developer Account ($99/year for App Store)

### 2. Configure iOS Project
```powershell
# Add iOS platform
npm run cap:add:ios

# Open in Xcode
npm run cap:open:ios
```

### 3. Xcode Configuration
1. **Set Team**: Click project → Signing & Capabilities → Team (select your Apple ID)
2. **Bundle Identifier**: Should be `com.beesmart.spelling`
3. **Deployment Target**: iOS 13.0+
4. **Permissions** (Info.plist):
   ```xml
   <key>NSCameraUsageDescription</key>
   <string>Take photos of word lists for spelling practice</string>
   
   <key>NSPhotoLibraryUsageDescription</key>
   <string>Upload word list images</string>
   ```

### 4. Run on Device
1. Connect iPhone/iPad via USB
2. Select device in Xcode toolbar
3. Click ▶️ Run button

---

## Android Setup

### 1. Prerequisites
- Android Studio (latest version)
- Java JDK 11+

### 2. Configure Android Project
```powershell
# Add Android platform
npm run cap:add:android

# Open in Android Studio
npm run cap:open:android
```

### 3. Android Studio Configuration
1. **Build Tools**: Android Studio will prompt to install required SDKs
2. **Package Name**: Should be `com.beesmart.spelling`
3. **Min SDK**: 22 (Android 5.1)
4. **Permissions** (AndroidManifest.xml - auto-added):
   ```xml
   <uses-permission android:name="android.permission.CAMERA" />
   <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
   <uses-permission android:name="android.permission.INTERNET" />
   ```

### 4. Run on Device/Emulator
1. Enable USB Debugging on Android device
2. Select device in Android Studio
3. Click ▶️ Run button

---

## Testing Checklist

### Core Features (Must Work)
- [ ] Login/Registration
- [ ] Avatar selection (3D models load)
- [ ] Quiz interface (keyboard input)
- [ ] Word pronunciation
- [ ] File upload (word lists)
- [ ] Progress tracking
- [ ] Dashboard (stats, badges)

### Native Features (New)
- [ ] Camera for word list upload
- [ ] Native TTS pronunciation
- [ ] Offline word list caching
- [ ] Push notifications (future)

### Performance
- [ ] 3D avatars load in < 3 seconds
- [ ] Quiz responds in < 100ms
- [ ] Session persists across app restarts

---

## Sync & Deploy Workflow

### After Code Changes
```powershell
# 1. Sync web assets to native projects
npm run cap:sync

# 2. iOS: Re-run in Xcode
npm run cap:open:ios

# 3. Android: Re-run in Android Studio
npm run cap:open:android
```

### Update Native Plugins
```powershell
npm run cap:update
```

---

## App Store Submission

### iOS (Apple App Store)
1. **Build Archive**: Xcode → Product → Archive
2. **Upload**: Window → Organizer → Distribute App
3. **App Store Connect**:
   - Screenshots (6.5" iPhone, 12.9" iPad)
   - Description: "Educational spelling practice for kids"
   - Keywords: spelling, education, kids, learning
   - Age Rating: 4+ (educational)
   - Category: Education

### Android (Google Play Store)
1. **Build APK**: Android Studio → Build → Build Bundle(s) / APK(s)
2. **Google Play Console**:
   - Create app listing
   - Upload APK/AAB
   - Content rating: Everyone
   - Screenshots (phone + tablet)
   - Feature graphic (1024x500)

---

## Troubleshooting

### "No web assets found" Error
```powershell
# Ensure static/ folder has index.html
# Create if missing:
echo '<html><body>Loading...</body></html>' > static/index.html

# Re-sync
npm run cap:sync
```

### 3D Models Don't Load
- Check CORS headers on Railway
- Verify URLs in capacitor.config.json
- Test in browser first: https://your-railway-app.railway.app

### Camera Permission Denied
- iOS: Check Settings → BeeSmart → Camera
- Android: Check App Info → Permissions → Camera

### Session Lost on App Restart
- Capacitor preserves cookies by default
- Verify Flask `SESSION_COOKIE_SECURE = False` for development

---

## Development vs Production

### Development (Local Testing)
```json
{
  "server": {
    "url": "http://localhost:5000",
    "cleartext": true
  }
}
```

### Production (Railway)
```json
{
  "server": {
    "url": "https://beesmartspellingbeeapp-production.up.railway.app"
  }
}
```

---

## Next Steps

1. ✅ Install dependencies: `npm install`
2. ✅ Add iOS platform: `npm run cap:add:ios` (macOS only)
3. ✅ Add Android platform: `npm run cap:add:android`
4. 📝 Test core features in browser first
5. 📱 Test on physical devices
6. 🚀 Submit to app stores

---

## Questions?

**Common Issues**:
- 3D models slow? → Use WiFi for first load (caches after)
- Login not working? → Check Railway is running
- Camera not working? → Verify permissions in device settings

**Need Help?**:
- Capacitor Docs: https://capacitorjs.com/docs
- BeeSmart GitHub: https://github.com/jalex0823/BeeSmartSpellingBeeApp

---

🐝 **Happy Building!** 🐝
